import html
import re
import tempfile
from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from news.models import Category, Post
from news.tests.factories import make_image


class PostListViewTest(TestCase):
    PERIOD = {"date_from": "2026-08-21", "date_to": "2026-08-23"}

    def setUp(self):
        self.url = reverse("news:post_list")
        self.category = Category.objects.create(name="sport")
        self.post = Post.objects.create(
            title="тест",
            slug="post",
            content="test_content",
            description="test_description",
            category=self.category,
            created_at="2026-08-22 14:30:00",
        )
        self.post.created_at = "2026-08-22 14:30:00"
        self.post.save()
        self.post2 = Post.objects.create(
            title="test2",
            slug="post2",
            content="test_content2",
            description="test_description2",
            category=self.category,
        )

    # ---------- помощники ----------

    def _set_category_count(self, total):
        for i in range(Category.objects.count(), total):
            Category.objects.create(name=f"cat{i}")
        self.assertEqual(Category.objects.count(), total)

    def _get_in_russian(self, params=None):
        self.addCleanup(translation.activate, "ru")
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = "ru"
        return self.client.get(self.url, params)

    def _make_posts(self, count, category, created="2026-08-22 14:30:00"):
        for i in range(count):
            post = Post.objects.create(
                title=f"p{category.id}-{i}", slug=f"p{category.id}-{i}",
                content="c", description="d", category=category,
            )
            Post.objects.filter(pk=post.pk).update(created_at=created)

    def _params(self, href):
        # &amp; в HTML -> &, иначе parse_qs неверно разберёт параметры
        return parse_qs(urlparse(html.unescape(href)).query)

    def _hrefs(self, response):
        return re.findall(r'href="([^"]*)"', response.content.decode("utf-8"))

    def _chip_href(self, response, text):
        match = re.search(
            rf'<a href="([^"]*)"[^>]*>\s*{text}\s*</a>',
            response.content.decode("utf-8"),
        )
        self.assertIsNotNone(match, f"Нет ссылки «{text}»")
        return match.group(1)

    def _filtered_page_two(self):
        self._make_posts(10, self.category)
        return self._get_in_russian(
            {"category_id": self.category.id, **self.PERIOD, "page": 2}
        )

    # ---------- существующие тесты ----------

    def test_post_filter_date(self):
        response = self.client.get(self.url, self.PERIOD)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_post_empty(self):
        self.post.delete()
        self.post2.delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["posts"]), [])

    def test_title_en_empty_falls_back_to_ru(self):
        self.addCleanup(translation.activate, "ru")

        self.client.cookies["django_language"] = "en"
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test")

    def test_post_without_image_renders_placeholder(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "main/images/news-placeholder.jpg")

    def test_post_with_image_does_not_render_placeholder(self):
        with (
            tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as media_root,
            override_settings(MEDIA_ROOT=media_root),
        ):
            Post.objects.all().delete()
            post = Post.objects.create(
                title="С картинкой", slug="s-kartinkoy", content="content",
                description="description", category=self.category, image=make_image(),
            )
            response = self.client.get(self.url)
            self.assertContains(response, post.image.url)
            self.assertNotContains(response, "main/images/news-placeholder.jpg")

    # ---------- фильтры и пагинация ----------

    def test_filter_by_category_returns_only_its_posts(self):
        other = Category.objects.create(name="other")
        Post.objects.create(
            title="other-post", slug="other-post", content="c",
            description="d", category=other,
        )
        response = self.client.get(self.url, {"category_id": self.category.id})
        self.assertEqual(response.status_code, 200)
        posts = list(response.context["posts"])
        self.assertTrue(posts)
        self.assertEqual({p.category_id for p in posts}, {self.category.id})
        self.assertNotContains(response, "other-post")

    def test_pagination_links_keep_filters_on_page_two(self):
        response = self._filtered_page_two()
        self.assertEqual(response.status_code, 200)
        page_links = [h for h in self._hrefs(response) if "page" in self._params(h)]
        self.assertTrue(page_links, "Ссылки пагинации не найдены")
        for href in page_links:
            q = self._params(href)
            self.assertEqual(q["category_id"], [str(self.category.id)], href)
            self.assertEqual(q["date_from"], [self.PERIOD["date_from"]], href)
            self.assertEqual(q["date_to"], [self.PERIOD["date_to"]], href)

    def test_other_category_chip_keeps_period_and_resets_page(self):
        other = Category.objects.create(name="other")
        response = self._filtered_page_two()
        q = self._params(self._chip_href(response, "other"))
        self.assertEqual(q["category_id"], [str(other.id)])
        self.assertEqual(q["date_from"], [self.PERIOD["date_from"]])
        self.assertEqual(q["date_to"], [self.PERIOD["date_to"]])
        self.assertNotIn("page", q)

    def test_all_chip_drops_category_and_keeps_period(self):
        response = self._filtered_page_two()
        q = self._params(self._chip_href(response, "Все"))
        self.assertNotIn("category_id", q)
        self.assertNotIn("page", q)
        self.assertEqual(q["date_from"], [self.PERIOD["date_from"]])
        self.assertEqual(q["date_to"], [self.PERIOD["date_to"]])

    # ---------- категории и «Ещё» ----------

    def test_up_to_seven_categories_have_no_more_button(self):
        self._set_category_count(7)
        response = self._get_in_russian()
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Ещё")

    def test_eight_categories_show_more_button(self):
        self._set_category_count(8)
        response = self._get_in_russian()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ещё 3")

    def test_more_categories_has_three_items_for_eight(self):
        self._set_category_count(8)
        response = self._get_in_russian()
        self.assertEqual(len(response.context["more_categories"]), 3)

    def test_more_categories_is_empty_for_five(self):
        self._set_category_count(5)
        response = self._get_in_russian()
        self.assertEqual(response.context["more_categories"], [])

    def test_active_hidden_category_moves_to_visible(self):
        self._set_category_count(8)
        hidden = self._get_in_russian().context["more_categories"][-1]
        response = self._get_in_russian({"category_id": hidden.id})
        self.assertIn(hidden, response.context["visible_categories"])
        self.assertNotIn(hidden, response.context["more_categories"])
        self.assertEqual(len(response.context["visible_categories"]), 5)


