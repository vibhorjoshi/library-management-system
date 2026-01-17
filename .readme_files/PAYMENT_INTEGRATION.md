# Payment Integration & MODULE 2 Complete ✅

## Status: MODULE 2 (Payments with Stripe) - 100% Complete

This document covers the complete implementation of Stripe payment processing and fine management for the library system.

---

## Overview

**MODULE 2** implements PCI-DSS compliant payment processing using Stripe's PaymentIntent API. The system handles:

- Fine creation and calculation (Rs. 2/day overdue)
- Payment intent generation for frontend integration
- Payment confirmation and atomic transactions
- Fine status tracking with Stripe payment IDs
- REST API endpoints for fine management
- Comprehensive error handling and validation

---

## Architecture

### Payment Flow

```
Student Portal (React)
        ↓
POST /api/payments/create-intent/ (Stripe API Key)
        ↓
Django Backend → Stripe API (Create PaymentIntent)
        ↓
Returns: client_secret, fine_id, amount
        ↓
Frontend: Stripe.js handles card collection
        ↓
POST /api/payments/confirm/ (payment_intent_id)
        ↓
Django: Verify with Stripe API
        ↓
Mark Fine as Paid (Atomic Transaction)
        ↓
Database Updated ✓
```

### Database Schema

**Fine Model (Enhanced for Stripe)**
```python
class Fine(models.Model):
    user = ForeignKey(User)
    issued_book = ForeignKey(IssuedBook, null=True, blank=True)
    amount = DecimalField(max_digits=10, decimal_places=2)
    paid = BooleanField(default=False)
    payment_intent_id = CharField(max_length=255, blank=True, default='')  # NEW
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

---

## API Endpoints

### 1. Create Payment Intent

**Endpoint:** `POST /api/payments/create-intent/`

**Authentication:** Required (JWT token)

**Request Body:**
```json
{
    "fine_id": 1,
    "amount": 50.00  // Optional, uses fine amount if not provided
}
```

**Success Response (201):**
```json
{
    "client_secret": "pi_1234567890_secret_abc123",
    "fine_id": 1,
    "amount": 50.00,
    "status": "success"
}
```

**Error Responses:**
- `400` - Missing/invalid fine_id, fine already paid
- `404` - Fine not found
- `500` - Stripe API error

**Backend Logic:**
1. Validate request with `CreatePaymentIntentSerializer`
2. Fetch fine for authenticated user
3. Create Stripe PaymentIntent (converts to paise)
4. Store payment_intent_id in database
5. Return client_secret to frontend

---

### 2. Confirm Payment

**Endpoint:** `POST /api/payments/confirm/`

**Authentication:** Required (JWT token)

**Request Body:**
```json
{
    "payment_intent_id": "pi_1234567890_secret_abc123"
}
```

**Success Response (200):**
```json
{
    "status": "paid",
    "message": "Fine payment confirmed and marked as paid",
    "fine": {
        "id": 1,
        "user": 1,
        "user_name": "john",
        "book_title": "Django Guide",
        "amount": 50.00,
        "paid": true,
        "payment_intent_id": "pi_1234567890_secret_abc123",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T11:45:00Z"
    }
}
```

**Error Responses:**
- `400` - Invalid payment_intent_id format, payment not succeeded
- `404` - Fine not found
- `500` - Stripe API error

**Backend Logic:**
1. Validate payment_intent_id format
2. Query Stripe API to verify payment succeeded
3. Atomic transaction:
   - Mark fine as paid in database
   - Update fine updated_at timestamp
4. Return serialized fine details

---

### 3. Get User's Fines

**Endpoint:** `GET /api/fines/`

**Authentication:** Required (JWT token)

**Query Parameters:**
- `paid` (optional) - Filter by paid status: `true` or `false`

**Example Requests:**
```
GET /api/fines/                    # All user's fines
GET /api/fines/?paid=false         # Unpaid fines only
GET /api/fines/?paid=true          # Paid fines only
```

**Success Response (200):**
```json
{
    "count": 3,
    "results": [
        {
            "id": 1,
            "user_name": "john",
            "book_title": "Django Guide",
            "amount": 50.00,
            "paid": false,
            "created_at": "2024-01-15T10:30:00Z"
        },
        {
            "id": 2,
            "user_name": "john",
            "book_title": "Python Basics",
            "amount": 30.00,
            "paid": true,
            "created_at": "2024-01-10T14:20:00Z"
        }
    ]
}
```

**Error Responses:**
- `500` - Database error

---

### 4. Get Fine Status

**Endpoint:** `GET /api/fines/<fine_id>/`

**Authentication:** Required (JWT token)

**Path Parameters:**
- `fine_id` (required) - ID of the fine to fetch

**Success Response (200):**
```json
{
    "id": 1,
    "user": 1,
    "user_name": "john",
    "book_title": "Django Guide",
    "amount": 50.00,
    "days_overdue": 25,
    "paid": false,
    "payment_intent_id": "",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `404` - Fine not found or not owned by user
- `500` - Database error

---

## Helper Functions

### `calculate_overdue_fine(issued_book: IssuedBook) → Decimal`

Calculates fine amount at Rs. 2 per day overdue.

```python
from library.payments import calculate_overdue_fine
from library.models import IssuedBook

issued_book = IssuedBook.objects.get(id=1)
fine_amount = calculate_overdue_fine(issued_book)  # Returns Decimal('50.00')
```

**Logic:**
- Returns 0 if book already returned
- Returns 0 if due_date not passed
- Calculates: (today - due_date) * 2 in rupees

---

### `create_or_update_fine(issued_book, user, amount) → Fine`

Creates or updates a fine record.

```python
from library.payments import create_or_update_fine
from library.models import IssuedBook, Fine

# Option 1: Auto-calculate from issued book
fine = create_or_update_fine(issued_book=issued_book)

# Option 2: Manual amount
fine = create_or_update_fine(
    user=request.user,
    amount=Decimal('100.00')
)
```

---

### `create_payment_intent(amount, description, metadata) → dict`

Creates a Stripe PaymentIntent directly.

```python
from library.payments import create_payment_intent
from decimal import Decimal

intent = create_payment_intent(
    amount=Decimal('50.00'),
    description='Fine for overdue book',
    metadata={
        'fine_id': '1',
        'user_id': '5',
    }
)
# Returns: {'id': 'pi_...', 'client_secret': 'pi_..._secret_...', ...}
```

**Error Handling:**
- Raises `StripePaymentError` for:
  - Card errors
  - Rate limits
  - Invalid requests
  - Authentication failures
  - Network failures

---

### `confirm_payment(payment_intent_id: str) → bool`

Verifies payment status with Stripe.

```python
from library.payments import confirm_payment

is_paid = confirm_payment('pi_1234567890_secret_abc123')
if is_paid:
    # Mark fine as paid
    fine.paid = True
    fine.save()
```

---

## Serializers

### `CreatePaymentIntentSerializer`
- Validates `fine_id` exists and belongs to user
- Validates fine not already paid
- Optional `amount` field

### `ConfirmPaymentSerializer`
- Validates `payment_intent_id` format (must start with `pi_`)

### `FineSerializer`
- Full fine details with related book info
- Calculates `days_overdue`

### `FineListSerializer`
- Lightweight version for list endpoints

---

## Setup & Configuration

### 1. Environment Variables

Create/update `.env` file:

```bash
# Stripe Keys (from https://dashboard.stripe.com/apikeys)
STRIPE_PUBLIC_KEY=pk_test_your_public_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
```

### 2. Django Settings

Already added to `library_config/settings.py`:

```python
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
```

### 3. Install Dependencies

```bash
pip install stripe>=14.0.0
```

Verify installation:
```bash
python manage.py shell -c "import stripe; print(stripe.__version__)"
```

---

## Usage Examples

### Example 1: Student Paying Fine from React Frontend

```javascript
// 1. Create payment intent
const response = await fetch('http://localhost:8000/api/payments/create-intent/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        fine_id: 1,
        amount: 50.00
    })
});

const { client_secret, fine_id } = await response.json();

// 2. Use Stripe.js to handle card payment
const stripe = Stripe('pk_test_...');
const elements = stripe.elements();
const cardElement = elements.create('card');

const { paymentIntent, error } = await stripe.confirmCardPayment(
    client_secret,
    {
        payment_method: {
            card: cardElement,
            billing_details: { name: 'John Doe' }
        }
    }
);

// 3. Confirm payment with backend
if (paymentIntent.status === 'succeeded') {
    const confirmResponse = await fetch('http://localhost:8000/api/payments/confirm/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            payment_intent_id: paymentIntent.id
        })
    });
    
    const result = await confirmResponse.json();
    console.log('Payment confirmed:', result.fine);
}
```

### Example 2: Check Fine Status

```python
# Backend: Check if student has unpaid fines
from library.models import Fine

unpaid_fines = Fine.objects.filter(
    user=request.user,
    paid=False
).order_by('-created_at')

for fine in unpaid_fines:
    print(f"Fine #{fine.id}: Rs. {fine.amount} (created {fine.created_at})")
```

### Example 3: Admin Dashboard Query

```python
from django.db.models import Sum
from library.models import Fine

# Total outstanding fines
total_outstanding = Fine.objects.filter(paid=False).aggregate(
    total=Sum('amount')
)['total']

# Recently paid fines
paid_today = Fine.objects.filter(
    paid=True,
    updated_at__date=timezone.now().date()
).count()
```

---

## Testing Payment Flow

### Test Stripe Keys

Get test keys from: https://dashboard.stripe.com/test/apikeys

### Test Card Numbers

```
Visa: 4242 4242 4242 4242
MasterCard: 5555 5555 5555 4444
Amex: 3782 822463 10005

Expiry: Any future date
CVC: Any 3 digits
```

### cURL Test Examples

```bash
# 1. Get JWT Token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"student1","password":"pass123"}'

# 2. Create Payment Intent
curl -X POST http://localhost:8000/api/payments/create-intent/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fine_id":1}'

# 3. Get User Fines
curl -X GET "http://localhost:8000/api/fines/?paid=false" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Get Fine Status
curl -X GET http://localhost:8000/api/fines/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Error Handling

### Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `STRIPE_SECRET_KEY not configured` | Missing env var | Add to `.env` file |
| `Invalid API Key` | Wrong Stripe key | Use correct test/live key |
| `Card error: Your card declined` | Test card used | Use correct test card |
| `Fine not found (404)` | Wrong fine_id | Verify fine exists for user |
| `Payment already made` | Fine marked paid | Fine already processed |

### StripePaymentError Details

```python
try:
    intent = create_payment_intent(amount=50)
except StripePaymentError as e:
    print(f"Error: {e.message}")
    if e.stripe_error:
        print(f"Stripe details: {e.stripe_error}")
```

---

## Security Considerations

✅ **Implemented:**
- JWT authentication on all payment endpoints
- User-level fine ownership validation
- Atomic database transactions for payment confirmation
- Stripe PaymentIntent (no card data stored)
- HTTPS only for production (Django settings)
- Environment variables for API keys

✅ **Best Practices:**
- Never log sensitive payment data
- Use Stripe webhooks for async payment confirmation (Phase 3+)
- Implement rate limiting on payment endpoints
- Validate all user inputs before Stripe API calls

---

## Next Steps

### For Production Deployment

1. **Get Live Stripe Keys**
   - Go to https://stripe.com
   - Complete business verification
   - Get live API keys

2. **Update Environment**
   ```bash
   STRIPE_SECRET_KEY=sk_live_your_live_key
   STRIPE_PUBLIC_KEY=pk_live_your_live_key
   ```

3. **Test with Real Payments**
   - Use real test cards
   - Verify payment processing
   - Monitor Stripe dashboard

4. **Implement Webhooks** (Optional)
   - Listen to `payment_intent.succeeded`
   - Handle failed payments
   - Send payment confirmation emails

### Upcoming Modules

- **MODULE 3**: Analytics Dashboard (fine statistics, payment trends)
- **MODULE 4**: Mobile App (React Native payment flow)
- **MODULE 5**: Multi-college SaaS (per-college payment processing)

---

## Summary

**MODULE 2 Completion Checklist:**

- ✅ Stripe PaymentIntent API integration
- ✅ 4 REST API endpoints (create, confirm, list, status)
- ✅ Fine model Stripe field support
- ✅ Comprehensive serializers
- ✅ Error handling & validation
- ✅ Atomic transactions
- ✅ Django migrations applied
- ✅ Environment configuration
- ✅ Documentation & examples

**Files Modified/Created:**
- `library/payments.py` (440 lines) - Complete Stripe integration
- `library/payment_serializers.py` (95 lines) - Request/response validation
- `library/urls.py` - 4 payment route mappings
- `library/models.py` - Fine model payment_intent_id field
- `library_config/settings.py` - Stripe configuration
- `requirements.txt` - stripe dependency

**Production Ready:** Yes, with live Stripe keys

---

**Ready to move to MODULE 3: Analytics Dashboard!** 📊
