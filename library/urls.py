from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    login_view,
    logout_view,
    register_view,
    student_dashboard,
    teacher_dashboard,
    staff_dashboard,
    dashboard_api,
    issue_book,
    return_book,
)
from .payments import (
    create_payment_for_fine,
    confirm_payment_for_fine,
    get_user_fines,
    get_fine_status,
)
from .analytics import (
    get_user_analytics,
    get_system_analytics,
    get_fine_statistics_api,
    get_payment_trends_api,
    get_overdue_analytics_api,
    get_revenue_analytics_api,
)
from .college_views import CollegeViewSet
from .college_analytics import (
    college_dashboard,
    college_fine_analytics,
    college_book_analytics,
    college_user_analytics,
    college_billing_report,
)

# Router for viewsets
router = DefaultRouter()
router.register(r'colleges', CollegeViewSet, basename='college')

urlpatterns = [
    # Authentication
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),

    # Dashboards
    path('student/', student_dashboard, name='student_dashboard'),
    path('teacher/', teacher_dashboard, name='teacher_dashboard'),
    path('staff/', staff_dashboard, name='staff_dashboard'),
    
    # API Endpoints
    path('api/dashboard/', dashboard_api, name='dashboard_api'),
    path('api/books/issue/', issue_book, name='issue_book'),
    path('api/books/return/', return_book, name='return_book'),
    
    # Payment Endpoints
    path('api/fines/', get_user_fines, name='get_user_fines'),
    path('api/fines/<int:fine_id>/', get_fine_status, name='get_fine_status'),
    path('api/payments/create-intent/', create_payment_for_fine, name='create_payment'),
    path('api/payments/confirm/', confirm_payment_for_fine, name='confirm_payment'),
    
    # Analytics Endpoints
    path('api/analytics/user/', get_user_analytics, name='user_analytics'),
    path('api/analytics/system/', get_system_analytics, name='system_analytics'),
    path('api/analytics/fines/', get_fine_statistics_api, name='fine_statistics'),
    path('api/analytics/payment-trends/', get_payment_trends_api, name='payment_trends'),
    path('api/analytics/overdue/', get_overdue_analytics_api, name='overdue_analytics'),
    path('api/analytics/revenue/', get_revenue_analytics_api, name='revenue_analytics'),
    
    # Multi-tenant/College Endpoints
    path('api/', include(router.urls)),
    path('api/college/dashboard/', college_dashboard, name='college_dashboard'),
    path('api/college/analytics/fines/', college_fine_analytics, name='college_fine_analytics'),
    path('api/college/analytics/books/', college_book_analytics, name='college_book_analytics'),
    path('api/college/analytics/users/', college_user_analytics, name='college_user_analytics'),
    path('api/college/billing/', college_billing_report, name='college_billing_report'),
]
