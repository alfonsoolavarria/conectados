import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Cabin, Member

CABANA_RE = re.compile(r"^Cabaña\s+(\d+)")
EDAD_RE = re.compile(r"\((.*?)\)")
INVISIBLES_RE = re.compile(r"[\u200b-\u200f\u2060\u00ad\uFEFF]")
TELEFONO_RE = re.compile(r"(\d[\d\- ]{6,12})")

ARCHIVOS = [("chicos.txt", "M"), ("chicas.txt", "F")]


def _limpiar(texto):
    texto = INVISIBLES_RE.sub("", texto)
    texto = re.sub(r"\t+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip(" .")


def _parsear_archivos():
    esperado = {}
    for nombre_archivo, genero in ARCHIVOS:
        path = settings.BASE_DIR / nombre_archivo
        if not path.exists():
            continue
        cabin_num = None
        es_primera_linea = False
        for linea in path.read_text().splitlines():
            linea = INVISIBLES_RE.sub("", linea).strip()
            if not linea:
                continue
            m = CABANA_RE.match(linea)
            if m:
                cabin_num = int(m.group(1))
                am = EDAD_RE.search(linea)
                edad = am.group(1) if am else ""
                ubicacion = _limpiar(linea[am.end():]) if am else ""
                key = (cabin_num, genero)
                if key not in esperado:
                    esperado[key] = {
                        "number": cabin_num,
                        "gender": genero,
                        "age_range": edad,
                        "location": ubicacion,
                        "members": [],
                    }
                else:
                    esperado[key]["age_range"] = edad
                    esperado[key]["location"] = ubicacion
                es_primera_linea = True
                continue
            if cabin_num is None:
                continue

            if es_primera_linea:
                es_primera_linea = False
                for lider in re.split(r",|\s+y\s+", linea):
                    lider = _limpiar(lider)
                    if not lider:
                        continue
                    esperado[(cabin_num, genero)]["members"].append({
                        "full_name": lider,
                        "role": "leader",
                        "phone": "",
                        "gender": genero,
                    })
            else:
                nombre = _limpiar(linea)
                mp = TELEFONO_RE.search(nombre)
                if mp:
                    telefono = mp.group(1)
                    nombre = _limpiar(nombre[:mp.start()])
                else:
                    telefono = ""
                if not nombre or "NO VA" in nombre.upper():
                    continue
                esperado[(cabin_num, genero)]["members"].append({
                    "full_name": nombre,
                    "role": "camper",
                    "phone": telefono,
                    "gender": genero,
                })
    return esperado


class Command(BaseCommand):
    help = (
        "Importa, actualiza y limpia acampantes y líderes desde "
        "chicos.txt y chicas.txt. Siempre se ejecuta."
    )

    def handle(self, *args, **options):
        esperado = _parsear_archivos()

        total_cabins = 0
        creados = 0
        actualizados = 0
        eliminados = 0

        claves_esperadas = set()

        for key, data in esperado.items():
            cabin_num, genero = key
            cabin, created = Cabin.objects.get_or_create(
                number=cabin_num,
                defaults={
                    "gender": genero,
                    "age_range": data["age_range"],
                    "location": data["location"],
                },
            )
            if not created:
                changed = False
                if cabin.age_range != data["age_range"]:
                    cabin.age_range = data["age_range"]
                    changed = True
                if cabin.location != data["location"]:
                    cabin.location = data["location"]
                    changed = True
                if changed:
                    cabin.save(update_fields=["age_range", "location"])
            if created:
                total_cabins += 1

            for mdata in data["members"]:
                claves_esperadas.add((cabin_num, mdata["full_name"], mdata["role"]))
                member, mcreated = Member.objects.get_or_create(
                    cabin=cabin,
                    full_name=mdata["full_name"],
                    role=mdata["role"],
                    defaults={
                        "phone": mdata["phone"],
                        "gender": mdata["gender"],
                        "is_active": True,
                    },
                )
                if mcreated:
                    creados += 1
                else:
                    changed = False
                    if member.phone != mdata["phone"]:
                        member.phone = mdata["phone"]
                        changed = True
                    if not member.is_active:
                        member.is_active = True
                        changed = True
                    if changed:
                        member.save(update_fields=["phone", "is_active"])
                        actualizados += 1

        for member in Member.objects.select_related("cabin").all():
            key = (member.cabin.number, member.full_name, member.role)
            if key not in claves_esperadas:
                self.stdout.write(
                    f"  Eliminando: {member.full_name} "
                    f"(Cabaña {member.cabin.number}, {member.role})"
                )
                member.delete()
                eliminados += 1

        self.stdout.write(self.style.SUCCESS(
            f"Cabañas nuevas: {total_cabins} | "
            f"Members creados: {creados} | "
            f"Members actualizados: {actualizados} | "
            f"Members eliminados: {eliminados}"
        ))
