from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

@csrf_exempt
@require_POST
def payment_webhook(request):
    """Handle payment gateway webhooks"""
    try:
        payload = json.loads(request.body)
        
        # Process webhook based on payment gateway
        if payload.get('event') == 'payment.success':
            # Handle successful payment
            transaction_id = payload.get('transaction_id')
            amount = payload.get('amount')
            
            # Update payment record
            # Implementation depends on your payment gateway
            
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=400)

# settings.py additions
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'invoicingModule',  # Replace with your app name
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}