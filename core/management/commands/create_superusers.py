from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

SUPERUSERS = [
    {
        "username": "admin",
        "email": "admin@conectados.com",
        "password": "admin12345",
        "first_name": "Samuel",
        "last_name": "Gil",
    },
]


class Command(BaseCommand):
    help = "Crea superusuarios de administración si no existen."

    def handle(self, *args, **options):
        for data in SUPERUSERS:
            if not User.objects.filter(username=data["username"]).exists():
                User.objects.create_superuser(
                    username=data["username"],
                    email=data["email"],
                    password=data["password"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Superusuario '{data['username']}' creado.")
                )
            else:
                self.stdout.write(
                    f"Superusuario '{data['username']}' ya existe, se omite."
                )
