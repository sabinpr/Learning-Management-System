from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, PaymentViewSet, AssessmentViewSet, EnrollmentViewSet, SubmissionViewSet, SponsorshipViewSet, NotificationViewSet, register_api_view, login_api_view, sponsor_dashboard_api_view, admin_dashboard_api_view
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Documentation using drf_yasg
schema_view = get_schema_view(
    openapi.Info(
        title="Learning Management API",
        default_version='v1',
        description="API documentation for managing Learning system",
        contact=openapi.Contact(email="sabinprajapati7@gmail.com"),
    ),
    public=True,
    permission_classes=[],
)

router = DefaultRouter()
router.register('course', CourseViewSet)
router.register('payment', PaymentViewSet)
router.register('assessment', AssessmentViewSet)
router.register('enrollment', EnrollmentViewSet)
router.register('submission', SubmissionViewSet)
router.register('sponsorship', SponsorshipViewSet)
router.register('notification', NotificationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('register/', register_api_view, name='register'),
    path('login/', login_api_view, name='login'),
    path('admin_dashboard/', admin_dashboard_api_view, name='admin_dashboard'),
    path('sponsor_dashboard/', sponsor_dashboard_api_view,
         name='sponsor_dashboard'),
    path('docs/', schema_view.as_view(), name='api-docs'),
]
