from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        admin = User.objects.filter(username="arischow").first()

        if admin:
            self.stdout.write("Overlord arischow existed.")
        else:
            User.objects.create_superuser(
                username="arischow", email="arischow@gmail.com", password="cnspurs8633"
            )
            self.stdout.write("Admin created.")