class PaginationPartialTest(TestCase):
    """Общий partial: Events и Resources используют тот же шаблон,
    поэтому проверяем его отдельно, без привязки к новостям.
    TestCase, а не SimpleTestCase: рендер с request запускает контекст-процессоры,
    а site_contacts обращается к БД."""

    def _render(self, get_params, **extra):
        request = RequestFactory().get("/", get_params)
        page_obj = Paginator(range(30), 5).page(3)  # 6 страниц, текущая 3
        return render_to_string(
            "partial/pagination.html", {"page_obj": page_obj, **extra},
            request=request,
        )

    def _hrefs(self, out):
        return re.findall(r'href="([^"]*)"', out)

    def test_links_keep_get_params_and_cover_all_pages(self):
        out = self._render(
            {"category_id": 3, "date_from": "2026-08-01", "page": 3}
        )
        pages = []
        for href in self._hrefs(out):
            q = parse_qs(urlparse(html.unescape(href)).query)
            self.assertEqual(q["category_id"], ["3"], href)
            self.assertEqual(q["date_from"], ["2026-08-01"], href)
            pages.append(int(q["page"][0]))
        self.assertEqual(sorted(pages), [1, 2, 4, 6])  # начало, назад, вперёд, конец

    def test_page_number_form_keeps_filters(self):
        out = self._render({"category_id": 3, "date_from": "2026-08-01"})
        self.assertIn('<input type="hidden" name="category_id" value="3">', out)
        self.assertIn('<input type="hidden" name="date_from" value="2026-08-01">', out)

    def test_explicit_query_keeps_old_behaviour(self):
        out = self._render({"category_id": 9}, query="a=1")
        hrefs = self._hrefs(out)
        self.assertIn("?page=4&a=1", hrefs)
        self.assertTrue(all("category_id" not in h for h in hrefs))

    class PostListInvalidParamsTest(TestCase):

        INVALID_CATEGORY_IDS = ["abc", "-1", "", "1.5", "<script>", "²"]
        INVALID_DATES = ["zzz", "2026-02-31", "31.12.2026"]

        def setUp(self):
            self.url = reverse("news:post_list")
            self.category = Category.objects.create(name="sport")
            self.old_post = self._make_post("old", "2025-01-10 12:00:00")
            self.new_post = self._make_post("new", "2026-06-10 12:00:00")

        def _make_post(self, slug, created):
            post = Post.objects.create(
                title=slug, slug=slug, content="c", description="d",
                category=self.category,
            )
            Post.objects.filter(pk=post.pk).update(created_at=created)
            post.refresh_from_db()
            return post

        def _date_input_values(self, response, name):
            values = []
            for tag in re.findall(r"<input[^>]*>", response.content.decode("utf-8")):
                if f'name="{name}"' in tag:
                    match = re.search(r'value="([^"]*)"', tag)
                    values.append(match.group(1) if match else "")
            return values

        def test_invalid_category_id_is_ignored(self):
            for value in self.INVALID_CATEGORY_IDS:
                with self.subTest(category_id=value):
                    response = self.client.get(self.url, {"category_id": value})
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(len(response.context["posts"]), 2)

        def test_unknown_numeric_category_id_gives_empty_list(self):
            response = self.client.get(self.url, {"category_id": "999999"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(list(response.context["posts"]), [])

        def test_invalid_date_is_ignored(self):
            for name in ("date_from", "date_to"):
                for value in self.INVALID_DATES:
                    with self.subTest(param=name, value=value):
                        response = self.client.get(self.url, {name: value})
                        self.assertEqual(response.status_code, 200)
                        self.assertEqual(len(response.context["posts"]), 2)

        def test_invalid_date_fields_are_empty(self):
            for name in ("date_from", "date_to"):
                for value in self.INVALID_DATES:
                    with self.subTest(param=name, value=value):
                        response = self.client.get(self.url, {name: value})
                        values = self._date_input_values(response, name)
                        self.assertTrue(values, f"Нет полей {name}")
                        self.assertEqual(set(values), {""})

        def test_invalid_date_does_not_break_valid_one(self):
            cases = [
                ({"date_from": "zzz", "date_to": "2025-12-31"}, [self.old_post]),
                ({"date_from": "2026-01-01", "date_to": "zzz"}, [self.new_post]),
                ({"date_from": "zzz", "date_to": "2026-02-31"}, [self.new_post, self.old_post]),
            ]
            for params, expected in cases:
                with self.subTest(params=params):
                    response = self.client.get(self.url, params)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(list(response.context["posts"]), expected)

        def test_valid_dates_still_filter(self):
            cases = [
                ({"date_from": "2026-01-01"}, [self.new_post]),
                ({"date_to": "2025-12-31"}, [self.old_post]),
                ({"date_from": "2025-01-01", "date_to": "2025-12-31"}, [self.old_post]),
            ]
            for params, expected in cases:
                with self.subTest(params=params):
                    response = self.client.get(self.url, params)
                    self.assertEqual(list(response.context["posts"]), expected)

        def test_valid_date_is_kept_in_fields(self):
            response = self.client.get(self.url, {"date_from": "2026-01-01"})
            values = self._date_input_values(response, "date_from")
            self.assertTrue(values)
            self.assertEqual(set(values), {"2026-01-01"})