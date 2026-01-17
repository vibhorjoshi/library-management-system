"""
Stripe Payment Integration for Library Management System
Handles payment processing and fine management with comprehensive error handling
"""

import stripe
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Fine, IssuedBook
from .payment_serializers import (
    CreatePaymentIntentSerializer,
    ConfirmPaymentSerializer,
    FineSerializer,
    FineListSerializer,
)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentError(Exception):
    """Custom exception for Stripe payment errors"""
    def __init__(self, message, stripe_error=None):
        self.message = message
        self.stripe_error = stripe_error
        super().__init__(self.message)


def create_payment_intent(amount: Decimal, description: str = "", metadata: dict = None) -> dict:
    """
    Create a Stripe PaymentIntent for the given amount.
    
    Args:
        amount: Amount in rupees (will be converted to paise for Stripe)
        description: Payment description
        metadata: Additional metadata for tracking
    
    Returns:
        PaymentIntent object dict with client_secret
    
    Raises:
        StripePaymentError: If payment intent creation fails
    """
    try:
        # Convert to paise (smallest unit in INR)
        amount_paise = int(amount * 100)
        
        intent = stripe.PaymentIntent.create(
            amount=amount_paise,
            currency='inr',
            description=description,
            metadata=metadata or {},
            payment_method_types=['card'],
        )
        return intent
    except stripe.error.CardError as e:
        raise StripePaymentError(f"Card error: {e.user_message}", e)
    except stripe.error.RateLimitError:
        raise StripePaymentError("Rate limit exceeded. Please try again later.", None)
    except stripe.error.InvalidRequestError as e:
        raise StripePaymentError(f"Invalid request: {str(e)}", e)
    except stripe.error.AuthenticationError:
        raise StripePaymentError("Authentication error with Stripe API", None)
    except stripe.error.APIConnectionError:
        raise StripePaymentError("Failed to connect to Stripe API", None)
    except stripe.error.StripeError as e:
        raise StripePaymentError(f"Stripe error: {str(e)}", e)


def confirm_payment(payment_intent_id: str) -> bool:
    """
    Confirm that a Stripe payment has succeeded.
    
    Args:
        payment_intent_id: Stripe PaymentIntent ID
    
    Returns:
        True if payment succeeded, False otherwise
    
    Raises:
        StripePaymentError: If payment confirmation fails
    """
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return intent.status == 'succeeded'
    except stripe.error.InvalidRequestError:
        raise StripePaymentError(f"Payment intent not found: {payment_intent_id}", None)
    except stripe.error.StripeError as e:
        raise StripePaymentError(f"Failed to confirm payment: {str(e)}", e)


def calculate_overdue_fine(issued_book: IssuedBook) -> Decimal:
    """
    Calculate fine for overdue book at Rs. 2 per day.
    
    Args:
        issued_book: IssuedBook instance
    
    Returns:
        Fine amount in rupees
    """
    if issued_book.return_date:
        # Book already returned, no fine
        return Decimal('0')
    
    due_date = issued_book.due_date
    today = timezone.now().date()
    
    if today <= due_date:
        return Decimal('0')
    
    days_overdue = (today - due_date).days
    fine_amount = Decimal(days_overdue) * Decimal('2')  # Rs. 2 per day
    return fine_amount


def create_or_update_fine(issued_book: IssuedBook = None, user=None, amount: Decimal = None) -> Fine:
    """
    Create or update fine for overdue book.
    
    Args:
        issued_book: IssuedBook instance (optional, for auto-calculation)
        user: User instance (required if issued_book is None)
        amount: Fine amount (optional, calculated if None)
    
    Returns:
        Fine instance
    """
    if issued_book:
        amount = calculate_overdue_fine(issued_book)
        user = issued_book.user
    
    if not user or amount is None:
        raise ValueError("Either issued_book or (user + amount) must be provided")
    
    # Get or create fine
    fine, created = Fine.objects.get_or_create(
        user=user,
        issued_book=issued_book,
        defaults={'amount': amount}
    )
    
    if not created and not fine.paid:
        # Update amount if already created but not paid
        fine.amount = amount
        fine.save()
    
    return fine


