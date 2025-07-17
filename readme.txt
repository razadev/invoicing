I have python setup on my localhost with different versions, i created virtual environment with python 3.10 version.

py -3.10 -m venv env
env\Scripts\activate

django-admin startproject invoicingSoftware
cd invoicingSoftware
edit settings.py
update database configuration
add lines 
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser
python manage.py collectstatic

python manage.py startapp invoicingModule

cd invoicingModule
edit admin.py
Add
from .models import *
admin.site.register(Client)

edit models.py
define table structure

cd invoicingSoftware
edit settings.py
update installed apps

python manage.py makemigrations invoicingModule
python manage.py makemigrations
python manage.py migrate

python manage.py runserver 0.0.0.0:5000

pgadmin4
user postgres
password test@123
port 5432

superadmin root
password test@123



# Quick Setup Commands:
# 1. pip install -r requirements.txt
# 2. python manage.py makemigrations
# 3. python manage.py migrate
# 4. python manage.py createsuperuser
# 5. python manage.py create_sample_data
# 6. python manage.py runserver

# API Endpoints:
# GET /api/invoices/ - List all invoices
# GET /api/invoices/?status=Unpaid - Filter by status
# POST /api/invoices/ - Create new invoice
# GET /api/invoices/{id}/ - Get specific invoice
# POST /api/invoices/{id}/pay/ - Make payment
# POST /api/invoices/{id}/cancel/ - Cancel invoice (managers only)
# DELETE /api/invoices/{id}/ - Delete invoice (managers only, no payments)

# Frontend URLs:
# / - Invoice list page
# /webhook/payment/ - Payment webhook handler