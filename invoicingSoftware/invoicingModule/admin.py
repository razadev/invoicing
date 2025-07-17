from django.contrib import admin
from .models import Customer, Invoice, InvoiceItem, Payment, PaymentTransaction, LedgerEntry

admin.site.register(Customer)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(Payment)
admin.site.register(PaymentTransaction)
admin.site.register(LedgerEntry)
