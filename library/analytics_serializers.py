from rest_framework import serializers


class FineStatisticsSerializer(serializers.Serializer):
    """Serializer for fine statistics"""
    total_fines = serializers.IntegerField()
    total_amount = serializers.FloatField()
    paid_amount = serializers.FloatField()
    pending_amount = serializers.FloatField()
    avg_fine_amount = serializers.FloatField()
    max_fine_amount = serializers.FloatField()
    min_fine_amount = serializers.FloatField()
    paid_count = serializers.IntegerField()
    unpaid_count = serializers.IntegerField()
    paid_percentage = serializers.FloatField()
    unpaid_percentage = serializers.FloatField()


class PaymentTrendSerializer(serializers.Serializer):
    """Serializer for payment trend data"""
    date = serializers.CharField()
    amount = serializers.FloatField()
    count = serializers.IntegerField()


class OverdueAnalyticsSerializer(serializers.Serializer):
    """Serializer for overdue books analytics"""
    total_overdue = serializers.IntegerField()
    overdue_users = serializers.IntegerField()
    total_overdue_fine = serializers.FloatField()
    books_by_days_overdue = serializers.DictField()


class RevenueAnalyticsSerializer(serializers.Serializer):
    """Serializer for revenue analytics"""
    period_days = serializers.IntegerField()
    total_revenue = serializers.FloatField()
    total_transactions = serializers.IntegerField()
    avg_transaction = serializers.FloatField()
    daily_average = serializers.FloatField()


class TopDefaulterSerializer(serializers.Serializer):
    """Serializer for top defaulters"""
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField()
    unpaid_fines = serializers.IntegerField()
    unpaid_amount = serializers.FloatField()


class TopBookSerializer(serializers.Serializer):
    """Serializer for top books"""
    book_id = serializers.IntegerField()
    title = serializers.CharField()
    author = serializers.CharField()
    times_issued = serializers.IntegerField()
    currently_issued = serializers.IntegerField()
    currently_overdue = serializers.IntegerField()


class UserAnalyticsSerializer(serializers.Serializer):
    """Serializer for user analytics"""
    user = serializers.DictField()
    fine_statistics = FineStatisticsSerializer()
    overdue_books = serializers.IntegerField()
    pending_fines = serializers.ListField()


class SystemAnalyticsSerializer(serializers.Serializer):
    """Serializer for system-wide analytics"""
    period_days = serializers.IntegerField()
    generated_at = serializers.CharField()
    fine_statistics = FineStatisticsSerializer()
    payment_trends = PaymentTrendSerializer(many=True)
    overdue_analytics = OverdueAnalyticsSerializer()
    revenue_analytics = RevenueAnalyticsSerializer()
    top_defaulters = TopDefaulterSerializer(many=True)
    top_books = TopBookSerializer(many=True)
