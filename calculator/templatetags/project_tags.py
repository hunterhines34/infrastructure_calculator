from django import template

register = template.Library()

@register.filter
def sum_cores(configurations):
    """Sum the total CPU cores across all configurations"""
    return sum(config.cpu.cores for config in configurations if config.cpu)

@register.filter
def sum_ram(configurations):
    """Sum the total RAM across all configurations"""
    return sum(config.ram.size for config in configurations if config.ram) 