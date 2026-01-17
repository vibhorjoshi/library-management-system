# Payment System Quick Reference

## Setup (30 seconds)

```bash
# 1. Install dependency
pip install stripe

# 2. Add to .env
STRIPE_PUBLIC_KEY=pk_test_51234567890...
STRIPE_SECRET_KEY=sk_test_51234567890...

# 3. Run migrations
python manage.py migrate

# Done! ✓
```

---

## API Endpoints

### Create Payment (Get client_secret)

```bash
curl -X POST http://localhost:8000/api/payments/create-intent/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fine_id": 1, "amount": 50.00}'

# Response:
# {
#   "client_secret": "pi_123_secret_abc",
#   "fine_id": 1,
#   "amount": 50.00,
#   "status": "success"
# }
```

### Confirm Payment

```bash
curl -X POST http://localhost:8000/api/payments/confirm/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"payment_intent_id": "pi_123_secret_abc"}'

# Response:
# {
#   "status": "paid",
#   "message": "Fine payment confirmed",
#   "fine": {...}
# }
```

### List Fines

```bash
# All fines
curl -X GET http://localhost:8000/api/fines/ \
  -H "Authorization: Bearer $TOKEN"

# Unpaid only
curl -X GET "http://localhost:8000/api/fines/?paid=false" \
  -H "Authorization: Bearer $TOKEN"
```

### Get One Fine

```bash
curl -X GET http://localhost:8000/api/fines/1/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Code Usage

### Calculate Fine

```python
from library.payments import calculate_overdue_fine
from library.models import IssuedBook

issued_book = IssuedBook.objects.get(id=1)
amount = calculate_overdue_fine(issued_book)  # Decimal('100.00')
```

### Create Fine

```python
from library.payments import create_or_update_fine

fine = create_or_update_fine(issued_book=issued_book)
# Saves to DB, returns Fine object
```

### Handle Payment Error

```python
from library.payments import create_payment_intent, StripePaymentError

try:
    intent = create_payment_intent(amount=50.00)
except StripePaymentError as e:
    print(f"Payment failed: {e.message}")
```

---

## Test Cards

| Type | Number | Result |
|------|--------|--------|
| Visa | 4242 4242 4242 4242 | ✓ Success |
| MC | 5555 5555 5555 4444 | ✓ Success |
| Declined | 4000 0000 0000 0002 | ✗ Declined |

**Expiry:** Any future date  
**CVC:** Any 3 digits

---

## Files

| File | Purpose | Lines |
|------|---------|-------|
| `payments.py` | Payment logic | 440 |
| `payment_serializers.py` | Validation | 95 |
| `urls.py` | Routes | +4 |
| `models.py` | Fine.payment_intent_id | +1 |

---

## Database

```python
# Fine model has:
- id
- user (ForeignKey)
- issued_book (ForeignKey, nullable)
- amount (Decimal)
- paid (Boolean)
- payment_intent_id (CharField) ← NEW
- created_at
- updated_at
```

---

## Errors

| Error | Fix |
|-------|-----|
| `stripe not found` | `pip install stripe` |
| `STRIPE_SECRET_KEY not configured` | Add to `.env` |
| `Fine not found` | Check fine_id exists |
| `Fine already paid` | Already processed |
| `Card declined` | Use valid test card |

---

## React Integration Example

```javascript
// Frontend
const response = await fetch('/api/payments/create-intent/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ fine_id: 1 })
});

const { client_secret } = await response.json();

// Use Stripe.js to charge card
const { paymentIntent } = await stripe.confirmCardPayment(client_secret);

if (paymentIntent.status === 'succeeded') {
    // Confirm with backend
    await fetch('/api/payments/confirm/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ payment_intent_id: paymentIntent.id })
    });
}
```

---

## Status Check

```bash
# Test if everything works
python manage.py shell -c "
from library.payments import create_payment_intent
print('✓ Payments ready')
"
```

---

## Documentation

- Full docs: `PAYMENT_INTEGRATION.md`
- Completion report: `MODULE_2_COMPLETION.md`
- This file: `PAYMENT_QUICK_REFERENCE.md`

---

**Ready to use!** Start with test Stripe keys, then upgrade to live keys for production.
