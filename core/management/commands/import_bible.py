import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import BibleBook, BibleVerse

ARCHIVO = settings.BASE_DIR / "core" / "data" / "biblia_rv1960.json"

ABBREVIATIONS = {
    "Génesis": "Gn", "Éxodo": "Éx", "Levítico": "Lv", "Números": "Nm",
    "Deuteronomio": "Dt", "Josué": "Jos", "Jueces": "Jue", "Rut": "Rt",
    "1 Samuel": "1 S", "2 Samuel": "2 S", "1 Reyes": "1 R", "2 Reyes": "2 R",
    "1 Crónicas": "1 Cr", "2 Crónicas": "2 Cr", "Esdras": "Esd", "Nehemías": "Neh",
    "Ester": "Est", "Job": "Job", "Salmos": "Sal", "Proverbios": "Pr",
    "Eclesiastés": "Ec", "Cantares": "Cnt", "Isaías": "Is", "Jeremías": "Jer",
    "Lamentaciones": "Lm", "Ezequiel": "Ez", "Daniel": "Dn", "Oseas": "Os",
    "Joel": "Jl", "Amós": "Am", "Abdías": "Abd", "Jonás": "Jon",
    "Miqueas": "Miq", "Nahúm": "Nah", "Habacuc": "Hab", "Sofonías": "Sof",
    "Hageo": "Hag", "Zacarías": "Zac", "Malaquías": "Mal",
    "Mateo": "Mt", "Marcos": "Mr", "Lucas": "Lc", "Juan": "Jn",
    "Hechos": "Hch", "Romanos": "Ro", "1 Corintios": "1 Co",
    "2 Corintios": "2 Co", "Gálatas": "Gá", "Efesios": "Ef",
    "Filipenses": "Flp", "Colosenses": "Col", "1 Tesalonicenses": "1 Ts",
    "2 Tesalonicenses": "2 Ts", "1 Timoteo": "1 Ti", "2 Timoteo": "2 Ti",
    "Tito": "Tit", "Filemón": "Flm", "Hebreos": "He", "Santiago": "Stg",
    "1 Pedro": "1 P", "2 Pedro": "2 P", "1 Juan": "1 Jn", "2 Juan": "2 Jn",
    "3 Juan": "3 Jn", "Judas": "Jud", "Apocalipsis": "Ap",
}


class Command(BaseCommand):
    help = (
        "Importa la Biblia Reina-Valera 1960 (RV1960) desde "
        "core/data/biblia_rv1960.json a la base de datos."
    )

    def handle(self, *args, **options):
        if not ARCHIVO.exists():
            self.stderr.write(
                self.style.ERROR(f"No se encontró el archivo: {ARCHIVO}")
            )
            return

        if BibleBook.objects.exists():
            self.stdout.write(
                self.style.WARNING("Ya hay datos en la BD. Borrando...")
            )
            BibleBook.objects.all().delete()

        data = json.loads(ARCHIVO.read_text(encoding="utf-8"))

        libros = {}
        for item in data:
            numero = item["BoookNumber"]
            if numero not in libros:
                libros[numero] = {
                    "name": item["Book"],
                    "testament": "NT" if item["Testament"] == "Nuevo" else "AT",
                    "chapters": set(),
                }
            libros[numero]["chapters"].add(item["Chapter"])

        pk_por_numero = {}
        for numero in sorted(libros.keys()):
            info = libros[numero]
            libro = BibleBook.objects.create(
                number=numero,
                name=info["name"],
                abbreviation=ABBREVIATIONS.get(info["name"], ""),
                testament=info["testament"],
                total_chapters=max(info["chapters"]),
            )
            pk_por_numero[numero] = libro.pk

        versos = []
        for item in data:
            v = BibleVerse(
                book_id=pk_por_numero[item["BoookNumber"]],
                chapter=item["Chapter"],
                verse=item["Verse"],
                text=item["Text"],
            )
            versos.append(v)
        BibleVerse.objects.bulk_create(versos, batch_size=1000)

        self.stdout.write(self.style.SUCCESS(
            f"Importados {len(libros)} libros y {len(versos)} versículos."
        ))
