from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import Cabin, Member

User = get_user_model()

SUPERUSERS = [
    {
        "username": "admin",
        "email": "admin@conectados.com",
        "password": "admin12345",
        "first_name": "Alfonso",
        "last_name": "Olavarria",
    },
]


class Command(BaseCommand):
    help = "Crea superusuarios de administración y los vincula a su Member."

    def handle(self, *args, **options):
        for data in SUPERUSERS:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                },
            )
            if created:
                user.set_password(data["password"])
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Superusuario '{data['username']}' creado."
                    )
                )
            else:
                self.stdout.write(
                    f"Superusuario '{data['username']}' ya existe."
                )

            full_name = f"{data['first_name']} {data['last_name']}"
            member = Member.objects.filter(full_name=full_name).first()

            if member is None:
                cabin = Cabin.objects.first()
                if cabin is None:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  → No hay cabañas. No se pudo crear Member "
                            f"para '{full_name}'."
                        )
                    )
                    continue
                member = Member.objects.create(
                    full_name=full_name,
                    role="leader",
                    cabin=cabin,
                    gender="M",
                    phone="",
                    is_active=True,
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  → Member '{full_name}' creado como líder "
                        f"(Cabaña {cabin.number})."
                    )
                )

            if member.user_id != user.id:
                member.user = user
                member.must_change_password = False
                member.save(update_fields=["user", "must_change_password"])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  → Vinculado al Member '{member.full_name}' "
                        f"({member.get_role_display()}, "
                        f"Cabaña {member.cabin.number})"
                    )
                )
            else:
                self.stdout.write(
                    f"  → Ya vinculado a '{member.full_name}'."
                )
