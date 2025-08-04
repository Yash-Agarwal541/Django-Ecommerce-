from django.contrib import admin
from django.urls import path
from store.views import index, sign_up, LoginUse, add_to_cart, payment_with_razor
from .views import all_products, cart, category_page, product_detail, remove_from_cart
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('cart', cart, name='cart'),
    path('signup', sign_up, name='signup'),
    path('login', LoginUse.as_view(), name='login'),
    path('logout', LogoutView.as_view(next_page='index'), name='logout'),
    path('<slug:product>', add_to_cart, name='create_cart'),
    path('cart/create-checkout-session', payment_with_razor, name='razorpay_payment'),
    path('cart/add/<slug:product>', add_to_cart, name='add_cart'),
    path('cart/remove/<slug:product>/', remove_from_cart, name='remove_from_cart'),
    path('category/<slug:category_slug>', category_page, name='category_page'),
    path('product/<slug:slug>/', product_detail, name='product_detail'),
    path('products/all/', all_products, name='all_products'),
]


