from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from decimal import Decimal
import random
from datetime import date, timedelta
from ...models import Customer, Invoice, InvoiceItem, Payment

class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        # Create user groups
        managers_group, created = Group.objects.get_or_create(name='Managers')
        
        # Create sample customers
        customers = []
        for i in range(5):
            customer = Customer.objects.create(
                name=f'Customer {i+1}',
                email=f'customer{i+1}@example.com',
                phone=f'123-456-{7890+i}',
                address=f'{i+1}23 Main St, City, State 12345'
            )
            customers.append(customer)
        
        # Create sample invoices
        for i in range(10):
            invoice = Invoice.objects.create(
                customer=random.choice(customers),
                subtotal=Decimal(str(random.randint(100, 1000))),
                tax_rate=Decimal('10.00'),
                invoice_date=date.today() - timedelta(days=random.randint(1, 30)),
                due_date=date.today() + timedelta(days=random.randint(1, 30))
            )
            
            # Add invoice items
            for j in range(random.randint(1, 5)):
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=f'Item {j+1}',
                    quantity=Decimal(str(random.randint(1, 10))),
                    unit_price=Decimal(str(random.randint(10, 100)))
                )
            
            # Add some payments
            if random.choice([True, False]):
                payment_amount = invoice.total_amount * Decimal(str(random.uniform(0.3, 1.0)))
                Payment.objects.create(
                    invoice=invoice,
                    amount=payment_amount,
                    payment_method=random.choice(['Cash', 'Card', 'Bank Transfer'])
                )
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
