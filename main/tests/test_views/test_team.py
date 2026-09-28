from django.test import TestCase
from django.urls import reverse

from main.models.team import TeamMember


class TestTeamView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("main:team")
        cls.founder = TeamMember.objects.create(
            full_name="Общественный фонд «Эргэнэ»",
            category=TeamMember.Category.FOUNDER,
            order=1,
        )
        cls.ambassador = TeamMember.objects.create(
            full_name="Кудайбергенова Индира Орозбаевна",
            position="Профессор, ректор КГМА",
            category=TeamMember.Category.AMBASSADOR,
            order=1,
        )
        cls.board_second = TeamMember.objects.create(
            full_name="Тургунбаев Эдильбек Шарипбекович",
            position="Сопредседатель Ассоциации",
            category=TeamMember.Category.BOARD,
            order=2,
        )
        cls.board_first = TeamMember.objects.create(
            full_name="Тургуналиева Милана Айбековна",
            position="Сопредседатель Ассоциации",
            bio="Кандидат фармацевтических наук.",
            category=TeamMember.Category.BOARD,
            order=1,
        )
        cls.team_member = TeamMember.objects.create(
            full_name="Каракчиева Назико Мажитовна",
            position="Врач-онколог",
            category=TeamMember.Category.TEAM,
            order=1,
        )

    def test_page_opens_and_uses_expected_template(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/team.html")

    def test_shows_people_with_positions_and_bio(self):
        response = self.client.get(self.url)

        self.assertContains(response, "Кудайбергенова Индира Орозбаевна")
        self.assertContains(response, "Профессор, ректор КГМА")
        self.assertContains(response, "Кандидат фармацевтических наук.")
        self.assertContains(response, "Общественный фонд «Эргэнэ»")

    def test_groups_follow_client_order(self):
        response = self.client.get(self.url)
        content = response.content.decode()

        positions = [
            content.index("Учредители"),
            content.index("Посол Доброй воли"),
            content.index("Управляющий совет"),
            content.index("Команда Ассоциации"),
        ]
        self.assertEqual(positions, sorted(positions))

    def test_members_ordered_by_order_field_inside_group(self):
        response = self.client.get(self.url)
        content = response.content.decode()

        self.assertLess(
            content.index("Тургуналиева Милана Айбековна"),
            content.index("Тургунбаев Эдильбек Шарипбекович"),
        )

    def test_empty_group_heading_is_hidden(self):
        TeamMember.objects.filter(category=TeamMember.Category.TEAM).delete()

        response = self.client.get(self.url)

        self.assertNotContains(response, "Команда Ассоциации")

    def test_member_without_photo_gets_placeholder(self):
        response = self.client.get(self.url)

        self.assertContains(response, "<svg", count=4)

    def test_nav_contains_team_link(self):
        response = self.client.get(reverse("main:home"))

        self.assertContains(response, f'href="{self.url}"')

    def test_headings_go_through_translation(self):
        """Заголовки групп не должны утекать по-русски при другом языке."""
        response = self.client.get(self.url, headers={"accept-language": "en"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Governing Board")
        self.assertNotContains(response, "Управляющий совет")
