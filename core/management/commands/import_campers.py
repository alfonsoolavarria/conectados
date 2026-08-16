import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Cabin, Member

CABANA_RE = re.compile(r"^Cabaña\s+(\d+)")
EDAD_RE = re.compile(r"\((.*?)\)")
ACAMPANTE_RE = re.compile(r"^\s*\d+[.)]\s*(.+)$")
TELEFONO_RE = re.compile(r"(\d[\d\- ]{6,12})\.?\s*(.*)$")
INVISIBLES_RE = re.compile(r"[\u200b-\u200f\u2060\u00ad\uFEFF]")

ARCHIVOS = [("chicos.txt", "M"), ("chicas.txt", "F")]


def _limpiar(texto):
    texto = INVISIBLES_RE.sub("", texto)
    return re.sub(r"\s+", " ", texto).strip(" .")


class Command(BaseCommand):
    help = "Importa acampantes y líderes de cabaña desde chicos.txt y chicas.txt"

    def handle(self, *args, **options):
        Member.objects.all().delete()
        Cabin.objects.all().delete()
        total_campers = 0
        total_leaders = 0
        total_cabins = 0
        for nombre_archivo, genero in ARCHIVOS:
            camper, leaders, cabins = self.importar(
                settings.BASE_DIR / nombre_archivo, genero
            )
            total_campers += camper
            total_leaders += leaders
            total_cabins += cabins
            self.stdout.write(
                self.style.SUCCESS(
                    f"{nombre_archivo}: {camper} acampantes, "
                    f"{leaders} líderes, {cabins} cabañas"
                )
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Total: {total_cabins} cabañas, {total_campers} acampantes, "
                f"{total_leaders} líderes"
            )
        )

    def importar(self, path: Path, genero: str):
        cabin = None
        n_campers = 0
        n_leaders = 0
        n_cabins = 0
        for linea in path.read_text().splitlines():
            linea = INVISIBLES_RE.sub("", linea).strip()
            if not linea:
                continue

            m = CABANA_RE.match(linea)
            if m:
                numero = int(m.group(1))
                edad = ""
                ubicacion = ""
                am = EDAD_RE.search(linea)
                if am:
                    edad = am.group(1)
                    ubicacion = _limpiar(linea[am.end() :])
                cabin, _ = Cabin.objects.get_or_create(
                    number=numero,
                    defaults={
                        "gender": genero,
                        "age_range": edad,
                        "location": ubicacion,
                    },
                )
                n_cabins += 1
                continue

            if cabin is None:
                continue

            mc = ACAMPANTE_RE.match(linea)
            if mc:
                contenido = mc.group(1)
                mp = TELEFONO_RE.search(contenido)
                if mp:
                    telefono = mp.group(1)
                    nombre = contenido[: mp.start(1)]
                    resto = mp.group(2)
                else:
                    telefono = ""
                    nombre = contenido
                    resto = ""
                if "NO VA" in resto.upper():
                    continue
                nombre = _limpiar(nombre)
                Member.objects.update_or_create(
                    cabin=cabin,
                    full_name=nombre,
                    defaults={
                        "phone": _limpiar(telefono),
                        "role": "camper",
                        "gender": genero,
                        "is_active": True,
                    },
                )
                n_campers += 1
            else:
                for lider in re.split(r",|\s+y\s+", linea):
                    lider = _limpiar(lider)
                    if not lider:
                        continue
                    Member.objects.update_or_create(
                        cabin=cabin,
                        full_name=lider,
                        defaults={
                            "phone": "",
                            "role": "leader",
                            "gender": genero,
                            "is_active": True,
                        },
                    )
                    n_leaders += 1
        return n_campers, n_leaders, n_cabins
