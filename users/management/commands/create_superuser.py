import os
from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):

    help = "This command creates superuser"

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME", None)
        admin = User.objects.get_or_none(username=username)
        if not admin:
            User.objects.create_superuser(
                username, os.environ.get("ADMIN_EMAIL"), os.environ.get("ADMIN_SECRET")
            )
            self.stdout.write(self.style.SUCCESS("Superuser created!"))
        else:
            self.stdout.write(self.style.SUCCESS("Superuser already exists"))
