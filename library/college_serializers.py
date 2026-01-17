from rest_framework import serializers
from .models import College, Profile


class CollegeSerializer(serializers.ModelSerializer):
    """Serializer for College/Tenant model."""
    
    subscription_limit = serializers.SerializerMethodField()
    can_add_user = serializers.SerializerMethodField()
    
    class Meta:
        model = College
        fields = [
            'id', 'name', 'code', 'location', 'admin_email',
            'subscription_plan', 'is_active', 'max_users',
            'current_users', 'subscription_limit', 'can_add_user',
            'monthly_fee', 'billing_cycle_start', 'billing_cycle_end',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'current_users', 'subscription_limit',
            'can_add_user', 'created_at', 'updated_at'
        ]
    
    def get_subscription_limit(self, obj):
        """Get maximum users allowed."""
        return obj.get_subscription_limit()
    
    def get_can_add_user(self, obj):
        """Check if college can add more users."""
        return obj.can_add_user()


class CollegeBillingSerializer(serializers.ModelSerializer):
    """Serializer for college billing information."""
    
    class Meta:
        model = College
        fields = [
            'id', 'name', 'code', 'subscription_plan',
            'monthly_fee', 'billing_cycle_start', 'billing_cycle_end',
            'payment_method', 'current_users', 'max_users'
        ]
        read_only_fields = [
            'id', 'name', 'code', 'current_users', 'max_users'
        ]


class CollegeStatsSerializer(serializers.Serializer):
    """Serializer for college statistics."""
    
    total_users = serializers.IntegerField()
    total_books = serializers.IntegerField()
    total_fines = serializers.DecimalField(max_digits=10, decimal_places=2)
    pending_fines = serializers.DecimalField(max_digits=10, decimal_places=2)
    active_issues = serializers.IntegerField()
    overdue_books = serializers.IntegerField()
    pending_reservations = serializers.IntegerField()
    subscription_usage = serializers.FloatField()  # Percentage


class UserWithCollegeSerializer(serializers.ModelSerializer):
    """Serializer for user with college information."""
    
    college = CollegeSerializer(source='profile.college', read_only=True)
    role = serializers.CharField(source='profile.role', read_only=True)
    
    class Meta:
        model = Profile.user.field.related_model  # User model
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'college', 'role', 'is_active'
        ]
