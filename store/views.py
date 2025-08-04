from itertools import product
from django import forms
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from .models import Category, Customer, Product
from django.contrib.auth.models import User, auth
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate, logout
from .models import SessionCart, ItemCard
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required



def index(request):
    products = Product.get_products()
    categories = Category.objects.all()

    # Build dictionary of category name → list of products
    category_sliders = {}
    for category in categories:
        category_products = Product.objects.filter(category=category)[:10]  # limit to 10 for slider
        if category_products.exists():
            category_sliders[category.name] = category_products

    return render(request, 'index.html', {
        'products': products[:6],  # only show 6 on index
        'categories': categories,
        'category_sliders': category_sliders,
    })
@login_required
def cart(request):
    user = request.user
    total = 0
    items = ItemCard.objects.filter(user = request.user)
    for item in items:
        total += item.total_cart_value 
    return render(request, 'cart.html', {'items': items, 'total': total})

class NewForm(forms.Form):
    name = forms.CharField(
        min_length=4, max_length=40,
        widget=forms.TextInput(attrs={
            'type': "text", 'class': "form-control signup-input", 
            'id': "name", 'placeholder': "Yash Agarwal"
        })
    )
    password = forms.CharField(
        min_length=4, max_length=12,
        widget=forms.TextInput(attrs={
            "type": "password", "class": "form-control signup-input", 
            "id": "password", "placeholder": "********"
        })
    )
    email = forms.EmailField(
        max_length=40,
        widget=forms.TextInput(attrs={
            "type": "email", "class": "form-control signup-input", 
            "id": "email", "placeholder": "you@example.com"
        })
    )
    address = forms.CharField(
        max_length=3000,
        widget=forms.TextInput(attrs={
            "type": "text", "class": "form-control signup-input", 
            "id": "address", "placeholder": "1234 Main St"
        })
    )
    city = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            "type": "text", "class": "form-control signup-input", 
            "id": "city"
        })
    )
    zip = forms.IntegerField(
        widget=forms.TextInput(attrs={
            "type": "number", "class": "form-control signup-input", 
            "id": "zip"
        })
    )

def sign_up(request):
    if request.method == 'POST':
        form = NewForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['name'], 
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            user.save()

            customer = Customer(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                zip=form.cleaned_data['zip']
            )
            customer.save()

            return redirect('index')
        else:
            # Form not valid, return form with errors
            return render(request, 'signup_form.html', {'form': form})

    # GET request, send empty form
    return render(request, 'signup_form.html', {'form': NewForm()})

class LoginUse(LoginView):
    def __init__(self):
        self.form = NewForm()

    def get(self, request):
        return render(request, 'login.html', {'form': self.form})

    def post(self, request):
        form = NewForm(request.POST)
        form.is_valid()
        username = form.cleaned_data['name']
        password = form.cleaned_data['password']
        user = auth.authenticate(username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'form': self.form})

def _cart_id(request):
    cart = request.session.session_key
    try:
        session = SessionCart.objects.get(user = request.user)
        return session.spc_id
    except SessionCart.DoesNotExist:
        cart = request.session.create()
        session = SessionCart(spc_id = request.session.session_key, user = request.user)
        session.save()
        return session.spc_id
    
def add_to_cart(request, product):
    product = Product.objects.get(slug=product)
    user = request.user  # ✅ This is the correct object to use

    cart, created = SessionCart.objects.get_or_create(
        spc_id=_cart_id(request),
        defaults={'user': user}
    )

    if not created and not cart.user:
        cart.user = user
        cart.save()

    try:
        cart_items = ItemCard.objects.get(slug=product.slug, product=product, cart=cart, user=user)
        cart_items.product_quantity += 1
        cart_items.total_cart_value += product.price
        cart_items.save()
    except ItemCard.DoesNotExist:
        ItemCard.objects.create(
            slug=product.slug,
            user=user,  # ✅ Correct User object here
            active=True,
            product=product,
            cart=cart,
            product_quantity=1,
            product_price=product.price,
            product_image=product.product_image,
            total_cart_value=product.price
        )
    messages.success(request, "✅ Item added to cart. <a href='/cart' class='text-dark font-weight-bold'>View Cart</a>")
    
    next_url = request.GET.get('next')
    return redirect(next_url) if next_url else redirect('index')


    


def payment_with_razor(request):
    if request.method == "POST":
        client = razorpay.Client(auth=(settings.RAZOR_PUB_KEY, settings.RAZOR_SEC_KEY))

        # Example amount (in paise): ₹200 = 20000 paise
        total = 0
        items = ItemCard.objects.filter(user=request.user)
        for item in items:
            total += item.total_cart_value

        if total == 0:
            return HttpResponse("Cart is empty", status=400)

        # Razorpay needs amount in paise
        amount = int(total * 100)
        currency = 'INR'
        order = client.order.create({
            'amount': amount,
            'currency': currency,
            'payment_capture': '1'
        })

        return render(request, 'payment.html', {
            'order_id': order['id'],
            'amount': total,
            'razorpay_key_id': settings.RAZOR_PUB_KEY  # Corrected key usage
        })

    return render(request, 'checkout.html')

def remove_from_cart(request, product):
    product = get_object_or_404(Product, slug=product)
    session_key = _cart_id(request)
    user = request.user if request.user.is_authenticated else None

    try:
        cart = SessionCart.objects.get(spc_id=session_key, user=user)
        cart_item = ItemCard.objects.get(product=product, cart=cart)
        
        if cart_item.product_quantity > 1:
            cart_item.product_quantity -= 1
            cart_item.total_cart_value -= cart_item.product_price
            cart_item.save()
        else:
            cart_item.delete()

    except (SessionCart.DoesNotExist, ItemCard.DoesNotExist):
        pass

    next_url = request.GET.get('next')
    return redirect(next_url) if next_url else redirect('index')


def category_page(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)

    return render(request, 'category_page.html', {
        'category': category,
        'products': products
    })
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'product_detail.html', {'product': product})

def all_products(request):
    products = Product.get_products()
    return render(request, 'all_products.html', {'products': products})
