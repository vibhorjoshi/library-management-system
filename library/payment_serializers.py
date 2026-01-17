from rest_framework import serializers
from .models import Fine, IssuedBook


class FineSerializer(serializers.ModelSerializer):
    """Serializer for fine details including payment status"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    book_title = serializers.CharField(source='issued_book.book.title', read_only=True, required=False)
    days_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Fine
        fields = [
            'id',
            'user',
            'user_name',
            'book_title',
            'amount',
            'days_overdue',
            'paid',
            'payment_intent_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'payment_intent_id']
    
    def get_days_overdue(self, obj):
        """Calculate days overdue from issued book"""
        if obj.issued_book:
            from django.utils import timezone
            from datetime import timedelta
            due_date = obj.issued_book.due_date
            days_overdue = (timezone.now().date() - due_date).days
            return max(0, days_overdue)
        return 0


class CreatePaymentIntentSerializer(serializers.Serializer):
    """Serializer for creating payment intent"""
    fine_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    def validate_fine_id(self, value):
        """Validate that fine exists and belongs to user"""
        try:
            fine = Fine.objects.get(id=value)
            return value
        except Fine.DoesNotExist:
            raise serializers.ValidationError("Fine not found")
    
    def validate(self, data):
        """Ensure payment hasn't been made already"""
        fine = Fine.objects.get(id=data['fine_id'])
        if fine.paid:
            raise serializers.ValidationError("This fine has already been paid")
        return data


class ConfirmPaymentSerializer(serializers.Serializer):
    """Serializer for confirming payment"""
    payment_intent_id = serializers.CharField()
    
    def validate_payment_intent_id(self, value):
        """Validate payment intent ID format"""
        if not value.startswith('pi_'):
            raise serializers.ValidationError("Invalid payment intent ID")
        return value


class PaymentResponseSerializer(serializers.Serializer):
    """Serializer for payment API responses"""
    client_secret = serializers.CharField(required=False)
    fine_id = serializers.IntegerField(required=False)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    status = serializers.CharField()
    message = serializers.CharField(required=False)
    payment_intent_id = serializers.CharField(required=False)
    fine = FineSerializer(required=False)


class FineListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing fines"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    book_title = serializers.CharField(source='issued_book.book.title', read_only=True, required=False)
    
    class Meta:
        model = Fine
        fields = [
            'id',
            'user_name',
            'book_title',
            'amount',
            'paid',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
