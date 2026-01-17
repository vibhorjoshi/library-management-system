from django.urls import path
from .views import (
    login_view,
    logout_view,
    student_dashboard,
    teacher_dashboard,
    staff_dashboard
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('student/', student_dashboard, name='student_dashboard'),
    path('teacher/', teacher_dashboard, name='teacher_dashboard'),
    path('staff/', staff_dashboard, name='staff_dashboard'),
]
