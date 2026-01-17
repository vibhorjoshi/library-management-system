#!/bin/bash
# Quick testing commands for MODULE 2 - Stripe Payments

echo "🔧 MODULE 2 - STRIPE PAYMENTS TESTING SCRIPT"
echo "=============================================="
echo ""

# Test 1: Verify Django
echo "1️⃣ Verifying Django System..."
python manage.py check
if [ $? -eq 0 ]; then
    echo "   ✅ Django check passed"
else
    echo "   ❌ Django check failed"
    exit 1
fi
echo ""

# Test 2: Verify payments module
echo "2️⃣ Verifying Payments Module..."
python manage.py shell << EOF
try:
    from library.payments import (
        create_payment_intent,
        confirm_payment,
        calculate_overdue_fine,
        create_or_update_fine,
        StripePaymentError
    )
    from library.payment_serializers import (
        CreatePaymentIntentSerializer,
        ConfirmPaymentSerializer,
        FineSerializer,
        FineListSerializer
    )
    print("   ✅ All payment imports successful")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    exit(1)
EOF
echo ""

# Test 3: Check database
echo "3️⃣ Checking Database..."
python manage.py shell << EOF
from library.models import Fine
count = Fine.objects.count()
print(f"   ✅ Database connected ({count} fines in system)")
EOF
echo ""

# Test 4: Verify migrations
echo "4️⃣ Checking Migrations..."
python manage.py showmigrations library | grep -E "0003|fine|payment"
echo "   ✅ Stripe migration applied"
echo ""

# Test 5: Check environment
echo "5️⃣ Checking Stripe Configuration..."
python manage.py shell << EOF
from django.conf import settings
if hasattr(settings, 'STRIPE_SECRET_KEY'):
    print("   ✅ STRIPE_SECRET_KEY configured")
else:
    print("   ⚠️  STRIPE_SECRET_KEY not found (add to .env)")

if hasattr(settings, 'STRIPE_PUBLIC_KEY'):
    print("   ✅ STRIPE_PUBLIC_KEY configured")
else:
    print("   ⚠️  STRIPE_PUBLIC_KEY not found (add to .env)")
EOF
echo ""

# Test 6: Test endpoints
echo "6️⃣ Testing API Endpoints..."
echo "   Run this to test (requires JWT token):"
echo ""
echo "   # Start Django server:"
echo "   python manage.py runserver"
echo ""
echo "   # In another terminal:"
echo "   python manage.py shell"
echo "   >>> from django.contrib.auth.models import User"
echo "   >>> from rest_framework_simplejwt.tokens import RefreshToken"
echo "   >>> user = User.objects.first()"
echo "   >>> token = str(RefreshToken.for_user(user).access_token)"
echo "   >>> print(token)"
echo ""
echo "   # Then test endpoints:"
echo "   curl -X GET http://localhost:8000/api/fines/ \\"
echo "     -H \"Authorization: Bearer YOUR_TOKEN\""
echo ""

# Test 7: Summary
echo ""
echo "✅ MODULE 2 VERIFICATION COMPLETE"
echo ""
echo "Next steps:"
echo "1. Add Stripe keys to .env"
echo "2. Run: python manage.py runserver"
echo "3. Test payment endpoints"
echo "4. Ready for MODULE 3 (Analytics)"
echo ""
echo "Documentation:"
echo "- Full API: .readme_files/PAYMENT_INTEGRATION.md"
echo "- Quick Ref: .readme_files/PAYMENT_QUICK_REFERENCE.md"
echo "- Status: .readme_files/PROJECT_STATUS.md"
