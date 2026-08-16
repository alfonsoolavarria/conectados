from django.conf import settings
from django.db import models


class DailyCommitment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="commitments",
        verbose_name="Acampante",
    )
    date = models.DateField(verbose_name="Fecha")
    is_completed = models.BooleanField(
        default=False, verbose_name="Completado"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "date"], name="unique_user_date"
            ),
        ]
        ordering = ["date"]
        verbose_name = "Compromiso diario"
        verbose_name_plural = "Compromisos diarios"

    def __str__(self):
        estado = "hecho" if self.is_completed else "pendiente"
        return f"{self.user} - {self.date} ({estado})"


class Cabin(models.Model):
    GENEROS = [
        ("M", "Masculino"),
        ("F", "Femenino"),
    ]

    number = models.PositiveSmallIntegerField(
        unique=True, verbose_name="Número de cabaña"
    )
    gender = models.CharField(
        max_length=1, choices=GENEROS, verbose_name="Género"
    )
    age_range = models.CharField(
        max_length=60, blank=True, verbose_name="Rango de edad"
    )
    location = models.CharField(
        max_length=200, blank=True, verbose_name="Ubicación"
    )

    class Meta:
        ordering = ["number"]
        verbose_name = "Cabaña"
        verbose_name_plural = "Cabañas"

    def __str__(self):
        return f"Cabaña {self.number}"

    def get_gender_display_es(self):
        return "Chicos" if self.gender == "M" else "Mujeres"


class Member(models.Model):
    ROLES = [
        ("camper", "Acampante"),
        ("leader", "Líder de cabaña"),
    ]
    GENEROS = Cabin.GENEROS

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="member",
        verbose_name="Usuario",
    )
    full_name = models.CharField(
        max_length=150, verbose_name="Nombre completo"
    )
    phone = models.CharField(
        max_length=30, blank=True, verbose_name="Teléfono"
    )
    role = models.CharField(
        max_length=10,
        choices=ROLES,
        default="camper",
        verbose_name="Rol",
    )
    cabin = models.ForeignKey(
        Cabin,
        on_delete=models.PROTECT,
        related_name="members",
        verbose_name="Cabaña",
    )
    gender = models.CharField(
        max_length=1, choices=GENEROS, verbose_name="Género"
    )
    is_active = models.BooleanField(default=True, verbose_name="Asiste")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cabin", "full_name", "role"],
                name="unique_cabin_name_role",
            ),
        ]
        ordering = ["cabin", "role", "full_name"]
        verbose_name = "Acampante/Líder"
        verbose_name_plural = "Acampantes y Líderes"

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()} - {self.cabin})"


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name="Remitente",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages",
        verbose_name="Destinatario",
    )
    body = models.TextField(verbose_name="Mensaje")
    is_read = models.BooleanField(default=False, verbose_name="Leído")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Enviado")

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"

    def __str__(self):
        return f"{self.sender} → {self.recipient}: {self.body[:30]}"
