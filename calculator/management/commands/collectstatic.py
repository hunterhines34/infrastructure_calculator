from django.core.management.commands import collectstatic
from django.conf import settings
import os

class Command(collectstatic.Command):
    def handle(self, *args, **options):
        print("Collecting static files...")
        for root, _, files in os.walk(settings.STATICFILES_DIRS[0]):
            for file in files:
                print(f"Found file: {os.path.join(root, file)}")
        super().handle(*args, **options)