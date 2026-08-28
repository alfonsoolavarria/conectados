from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Cabin, Member, Message

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
