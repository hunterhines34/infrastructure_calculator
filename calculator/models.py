from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal

class Manufacturer(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name

class CPU(models.Model):
    name = models.CharField(max_length=255)
    model = models.CharField(max_length=255, blank=True, null=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    ARCHITECTURE_CHOICES = [
        ('x86', 'x86'),
        ('x86_64', 'x86_64'),
        ('arm', 'ARM'),
        ('arm64', 'ARM64'),
    ]
    architecture = models.CharField(max_length=50, choices=ARCHITECTURE_CHOICES, default='x86_64')
    cores = models.IntegerField()
    threads = models.IntegerField()
    clock_speed = models.FloatField()
    power_consumption_watts = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = "CPU"

    def __str__(self):
        return self.name

class RAM(models.Model):
    name = models.CharField(max_length=255)
    model = models.CharField(max_length=255, blank=True, null=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    capacity_gb = models.IntegerField()
    speed = models.IntegerField()
    RAM_TYPE_CHOICES = [
        ('ddr4', 'DDR4'),
        ('ddr4_ecc', 'DDR4 ECC'),
        ('ddr5', 'DDR5'),
        ('ddr5_ecc', 'DDR5 ECC'),
    ]
    ram_type = models.CharField(max_length=50, choices=RAM_TYPE_CHOICES)
    latency_ns = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = "RAM"

    def __str__(self):
        return self.name

class Storage(models.Model):
    name = models.CharField(max_length=255)
    capacity = models.IntegerField()
    CAPACITY_UNIT_CHOICES = [
        ('gb', 'GB'),
        ('tb', 'TB'),
        ('pb', 'PB'),
    ]
    capacity_unit = models.CharField(max_length=2, choices=CAPACITY_UNIT_CHOICES, default='tb')
    STORAGE_TYPE_CHOICES = [
        ('ssd', 'SSD'),
        ('hdd', 'HDD'),
        ('nvme', 'NVMe'),
    ]
    storage_type = models.CharField(max_length=50, choices=STORAGE_TYPE_CHOICES)
    INTERFACE_CHOICES = [
        ('sata', 'SATA'),
        ('sas', 'SAS'),
        ('pcie', 'PCIe'),
    ]
    interface = models.CharField(max_length=50, choices=INTERFACE_CHOICES)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    price_per_gb = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_per_tb = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_per_pb = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    form_factor = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name

class GPU(models.Model):
    name = models.CharField(max_length=255)
    memory_gb = models.IntegerField()
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    model = models.CharField(max_length=255, blank=True, null=True)
    clock_speed = models.FloatField(blank=True, null=True)
    power_consumption_watts = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = "GPU"

    def __str__(self):
        return self.name

class NetworkCard(models.Model):
    name = models.CharField(max_length=255)
    speed_gbps = models.FloatField()
    INTERFACE_CHOICES = [
        ('ethernet', 'Ethernet'),
        ('fiber', 'Fiber Channel'),
    ]
    interface = models.CharField(max_length=50, choices=INTERFACE_CHOICES)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    model = models.CharField(max_length=255, blank=True, null=True)
    port_type = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name

class LicenseMetric(models.Model):
    name = models.CharField(max_length=100)  # e.g., "Core Pack", "User CAL", "Socket"
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class LicenseProduct(models.Model):
    name = models.CharField(max_length=255)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    version = models.CharField(max_length=50, blank=True, null=True)
    EDITION_CHOICES = [
        ('developer', 'Developer'),
        ('standard', 'Standard'),
        ('enterprise', 'Enterprise'),
        ('datacenter', 'Datacenter'),
        ('web', 'Web'),
    ]
    edition = models.CharField(max_length=50, choices=EDITION_CHOICES)
    is_core_based = models.BooleanField(default=False)
    is_socket_based = models.BooleanField(default=False)
    is_user_based = models.BooleanField(default=False)
    min_cores_per_processor = models.IntegerField(default=0)
    min_cores_per_server = models.IntegerField(default=0)
    core_pack_size = models.IntegerField(default=2)
    requires_cal = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} {self.version} {self.edition}"

class LicensePricing(models.Model):
    license_product = models.ForeignKey(LicenseProduct, on_delete=models.CASCADE)
    metric = models.ForeignKey(LicenseMetric, on_delete=models.CASCADE)
    quantity_per_pack = models.IntegerField(default=1)  # e.g., 2 for core packs
    price = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-valid_from']
    
    def __str__(self):
        return f"{self.license_product} - {self.metric} - ${self.price}"

class Project(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Return the URL to access a particular project instance."""
        return reverse('project_detail', args=[str(self.id)])

    def calculate_hardware_costs(self):
        """Calculate total hardware costs for all configurations"""
        return sum(
            config.calculate_hardware_cost() 
            for config in self.server_configurations.all()
        )

    def calculate_license_costs(self):
        """Calculate total license costs for all configurations"""
        return sum(
            config.calculate_license_costs() 
            for config in self.server_configurations.all()
        )

    def calculate_total_cost(self):
        """Calculate total project cost"""
        return self.calculate_hardware_costs() + self.calculate_license_costs()

    @property
    def estimated_cost(self):
        """Property to get total estimated cost"""
        return self.calculate_total_cost()

    def delete(self, *args, **kwargs):
        # Clean up related objects first
        ProjectActivity.objects.filter(project=self).delete()
        ServerConfiguration.objects.filter(project=self).delete()
        SavedConfiguration.objects.filter(project=self).delete()
        try:
            self.approval.delete()
        except ProjectApproval.DoesNotExist:
            pass
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class ServerConfiguration(models.Model):
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='server_configurations',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    cpu = models.ForeignKey(CPU, on_delete=models.SET_NULL, blank=True, null=True)
    ram = models.ForeignKey(RAM, on_delete=models.SET_NULL, blank=True, null=True)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, blank=True, null=True)
    gpu = models.ForeignKey(GPU, on_delete=models.SET_NULL, blank=True, null=True)
    network_card = models.ForeignKey(NetworkCard, on_delete=models.SET_NULL, blank=True, null=True)
    os = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    def calculate_hardware_cost(self):
        """Calculate total hardware cost for this configuration"""
        # Start with base components
        total_cost = Decimal('0.00')
        
        # Add base component costs
        if self.cpu:
            total_cost += self.cpu.price
        if self.ram:
            total_cost += self.ram.price
        if self.storage:
            total_cost += self.storage.price
        if self.gpu:
            total_cost += self.gpu.price
        if self.network_card:
            total_cost += self.network_card.price
        
        # Add additional components cost
        components_cost = sum(
            component.calculate_cost() 
            for component in self.serverconfigurationcomponent_set.all()
        )
        
        return total_cost + components_cost

    def calculate_license_costs(self):
        """Calculate total license costs for this configuration"""
        total = Decimal('0.00')
        
        if not self.os:
            return total

        # Get current date for valid pricing
        current_date = timezone.now().date()
        
        # Find matching license products based on OS
        if 'windows' in self.os.lower():
            license_products = LicenseProduct.objects.filter(
                name__icontains='Windows Server',
                edition__in=['datacenter', 'standard']
            )
        elif 'red hat' in self.os.lower() or 'rhel' in self.os.lower():
            license_products = LicenseProduct.objects.filter(
                name__icontains='Red Hat'
            )
        else:
            return total  # Return 0 for unknown OS types

        for product in license_products:
            # Get the latest valid pricing
            pricing = LicensePricing.objects.filter(
                license_product=product,
                valid_from__lte=current_date
            ).filter(
                Q(valid_to__gte=current_date) | Q(valid_to__isnull=True)
            ).first()

            if not pricing:
                continue

            # Calculate cost based on licensing model
            if product.is_core_based and self.cpu:
                # Calculate number of core packs needed
                cores = self.cpu.cores
                min_cores = max(
                    product.min_cores_per_processor,
                    product.min_cores_per_server
                )
                cores = max(cores, min_cores)
                core_packs = (cores + product.core_pack_size - 1) // product.core_pack_size
                total += pricing.price * Decimal(core_packs)

            elif product.is_socket_based and self.cpu:
                # Assume 1 socket per CPU for simplicity
                total += pricing.price

            # Add SQL Server costs if Windows OS
            if 'windows' in self.os.lower():
                sql_products = LicenseProduct.objects.filter(
                    name__icontains='SQL Server'
                )
                for sql_product in sql_products:
                    sql_pricing = LicensePricing.objects.filter(
                        license_product=sql_product,
                        valid_from__lte=current_date
                    ).filter(
                        Q(valid_to__gte=current_date) | Q(valid_to__isnull=True)
                    ).first()

                    if sql_pricing and self.cpu:
                        cores = self.cpu.cores
                        min_cores = max(
                            sql_product.min_cores_per_processor,
                            sql_product.min_cores_per_server
                        )
                        cores = max(cores, min_cores)
                        core_packs = (cores + sql_product.core_pack_size - 1) // sql_product.core_pack_size
                        total += sql_pricing.price * Decimal(core_packs)

        return total

    def calculate_total_cost(self):
        """Calculate total cost for this configuration"""
        return self.calculate_hardware_cost() + self.calculate_license_costs()

class SavedConfiguration(models.Model):
    project = models.ForeignKey(
        Project, 
        on_delete=models.SET_NULL, 
        related_name='saved_configurations',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    cpu = models.ForeignKey(CPU, on_delete=models.SET_NULL, blank=True, null=True)
    ram = models.ForeignKey(RAM, on_delete=models.SET_NULL, blank=True, null=True)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, blank=True, null=True)
    gpu = models.ForeignKey(GPU, on_delete=models.SET_NULL, blank=True, null=True)
    network_card = models.ForeignKey(NetworkCard, on_delete=models.SET_NULL, blank=True, null=True)
    os = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class UserActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "User Activities"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.email} - {self.title}"

class ProjectActivity(models.Model):
    project = models.ForeignKey(
        'Project', 
        on_delete=models.CASCADE,
        related_name='activities'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('approval_needed', 'Approval Needed'),
        ('project_updated', 'Project Updated'),
        # Add more types as needed
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_link = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class ProjectApproval(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    project = models.OneToOneField(
        'Project', 
        on_delete=models.CASCADE, 
        related_name='approval',
        null=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approval_requests')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_approvals')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"Approval for {self.project.name} - {self.get_status_display()}"

    def create_notification(self):
        staff_users = User.objects.filter(is_staff=True)
        for user in staff_users:
            Notification.objects.create(
                recipient=user,
                notification_type='approval_needed',
                title='New Project Needs Approval',
                message=f'Project "{self.project.name}" requires your approval',
                related_link=reverse('project_detail', kwargs={'pk': self.project.pk})
            )

class ServerConfigurationComponent(models.Model):
    server_configuration = models.ForeignKey('ServerConfiguration', on_delete=models.CASCADE)
    cpu = models.ForeignKey(CPU, on_delete=models.SET_NULL, null=True, blank=True)
    ram = models.ForeignKey(RAM, on_delete=models.SET_NULL, null=True, blank=True)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True, blank=True)
    gpu = models.ForeignKey(GPU, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    
    def calculate_cost(self):
        total = Decimal('0.00')
        if self.cpu:
            total += self.cpu.price * self.quantity
        if self.ram:
            total += self.ram.price * self.quantity
        if self.storage:
            total += self.storage.price * self.quantity
        if self.gpu:
            total += self.gpu.price * self.quantity
        return total