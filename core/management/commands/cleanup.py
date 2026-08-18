import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Cabin, Member

CABANA_RE = re.compile(r"^Cabaña\s+(\d+)")
ACAMPANTE_RE = re.compile(r"^\s*\d+[.)]\s*(.+)$")
INVISIBLES_RE = re.compile(r"[\u200b-\u200f\u2060\u00ad\uFEFF]")
TELEFONO_RE = re.compile(r"(\d[\d\- ]{6,12})\.?\s*(.*)$")

ARCHIVOS = [("chicos.txt", "M"), ("chicas.txt", "F")]


def _limpiar(texto):
    texto = INVISIBLES_RE.sub("", texto)
    return re.sub(r"\s+", " ", texto).strip(" .")


def _esperados():
    esperado = set()
    for nombre_archivo, genero in ARCHIVOS:
        path = settings.BASE_DIR / nombre_archivo
        if not path.exists():
            continue
        cabin_num = None
        for linea in path.read_text().splitlines():
            linea = INVISIBLES_RE.sub("", linea).strip()
            if not linea:
                continue
            m = CABANA_RE.match(linea)
            if m:
                cabin_num = int(m.group(1))
                continue
            if cabin_num is None:
                continue
            mc = ACAMPANTE_RE.match(linea)
            if mc:
                contenido = mc.group(1)
                mp = TELEFONO_RE.search(contenido)
                nombre = _limpiar(contenido[: mp.start(1)]) if mp else _limpiar(contenido)
                esperado.add((cabin_num, nombre, "camper"))
            else:
                for lider in re.split(r",|\s+y\s+", linea):
                    lider = _limpiar(lider)
                    if lider:
                        esperado.add((cabin_num, lider, "leader"))
    return esperado


class Command(BaseCommand):
    help = "Elimina Members que no existen en chicos.txt / chicas.txt"

    def handle(self, *args, **options):
        esperado = _esperados()
        eliminados = 0
        for member in Member.objects.select_related("cabin").all():
            key = (member.cabin.number, member.full_name, member.role)
            if key not in esperado:
                self.stdout.write(
                    f"  Eliminando: {member.full_name} "
                    f"(Cabaña {member.cabin.number}, {member.role})"
                )
                member.delete()
                eliminados += 1
        if eliminados:
            self.stdout.write(
                self.style.SUCCESS(f"Members eliminados: {eliminados}")
            )
        else:
            self.stdout.write("Todos los Members son válidos.")
