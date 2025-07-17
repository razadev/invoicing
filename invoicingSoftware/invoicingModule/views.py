from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db import transaction
from decimal import Decimal
from .models import Invoice, Payment, PaymentTransaction, LedgerEntry
from .serializers import InvoiceSerializer, PaymentCreateSerializer
from django.http import HttpResponse
from django.template.loader import render_to_string
import os
import io
from weasyprint import HTML
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = []
    def get_queryset(self):
        queryset = Invoice.objects.all()
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        invoice = self.get_object()
        if invoice.payments.exists():
            return Response(
                {'error': 'Cannot delete invoice with payments'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is manager for cancellation
        if not request.user.groups.filter(name='Managers').exists():
            return Response(
                {'error': 'Only managers can delete invoices'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        invoice = self.get_object()
        serializer = PaymentCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            payment_amount = serializer.validated_data['amount']
            
            # Check for overpayment
            if payment_amount > invoice.due_amount:
                return Response(
                    {'error': f'Payment amount ({payment_amount}) exceeds due amount ({invoice.due_amount})'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                with transaction.atomic():
                    # Create payment record
                    payment = Payment.objects.create(
                        invoice=invoice,
                        amount=payment_amount,
                        payment_method=serializer.validated_data['payment_method'],
                        reference_number=serializer.validated_data.get('reference_number', ''),
                        notes=serializer.validated_data.get('notes', ''),
                        created_by=request.user
                    )
                    
                    # Create payment transaction
                    PaymentTransaction.objects.create(
                        payment=payment,
                        amount=payment_amount,
                        transaction_type='Payment'
                    )
                    
                    # Update invoice paid amount
                    invoice.paid_amount += payment_amount
                    invoice.save()
                    
                    # Create ledger entries
                    LedgerEntry.objects.create(
                        invoice=invoice,
                        payment=payment,
                        entry_type='Credit',
                        amount=payment_amount,
                        description=f'Payment received via {payment.payment_method}'
                    )
                    
                    return Response({
                        'message': 'Payment processed successfully',
                        'payment_id': payment.id,
                        'new_status': invoice.status,
                        'remaining_due': invoice.due_amount
                    })
                    
            except Exception as e:
                return Response(
                    {'error': f'Payment processing failed: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        # Only managers can cancel invoices
        if not request.user.groups.filter(name='Managers').exists():
            return Response(
                {'error': 'Only managers can cancel invoices'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        invoice = self.get_object()
        
        if invoice.status != 'Unpaid':
            return Response(
                {'error': 'Only unpaid invoices can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.status = 'Cancelled'
        invoice.save()
        
        return Response({'message': 'Invoice cancelled successfully'})
# Simple version for basic needs
def generate_invoice_pdf_simple(request, invoice_id):
    """
    Simple PDF generation using canvas
    """
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id)
        
        # Create response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_id}.pdf"'
        
        # Create PDF directly to response
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        
        # Title
        p.setFont("Helvetica-Bold", 20)
        p.drawString(100, height - 100, f"INVOICE #{invoice.id}")
        
        # Invoice details
        p.setFont("Helvetica", 12)
        y_position = height - 150
        
        fields = [
            ('Invoice ID:', str(invoice.id)),
            ('Date:', invoice.date.strftime('%Y-%m-%d') if hasattr(invoice, 'date') else 'N/A'),
            ('Customer:', str(invoice.customer) if hasattr(invoice, 'customer') else 'N/A'),
            ('Status:', invoice.status if hasattr(invoice, 'status') else 'N/A'),
        ]
        
        for label, value in fields:
            p.drawString(100, y_position, f"{label} {value}")
            y_position -= 25
        
        # Total
        if hasattr(invoice, 'total_amount'):
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, y_position - 30, f"Total: ${invoice.total_amount}")
        
        p.save()
        return response
        
    except Invoice.DoesNotExist:
        return HttpResponse("Invoice not found", status=404)
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)

def generate_invoice_pdf(request,invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
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

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class InvoiceListView(LoginRequiredMixin, TemplateView):
    template_name = 'invoices/list.html'