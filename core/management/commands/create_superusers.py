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
        "member_name": "Alfonso",
        "member_cabin": 6,
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

            cabin = Cabin.objects.filter(number=data["member_cabin"]).first()
            if cabin is None:
                self.stdout.write(
                    self.style.WARNING(
                        f"  → Cabaña {data['member_cabin']} no encontrada."
                    )
                )
                continue

            member = Member.objects.filter(
                full_name=data["member_name"],
                cabin=cabin,
                role="leader",
            ).first()

            if member is None:
                self.stdout.write(
                    self.style.WARNING(
                        f"  → Member '{data['member_name']}' no encontrado "
                        f"en Cabaña {data['member_cabin']}."
                    )
                )
                continue

            if member.user_id != user.id:
                Member.objects.filter(user=user).update(user=None)
                member.user = user
                member.must_change_password = False
                member.save(update_fields=["user", "must_change_password"])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  → Vinculado a '{member.full_name}' "
                        f"({member.get_role_display()}, "
                        f"Cabaña {member.cabin.number})"
                    )
                )
            else:
                self.stdout.write(
                    f"  → Ya vinculado a '{member.full_name}'."
                )
