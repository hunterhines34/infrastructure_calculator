from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import (
    UserActivity, Project, ServerConfiguration, 
    SavedConfiguration, CPU, RAM, Storage, 
    GPU, NetworkCard, Manufacturer,
    LicenseMetric, LicenseProduct,
    ProjectActivity
)

def create_activity(user, title, description=None):
    """Helper function to create activity records"""
    if user and user.is_authenticated:
        UserActivity.objects.create(
            user=user,
            title=title,
            description=description
        )

def create_project_activity(project, user, title, description=None):
    """Helper function to create project activity records"""
    ProjectActivity.objects.create(
        project=project,
        created_by=user,
        title=title,
        description=description
    )

# Project activities
@receiver([post_save, post_delete], sender=Project)
def track_project_activity(sender, instance, **kwargs):
    if not instance.created_by:
        return
        
    if kwargs.get('created', False):
        create_project_activity(
            instance,
            instance.created_by,
            "Project Created",
            f"Project initialized with status: {instance.get_status_display()} by {instance.created_by.get_full_name() or instance.created_by.username}"
        )
    elif kwargs.get('signal', None) == post_delete:
        create_activity(
            instance.created_by,
            f"Deleted project: {instance.name}",
            f"Project deleted by {instance.created_by.get_full_name() or instance.created_by.username}"
        )
    else:
        create_project_activity(
            instance,
            instance.created_by,
            "Project Updated",
            f"Project details modified by {instance.created_by.get_full_name() or instance.created_by.username}"
        )

# Server Configuration activities
@receiver([post_save, post_delete], sender=ServerConfiguration)
def track_server_config_activity(sender, instance, **kwargs):
    if not instance.project.created_by:
        return
        
    user = instance.project.created_by
    user_display = user.get_full_name() or user.username
        
    if kwargs.get('created', False):
        create_project_activity(
            instance.project,
            user,
            "Server Configuration Added",
            f"{user_display} added new configuration: {instance.name}"
        )
    elif kwargs.get('signal', None) == post_delete:
        create_project_activity(
            instance.project,
            user,
            "Server Configuration Deleted",
            f"{user_display} removed configuration: {instance.name}"
        )
    else:
        create_project_activity(
            instance.project,
            user,
            "Server Configuration Updated",
            f"{user_display} modified configuration: {instance.name}"
        )

# Saved Configuration activities
@receiver([post_save, post_delete], sender=SavedConfiguration)
def track_saved_config_activity(sender, instance, **kwargs):
    if not instance.created_by:
        return
        
    if kwargs.get('created', False):
        create_activity(
            instance.created_by,
            f"Created saved configuration: {instance.name}",
            instance.description
        )
    elif kwargs.get('signal', None) == post_delete:
        create_activity(
            instance.created_by,
            f"Deleted saved configuration: {instance.name}"
        )
    else:
        create_activity(
            instance.created_by,
            f"Updated saved configuration: {instance.name}"
        )

# Hardware Component Activities
@receiver([post_save, post_delete], sender=CPU)
def track_cpu_activity(sender, instance, request=None, **kwargs):
    user = getattr(instance, '_current_user', None)
    if not user:
        return
        
    if kwargs.get('created', False):
        create_activity(
            user,
            f"Added new CPU: {instance.name}",
            f"Manufacturer: {instance.manufacturer.name}"
        )
    elif kwargs.get('signal', None) == post_delete:
        create_activity(
            user,
            f"Deleted CPU: {instance.name}"
        )
    else:
        create_activity(
            user,
            f"Updated CPU: {instance.name}"
        )

@receiver([post_save, post_delete], sender=RAM)
def track_ram_activity(sender, instance, **kwargs):
    user = getattr(instance, '_current_user', None)
    if not user:
        return
        
    if kwargs.get('created', False):
        create_activity(
            user,
            f"Added new RAM: {instance.name}",
            f"Manufacturer: {instance.manufacturer.name}, Capacity: {instance.capacity_gb}GB"
        )
    elif kwargs.get('signal', None) == post_delete:
        create_activity(
            user,
            f"Deleted RAM: {instance.name}"
        )
    else:
        create_activity(
            user,
            f"Updated RAM: {instance.name}"
        )

