from rest_framework import serializers
from django.contrib.auth.models import User, Group
from calculator.models import (
    Manufacturer, CPU, RAM, Storage, GPU, NetworkCard,
    LicenseMetric, LicenseProduct, LicensePricing,
    Project, ServerConfiguration, SavedConfiguration,
    UserActivity, ProjectActivity, Notification, ProjectApproval
)

# User and Group Serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
        read_only_fields = ['is_staff']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

# Hardware Component Serializers
class GPUSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)
    
    class Meta:
        model = GPU
        fields = ['id', 'name', 'memory_gb', 'manufacturer', 'manufacturer_name',
                 'model', 'clock_speed', 'power_consumption_watts', 'price']

class NetworkCardSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)
    
    class Meta:
        model = NetworkCard
        fields = ['id', 'name', 'speed_gbps', 'interface', 'manufacturer',
                 'manufacturer_name', 'model', 'port_type', 'price']

# License-related Serializers
class LicenseMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseMetric
        fields = ['id', 'name', 'description']

class LicenseProductSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)
    
    class Meta:
        model = LicenseProduct
        fields = '__all__'

class LicensePricingSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='license_product.name', read_only=True)
    metric_name = serializers.CharField(source='metric.name', read_only=True)
    
    class Meta:
        model = LicensePricing
        fields = '__all__'

# Configuration Serializers
class ServerConfigurationSerializer(serializers.ModelSerializer):
    hardware_cost = serializers.DecimalField(
        source='calculate_hardware_cost',
        read_only=True,
        max_digits=10,
        decimal_places=2
    )
    license_costs = serializers.DecimalField(
        source='calculate_license_costs',
        read_only=True,
        max_digits=10,
        decimal_places=2
    )
    total_cost = serializers.DecimalField(
        source='calculate_total_cost',
        read_only=True,
        max_digits=10,
        decimal_places=2
    )
    
    class Meta:
        model = ServerConfiguration
        fields = '__all__'

class SavedConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedConfiguration
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']

# Activity and Notification Serializers
class UserActivitySerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = '__all__'
        read_only_fields = ['timestamp']

class ProjectActivitySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ProjectActivity
        fields = '__all__'
        read_only_fields = ['created_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_at']

class ProjectApprovalSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    
    class Meta:
        model = ProjectApproval
        fields = '__all__'
        read_only_fields = ['requested_at', 'reviewed_at']

# Hardware Component Serializers
class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'website', 'description', 'contact_email']

class CPUSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)
    
    class Meta:
        model = CPU
        fields = ['id', 'name', 'model', 'manufacturer', 'manufacturer_name',
                 'architecture', 'cores', 'threads', 'clock_speed',
                 'power_consumption_watts', 'price']

class RAMSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)
    
    class Meta:
        model = RAM
        fields = ['id', 'name', 'model', 'manufacturer', 'manufacturer_name',
                 'capacity_gb', 'speed', 'ram_type', 'latency_ns', 'price']

class StorageSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)
    
    class Meta:
        model = Storage
        fields = ['id', 'name', 'capacity', 'capacity_unit', 'storage_type',
                 'interface', 'manufacturer', 'manufacturer_name', 'model',
                 'form_factor', 'price_per_gb', 'price_per_tb', 'price_per_pb', 'price']

class ProjectSerializer(serializers.ModelSerializer):
    hardware_costs = serializers.DecimalField(
        source='calculate_hardware_costs',
        read_only=True,
        max_digits=10,
        decimal_places=2
    )
    license_costs = serializers.DecimalField(
        source='calculate_license_costs',
        read_only=True,
        max_digits=10,
        decimal_places=2
    )
    total_cost = serializers.DecimalField(
        source='calculate_total_cost',
        read_only=True,
        max_digits=10,
        decimal_places=2
    )
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'start_date', 'end_date',
                 'created_at', 'updated_at', 'created_by', 'status',
                 'hardware_costs', 'license_costs', 'total_cost']
        read_only_fields = ['created_at', 'updated_at', 'created_by']
