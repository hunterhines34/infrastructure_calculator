from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .views import (
    UserViewSet, GroupViewSet, ManufacturerViewSet, CPUViewSet,
    RAMViewSet, StorageViewSet, GPUViewSet, NetworkCardViewSet,
    LicenseMetricViewSet, LicenseProductViewSet, LicensePricingViewSet,
    ProjectViewSet, ServerConfigurationViewSet, SavedConfigurationViewSet,
    UserActivityViewSet, ProjectActivityViewSet, NotificationViewSet,
    ProjectApprovalViewSet
)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

class APIRootView(APIView):
    """
    Infrastructure Calculator API Root
    """
    def get(self, request, format=None):
        return Response({
            'Hardware Components': {
                'cpus': reverse('cpu-list', request=request, format=format),
                'ram': reverse('ram-list', request=request, format=format),
                'storage': reverse('storage-list', request=request, format=format),
                'gpus': reverse('gpu-list', request=request, format=format),
                'network_cards': reverse('networkcard-list', request=request, format=format),
            },
            'Licensing': {
                'license_metrics': reverse('licensemetric-list', request=request, format=format),
                'license_products': reverse('licenseproduct-list', request=request, format=format),
                'license_pricing': reverse('licensepricing-list', request=request, format=format),
            },
            'Projects': {
                'projects': reverse('project-list', request=request, format=format),
                'server_configurations': reverse('server-configuration-list', request=request, format=format),
                'saved_configurations': reverse('saved-configuration-list', request=request, format=format),
            },
            'User Management': {
                'users': reverse('user-list', request=request, format=format),
                'groups': reverse('group-list', request=request, format=format),
                'notifications': reverse('notification-list', request=request, format=format),
                'user_activities': reverse('user-activity-list', request=request, format=format),
            }
        })

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'manufacturers', ManufacturerViewSet)
router.register(r'cpus', CPUViewSet)
router.register(r'ram', RAMViewSet)
router.register(r'storage', StorageViewSet)
router.register(r'gpus', GPUViewSet)
router.register(r'network-cards', NetworkCardViewSet)
router.register(r'license-metrics', LicenseMetricViewSet)
router.register(r'license-products', LicenseProductViewSet)
router.register(r'license-pricing', LicensePricingViewSet)
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'server-configurations', ServerConfigurationViewSet, basename='server-configuration')
router.register(r'saved-configurations', SavedConfigurationViewSet, basename='saved-configuration')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'project-approvals', ProjectApprovalViewSet, basename='project-approval')
router.register(r'user-activities', UserActivityViewSet, basename='user-activity')
router.register(r'project-activities', ProjectActivityViewSet, basename='project-activity')

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('', include(router.urls)),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