@receiver([post_save, post_delete], sender=Storage)
def track_storage_activity(sender, instance, **kwargs):
    user = getattr(instance, '_current_user', None)
    if not user:
        return
        
    if kwargs.get('created', False):
        create_activity(
            user,
            f"Added new Storage: {instance.name}",
            f"Type: {instance.get_storage_type_display()}, Capacity: {instance.capacity}{instance.capacity_unit}"
        )
    elif kwargs.get('signal', None) == post_delete:
        create_activity(
            user,
            f"Deleted Storage: {instance.name}"
        )
    else:
        create_activity(
            user,
            f"Updated Storage: {instance.name}"
        )

@receiver([post_save, post_delete], sender=GPU)
def track_gpu_activity(sender, instance, **kwargs):
    user = getattr(instance, '_current_user', None)
    if not user:
        return
        
    if kwargs.get('created', False):
        create_activity(
            user,
            f"Added new GPU: {instance.name}",
            f"Manufacturer: {instance.manufacturer.name}, Memory: {instance.memory_gb}GB"
        )
    elif kwargs.get('signal', None) == post_delete:
        create_activity(
            user,
            f"Deleted GPU: {instance.name}"
        )
    else:
        create_activity(
            user,
            f"Updated GPU: {instance.name}"
        )

@receiver([post_save, post_delete], sender=NetworkCard)
def track_network_card_activity(sender, instance, **kwargs):
    user = getattr(instance, '_current_user', None)
    if not user:
        return
        
    if kwargs.get('created', False):
        create_activity(
            user,
            f"Added new Network Card: {instance.name}",
            f"Speed: {instance.speed_gbps}Gbps, Interface: {instance.get_interface_display()}"
        )
    elif kwargs.get('signal', None) == post_delete:
        create_activity(
            user,
            f"Deleted Network Card: {instance.name}"
        )
    else:
        create_activity(
            user,
            f"Updated Network Card: {instance.name}"
        )

@receiver([post_save, post_delete], sender=Manufacturer)
def track_manufacturer_activity(sender, instance, **kwargs):
    user = getattr(instance, '_current_user', None)
    if not user:
        return
        
    if kwargs.get('created', False):
        create_activity(
            user,
            f"Added new Manufacturer: {instance.name}",
            instance.description
        )
    elif kwargs.get('signal', None) == post_delete:
        create_activity(
            user,
            f"Deleted Manufacturer: {instance.name}"
        )
    else:
        create_activity(
            user,
            f"Updated Manufacturer: {instance.name}"
        )

@receiver([post_save, post_delete], sender=LicenseProduct)
def track_license_product_activity(sender, instance, **kwargs):
    user = getattr(instance, '_current_user', None)
    if not user:
        return
        
    if kwargs.get('created', False):
        create_activity(
            user,
            f"Added new License Product: {instance.name}",
            f"Edition: {instance.edition}, Version: {instance.version}"
        )
    elif kwargs.get('signal', None) == post_delete:
        create_activity(
            user,
            f"Deleted License Product: {instance.name}"
        )
    else:
        create_activity(
            user,
            f"Updated License Product: {instance.name}"
        )

@receiver([post_save, post_delete], sender=LicenseMetric)
def track_license_metric_activity(sender, instance, **kwargs):
    user = getattr(instance, '_current_user', None)
    if not user:
        return
        
    if kwargs.get('created', False):
        create_activity(
            user,
            f"Added new License Metric: {instance.name}",
            instance.description
        )
    elif kwargs.get('signal', None) == post_delete:
        create_activity(
            user,
            f"Deleted License Metric: {instance.name}"
        )
    else:
        create_activity(
            user,
            f"Updated License Metric: {instance.name}"
        ) 