from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, GroupViewSet, ManufacturerViewSet, CPUViewSet,
    RAMViewSet, StorageViewSet, GPUViewSet, NetworkCardViewSet,
    LicenseMetricViewSet, LicenseProductViewSet, LicensePricingViewSet,
    ProjectViewSet, ServerConfigurationViewSet, SavedConfigurationViewSet,
    UserActivityViewSet, ProjectActivityViewSet, NotificationViewSet,
    ProjectApprovalViewSet
)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

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
    path('', include(router.urls)),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
