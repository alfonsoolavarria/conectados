import calendar
import os
from datetime import date, datetime, timedelta

import segno
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import LoginForm
from .models import Cabin, Challenge, DailyCommitment, Message

User = get_user_model()


def _desafio_activo(challenges):
    for ch in challenges:
        if ch.is_active:
            return ch
    return None

MESES_ES = [
    "",
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_initial(self):
        initial = super().get_initial()
        username = self.request.GET.get("username", "").strip()
        if username:
            initial["identifier"] = username
        return initial

    def get_success_url(self):
        return reverse("home")


def _mes_dias(user, ref_date=None, challenge=None):
    hoy = date.today()
    if challenge is not None:
        inicio = challenge.fecha_inicio
        fin = challenge.fecha_fin
        completados = set(
            user.commitments.filter(
                date__gte=inicio,
                date__lte=fin,
                is_completed=True,
            ).values_list("date", flat=True)
        )
        dias = []
        for i in range(challenge.duration_days):
            dia_date = inicio + timedelta(days=i)
            dias.append({
                "number": dia_date.day,
                "date": dia_date,
                "completed": dia_date in completados,
                "is_today": dia_date == hoy,
            })
        return {
            "days": dias,
            "month_name": f"{challenge.duration_days} días",
            "num_days": challenge.duration_days,
        }
    ref_date = ref_date or hoy
    num_dias = calendar.monthrange(ref_date.year, ref_date.month)[1]
    completados = set(
        user.commitments.filter(
            date__year=ref_date.year,
            date__month=ref_date.month,
            is_completed=True,
        ).values_list("date", flat=True)
    )
    dias = [
        {
            "number": dia,
            "date": date(ref_date.year, ref_date.month, dia),
            "completed": date(ref_date.year, ref_date.month, dia) in completados,
            "is_today": date(ref_date.year, ref_date.month, dia) == hoy,
        }
        for dia in range(1, num_dias + 1)
    ]
    return {
        "days": dias,
        "month_name": MESES_ES[ref_date.month],
        "num_days": num_dias,
    }


@login_required
def home(request):
    member = getattr(request.user, "member", None)
    if member is not None and member.role == "leader":
        return _dashboard_lideres(request)
    active_challenge = (
        _desafio_activo(member.cabin.challenges.all())
        if member is not None
        else None
    )
    context = _mes_dias(request.user, challenge=active_challenge)
    context["completed_count"] = request.user.commitments.filter(
        is_completed=True
    ).count()
    context["challenge"] = active_challenge
    return render(request, "home.html", context)


def _dashboard_lideres(request):
    member = request.user.member
    hoy = date.today()
    cabanas_data = []
    for cab in Cabin.objects.prefetch_related("members").all():
        active_ch = _desafio_activo(cab.challenges.all())
        if active_ch is not None:
            challenge_start = active_ch.fecha_inicio
            challenge_end = active_ch.fecha_fin
            total_days = active_ch.duration_days
            completados_por_user = {
                user_id: total
                for user_id, total in DailyCommitment.objects.filter(
                    date__gte=challenge_start,
                    date__lte=challenge_end,
                    is_completed=True,
                ).values_list("user_id").annotate(total=Count("id"))
            }
        else:
            total_days = calendar.monthrange(hoy.year, hoy.month)[1]
            completados_por_user = {
                user_id: total
                for user_id, total in DailyCommitment.objects.filter(
                    date__year=hoy.year, date__month=hoy.month, is_completed=True
                ).values_list("user_id").annotate(total=Count("id"))
            }
        miembros_con_progreso = []
        for m in cab.members.filter(is_active=True).select_related("user"):
            miembros_con_progreso.append(
                {
                    "member": m,
                    "completed": completados_por_user.get(m.user_id, 0),
                    "total": total_days,
                    "is_leader": m.role == "leader",
                }
            )
        cabanas_data.append(
            {
                "cabin": cab,
                "leaders": cab.members.filter(role="leader"),
                "campers": miembros_con_progreso,
                "num_days": total_days,
                "challenge": active_ch,
                "es_mia": member.cabin_id == cab.pk,
            }
        )
    cabinas_masc = [c for c in cabanas_data if c["cabin"].gender == "M"]
    cabinas_fem = [c for c in cabanas_data if c["cabin"].gender == "F"]
    my_challenge = _desafio_activo(member.cabin.challenges.all())
    my_days = _mes_dias(request.user, challenge=my_challenge)
    return render(
        request,
        "lideres.html",
        {
            "cabins": cabanas_data,
            "cabinas_masc": cabinas_masc,
            "cabinas_fem": cabinas_fem,
            "month_name": MESES_ES[hoy.month],
            "total_campers": sum(
                1
                for c in cabanas_data
                for m in c["campers"]
                if not m["is_leader"]
            ),
            "total_leaders": sum(len(c["leaders"]) for c in cabanas_data),
            "num_days": my_challenge.duration_days if my_challenge else calendar.monthrange(hoy.year, hoy.month)[1],
            "my_days": my_days,
        },
    )


@require_POST
@login_required
def toggle_day(request):
    try:
        day_date = date.fromisoformat(request.POST.get("day", ""))
    except ValueError:
        return HttpResponseRedirect(reverse("home"))
    compromiso, _ = DailyCommitment.objects.get_or_create(
        user=request.user, date=day_date
    )
    compromiso.is_completed = not compromiso.is_completed
    compromiso.save()
    return HttpResponseRedirect(reverse("home"))


@login_required
def estadisticas(request):
    user = request.user
    hoy = date.today()
    contexto = _mes_dias(user)

    completados_mes = user.commitments.filter(
        date__year=hoy.year, date__month=hoy.month, is_completed=True
    ).count()
    pendientes = contexto["num_days"] - completados_mes
    porcentaje = (
        round(completados_mes / contexto["num_days"] * 100)
        if contexto["num_days"]
        else 0
    )

    racha = 0
    cursor = (
        hoy
        if user.commitments.filter(date=hoy, is_completed=True).exists()
        else hoy - timedelta(days=1)
    )
    while user.commitments.filter(date=cursor, is_completed=True).exists():
        racha += 1
        cursor -= timedelta(days=1)

    contexto.update(
        {
            "completed_month": completados_mes,
            "pending": pendientes,
            "percent": porcentaje,
            "streak": racha,
            "total_completed": user.commitments.filter(is_completed=True).count(),
        }
    )
    return render(request, "estadisticas.html", contexto)


def _puede_chatear(member, contact):
    contact_member = getattr(contact, "member", None)
    if contact_member is None or contact_member.cabin_id != member.cabin_id:
        return False
    if member.role == "leader":
        return contact_member.role == "camper"
    if member.role == "camper":
        return contact_member.role == "leader"
    return False


@login_required
def mensajeria(request):
    member = getattr(request.user, "member", None)
    threads = []
    if member is not None:
        if member.role == "leader":
            contactos = member.cabin.members.filter(
                role="camper", is_active=True
            ).exclude(user__isnull=True).select_related("user")
        else:
            contactos = member.cabin.members.filter(
                role="leader"
            ).exclude(user__isnull=True).select_related("user")
        for c in contactos:
            ultimo = (
                Message.objects.filter(
                    Q(sender=request.user, recipient=c.user)
                    | Q(sender=c.user, recipient=request.user)
                )
                .order_by("-created_at")
                .first()
            )
            no_leidos = Message.objects.filter(
                sender=c.user, recipient=request.user, is_read=False
            ).count()
            threads.append(
                {
                    "contact": c,
                    "last": ultimo,
                    "unread": no_leidos,
                }
            )
        threads.sort(
            key=lambda t: t["last"].created_at if t["last"] else datetime.min,
            reverse=True,
        )
    return render(
        request,
        "mensajeria.html",
        {
            "threads": threads,
            "total_unread": sum(t["unread"] for t in threads),
        },
    )


@login_required
def conversacion(request, user_id):
    contact = get_object_or_404(User, pk=user_id)
    member = getattr(request.user, "member", None)
    if member is None or not _puede_chatear(member, contact):
        return HttpResponseRedirect(reverse("mensajeria"))

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        if body:
            Message.objects.create(
                sender=request.user, recipient=contact, body=body
            )
        return HttpResponseRedirect(
            reverse("conversacion", args=[contact.pk])
        )

    Message.objects.filter(
        sender=contact, recipient=request.user, is_read=False
    ).update(is_read=True)
    mensajes = Message.objects.filter(
        Q(sender=request.user, recipient=contact)
        | Q(sender=contact, recipient=request.user)
    ).order_by("created_at")
    return render(
        request,
        "conversacion.html",
        {
            "contact": contact,
            "contact_member": getattr(contact, "member", None),
            "messages": mensajes,
        },
    )


@login_required
def challenge(request, cabin_id):
    member = getattr(request.user, "member", None)
    cab = get_object_or_404(Cabin, pk=cabin_id)
    if member is None or member.role != "leader" or member.cabin_id != cab.pk:
        return HttpResponseRedirect(reverse("home"))

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        duration = int(request.POST.get("duration_days", 30))
        if body:
            active_old = _desafio_activo(cab.challenges.all())
            if active_old is not None:
                from django.utils import timezone as tz
                from datetime import timedelta
                active_old.created_at = tz.now() - timedelta(days=active_old.duration_days + 1)
                active_old.save(update_fields=["created_at"])
            Challenge.objects.create(
                cabin=cab, body=body, created_by=request.user,
                duration_days=duration,
            )
        return HttpResponseRedirect(reverse("home"))

    active = _desafio_activo(cab.challenges.all())
    challenges = cab.challenges.all()
    return render(
        request,
        "challenge.html",
        {
            "cab": cab,
            "current": active,
            "challenges": challenges,
        },
    )


@login_required
def qr_lideres(request):
    member = getattr(request.user, "member", None)
    if member is None or member.role != "leader":
        return HttpResponseRedirect(reverse("home"))
    site_url = os.getenv("SITE_URL", request.build_absolute_uri("/")).rstrip("/")
    cabinas = []
    for cab in Cabin.objects.prefetch_related("members").all():
        lideres = []
        for m in cab.members.filter(role="leader", is_active=True).exclude(
            user__isnull=True
        ).select_related("user"):
            url = f"{site_url}/login/?username={m.user.username}"
            qr = segno.make(url, error="m")
            lideres.append(
                {
                    "member": m,
                    "username": m.user.username,
                    "qr": qr.svg_data_uri(scale=4, border=1),
                    "url": url,
                }
            )
        acampantes = []
        for m in cab.members.filter(role="camper", is_active=True).exclude(
            user__isnull=True
        ).select_related("user"):
            url = f"{site_url}/login/?username={m.user.username}"
            qr = segno.make(url, error="m")
            acampantes.append(
                {
                    "member": m,
                    "username": m.user.username,
                    "qr": qr.svg_data_uri(scale=4, border=1),
                    "url": url,
                }
            )
        if lideres or acampantes:
            cabinas.append({
                "cabin": cab,
                "leaders": lideres,
                "campers": acampantes,
            })
    return render(request, "qr_print.html", {"cabinas": cabinas})


@login_required
def cambiar_contrasena(request):
    member = getattr(request.user, "member", None)
    if request.method == "POST":
        nueva = request.POST.get("new_password", "").strip()
        if nueva:
            request.user.set_password(nueva)
            request.user.save()
            from django.contrib.auth import login as auth_login
            auth_login(request, request.user, backend="core.backends.UsernameOrEmailBackend")
        if member is not None:
            member.must_change_password = False
            member.save(update_fields=["must_change_password"])
        messages.success(request, "Contraseña actualizada." if nueva else "Continuaste sin cambiar.")
        return HttpResponseRedirect(reverse("home"))
    return render(request, "cambiar_contrasena.html")


@login_required
def perfil_imagen(request):
    member = getattr(request.user, "member", None)
    if member is None:
        return HttpResponseRedirect(reverse("home"))

    perfiles_dir = settings.BASE_DIR / "perfiles"
    imagenes = sorted(
        f.name for f in perfiles_dir.iterdir()
        if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
    )

    if request.method == "POST":
        seleccion = request.POST.get("imagen", "").strip()
        if seleccion in imagenes:
            member.profile_image = seleccion
            member.save(update_fields=["profile_image"])
            messages.success(request, "Imagen de perfil actualizada.")
            return HttpResponseRedirect(reverse("home"))

    return render(
        request,
        "perfil_imagen.html",
        {"imagenes": imagenes, "actual": member.profile_image},
    )
