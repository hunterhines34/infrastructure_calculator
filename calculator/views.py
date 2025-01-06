from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    CPU, RAM, Storage, GPU, NetworkCard, 
    LicenseMetric, LicenseProduct,
    Manufacturer, Project, ServerConfiguration, 
    SavedConfiguration, UserActivity, Notification, LicensePricing, ServerConfigurationComponent
)
from iommi import Table
from django.shortcuts import render, redirect
from django import forms
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.views.decorators.http import require_POST
import csv
from django.http import HttpResponse
from django.urls import reverse
from django.http import JsonResponse
from datetime import datetime
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Count, Sum, Avg
import json
from datetime import timedelta
from decimal import Decimal
from django.db.models import Q

def get_dashboard_context():
    all_projects = Project.objects.all()
    
    # Organize projects by status
    project_tabs = {
        'draft': all_projects.filter(status='draft'),
        'pending': all_projects.filter(status='pending'),
        'active': all_projects.filter(status='active'),
        'completed': all_projects.filter(status='completed'),
        'cancelled': all_projects.filter(status='cancelled'),
    }
    
    # Get counts for each status
    status_counts = {
        f"{status}_projects_count": projects.count()
        for status, projects in project_tabs.items()
    }
    
    return {
        'project_count': all_projects.count(),
        'server_count': ServerConfiguration.objects.count(),
        'saved_config_count': SavedConfiguration.objects.count(),
        'project_tabs': project_tabs,
        **status_counts,  # This unpacks all the status counts
    }

def dashboard(request):
    # Get all projects
    projects = Project.objects.all()

    # Get current page and status from URL parameters
    current_page = request.GET.get('page', 1)
    current_status = request.GET.get('status', 'draft')
    try:
        current_page = int(current_page)
    except ValueError:
        current_page = 1

    items_per_page = 10

    # Create project_tabs dictionary with filtered projects
    project_tabs = {
        'draft': projects.filter(status='draft'),
        'pending': projects.filter(status='pending'),
        'active': projects.filter(status='active'),
        'completed': projects.filter(status='completed'),
        'cancelled': projects.filter(status='cancelled')
    }

    # Calculate pagination for current status
    current_projects = project_tabs[current_status]
    total_items = len(current_projects)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    start_idx = (current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)

    # Create the context dictionary
    context = {
        'project_count': projects.count(),
        'active_projects_count': projects.filter(status='active').count(),
        'pending_projects_count': projects.filter(status='pending').count(),
        'draft_projects_count': projects.filter(status='draft').count(),
        'completed_projects_count': projects.filter(status='completed').count(),
        'cancelled_projects_count': projects.filter(status='cancelled').count(),
        'server_count': ServerConfiguration.objects.count(),
        'saved_config_count': SavedConfiguration.objects.count(),
        'project_tabs': project_tabs,
        # Pagination context
        'current_page': current_page,
        'total_pages': total_pages,
        'page_start': start_idx,
        'page_end': end_idx,
        'page_range': range(1, total_pages + 1),
        'current_status': current_status,
    }

    return render(request, 'calculator/dashboard.html', context)

