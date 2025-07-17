from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return self.name


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('Unpaid', 'Unpaid'),
        ('Partial', 'Partial'),
        ('Paid', 'Paid'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date_issued = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unpaid')

    def update_status(self):
        total_paid = sum(payment.amount for payment in self.payments.all())
        if total_paid >= self.total_amount:
            self.status = 'Paid'
        elif total_paid > 0:
            self.status = 'Partial'
        else:
            self.status = 'Unpaid'
        self.save()

    def __str__(self):
        return f"Invoice {self.id} - {self.customer.name}"


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="payments", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    method = models.CharField(max_length=50, default="Cash")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invoice.update_status()

    def __str__(self):
        return f"Payment {self.id} for Invoice {self.invoice.id}"
