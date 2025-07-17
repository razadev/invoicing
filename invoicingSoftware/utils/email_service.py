from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def send_invoice_email(invoice):
    subject = f'Invoice #{invoice.invoice_number}'
    message = render_to_string('emails/invoice_email.html', {'invoice': invoice})
    
    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [invoice.customer.email]
    )
    
    # Attach PDF
    pdf_buffer = generate_invoice_pdf(invoice)
    email.attach(f'invoice_{invoice.invoice_number}.pdf', pdf_buffer.read(), 'application/pdf')
    
    email.send()