class ServerConfigurationListView(ListView):
    model = ServerConfiguration
    template_name = 'calculator/serverconfiguration_list.html'
    context_object_name = 'configurations'

    def get_queryset(self):
        return ServerConfiguration.objects.filter(project__created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'serverconfigurations'
        return context

class ServerConfigurationCreateView(CreateView):
    model = ServerConfiguration
    fields = ['project', 'name', 'cpu', 'ram', 'storage', 'gpu', 'network_card', 'os', 'notes']
    
    def get_success_url(self):
        if 'project' in self.request.GET:
            return reverse_lazy('project_detail', kwargs={'pk': self.request.GET['project']})
        return reverse_lazy('serverconfiguration_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add choices for components
        context.update({
            'cpu_choices': CPU.objects.all(),
            'ram_choices': RAM.objects.all(),
            'storage_choices': Storage.objects.all(),
            'gpu_choices': GPU.objects.all(),
        })
        
        # Handle project field
        if 'project' in self.request.GET:
            context['cancel_url'] = reverse_lazy('project_detail', kwargs={'pk': self.request.GET['project']})
            context['form'].fields['project'].initial = self.request.GET['project']
            context['form'].fields['project'].widget = forms.HiddenInput()
        else:
            context['cancel_url'] = reverse_lazy('serverconfiguration_list')
            
        return context

    def form_valid(self, form):
        # If project is in GET parameters, set it before saving
        if 'project' in self.request.GET:
            form.instance.project_id = self.request.GET['project']
        return super().form_valid(form)

class ServerConfigurationUpdateView(UpdateView):
    model = ServerConfiguration
    fields = ['name', 'cpu', 'ram', 'storage', 'gpu', 'network_card', 'os', 'notes']
    
    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.project.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add choices for components
        context.update({
            'cpu_choices': CPU.objects.all(),
            'ram_choices': RAM.objects.all(),
            'storage_choices': Storage.objects.all(),
            'gpu_choices': GPU.objects.all(),
        })
        
        context['cancel_url'] = reverse_lazy('project_detail', kwargs={'pk': self.object.project.pk})
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Handle additional components
        for component_type in ['cpu', 'ram', 'storage', 'gpu']:
            components = self.request.POST.getlist(f'additional_{component_type}[]')
            quantities = self.request.POST.getlist(f'additional_{component_type}_quantity[]')
            
            for component_id, quantity in zip(components, quantities):
                if component_id and quantity:
                    ServerConfigurationComponent.objects.create(
                        server_configuration=self.object,
                        **{component_type: get_object_or_404(
                            {'cpu': CPU, 'ram': RAM, 'storage': Storage, 'gpu': GPU}[component_type], 
                            pk=component_id
                        )},
                        quantity=quantity
                    )
        
        return response

class ServerConfigurationDeleteView(LoginRequiredMixin, DeleteView):
    model = ServerConfiguration
    
    def get_success_url(self):
        project_id = self.object.project.id
        return reverse_lazy('project_detail', kwargs={'pk': project_id})

class SavedConfigurationListView(LoginRequiredMixin, ListView):
    model = SavedConfiguration
    template_name = 'calculator/savedconfiguration_list.html'
    context_object_name = 'table'
    paginate_by = 10

    def get_queryset(self):
        # Filter based on user permissions
        if self.request.user.is_staff:
            queryset = SavedConfiguration.objects.all()
        else:
            queryset = SavedConfiguration.objects.filter(created_by=self.request.user)

        # Keep existing search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Keep existing sorting functionality
        sort_by = self.request.GET.get('sort', '-created_at')
        return queryset.order_by(sort_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        # Format the data for the template
        context['table'] = {
            'rows': queryset  # This matches what the template expects
        }
        
        # Calculate pagination values
        current_page = self.request.GET.get('page', 1)
        try:
            current_page = int(current_page)
        except ValueError:
            current_page = 1

        items_per_page = self.paginate_by
        total_items = queryset.count()
        total_pages = (total_items + items_per_page - 1) // items_per_page
        start_idx = (current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)

        # Update context with pagination data
        context.update({
            'current_page': current_page,
            'total_pages': total_pages,
            'page_start': start_idx,
            'page_end': end_idx,
            'page_range': range(1, total_pages + 1),
            'sort_by': self.request.GET.get('sort', '-created_at'),
            'search_query': self.request.GET.get('search', ''),
        })

        return context

class SavedConfigurationCreateView(CreateView):
    model = SavedConfiguration
    template_name = 'calculator/savedconfiguration_form.html'
    fields = ['name', 'description', 'cpu', 'ram', 'storage', 'gpu', 'network_card', 'os', 'notes']
    success_url = reverse_lazy('savedconfiguration_list')

class SavedConfigurationUpdateView(UpdateView):
    model = SavedConfiguration
    template_name = 'calculator/savedconfiguration_form.html'
    fields = ['name', 'description', 'cpu', 'ram', 'storage', 'gpu', 'network_card', 'os', 'notes']
    success_url = reverse_lazy('savedconfiguration_list')

class SavedConfigurationDeleteView(LoginRequiredMixin, DeleteView):
    model = SavedConfiguration
    
    def get_success_url(self):
        if 'project_id' in self.request.GET:
            return reverse_lazy('project_detail', kwargs={'pk': self.request.GET['project_id']})
        return reverse_lazy('savedconfiguration_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)
    
    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

# New CPU Views
class CPUListView(ListView):
    model = CPU
    template_name = 'calculator/cpu_list.html'
    context_object_name = 'cpus'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['manufacturers'] = Manufacturer.objects.all()
        context['active_tab'] = 'cpus'
        return context

class CPUCreateView(CreateView):
    model = CPU
    template_name = 'calculator/cpu_form.html'
    fields = ['name', 'model', 'manufacturer', 'architecture', 'cores', 'threads', 'clock_speed', 'power_consumption_watts']
    success_url = reverse_lazy('cpu_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['manufacturers'] = Manufacturer.objects.all()
        return context

class CPUUpdateView(UpdateView):
    model = CPU
    template_name = 'calculator/cpu_form.html'
    fields = ['name', 'model', 'manufacturer', 'architecture', 'cores', 'threads', 'clock_speed', 'power_consumption_watts']
    success_url = reverse_lazy('cpu_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['manufacturers'] = Manufacturer.objects.all()
        return context

class UserTrackingDeleteMixin:
    def delete(self, request, *args, **kwargs):
        # Set the current user before deletion for signal handling
        self.object = self.get_object()
        self.object._current_user = request.user
        return super().delete(request, *args, **kwargs)

# CPU Views
class CPUDeleteView(UserTrackingDeleteMixin, DeleteView):
    model = CPU
    success_url = reverse_lazy('cpu_list')
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

class RAMListView(ListView):
    model = RAM
    template_name = 'calculator/ram_list.html'
    context_object_name = 'rams'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['manufacturers'] = Manufacturer.objects.all()
        context['active_tab'] = 'ram'
        return context

class RAMCreateView(CreateView):
    model = RAM
    template_name = 'calculator/ram_form.html'
    fields = ['name', 'model', 'manufacturer', 'capacity_gb', 'speed', 'ram_type', 'latency_ns']
    success_url = reverse_lazy('ram_list')

class RAMUpdateView(UpdateView):
    model = RAM
    template_name = 'calculator/ram_form.html'
    fields = ['name', 'model', 'manufacturer', 'capacity_gb', 'speed', 'ram_type', 'latency_ns']
    success_url = reverse_lazy('ram_list')

# RAM Views
class RAMDeleteView(UserTrackingDeleteMixin, DeleteView):
    model = RAM
    success_url = reverse_lazy('ram_list')
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

class StorageListView(ListView):
    model = Storage
    template_name = 'calculator/storage_list.html'
    context_object_name = 'storages'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['manufacturers'] = Manufacturer.objects.all()
        context['active_tab'] = 'storage'
        return context

class StorageCreateView(CreateView):
    model = Storage
    template_name = 'calculator/storage_form.html'
    fields = ['name', 'model', 'manufacturer', 'capacity', 'capacity_unit', 
              'storage_type', 'interface', 'price_per_gb', 'price_per_tb', 
              'price_per_pb', 'form_factor']
    success_url = reverse_lazy('storage_list')

class StorageUpdateView(UpdateView):
    model = Storage
    template_name = 'calculator/storage_form.html'
    fields = ['name', 'model', 'manufacturer', 'capacity', 'capacity_unit', 
              'storage_type', 'interface', 'price_per_gb', 'price_per_tb', 
              'price_per_pb', 'form_factor']
    success_url = reverse_lazy('storage_list')

# Storage Views
class StorageDeleteView(UserTrackingDeleteMixin, DeleteView):
    model = Storage
    success_url = reverse_lazy('storage_list')
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

class GPUListView(ListView):
    model = GPU
    template_name = 'calculator/gpu_list.html'
    context_object_name = 'gpus'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['manufacturers'] = Manufacturer.objects.all()
        context['active_tab'] = 'gpus'
        return context

class GPUCreateView(CreateView):
    model = GPU
    template_name = 'calculator/gpu_form.html'
    fields = ['name', 'model', 'manufacturer', 'memory_gb', 'clock_speed', 'power_consumption_watts']
    success_url = reverse_lazy('gpu_list')

class GPUUpdateView(UpdateView):
    model = GPU
    template_name = 'calculator/gpu_form.html'
    fields = ['name', 'model', 'manufacturer', 'memory_gb', 'clock_speed', 'power_consumption_watts']
    success_url = reverse_lazy('gpu_list')

# GPU Views
class GPUDeleteView(UserTrackingDeleteMixin, DeleteView):
    model = GPU
    success_url = reverse_lazy('gpu_list')
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

class NetworkCardListView(ListView):
    model = NetworkCard
    template_name = 'calculator/networkcard_list.html'
    context_object_name = 'networkcards'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['manufacturers'] = Manufacturer.objects.all()
        context['active_tab'] = 'networkcards'
        return context

class NetworkCardCreateView(CreateView):
    model = NetworkCard
    template_name = 'calculator/networkcard_form.html'
    fields = ['name', 'model', 'manufacturer', 'speed_gbps', 'interface', 'port_type']
    success_url = reverse_lazy('networkcard_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['manufacturers'] = Manufacturer.objects.all()
        return context

class NetworkCardUpdateView(UpdateView):
    model = NetworkCard
    template_name = 'calculator/networkcard_form.html'
    fields = ['name', 'model', 'manufacturer', 'speed_gbps', 'interface', 'port_type']
    success_url = reverse_lazy('networkcard_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['manufacturers'] = Manufacturer.objects.all()
        return context

# Network Card Views
class NetworkCardDeleteView(UserTrackingDeleteMixin, DeleteView):
    model = NetworkCard
    success_url = reverse_lazy('networkcard_list')
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

class ManufacturerListView(ListView):
    model = Manufacturer
    template_name = 'calculator/manufacturer_list.html'
    context_object_name = 'manufacturers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'manufacturers'
        return context

class ManufacturerCreateView(CreateView):
    model = Manufacturer
    template_name = 'calculator/manufacturer_form.html'
    fields = ['name', 'website', 'description', 'contact_email']
    success_url = reverse_lazy('manufacturer_list')

class ManufacturerUpdateView(UpdateView):
    model = Manufacturer
    template_name = 'calculator/manufacturer_form.html'
    fields = ['name', 'website', 'description', 'contact_email']
    success_url = reverse_lazy('manufacturer_list')

# Manufacturer Views
class ManufacturerDeleteView(UserTrackingDeleteMixin, DeleteView):
    model = Manufacturer
    success_url = reverse_lazy('manufacturer_list')
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

class ProjectListView(ListView):
    model = Project
    template_name = 'calculator/project_list.html'
    context_object_name = 'projects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all projects
        all_projects = Project.objects.all()
        
        # Get current page and status from URL parameters
        current_page = self.request.GET.get('page', 1)
        current_status = self.request.GET.get('status', 'draft')
        try:
            current_page = int(current_page)
        except ValueError:
            current_page = 1

        items_per_page = 10
        
        # Organize projects by status
        project_tabs = {
            'draft': all_projects.filter(status='draft'),
            'pending': all_projects.filter(status='pending'),
            'active': all_projects.filter(status='active'),
            'completed': all_projects.filter(status='completed'),
            'cancelled': all_projects.filter(status='cancelled'),
        }
        
        # Calculate pagination for current status
        current_projects = project_tabs[current_status]
        total_items = len(current_projects)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        start_idx = (current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        
        # Get counts for each status
        status_counts = {
            f"{status}_projects_count": projects.count()
            for status, projects in project_tabs.items()
        }
        
        context.update({
            'project_tabs': project_tabs,
            **status_counts,
            # Pagination context
            'current_page': current_page,
            'total_pages': total_pages,
            'page_start': start_idx,
            'page_end': end_idx,
            'page_range': range(1, total_pages + 1),
            'current_status': current_status,
        })
        
        return context

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date']

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'calculator/project_form.html'
    fields = ['name', 'description', 'start_date', 'end_date']
    success_url = reverse_lazy('project_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # If this is an existing project (editing)
        if self.object and self.object.pk:
            context['cancel_url'] = reverse_lazy('project_detail', kwargs={'pk': self.object.pk})
        else:
            # If this is a new project
            context['cancel_url'] = reverse_lazy('project_list')
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    template_name = 'calculator/project_form.html'
    fields = ['name', 'description', 'start_date', 'end_date', 'status']
    
    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('project_detail', kwargs={'pk': self.object.pk})
        return context

    def test_func(self):
        project = self.get_object()
        # Allow access if user is staff or is the project owner
        return self.request.user.is_staff or project.created_by == self.request.user

    def form_valid(self, form):
        if not self.request.user.is_staff:
            # Regular users can only set certain statuses
            new_status = form.cleaned_data.get('status')
            allowed_statuses = ['draft', 'pending', 'cancelled']
            current_status = self.get_object().status
            
            if current_status in ['active', 'completed'] and new_status not in allowed_statuses:
                form.add_error('status', 'You do not have permission to set this status.')
                return self.form_invalid(form)
                
        return super().form_valid(form)

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    success_url = reverse_lazy('project_list')
    
    def delete(self, request, *args, **kwargs):
        try:
            project = get_object_or_404(Project, pk=self.kwargs['pk'])
            project_name = project.name
            project.delete()
            messages.success(request, f'Project "{project_name}" was successfully deleted.')
            return HttpResponseRedirect(self.success_url)
        except Project.DoesNotExist:
            messages.error(request, 'Project could not be found.')
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            messages.error(request, f'An error occurred while deleting the project: {str(e)}')
            return HttpResponseRedirect(self.success_url)

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'calculator/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        
        # Add cost calculations to existing context
        context.update({
            'hardware_costs': project.calculate_hardware_costs(),
            'license_costs': project.calculate_license_costs(),
            'total_cost': project.calculate_total_cost(),
        })
        
        # Existing context data
        context['activities'] = self.object.activities.all()[:5]
        context['saved_configurations'] = SavedConfiguration.objects.all()
        
        return context

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'calculator/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get counts
        context['projects_count'] = Project.objects.filter(created_by=user).count()
        context['configurations_count'] = ServerConfiguration.objects.filter(
            project__created_by=user
        ).count()
        context['saved_configs_count'] = SavedConfiguration.objects.count()
        
        # Get recent activities
        recent_activities = UserActivity.objects.filter(user=user)[:10]
        context['recent_activities'] = recent_activities
        context['recent_activities_count'] = recent_activities.count()
        
        context['active_tab'] = 'profile'  # For sidebar highlighting
        return context

class LicenseProductListView(ListView):
    model = LicenseProduct
    template_name = 'calculator/license_list.html'
    context_object_name = 'licenses'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'licenses'
        return context

class LicenseProductCreateView(CreateView):
    model = LicenseProduct
    template_name = 'calculator/license_form.html'
    fields = ['name', 'manufacturer', 'version', 'edition', 
              'is_core_based', 'is_socket_based', 'is_user_based',
              'min_cores_per_processor', 'min_cores_per_server',
              'core_pack_size', 'requires_cal', 'notes']
    success_url = reverse_lazy('license_list')

class LicenseProductUpdateView(UpdateView):
    model = LicenseProduct
    template_name = 'calculator/license_form.html'
    fields = ['name', 'manufacturer', 'version', 'edition', 
              'is_core_based', 'is_socket_based', 'is_user_based',
              'min_cores_per_processor', 'min_cores_per_server',
              'core_pack_size', 'requires_cal', 'notes']
    success_url = reverse_lazy('license_list')

class LicenseProductDeleteView(UserTrackingDeleteMixin, DeleteView):
    model = LicenseProduct
    success_url = reverse_lazy('license_list')
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

class LicenseMetricListView(ListView):
    model = LicenseMetric
    template_name = 'calculator/license_metric_list.html'
    context_object_name = 'metrics'

class LicenseMetricCreateView(CreateView):
    model = LicenseMetric
    template_name = 'calculator/license_metric_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('license_metric_list')

class LicenseMetricUpdateView(UpdateView):
    model = LicenseMetric
    template_name = 'calculator/license_metric_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('license_metric_list')

class LicenseMetricDeleteView(DeleteView):
    model = LicenseMetric
    success_url = reverse_lazy('license_metric_list')
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

@require_POST
@login_required
def project_submit_review(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.status == 'draft':
        project.status = 'pending'
        project.save()
        
        # Create notifications for all staff users
        from django.contrib.auth.models import User
        staff_users = User.objects.filter(is_staff=True)
        for user in staff_users:
            # Check if a notification already exists for this project and user
            existing_notification = Notification.objects.filter(
                recipient=user,
                notification_type='approval_needed',
                related_link=reverse('project_detail', kwargs={'pk': project.pk}),
                is_read=False
            ).exists()
            
            # Only create notification if one doesn't already exist
            if not existing_notification:
                Notification.objects.create(
                    recipient=user,
                    notification_type='approval_needed',
                    title='New Project Needs Approval',
                    message=f'Project "{project.name}" requires your approval',
                    related_link=reverse('project_detail', kwargs={'pk': project.pk}),
                    is_read=False
                )
        
        messages.success(request, 'Project submitted for review successfully.')
    return redirect('project_detail', pk=pk)

@require_POST
@login_required
def project_approve(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user.is_staff and project.status == 'pending':
        project.status = 'active'
        project.save()
        messages.success(request, 'Project approved successfully.')
    return redirect('project_detail', pk=pk)

@require_POST
@login_required
def project_reject(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user.is_staff and project.status == 'pending':
        project.status = 'cancelled'
        project.save()
        messages.success(request, 'Project rejected.')
    return redirect('project_detail', pk=pk)

@require_POST
@login_required
def load_saved_configuration(request, project_pk, config_pk):
    project = get_object_or_404(Project, pk=project_pk)
    saved_config = get_object_or_404(SavedConfiguration, pk=config_pk)
    
    # Create new server configuration from saved configuration
    new_config = ServerConfiguration.objects.create(
        project=project,
        name=f"Loaded: {saved_config.name}",
        cpu=saved_config.cpu,
        ram=saved_config.ram,
        storage=saved_config.storage,
        gpu=saved_config.gpu,
        network_card=saved_config.network_card,
        os=saved_config.os,
        notes=saved_config.notes
    )
    
    messages.success(request, f'Configuration "{saved_config.name}" loaded successfully.')
    return redirect('project_detail', pk=project_pk)

@require_POST
@login_required
def project_revert_to_draft(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.status == 'pending':
        project.status = 'draft'
        project.save()
        messages.success(request, 'Project reverted to draft status.')
    return redirect('project_detail', pk=pk)

@login_required
def export_configurations(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="server_configurations.csv"'},
    )
    
    writer = csv.writer(response)
    # Add more comprehensive headers
    writer.writerow([
        'Name',
        'CPU Model',
        'CPU Cores',
        'Memory (GB)',
        'Storage Capacity',
        'Storage Type',
        'GPU Model',
        'Network Card',
        'Operating System',
        'Hardware Cost',
        'License Cost',
        'Total Cost'
    ])
    
    configurations = ServerConfiguration.objects.all()
    for config in configurations:
        writer.writerow([
            config.name,
            config.cpu.name if config.cpu else 'N/A',
            config.cpu.cores if config.cpu else 'N/A',
            config.ram.capacity_gb if config.ram else 'N/A',
            f"{config.storage.capacity} {config.storage.get_capacity_unit_display()}" if config.storage else 'N/A',
            config.storage.get_storage_type_display() if config.storage else 'N/A',
            config.gpu.name if config.gpu else 'N/A',
            config.network_card.name if config.network_card else 'N/A',
            config.os or 'N/A',
            f"${config.calculate_hardware_cost():,.2f}",
            f"${config.calculate_license_costs():,.2f}",
            f"${config.calculate_total_cost():,.2f}"
        ])
    
    return response

class NotificationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Notification
    template_name = 'calculator/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 10  # Show 10 notifications per page
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user,
            is_read=False  # Only show unread notifications
        ).order_by('-created_at')

@require_POST
@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

@require_POST
@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    return JsonResponse({'status': 'success'})

class ApprovalsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Project
    template_name = 'calculator/approvals.html'
    context_object_name = 'projects'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        return Project.objects.filter(status='pending').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'approvals'
        return context

class LicensePricingCreateView(CreateView):
    model = LicensePricing
    fields = ['license_product', 'metric', 'quantity_per_pack', 'price', 'valid_from', 'valid_to']
    template_name = 'calculator/license_pricing_form.html'
    success_url = reverse_lazy('license_list')

    def get_initial(self):
        initial = super().get_initial()
        license_id = self.request.GET.get('license')
        if license_id:
            initial['license_product'] = license_id
        return initial

class LicensePricingEditView(UpdateView):
    model = LicensePricing
    fields = ['license_product', 'metric', 'quantity_per_pack', 'price', 'valid_from', 'valid_to']
    template_name = 'calculator/license_pricing_form.html'
    success_url = reverse_lazy('license_list')

class LicensePricingDeleteView(DeleteView):
    model = LicensePricing
    success_url = reverse_lazy('license_list')

class ServerConfigurationDetailView(DetailView):
    model = ServerConfiguration
    template_name = 'calculator/serverconfiguration_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = self.object
        context.update({
            'hardware_cost': config.calculate_hardware_cost(),
            'license_cost': config.calculate_license_costs(),
            'total_cost': config.calculate_total_cost(),
        })
        return context

def saved_configurations_export(request):
    """Export saved configurations to CSV"""
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    # Create a view instance with the request
    view = SavedConfigurationListView()
    view.request = request  # Set the request
    view.kwargs = {}  # Initialize kwargs if needed
    view.args = []    # Initialize args if needed
    
    # Get configurations with search filter if present
    configurations = view.get_queryset()

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="saved_configurations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(['Name', 'Description', 'CPU', 'RAM', 'Storage', 'Created Date'])

    for config in configurations:
        writer.writerow([
            config.name,
            config.description or '',
            config.cpu.name if config.cpu else '',
            config.ram.name if config.ram else '',
            config.storage.name if config.storage else '',
            config.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response

class ProjectExportView(LoginRequiredMixin, View):
    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        
        # Calculate total costs
        hardware_cost = sum(config.calculate_hardware_cost() for config in project.server_configurations.all())
        license_cost = sum(config.calculate_license_costs() for config in project.server_configurations.all())
        total_cost = hardware_cost + license_cost
        
        # Create the HttpResponse object with CSV header
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{project.name}_details.csv"'},
        )
        
        writer = csv.writer(response)
        
        # Write project details header
        writer.writerow(['Project Details'])
        writer.writerow(['Name', 'Status', 'Created By', 'Created Date', 'Last Updated'])
        writer.writerow([
            project.name,
            project.get_status_display(),
            project.created_by.get_full_name() if project.created_by else 'System',
            project.created_at.strftime('%Y-%m-%d'),
            project.updated_at.strftime('%Y-%m-%d')
        ])
        
        # Add a blank row for spacing
        writer.writerow([])
        
        # Write cost summary
        writer.writerow(['Cost Summary'])
        writer.writerow(['Hardware Costs', 'License Costs', 'Total Cost'])
        writer.writerow([
            f'${hardware_cost:,.2f}',
            f'${license_cost:,.2f}',
            f'${total_cost:,.2f}'
        ])
        
        # Add a blank row for spacing
        writer.writerow([])
        
        # Write server configurations
        writer.writerow(['Server Configurations'])
        writer.writerow([
            'Name',
            'CPU',
            'Cores',
            'RAM (GB)',
            'Storage',
            'Storage Type',
            'GPU',
            'GPU Memory (GB)',
            'Network Card',
            'Network Speed',
            'Operating System',
            'Hardware Cost',
            'License Cost',
            'Total Cost'
        ])
        
        for config in project.server_configurations.all():
            writer.writerow([
                config.name,
                config.cpu.name if config.cpu else 'N/A',
                config.cpu.cores if config.cpu else 'N/A',
                config.ram.capacity_gb if config.ram else 'N/A',
                f"{config.storage.capacity} {config.storage.get_capacity_unit_display()}" if config.storage else 'N/A',
                config.storage.get_storage_type_display() if config.storage else 'N/A',
                config.gpu.name if config.gpu else 'N/A',
                config.gpu.memory_gb if config.gpu else 'N/A',
                config.network_card.name if config.network_card else 'N/A',
                f"{config.network_card.speed_gbps} Gbps" if config.network_card else 'N/A',
                config.os or 'N/A',
                f'${config.calculate_hardware_cost():,.2f}',
                f'${config.calculate_license_costs():,.2f}',
                f'${config.calculate_total_cost():,.2f}'
            ])
        
        return response

class ReportsView(TemplateView):
    template_name = 'calculator/reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all projects for the projects table
        context['projects'] = Project.objects.all().order_by('-created_at')
        
        # Keep all existing context data
        active_projects = Project.objects.exclude(status='cancelled')
        context['active_projects_count'] = active_projects.count()
        
        # Calculate total costs
        total_hardware_cost = sum(
            project.calculate_hardware_costs() 
            for project in active_projects
        )
        total_license_cost = sum(
            project.calculate_license_costs() 
            for project in active_projects
        )
        
        context['total_hardware_cost'] = total_hardware_cost
        context['total_license_cost'] = total_license_cost
        context['avg_project_cost'] = (total_hardware_cost + total_license_cost) / active_projects.count() if active_projects.count() > 0 else 0
        
        # Project status data for chart
        status_data = Project.objects.values('status').annotate(count=Count('id'))
        context['project_status_labels'] = json.dumps([item['status'].title() for item in status_data])
        context['project_status_data'] = json.dumps([item['count'] for item in status_data])
        
        # Keep all other existing context data...
        # CPU Analysis
        cpu_manufacturer_data = CPU.objects.values(
            'manufacturer__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        context['cpu_manufacturer_labels'] = json.dumps(
            [item['manufacturer__name'] for item in cpu_manufacturer_data]
        )
        context['cpu_manufacturer_data'] = json.dumps(
            [item['count'] for item in cpu_manufacturer_data]
        )
        
        # Storage Analysis
        storage_type_data = Storage.objects.values(
            'storage_type'
        ).annotate(
            count=Count('id')
        )
        
        context['storage_type_labels'] = json.dumps(
            [item['storage_type'].upper() for item in storage_type_data]
        )
        context['storage_type_data'] = json.dumps(
            [item['count'] for item in storage_type_data]
        )
        
        # Cost trend data
        months = 6
        cost_trend_labels = []
        cost_trend_data = []
        
        for i in range(months-1, -1, -1):
            date = timezone.now() - timedelta(days=i*30)
            month_projects = Project.objects.filter(
                created_at__year=date.year,
                created_at__month=date.month
            )
            total_cost = sum(
                project.calculate_total_cost() 
                for project in month_projects
            )
            cost_trend_labels.append(date.strftime('%B %Y'))
            cost_trend_data.append(float(total_cost))
        
        context['cost_trend_labels'] = json.dumps(cost_trend_labels)
        context['cost_trend_data'] = json.dumps(cost_trend_data)
        
        # RAM Type Analysis
        ram_type_data = RAM.objects.values(
            'ram_type'
        ).annotate(
            count=Count('id')
        )
        context['ram_type_labels'] = json.dumps(
            [item['ram_type'].upper() for item in ram_type_data]
        )
        context['ram_type_data'] = json.dumps(
            [item['count'] for item in ram_type_data]
        )

        # RAM Capacity Analysis
        ram_capacity_data = RAM.objects.values(
            'capacity_gb'
        ).annotate(
            count=Count('id')
        ).order_by('capacity_gb')
        context['ram_capacity_labels'] = json.dumps(
            [f"{item['capacity_gb']}GB" for item in ram_capacity_data]
        )
        context['ram_capacity_data'] = json.dumps(
            [item['count'] for item in ram_capacity_data]
        )

        # GPU Memory Analysis
        gpu_memory_data = GPU.objects.values(
            'memory_gb'
        ).annotate(
            count=Count('id')
        ).order_by('memory_gb')
        context['gpu_memory_labels'] = json.dumps(
            [f"{item['memory_gb']}GB" for item in gpu_memory_data]
        )
        context['gpu_memory_data'] = json.dumps(
            [item['count'] for item in gpu_memory_data]
        )

        # Network Card Interface Analysis
        network_interface_data = NetworkCard.objects.values(
            'interface'
        ).annotate(
            count=Count('id')
        )
        context['network_interface_labels'] = json.dumps(
            [item['interface'].title() for item in network_interface_data]
        )
        context['network_interface_data'] = json.dumps(
            [item['count'] for item in network_interface_data]
        )

        # Component Cost Analysis
        component_costs = []
        
        # CPU Costs
        cpu_data = CPU.objects.aggregate(
            total_cost=Sum('price'),
            avg_cost=Avg('price'),
            total_units=Count('id')
        )
        if cpu_data['total_units'] > 0:
            component_costs.append({
                'type': 'CPU',
                'avg_cost': round(Decimal(cpu_data['avg_cost'] or 0), 2),
                'total_units': cpu_data['total_units'],
                'total_cost': round(Decimal(cpu_data['total_cost'] or 0), 2)
            })

        # RAM Costs
        ram_data = RAM.objects.aggregate(
            total_cost=Sum('price'),
            avg_cost=Avg('price'),
            total_units=Count('id')
        )
        if ram_data['total_units'] > 0:
            component_costs.append({
                'type': 'RAM',
                'avg_cost': round(Decimal(ram_data['avg_cost'] or 0), 2),
                'total_units': ram_data['total_units'],
                'total_cost': round(Decimal(ram_data['total_cost'] or 0), 2)
            })

        # Storage Costs
        storage_data = Storage.objects.aggregate(
            total_cost=Sum('price'),
            avg_cost=Avg('price'),
            total_units=Count('id')
        )
        if storage_data['total_units'] > 0:
            component_costs.append({
                'type': 'Storage',
                'avg_cost': round(Decimal(storage_data['avg_cost'] or 0), 2),
                'total_units': storage_data['total_units'],
                'total_cost': round(Decimal(storage_data['total_cost'] or 0), 2)
            })

        # GPU Costs
        gpu_data = GPU.objects.aggregate(
            total_cost=Sum('price'),
            avg_cost=Avg('price'),
            total_units=Count('id')
        )
        if gpu_data['total_units'] > 0:
            component_costs.append({
                'type': 'GPU',
                'avg_cost': round(Decimal(gpu_data['avg_cost'] or 0), 2),
                'total_units': gpu_data['total_units'],
                'total_cost': round(Decimal(gpu_data['total_cost'] or 0), 2)
            })

        # Network Card Costs
        network_data = NetworkCard.objects.aggregate(
            total_cost=Sum('price'),
            avg_cost=Avg('price'),
            total_units=Count('id')
        )
        if network_data['total_units'] > 0:
            component_costs.append({
                'type': 'Network Card',
                'avg_cost': round(Decimal(network_data['avg_cost'] or 0), 2),
                'total_units': network_data['total_units'],
                'total_cost': round(Decimal(network_data['total_cost'] or 0), 2)
            })

        context['component_costs'] = component_costs
        
        return context