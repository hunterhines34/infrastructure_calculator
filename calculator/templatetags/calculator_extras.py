from django import template
import logging

logger = logging.getLogger(__name__)
register = template.Library()

@register.filter
def get_range(value):
    return range(1, value + 1)

@register.filter
def percentage(value, total):
    try:
        return (value / total) * 100
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0 

@register.filter
def status_icon(status):
    """Returns the appropriate Font Awesome icon class for a given status."""
    icons = {
        'draft': 'pencil-alt',
        'pending': 'clock',
        'active': 'play',
        'completed': 'check-circle',
        'rejected': 'times-circle'
    }
    return icons.get(status, 'question-circle') 

@register.filter
def subtract(value, arg):
    """Subtract the arg from the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0 

@register.filter
def sum_cores(configurations):
    total_cores = 0
    for config in configurations:
        if config.cpu and hasattr(config.cpu, 'cores'):
            try:
                total_cores += int(config.cpu.cores)
            except (ValueError, TypeError):
                continue
    return total_cores

@register.filter
def sum_ram(configurations):
    total_ram = 0
    for config in configurations:
        if config.ram and hasattr(config.ram, 'capacity_gb'):
            try:
                total_ram += int(config.ram.capacity_gb)
            except (ValueError, TypeError):
                continue
    return total_ram

@register.filter
def sum_storage(configurations):
    total_gb = 0
    for config in configurations:
        if config.storage and hasattr(config.storage, 'capacity'):
            try:
                capacity = int(config.storage.capacity)
                # Convert all storage to GB for consistent summing
                if config.storage.capacity_unit == 'tb':
                    capacity *= 1024
                elif config.storage.capacity_unit == 'pb':
                    capacity *= 1024 * 1024
                total_gb += capacity
            except (ValueError, TypeError):
                continue
    # Convert back to most appropriate unit
    if total_gb >= 1024 * 1024:
        return f"{total_gb // (1024 * 1024)} PB"
    elif total_gb >= 1024:
        return f"{total_gb // 1024} TB"
    return f"{total_gb} GB"

@register.filter
def sum_gpu_memory(configurations):
    total_memory = 0
    gpu_count = 0
    for config in configurations:
        if config.gpu and hasattr(config.gpu, 'memory_gb'):
            try:
                total_memory += int(config.gpu.memory_gb)
                gpu_count += 1
            except (ValueError, TypeError):
                continue
    if gpu_count > 0:
        return f"{gpu_count} GPU{'s' if gpu_count > 1 else ''} ({total_memory} GB)"
    return None 