from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta


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
    must_change_password = models.BooleanField(
        default=True, verbose_name="Debe cambiar contraseña"
    )
    profile_image = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Imagen de perfil",
    )

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


class Challenge(models.Model):
    DURACIONES = [
        (5, "5 días"),
        (10, "10 días"),
        (20, "20 días"),
        (30, "1 mes"),
    ]
    cabin = models.ForeignKey(
        Cabin,
        on_delete=models.CASCADE,
        related_name="challenges",
        verbose_name="Cabaña",
    )
    body = models.TextField(verbose_name="Desafío")
    duration_days = models.PositiveSmallIntegerField(
        choices=DURACIONES,
        default=30,
        verbose_name="Duración (días)",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_challenges",
        verbose_name="Creado por",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Desafío"
        verbose_name_plural = "Desafíos"

    def __str__(self):
        return f"Desafío {self.cabin}: {self.body[:40]}"

    @property
    def is_active(self):
        fin = self.created_at + timedelta(days=self.duration_days)
        return timezone.now() <= fin

    @property
    def fecha_inicio(self):
        return self.created_at.date()

    @property
    def fecha_fin(self):
        return self.created_at.date() + timedelta(days=self.duration_days)

    @property
    def dias_transcurridos(self):
        from datetime import date as today_date
        hoy = today_date.today()
        inicio = self.fecha_inicio
        fin = self.fecha_fin
        if hoy < inicio:
            return 0
        if hoy > fin:
            return self.duration_days
        return (hoy - inicio).days + 1

    @property
    def author_name(self):
        if self.created_by_id is None:
            return "—"
        member = getattr(self.created_by, "member", None)
        if member is not None and member.full_name:
            return member.full_name
        return self.created_by.username or "—"


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
