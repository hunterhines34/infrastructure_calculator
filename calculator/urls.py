from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .views import ReportsView

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('cpus/', views.CPUListView.as_view(), name='cpu_list'),
    path('cpus/create/', views.CPUCreateView.as_view(), name='cpu_create'),
    path('cpus/<int:pk>/edit/', views.CPUUpdateView.as_view(), name='cpu_edit'),
    path('cpus/<int:pk>/delete/', views.CPUDeleteView.as_view(), name='cpu_delete'),
    path('ram/', views.RAMListView.as_view(), name='ram_list'),
    path('ram/create/', views.RAMCreateView.as_view(), name='ram_create'),
    path('ram/<int:pk>/edit/', views.RAMUpdateView.as_view(), name='ram_edit'),
    path('ram/<int:pk>/delete/', views.RAMDeleteView.as_view(), name='ram_delete'),
    path('storage/', views.StorageListView.as_view(), name='storage_list'),
    path('storage/create/', views.StorageCreateView.as_view(), name='storage_create'),
    path('storage/<int:pk>/edit/', views.StorageUpdateView.as_view(), name='storage_edit'),
    path('storage/<int:pk>/delete/', views.StorageDeleteView.as_view(), name='storage_delete'),
    path('gpus/', views.GPUListView.as_view(), name='gpu_list'),
    path('gpus/create/', views.GPUCreateView.as_view(), name='gpu_create'),
    path('gpus/<int:pk>/edit/', views.GPUUpdateView.as_view(), name='gpu_edit'),
    path('gpus/<int:pk>/delete/', views.GPUDeleteView.as_view(), name='gpu_delete'),
    path('networkcards/', views.NetworkCardListView.as_view(), name='networkcard_list'),
    path('networkcards/create/', views.NetworkCardCreateView.as_view(), name='networkcard_create'),
    path('networkcards/<int:pk>/edit/', views.NetworkCardUpdateView.as_view(), name='networkcard_edit'),
    path('networkcards/<int:pk>/delete/', views.NetworkCardDeleteView.as_view(), name='networkcard_delete'),
    path('licenses/', views.LicenseProductListView.as_view(), name='license_list'),
    path('licenses/add/', views.LicenseProductCreateView.as_view(), name='license_create'),
    path('licenses/<int:pk>/edit/', views.LicenseProductUpdateView.as_view(), name='license_update'),
    path('licenses/<int:pk>/delete/', views.LicenseProductDeleteView.as_view(), name='license_delete'),
    path('licenses/pricing/create/', views.LicensePricingCreateView.as_view(), name='license_pricing_create'),
    path('licenses/pricing/<int:pk>/edit/', views.LicensePricingEditView.as_view(), name='license_pricing_edit'),
    path('licenses/pricing/<int:pk>/delete/', views.LicensePricingDeleteView.as_view(), name='license_pricing_delete'),
    path('manufacturers/', views.ManufacturerListView.as_view(), name='manufacturer_list'),
    path('manufacturers/create/', views.ManufacturerCreateView.as_view(), name='manufacturer_create'),
    path('manufacturers/<int:pk>/edit/', views.ManufacturerUpdateView.as_view(), name='manufacturer_edit'),
    path('manufacturers/<int:pk>/delete/', views.ManufacturerDeleteView.as_view(), name='manufacturer_delete'),
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_edit'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/submit-review/', views.project_submit_review, name='project_submit_review'),
    path('projects/<int:pk>/approve/', views.project_approve, name='project_approve'),
    path('projects/<int:pk>/reject/', views.project_reject, name='project_reject'),
    path('projects/<int:project_pk>/load-configuration/<int:config_pk>/', views.load_saved_configuration, name='load_saved_configuration'),
    path('projects/<int:pk>/revert-to-draft/', views.project_revert_to_draft, name='project_revert_to_draft'),
    path('projects/<int:pk>/export/', views.ProjectExportView.as_view(), name='project_export'),     
    path('serverconfigurations/', views.ServerConfigurationListView.as_view(), name='serverconfiguration_list'),
    path('serverconfigurations/create/', views.ServerConfigurationCreateView.as_view(), name='serverconfiguration_create'),
    path('serverconfigurations/<int:pk>/update/', views.ServerConfigurationUpdateView.as_view(), name='serverconfiguration_update'),
    path('serverconfigurations/<int:pk>/delete/', views.ServerConfigurationDeleteView.as_view(), name='serverconfiguration_delete'),
    path('savedconfigurations/', views.SavedConfigurationListView.as_view(), name='savedconfiguration_list'),
    path('savedconfigurations/create/', views.SavedConfigurationCreateView.as_view(), name='savedconfiguration_create'),
    path('savedconfigurations/<int:pk>/edit/', views.SavedConfigurationUpdateView.as_view(), name='savedconfiguration_edit'),
    path('savedconfigurations/<int:pk>/delete/', views.SavedConfigurationDeleteView.as_view(), name='savedconfiguration_delete'),
    path('saved-configurations/export/', views.saved_configurations_export, name='saved_configurations_export'),
    path('metrics/', views.LicenseMetricListView.as_view(), name='license_metric_list'),
    path('metrics/add/', views.LicenseMetricCreateView.as_view(), name='license_metric_create'),
    path('metrics/<int:pk>/edit/', views.LicenseMetricUpdateView.as_view(), name='license_metric_edit'),
    path('metrics/<int:pk>/delete/', views.LicenseMetricDeleteView.as_view(), name='license_metric_delete'),
    path('configurations/<int:pk>/', views.ServerConfigurationDetailView.as_view(), name='serverconfiguration_detail'),
    path('configurations/<int:pk>/edit/', views.ServerConfigurationUpdateView.as_view(), name='serverconfiguration_edit'),
    path('configurations/<int:pk>/delete/', views.ServerConfigurationDeleteView.as_view(), name='serverconfiguration_delete'),
    path('configurations/export/', views.export_configurations, name='export_configurations'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('approvals/', views.ApprovalsListView.as_view(), name='approvals'),
    path('reports/', ReportsView.as_view(), name='reports'),
    path('api/', include('calculator.api.urls')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]