import unicodedata
from collections import Counter

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import Member

User = get_user_model()

PASSWORD = "campo12345"


def _normalizar(nombre):
    nombre = unicodedata.normalize("NFKD", nombre)
    nombre = "".join(c for c in nombre if not unicodedata.combining(c))
    return nombre.strip()


def _username_para(full_name, usados):
    tokens = [
        t.lower()
        for t in _normalizar(full_name).split()
        if t
    ]
    if not tokens:
        tokens = ["usuario"]
    base = ".".join(tokens)
    base = base.replace("ñ", "n").replace("á", "a").replace("é", "e").replace(
        "í", "i"
    ).replace("ó", "o").replace("ú", "u")
    username = base
    n = 2
    while username in usados:
        username = f"{base}{n}"
        n += 1
    usados.add(username)
    return username


class Command(BaseCommand):
    help = (
        "Crea una cuenta de usuario para cada acampante/líder que aún no "
        "tenga una, usando su nombre completo como nombre de usuario."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default=PASSWORD,
            help=f"Contraseña por defecto para las nuevas cuentas (default: {PASSWORD})",
        )

    def handle(self, *args, **options):
        password = options["password"]
        usados = set(
            User.objects.values_list("username", flat=True)
        )
        creadas = 0
        ya_tenian = 0
        errores = 0
        for member in Member.objects.filter(user__isnull=True).order_by("cabin"):
            try:
                username = _username_para(member.full_name, usados)
                partes = _normalizar(member.full_name).split()
                first_name = partes[0]
                last_name = " ".join(partes[1:])
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                member.user = user
                member.save(update_fields=["user"])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{member.full_name} ({member.get_role_display()}, "
                        f"Cabaña {member.cabin.number}) -> {username}"
                    )
                )
                creadas += 1
            except Exception as e:  # noqa: BLE001
                self.stderr.write(
                    self.style.ERROR(
                        f"No se pudo crear cuenta para {member.full_name}: {e}"
                    )
                )
                errores += 1
        ya_tenian = Member.objects.exclude(user__isnull=True).count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Cuentas creadas: {creadas} | Ya tenían cuenta: {ya_tenian} | "
                f"Errores: {errores} | Contraseña: {password}"
            )
        )
