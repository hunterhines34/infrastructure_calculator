from django.core.management.base import BaseCommand
from django.utils import timezone
from calculator.models import *
from decimal import Decimal
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Loads sample data for testing the calculator application'

    def handle(self, *args, **kwargs):
        # Clear existing data except Projects
        self.stdout.write('Clearing existing component data...')
        models_to_clear = [
            Manufacturer, CPU, RAM, Storage, GPU, NetworkCard,
            LicenseMetric, LicenseProduct, LicensePricing,
            ServerConfiguration, SavedConfiguration
        ]
        for model in models_to_clear:
            model.objects.all().delete()

        # Create Manufacturers (add NVIDIA)
        self.stdout.write('Creating manufacturers...')
        manufacturers = {
            'intel': Manufacturer.objects.create(
                name='Intel Corporation',
                website='https://www.intel.com',
                contact_email='enterprise@intel.com'
            ),
            'amd': Manufacturer.objects.create(
                name='AMD',
                website='https://www.amd.com',
                contact_email='enterprise@amd.com'
            ),
            'microsoft': Manufacturer.objects.create(
                name='Microsoft',
                website='https://www.microsoft.com',
                contact_email='enterprise@microsoft.com'
            ),
            'redhat': Manufacturer.objects.create(
                name='Red Hat',
                website='https://www.redhat.com',
                contact_email='enterprise@redhat.com'
            ),
            'samsung': Manufacturer.objects.create(
                name='Samsung',
                website='https://www.samsung.com',
                contact_email='enterprise@samsung.com'
            ),
            'mellanox': Manufacturer.objects.create(
                name='NVIDIA Mellanox',
                website='https://www.nvidia.com/networking',
                contact_email='enterprise@nvidia.com'
            ),
            'nvidia': Manufacturer.objects.create(
                name='NVIDIA',
                website='https://www.nvidia.com',
                contact_email='enterprise@nvidia.com'
            )
        }

        # Create CPUs
        self.stdout.write('Creating CPUs...')
        CPU.objects.create(
            name='Intel Xeon Platinum 8380',
            model='8380',
            manufacturer=manufacturers['intel'],
            architecture='x86_64',
            cores=40,
            threads=80,
            clock_speed=2.3,
            power_consumption_watts=270,
            price=Decimal('8099.00')
        )
        
        CPU.objects.create(
            name='AMD EPYC 7763',
            model='7763',
            manufacturer=manufacturers['amd'],
            architecture='x86_64',
            cores=64,
            threads=128,
            clock_speed=2.45,
            power_consumption_watts=280,
            price=Decimal('7890.00')
        )

        # Create RAM
        self.stdout.write('Creating RAM...')
        RAM.objects.create(
            name='Samsung DDR4 ECC Server Memory',
            model='M386A8K40DM2-CWE',
            manufacturer=manufacturers['samsung'],
            capacity_gb=64,
            speed=3200,
            ram_type='ddr4_ecc',
            latency_ns=22,
            price=Decimal('389.99')
        )
        
        RAM.objects.create(
            name='Samsung DDR5 ECC Server Memory',
            model='M386A8K40EM2-CWE',
            manufacturer=manufacturers['samsung'],
            capacity_gb=128,
            speed=4800,
            ram_type='ddr5_ecc',
            latency_ns=20,
            price=Decimal('799.99')
        )

        # Create Storage
        self.stdout.write('Creating storage devices...')
        Storage.objects.create(
            name='Samsung PM1733 Enterprise SSD',
            capacity=3840,
            capacity_unit='gb',
            storage_type='nvme',
            interface='pcie',
            manufacturer=manufacturers['samsung'],
            price_per_gb=Decimal('0.80'),
            model='MZWLJ3T8HBLS-00007',
            form_factor='2.5"',
            price=Decimal('3072.00')
        )
        
        Storage.objects.create(
            name='Samsung PM1643a Enterprise SSD',
            capacity=15360,
            capacity_unit='gb',
            storage_type='ssd',
            interface='sas',
            manufacturer=manufacturers['samsung'],
            price_per_gb=Decimal('0.65'),
            model='MZILT15THMLA-00007',
            form_factor='2.5"',
            price=Decimal('9984.00')
        )

        # Create Network Cards
        self.stdout.write('Creating network cards...')
        NetworkCard.objects.create(
            name='Mellanox ConnectX-6 Dx',
            speed_gbps=100,
            interface='ethernet',
            manufacturer=manufacturers['mellanox'],
            model='MCX623106AN-CDAT',
            port_type='QSFP56',
            price=Decimal('899.99')
        )
        
        NetworkCard.objects.create(
            name='Mellanox ConnectX-7',
            speed_gbps=200,
            interface='ethernet',
            manufacturer=manufacturers['mellanox'],
            model='MCX713106AS-VEAT',
            port_type='QSFP112',
            price=Decimal('1499.99')
        )

        # Create License Metrics
        self.stdout.write('Creating license metrics...')
        metrics = {
            'core': LicenseMetric.objects.create(
                name='Core Pack',
                description='Licensed per physical core'
            ),
            'socket': LicenseMetric.objects.create(
                name='Socket',
                description='Licensed per CPU socket'
            ),
            'user': LicenseMetric.objects.create(
                name='User CAL',
                description='Client Access License per user'
            )
        }

        # Create License Products
        self.stdout.write('Creating license products...')
        windows_server = LicenseProduct.objects.create(
            name='Windows Server',
            manufacturer=manufacturers['microsoft'],
            version='2022',
            edition='datacenter',
            is_core_based=True,
            min_cores_per_processor=8,
            min_cores_per_server=16,
            core_pack_size=2,
            requires_cal=True
        )

        rhel = LicenseProduct.objects.create(
            name='Red Hat Enterprise Linux',
            manufacturer=manufacturers['redhat'],
            version='9',
            edition='enterprise',
            is_socket_based=True,
            requires_cal=False
        )

        sql_server = LicenseProduct.objects.create(
            name='Microsoft SQL Server',
            manufacturer=manufacturers['microsoft'],
            version='2022',
            edition='enterprise',
            is_core_based=True,
            min_cores_per_processor=4,
            min_cores_per_server=8,
            core_pack_size=2,
            requires_cal=True,
            notes='Software Assurance required for production use. Each core pack licenses 2 cores.'
        )

        # Create License Pricing
        self.stdout.write('Creating license pricing...')
        today = date.today()
        LicensePricing.objects.create(
            license_product=windows_server,
            metric=metrics['core'],
            quantity_per_pack=2,
            price=Decimal('1069.00'),
            valid_from=today,
            valid_to=today + timedelta(days=365)
        )

        LicensePricing.objects.create(
            license_product=windows_server,
            metric=metrics['user'],
            quantity_per_pack=1,
            price=Decimal('38.00'),
            valid_from=today,
            valid_to=today + timedelta(days=365)
        )

        LicensePricing.objects.create(
            license_product=rhel,
            metric=metrics['socket'],
            quantity_per_pack=2,
            price=Decimal('799.00'),
            valid_from=today,
            valid_to=today + timedelta(days=365)
        )

        LicensePricing.objects.create(
            license_product=sql_server,
            metric=metrics['core'],
            quantity_per_pack=2,
            price=Decimal('7128.00'),
            valid_from=today,
            valid_to=today + timedelta(days=365)
        )

        LicensePricing.objects.create(
            license_product=sql_server,
            metric=metrics['user'],
            quantity_per_pack=1,
            price=Decimal('209.00'),
            valid_from=today,
            valid_to=today + timedelta(days=365)
        )

        # Add GPUs
        self.stdout.write('Creating GPUs...')
        gpus = [
            GPU.objects.create(
                name='NVIDIA A100',
                memory_gb=80,
                manufacturer=manufacturers['nvidia'],
                model='A100-SXM4-80GB',
                clock_speed=1.41,
                power_consumption_watts=400,
                price=Decimal('10999.00')
            ),
            GPU.objects.create(
                name='NVIDIA A40',
                memory_gb=48,
                manufacturer=manufacturers['nvidia'],
                model='A40-48GB',
                clock_speed=1.37,
                power_consumption_watts=300,
                price=Decimal('5499.00')
            ),
            GPU.objects.create(
                name='NVIDIA L40',
                memory_gb=48,
                manufacturer=manufacturers['nvidia'],
                model='L40-48GB',
                clock_speed=1.62,
                power_consumption_watts=300,
                price=Decimal('6999.00')
            )
        ]

        # Create Sample Saved Configurations
        self.stdout.write('Creating saved configurations...')
        saved_configs = [
            {
                'name': 'High-Performance Database Server',
                'description': 'Optimized for enterprise database workloads',
                'cpu': CPU.objects.first(),
                'ram': RAM.objects.filter(ram_type='ddr5_ecc').first(),
                'storage': Storage.objects.filter(storage_type='nvme').first(),
                'network_card': NetworkCard.objects.order_by('-speed_gbps').first(),
                'os': 'Windows Server 2022 Datacenter'
            },
            {
                'name': 'AI Training Server',
                'description': 'Configured for deep learning workloads',
                'cpu': CPU.objects.last(),
                'ram': RAM.objects.filter(capacity_gb__gte=128).first(),
                'storage': Storage.objects.filter(storage_type='nvme').first(),
                'gpu': GPU.objects.filter(name='NVIDIA A100').first(),
                'network_card': NetworkCard.objects.order_by('-speed_gbps').first(),
                'os': 'Red Hat Enterprise Linux 9'
            },
            {
                'name': 'General Purpose Enterprise Server',
                'description': 'Balanced configuration for mixed workloads',
                'cpu': CPU.objects.first(),
                'ram': RAM.objects.filter(ram_type='ddr4_ecc').first(),
                'storage': Storage.objects.filter(storage_type='ssd').first(),
                'network_card': NetworkCard.objects.order_by('speed_gbps').first(),
                'os': 'Windows Server 2022 Standard'
            }
        ]

        for config in saved_configs:
            SavedConfiguration.objects.create(**config)

        # Create Server Configurations for existing projects
        self.stdout.write('Creating server configurations for existing projects...')
        projects = Project.objects.all()
        
        for project in projects:
            # Create 2-3 configurations per project
            for i in range(random.randint(2, 3)):
                # Randomly select a saved config as template
                template = random.choice(saved_configs)
                
                ServerConfiguration.objects.create(
                    project=project,
                    name=f"{project.name} - Server {i+1}",
                    cpu=template['cpu'],
                    ram=template['ram'],
                    storage=template['storage'],
                    gpu=template.get('gpu'),
                    network_card=template['network_card'],
                    os=template['os'],
                    notes=f"Configuration based on {template['name']} template"
                )

        # Create Sample Projects
        self.stdout.write('Creating sample projects...')
        sample_projects = [
            {
                'name': 'Data Center Expansion Phase 1',
                'description': 'Expanding primary data center with high-performance compute nodes',
                'status': 'draft',
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=180)
            },
            {
                'name': 'ML Research Cluster',
                'description': 'New machine learning research cluster with GPU acceleration',
                'status': 'pending',
                'start_date': date.today() + timedelta(days=30),
                'end_date': date.today() + timedelta(days=210)
            },
            {
                'name': 'Database Server Migration',
                'description': 'Migration of legacy database servers to new hardware',
                'status': 'active',
                'start_date': date.today() - timedelta(days=30),
                'end_date': date.today() + timedelta(days=90)
            },
            {
                'name': 'Web Application Infrastructure',
                'description': 'Completed infrastructure upgrade for web applications',
                'status': 'completed',
                'start_date': date.today() - timedelta(days=180),
                'end_date': date.today() - timedelta(days=30)
            },
            {
                'name': 'Legacy System Replacement',
                'description': 'Cancelled project for replacing legacy systems',
                'status': 'cancelled',
                'start_date': date.today() - timedelta(days=90),
                'end_date': date.today() + timedelta(days=90)
            }
        ]

        # Get the admin user
        admin_user = User.objects.get(username='admin')

        # Create projects and add some activity
        for project_data in sample_projects:
            project = Project.objects.create(
                created_by=admin_user,
                **project_data
            )
            
            # Create project activity
            ProjectActivity.objects.create(
                project=project,
                title='Project Created',
                description=f'Project {project.name} was created',
                created_by=admin_user
            )
            
            if project.status != 'draft':
                ProjectActivity.objects.create(
                    project=project,
                    title='Status Changed',
                    description=f'Project status changed to {project.status}',
                    created_by=admin_user
                )

            # Create approval request for pending projects
            if project.status == 'pending':
                ProjectApproval.objects.create(
                    project=project,
                    requested_by=admin_user,
                    status='pending',
                    comments='Requesting approval for project implementation'
                )

        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data and created configurations')) 