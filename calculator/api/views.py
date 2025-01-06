from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    UserSerializer, GroupSerializer, ManufacturerSerializer,
    CPUSerializer, RAMSerializer, StorageSerializer, GPUSerializer,
    NetworkCardSerializer, LicenseMetricSerializer, LicenseProductSerializer,
    LicensePricingSerializer, ProjectSerializer, ServerConfigurationSerializer,
    SavedConfigurationSerializer, UserActivitySerializer, ProjectActivitySerializer,
    NotificationSerializer, ProjectApprovalSerializer
)
from calculator.models import (
    Manufacturer, CPU, RAM, Storage, GPU, NetworkCard,
    LicenseMetric, LicenseProduct, LicensePricing,
    Project, ServerConfiguration, SavedConfiguration,
    UserActivity, ProjectActivity, Notification, ProjectApproval
)
from django.utils import timezone
from django.db.models import Q

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]

class GPUViewSet(viewsets.ModelViewSet):
    queryset = GPU.objects.all()
    serializer_class = GPUSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['manufacturer', 'memory_gb']
    search_fields = ['name', 'model']

class NetworkCardViewSet(viewsets.ModelViewSet):
    queryset = NetworkCard.objects.all()
    serializer_class = NetworkCardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['manufacturer', 'interface']
    search_fields = ['name', 'model']

class LicenseMetricViewSet(viewsets.ModelViewSet):
    queryset = LicenseMetric.objects.all()
    serializer_class = LicenseMetricSerializer
    permission_classes = [permissions.IsAuthenticated]

class LicenseProductViewSet(viewsets.ModelViewSet):
    queryset = LicenseProduct.objects.all()
    serializer_class = LicenseProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['manufacturer', 'edition']
    search_fields = ['name', 'version']

class ServerConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = ServerConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ServerConfiguration.objects.filter(
            project__created_by=self.request.user
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class SavedConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = SavedConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SavedConfiguration.objects.filter(
            created_by=self.request.user
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

class ProjectApprovalViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectApprovalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ProjectApproval.objects.all()
        return ProjectApproval.objects.filter(requested_by=user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        approval = self.get_object()
        if request.user.is_staff:
            approval.status = 'approved'
            approval.reviewed_by = request.user
            approval.save()
            return Response({'status': 'project approved'})
        return Response({'error': 'unauthorized'}, status=403)

class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']

class CPUViewSet(viewsets.ModelViewSet):
    queryset = CPU.objects.all()
    serializer_class = CPUSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['manufacturer', 'architecture']
    search_fields = ['name', 'model']

class RAMViewSet(viewsets.ModelViewSet):
    queryset = RAM.objects.all()
    serializer_class = RAMSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['manufacturer', 'ram_type']
    search_fields = ['name', 'model']

class StorageViewSet(viewsets.ModelViewSet):
    queryset = Storage.objects.all()
    serializer_class = StorageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['manufacturer', 'storage_type', 'interface']
    search_fields = ['name', 'model']

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Project.objects.all()
        return Project.objects.filter(created_by=user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        project = self.get_object()
        if project.status == 'draft':
            project.status = 'pending'
            project.save()
            return Response({'status': 'submitted for review'})
        return Response(
            {'error': 'Project must be in draft status to submit for review'},
            status=400
        )

class LicensePricingViewSet(viewsets.ModelViewSet):
    queryset = LicensePricing.objects.all()
    serializer_class = LicensePricingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['license_product', 'metric']
    
    def get_queryset(self):
        queryset = LicensePricing.objects.all()
        current_date = timezone.now().date()
        
        # Filter by valid dates if requested
        if self.request.query_params.get('current_only', False):
            queryset = queryset.filter(
                valid_from__lte=current_date
            ).filter(
                Q(valid_to__gte=current_date) | Q(valid_to__isnull=True)
            )
        
        return queryset

class UserActivityViewSet(viewsets.ModelViewSet):
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)

class ProjectActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ProjectActivity.objects.all()
        return ProjectActivity.objects.filter(project__created_by=user)
