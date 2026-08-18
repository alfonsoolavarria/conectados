from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import Cabin, Member

User = get_user_model()

ARCHIVO = Path(__file__).resolve().parent.parent.parent.parent / "usuarios.txt"


class Command(BaseCommand):
    help = "Exporta usuarios y contraseñas por cabaña a usuarios.txt"

    def handle(self, *args, **options):
        lineas = []
        lineas.append("=" * 60)
        lineas.append("  CONECTADOS - Usuarios y contraseñas")
        lineas.append("=" * 60)
        lineas.append("")

        superusers = User.objects.filter(is_superuser=True).order_by("username")
        if superusers.exists():
            lineas.append("--- SUPERUSUARIOS (Administración) ---")
            lineas.append("")
            for u in superusers:
                member = getattr(u, "member", None)
                rol = f" ({member.get_role_display()}, {member.cabin})" if member else ""
                lineas.append(f"  Usuario:  {u.username}")
                lineas.append(f"  Nombre:   {u.get_full_name() or u.username}")
                lineas.append(f"  Contraseña: admin12345")
                lineas.append(f"  Rol:      Superusuario{rol}")
                lineas.append("")
            lineas.append("")

        for cabin in Cabin.objects.order_by("number"):
            members = cabin.members.select_related("user").order_by(
                "role", "full_name"
            )
            if not members:
                continue
            lineas.append(
                f"--- {cabin} ({cabin.get_gender_display_es()}) "
                f"---"
            )
            lineas.append("")
            for m in members:
                username = m.user.username if m.user else "(sin cuenta)"
                lineas.append(
                    f"  {m.full_name:<25} "
                    f"{m.get_role_display():<18} "
                    f"{username:<25} campo12345"
                )
            lineas.append("")

        lineas.append("=" * 60)
        lineas.append("  Contraseña por defecto acampantes/líderes: campo12345")
        lineas.append("  Contraseña superusuario: admin12345")
        lineas.append("=" * 60)

        ARCHIVO.write_text("\n".join(lineas) + "\n", encoding="utf-8")
        self.stdout.write(
            self.style.SUCCESS(f"Archivo generado: {ARCHIVO}")
        )
