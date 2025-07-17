from django.contrib import admin
from .models import Customer, Invoice, Payment

admin.site.register(Customer)
admin.site.register(Invoice)
admin.site.register(Payment)