# ============================================================================
# API Endpoints
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_for_fine(request):
    """
    API endpoint to create a payment intent for a fine.
    
    Expected POST data:
    {
        "fine_id": 1,
        "amount": 50.00  # Optional, uses fine amount if not provided
    }
    
    Returns:
    {
        "client_secret": "pi_xxx_secret_xxx",
        "fine_id": 1,
        "amount": 50.00,
        "status": "success"
    }
    """
    serializer = CreatePaymentIntentSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': serializer.errors, 'status': 'validation_error'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        fine_id = serializer.validated_data['fine_id']
        amount = serializer.validated_data.get('amount')
        
        # Fetch the fine
        fine = Fine.objects.get(id=fine_id, user=request.user)
        
        # Use provided amount or fine amount
        if amount is None:
            amount = fine.amount
        
        # Create payment intent
        intent = create_payment_intent(
            amount=Decimal(str(amount)) if not isinstance(amount, Decimal) else amount,
            description=f"Fine payment for {request.user.username}",
            metadata={
                'fine_id': str(fine_id),
                'user_id': str(request.user.id),
                'username': request.user.username,
            }
        )
        
        # Update fine with payment intent ID
        fine.payment_intent_id = intent['id']
        fine.save()
        
        response_data = {
            'client_secret': intent['client_secret'],
            'fine_id': fine_id,
            'amount': float(amount),
            'status': 'success'
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    except Fine.DoesNotExist:
        return Response(
            {'error': 'Fine not found', 'status': 'not_found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except StripePaymentError as e:
        return Response(
            {'error': e.message, 'status': 'stripe_error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {'error': str(e), 'status': 'error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment_for_fine(request):
    """
    API endpoint to confirm payment and mark fine as paid.
    
    Expected POST data:
    {
        "payment_intent_id": "pi_xxx_secret_xxx",
        "fine_id": 1  # Optional, can be inferred from payment_intent_id
    }
    
    Returns:
    {
        "status": "paid",
        "message": "Fine payment confirmed",
        "fine": {...}  # FineSerializer data
    }
    """
    serializer = ConfirmPaymentSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': serializer.errors, 'status': 'validation_error'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        payment_intent_id = serializer.validated_data['payment_intent_id']
        
        # Verify payment with Stripe
        if not confirm_payment(payment_intent_id):
            return Response(
                {
                    'error': 'Payment was not successful',
                    'status': 'payment_failed'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use atomic transaction to ensure consistency
        with transaction.atomic():
            # Find fine by payment intent ID
            fine = Fine.objects.get(
                payment_intent_id=payment_intent_id,
                user=request.user
            )
            
            # Mark as paid
            fine.paid = True
            fine.save()
        
        # Serialize response
        fine_serializer = FineSerializer(fine)
        
        return Response(
            {
                'status': 'paid',
                'message': 'Fine payment confirmed and marked as paid',
                'fine': fine_serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    except Fine.DoesNotExist:
        return Response(
            {'error': 'Fine not found', 'status': 'not_found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except StripePaymentError as e:
        return Response(
            {'error': e.message, 'status': 'stripe_error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {'error': str(e), 'status': 'error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_fines(request):
    """
    API endpoint to get all fines for the current user.
    
    Query parameters:
    - paid (bool): Filter by paid status (true/false)
    
    Returns:
    {
        "count": 5,
        "results": [{...}, ...]  # List of FineListSerializer data
    }
    """
    try:
        # Get user's fines
        fines = Fine.objects.filter(user=request.user).order_by('-created_at')
        
        # Filter by paid status if requested
        paid = request.query_params.get('paid')
        if paid is not None:
            paid_bool = paid.lower() == 'true'
            fines = fines.filter(paid=paid_bool)
        
        # Serialize
        serializer = FineListSerializer(fines, many=True)
        
        return Response(
            {
                'count': fines.count(),
                'results': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {'error': str(e), 'status': 'error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_fine_status(request, fine_id):
    """
    API endpoint to get status of a specific fine.
    
    Path parameters:
    - fine_id: ID of the fine
    
    Returns:
    {
        "id": 1,
        "user": 1,
        "user_name": "john",
        "book_title": "Django Guide",
        "amount": 50.00,
        "paid": false,
        "payment_intent_id": "pi_xxx",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
    """
    try:
        # Fetch fine - ensure user owns it
        fine = Fine.objects.get(id=fine_id, user=request.user)
        
        # Serialize
        serializer = FineSerializer(fine)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Fine.DoesNotExist:
        return Response(
            {'error': 'Fine not found', 'status': 'not_found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e), 'status': 'error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
