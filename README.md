# 🛍️ Django E-Commerce Store

A simple e-commerce web application built with Django that supports:

- ✅ User authentication & database
- 💳 Razorpay test mode integration
- 🚀 Deployment on Render

---

## 📦 Features

- User Signup / Login / Logout
- Add/Remove items to Cart
- Product Categories & Details
- Razorpay Payment Integration (Test Mode)
- Admin Dashboard for managing products
- Live Deployment on Render

---

## 🔧 Technologies Used

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS
- **Database:** SQLite (default)
- **Payment Gateway:** Razorpay (test mode)

---

## 🚀 Getting Started Locally

### 1. Clone the Repository
bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
Set Up Virtual Environment
bash
Copy code
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
3. Install Dependencies
bash
Copy code
pip install -r requirements.txt
4. Apply Migrations & Create Superuser
bash
Copy code
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
5. Run Server
bash
Copy code
python manage.py runserver
Now visit http://127.0.0.1:8000 to view the project.

💳 Razorpay Test Mode Setup
Go to Razorpay Dashboard

Create a test account & get your KEY_ID and KEY_SECRET

Add them to your Django settings.py:

python
Copy code
RAZOR_KEY_ID = 'your_key_id'
RAZOR_KEY_SECRET = 'your_key_secret'
🌐 Deployment on Render
1. Push to GitHub
Ensure your project is committed and pushed to GitHub.

2. Set Up Render
Go to Render

Create a new Web Service from your GitHub repo

Add environment variables (e.g. SECRET_KEY, Razorpay keys)

Set build command:

bash
Copy code
pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate
Start command:

bash
Copy code
gunicorn your_project_name.wsgi:application
3. Configure Static Files
Ensure in settings.py:

python
Copy code
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
Then run:

bash
Copy code
python manage.py collectstatic
