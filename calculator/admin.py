from django.contrib import admin
from .models import (
    CPU, RAM, Storage, GPU, NetworkCard, Manufacturer, 
    Project, ServerConfiguration, SavedConfiguration,
    LicenseMetric, LicenseProduct, LicensePricing
)

admin.site.site_header = "Calculator Admin"
admin.site.index_title = "Admin"
admin.site.site_title = "Calculator Admin"

class CPUAdmin(admin.ModelAdmin):
    verbose_name = "CPU"
    list_display = ("name", "model", "manufacturer")

class RAMAdmin(admin.ModelAdmin):
    verbose_name = "RAM"
    list_display = ("name", "model", "manufacturer")

class GPUAdmin(admin.ModelAdmin):
    verbose_name = "GPU"
    list_display = ("name", "model", "manufacturer")

class StorageAdmin(admin.ModelAdmin):
    list_display = ("name", "model", "manufacturer")

class NetworkCardAdmin(admin.ModelAdmin):
    list_display = ("name", "model", "manufacturer")

class LicenseAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor")

class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "website", "contact_email")

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at', 'updated_at']

    def delete_model(self, request, obj):
        """Custom delete method for single object deletion"""
        try:
            # Delete related objects first
            obj.server_configurations.all().delete()
            obj.activities.all().delete()
            if hasattr(obj, 'approval'):
                obj.approval.delete()
            # Finally delete the project
            obj.delete()
        except Exception as e:
            self.message_user(request, f"Error deleting project: {str(e)}", level='ERROR')

    def delete_queryset(self, request, queryset):
        """Custom delete method for queryset (bulk deletion)"""
        for obj in queryset:
            self.delete_model(request, obj)

class ServerConfigurationAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "cpu", "ram", "storage", "gpu", "network_card", "os")

class SavedConfigurationAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "cpu", "ram", "storage", "gpu", "network_card", "os")

admin.site.register(CPU, CPUAdmin)
admin.site.register(RAM, RAMAdmin)
admin.site.register(Storage, StorageAdmin)
admin.site.register(GPU, GPUAdmin)
admin.site.register(NetworkCard, NetworkCardAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(ServerConfiguration, ServerConfigurationAdmin)
admin.site.register(SavedConfiguration, SavedConfigurationAdmin)
admin.site.register(LicenseMetric)
admin.site.register(LicenseProduct)

@admin.register(LicensePricing)
class LicensePricingAdmin(admin.ModelAdmin):
    list_display = ['license_product', 'metric', 'price', 'valid_from', 'valid_to']
    list_filter = ['license_product', 'metric', 'valid_from']
    search_fields = ['license_product__name', 'metric__name']