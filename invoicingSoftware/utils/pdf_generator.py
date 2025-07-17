from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
import io

def generate_invoice_pdf(invoice):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Header
    p.drawString(100, 750, f"Invoice #{invoice.invoice_number}")
    p.drawString(100, 730, f"Date: {invoice.invoice_date}")
    p.drawString(100, 710, f"Due Date: {invoice.due_date}")
    
    # Customer info
    p.drawString(100, 680, f"Bill To:")
    p.drawString(100, 660, f"{invoice.customer.name}")
    p.drawString(100, 640, f"{invoice.customer.email}")
    p.drawString(100, 620, f"{invoice.customer.address}")
    
    # Items
    y = 580
    p.drawString(100, y, "Description")
    p.drawString(300, y, "Quantity")
    p.drawString(400, y, "Unit Price")
    p.drawString(500, y, "Total")
    
    y -= 20
    for item in invoice.items.all():
        p.drawString(100, y, item.description)
        p.drawString(300, y, str(item.quantity))
        p.drawString(400, y, f"${item.unit_price}")
        p.drawString(500, y, f"${item.total_price}")
        y -= 20
    
    # Totals
    y -= 20
    p.drawString(400, y, f"Subtotal: ${invoice.subtotal}")
    y -= 20
    p.drawString(400, y, f"Tax: ${invoice.tax_amount}")
    y -= 20
    p.drawString(400, y, f"Total: ${invoice.total_amount}")
    y -= 20
    p.drawString(400, y, f"Paid: ${invoice.paid_amount}")
    y -= 20
    p.drawString(400, y, f"Due: ${invoice.due_amount}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer