from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Cabin,
    CompetitionPhoto,
    DailyCommitment,
    Member,
    Message,
    PhotoComment,
    PhotoReaction,
)

User = get_user_model()


class MensajeriaViewTests(TestCase):
    def setUp(self):
        self.cabin = Cabin.objects.create(
            number=1, gender="M", age_range="12-15", location="Principal"
        )
        self.leader_user = User.objects.create_user(
            username="leader1", password="pass12345"
        )
        self.camper_user = User.objects.create_user(
            username="camper1", password="pass12345"
        )
        self.other_camper_user = User.objects.create_user(
            username="camper2", password="pass12345"
        )
        self.leader = Member.objects.create(
            user=self.leader_user,
            full_name="Líder Uno",
            role="leader",
            cabin=self.cabin,
            gender="M",
        )
        self.camper = Member.objects.create(
            user=self.camper_user,
            full_name="Acampante Uno",
            role="camper",
            cabin=self.cabin,
            gender="M",
        )
        self.other_camper = Member.objects.create(
            user=self.other_camper_user,
            full_name="Acampante Dos",
            role="camper",
            cabin=self.cabin,
            gender="M",
        )

    def test_mensajeria_with_messages_sorts_ok(self):
        Message.objects.create(
            sender=self.camper_user,
            recipient=self.leader_user,
            body="Hola líder",
        )
        Message.objects.create(
            sender=self.other_camper_user,
            recipient=self.leader_user,
            body="Mensaje de otro",
        )
        self.client.force_login(self.leader_user)
        response = self.client.get(reverse("mensajeria"))
        self.assertEqual(response.status_code, 200)
        threads = response.context["threads"]
        # The thread with the most recent message should be first
        self.assertEqual(
            threads[0]["last"].body,
            Message.objects.order_by("-created_at").first().body,
        )

    def test_mensajeria_leader_with_without_messages(self):
        # One contact has a message, another has none (reproduces the
        # naive/aware datetime comparison bug).
        Message.objects.create(
            sender=self.camper_user,
            recipient=self.leader_user,
            body="Hola líder",
        )
        self.client.force_login(self.leader_user)
        response = self.client.get(reverse("mensajeria"))
        self.assertEqual(response.status_code, 200)
        threads = response.context["threads"]
        self.assertEqual(len(threads), 2)
        # The thread with the message sorts first (reverse=True)
        self.assertIsNotNone(threads[0]["last"])
        self.assertIsNone(threads[1]["last"])

    def test_mensajeria_no_contacts(self):
        # A leader with no campers assigned has no threads.
        cabin_vacio = Cabin.objects.create(
            number=99, gender="F", age_range="12-15", location="Otro"
        )
        leader = User.objects.create_user(username="leader2", password="pass12345")
        Member.objects.create(
            user=leader,
            full_name="Líder Solo",
            role="leader",
            cabin=cabin_vacio,
            gender="M",
        )
        self.client.force_login(leader)
        response = self.client.get(reverse("mensajeria"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["threads"], [])

    def test_mensajeria_requires_login(self):
        response = self.client.get(reverse("mensajeria"))
        self.assertEqual(response.status_code, 302)


class HomeViewTests(TestCase):
    def setUp(self):
        self.cabin = Cabin.objects.create(
            number=1, gender="M", age_range="12-15", location="Principal"
        )
        self.camper_user = User.objects.create_user(
            username="camper1", password="pass12345"
        )
        Member.objects.create(
            user=self.camper_user,
            full_name="Acampante Uno",
            role="camper",
            cabin=self.cabin,
            gender="M",
        )

    def test_home_dashboard_renders_for_camper(self):
        self.client.force_login(self.camper_user)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mi Espacio")


def _make_camper(username, cabin_number):
    cabin = Cabin.objects.create(
        number=cabin_number, gender="M", age_range="12-15", location="A"
    )
    user = User.objects.create_user(username=username, password="pass12345")
    Member.objects.create(
        user=user,
        full_name=f"Acampante {username}",
        role="camper",
        cabin=cabin,
        gender="M",
    )
    return user


class CompetenciasViewTests(TestCase):
    def setUp(self):
        self.user = _make_camper("camperx", 1)
        self.user2 = _make_camper("campery", 2)
        self.leader_cabin = Cabin.objects.create(
            number=5, gender="M", age_range="12-15", location="Principal"
        )
        self.leader_user = User.objects.create_user(
            username="liderz", password="pass12345"
        )
        Member.objects.create(
            user=self.leader_user,
            full_name="Líder Z",
            role="leader",
            cabin=self.leader_cabin,
            gender="M",
        )
        self.photo = CompetitionPhoto.objects.create(
            color="blanco", filename="uno.jpg"
        )

    def test_competencias_renders_for_member(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("competencias"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Competencias")

    def test_competencias_redirects_for_non_member(self):
        user = User.objects.create_user(username="nobody", password="pass12345")
        self.client.force_login(user)
        response = self.client.get(reverse("competencias"))
        self.assertEqual(response.status_code, 302)

    def test_react_adds_reaction(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("competencia_react", args=[self.photo.id]),
            {"reaction": "heart"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["counts"]["heart"], 1)
        self.assertTrue(
            PhotoReaction.objects.filter(
                photo=self.photo, user=self.user, reaction="heart"
            ).exists()
        )

    def test_react_adds_fire_reaction(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("competencia_react", args=[self.photo.id]),
            {"reaction": "fire"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["counts"]["fire"], 1)
        self.assertTrue(
            PhotoReaction.objects.filter(
                photo=self.photo,
                user=self.user,
                reaction="fire",
            ).exists()
        )

    def test_react_returns_people(self):
        PhotoReaction.objects.create(
            photo=self.photo, user=self.user2, reaction="like"
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("competencia_react", args=[self.photo.id]),
            {"reaction": "like"},
        )
        data = response.json()
        self.assertEqual(len(data["people"]["like"]), 2)
        self.assertEqual(data["counts"]["like"], 2)

    def test_react_toggles_off_when_same(self):
        PhotoReaction.objects.create(
            photo=self.photo, user=self.user, reaction="like"
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("competencia_react", args=[self.photo.id]),
            {"reaction": "like"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["counts"]["like"], 0)
        self.assertIsNone(response.json()["active"])
        self.assertFalse(
            PhotoReaction.objects.filter(photo=self.photo, user=self.user).exists()
        )

    def test_react_changes_reaction(self):
        PhotoReaction.objects.create(
            photo=self.photo, user=self.user, reaction="like"
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("competencia_react", args=[self.photo.id]),
            {"reaction": "llama"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["counts"]["like"], 0)
        self.assertEqual(response.json()["counts"]["llama"], 1)
        self.assertEqual(response.json()["active"], "llama")

    def test_react_rejects_invalid(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("competencia_react", args=[self.photo.id]),
            {"reaction": "sad"},
        )
        self.assertEqual(response.status_code, 400)

    def test_react_requires_login(self):
        response = self.client.post(
            reverse("competencia_react", args=[self.photo.id]),
            {"reaction": "like"},
        )
        self.assertEqual(response.status_code, 302)

    def test_comment_creates_comment(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("competencia_comment", args=[self.photo.id]),
            {"body": "Hola de prueba"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PhotoComment.objects.count(), 1)
        self.assertEqual(response.json()["body"], "Hola de prueba")

    def test_comment_empty_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("competencia_comment", args=[self.photo.id]),
            {"body": "   "},
        )
        self.assertEqual(response.status_code, 400)

    def test_comment_too_long_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("competencia_comment", args=[self.photo.id]),
            {"body": "x" * 300},
        )
        self.assertEqual(response.status_code, 400)

    def test_comment_allows_200_chars(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("competencia_comment", args=[self.photo.id]),
            {"body": "x" * 200},
        )
        self.assertEqual(response.status_code, 200)

    def test_comment_created_time_is_caracas(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("competencia_comment", args=[self.photo.id]),
            {"body": "Hora local"},
        )
        comment = PhotoComment.objects.get()
        expected = timezone.localtime(comment.created_at).strftime("%d/%m %H:%M")
        self.assertEqual(response.json()["created"], expected)
        utc_naive = comment.created_at.strftime("%d/%m %H:%M")
        self.assertNotEqual(response.json()["created"], utc_naive)

    def test_comment_owner_can_edit(self):
        comment = PhotoComment.objects.create(
            photo=self.photo, user=self.user, body="original"
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("competencia_comment_edit", args=[comment.id]),
            {"body": "editado"},
        )
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.body, "editado")

    def test_comment_camper_cannot_edit_others(self):
        comment = PhotoComment.objects.create(
            photo=self.photo, user=self.user2, body="de otro"
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("competencia_comment_edit", args=[comment.id]),
            {"body": "hack"},
        )
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertEqual(comment.body, "de otro")

    def test_comment_leader_cannot_edit_others(self):
        comment = PhotoComment.objects.create(
            photo=self.photo, user=self.user, body="original"
        )
        self.client.force_login(self.leader_user)
        response = self.client.post(
            reverse("competencia_comment_edit", args=[comment.id]),
            {"body": "editado por líder"},
        )
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertEqual(comment.body, "original")

    def test_comment_superuser_can_edit_others(self):
        comment = PhotoComment.objects.create(
            photo=self.photo, user=self.user, body="original"
        )
        admin = User.objects.create_superuser(
            username="alfonso", password="pass12345"
        )
        self.client.force_login(admin)
        response = self.client.post(
            reverse("competencia_comment_edit", args=[comment.id]),
            {"body": "editado por admin"},
        )
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.body, "editado por admin")

    def test_comment_owner_can_delete(self):
        comment = PhotoComment.objects.create(
            photo=self.photo, user=self.user, body="borrar"
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("competencia_comment_delete", args=[comment.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            PhotoComment.objects.filter(pk=comment.pk).exists()
        )

    def test_comment_camper_cannot_delete_others(self):
        comment = PhotoComment.objects.create(
            photo=self.photo, user=self.user2, body="de otro"
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("competencia_comment_delete", args=[comment.id])
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(PhotoComment.objects.filter(pk=comment.pk).exists())

    def test_comment_leader_can_delete_others(self):
        comment = PhotoComment.objects.create(
            photo=self.photo, user=self.user, body="borrar"
        )
        self.client.force_login(self.leader_user)
        response = self.client.post(
            reverse("competencia_comment_delete", args=[comment.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(PhotoComment.objects.filter(pk=comment.pk).exists())

    def test_comment_edit_requires_login(self):
        comment = PhotoComment.objects.create(
            photo=self.photo, user=self.user, body="x"
        )
        response = self.client.post(
            reverse("competencia_comment_edit", args=[comment.id]),
            {"body": "y"},
        )
        self.assertEqual(response.status_code, 302)

    def test_comment_reply_creates_nested(self):
        parent = PhotoComment.objects.create(
            photo=self.photo, user=self.user, body="padre"
        )
        self.client.force_login(self.user2)
        response = self.client.post(
            reverse("competencia_comment", args=[self.photo.id]),
            {"body": "respuesta", "parent": parent.id},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["parent_id"], parent.id)
        reply = PhotoComment.objects.get(body="respuesta")
        self.assertEqual(reply.parent_id, parent.id)

    def test_comment_cannot_reply_to_reply(self):
        top = PhotoComment.objects.create(
            photo=self.photo, user=self.user, body="top"
        )
        lvl1 = PhotoComment.objects.create(
            photo=self.photo, user=self.user, body="nivel1", parent=top
        )
        self.client.force_login(self.user2)
        response = self.client.post(
            reverse("competencia_comment", args=[self.photo.id]),
            {"body": "no permitido", "parent": lvl1.id},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(PhotoComment.objects.count(), 2)

    def test_comment_parent_must_belong_to_photo(self):
        other = CompetitionPhoto.objects.create(
            color="blanco", filename="otra.jpg"
        )
        parent = PhotoComment.objects.create(
            photo=other, user=self.user, body="de otra foto"
        )
        self.client.force_login(self.user2)
        response = self.client.post(
            reverse("competencia_comment", args=[self.photo.id]),
            {"body": "hack", "parent": parent.id},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(PhotoComment.objects.count(), 1)


class ToggleDayTests(TestCase):
    def setUp(self):
        self.user = _make_camper("campert", 3)

    def test_redirects_back_to_next_page(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("toggle_day"),
            {"day": "2026-08-01", "next": "/mis-desafios/"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/mis-desafios/")
        self.assertTrue(
            DailyCommitment.objects.filter(
                user=self.user, date="2026-08-01", is_completed=True
            ).exists()
        )

    def test_ignores_external_next(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("toggle_day"),
            {"day": "2026-08-01", "next": "https://evil.com"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(response.url, "https://evil.com")

    def test_falls_back_to_home_without_next(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("toggle_day"),
            {"day": "2026-08-01"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))
