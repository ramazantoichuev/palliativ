import ast
import os
import re
from pathlib import Path

import polib
from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import translation
from django.utils.html import escape
from django.utils.translation import gettext

BASE = Path(settings.BASE_DIR)
LANGS = ("ky", "en")
CYR = re.compile(r"[А-Яа-яЁёӨөҮүҢң]")
BRAND = "Паллиатив.kg"
SKIP_DIRS = {"venv", ".venv", "env", "node_modules", "migrations", "tests",
             "static", "staticfiles", "media", "locale", ".git", "__pycache__"}
SKIP_PY = ("settings", "manage", "wsgi", "asgi", "conftest", "test")
GETTEXT = {"_", "gettext", "gettext_lazy", "gettext_noop", "ngettext",
           "ngettext_lazy", "pgettext", "pgettext_lazy", "npgettext"}
LOGGERS = {"logger", "log", "logging"}

SAME_OK = {
    "ky": {"Администратор", "Менеджер", "Категория", "Категория:", "Файл",
           "Видео", "ФИО", "Диагноз", "Команда", "Логин", "Модератор",
           "Репутация", "Ресурс", "Слаг", "Текст", "Телефон"},
    "en": set(),
}

# (url_name, GET-параметры, ключевые msgid страницы)
PAGES = [
    ("main:home", None, ["Нужна помощь или консультация?", "Оставить заявку"]),
    ("main:about", None, ["Законодательство и нормативная база",
                          "Международное сотрудничество"]),
    ("main:contacts", None, ["Контакты", "Адрес"]),
    ("main:team", None, ["Команда и руководство"]),
    ("main:privacy_policy", None,
     ["Политика обработки персональных данных", "Срок хранения"]),
    ("main:new-consultation", None, ["Заявка на консультацию", "Отправить заявку"]),
    ("main:search", {"q": "z"}, ["Введите не менее 2 символов для поиска."]),
    ("main:search", {"q": "zzzzzz"}, ["По вашему запросу ничего не найдено."]),
]
TEXT_BLOCK_MODEL = "EditableTextBlock"


def files(ext):
    for root, dirs, names in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        yield from (Path(root) / n for n in names if n.endswith(ext))


def has_cyr(text):
    return bool(CYR.search(text.replace(BRAND, "")))


class CatalogTests(SimpleTestCase):
    """.po без fuzzy/пустых, .mo скомпилирован, KY/EN реально переведены."""
    def test_catalogs(self):
        problems = []
        for lang in LANGS:
            path = BASE / "locale" / lang / "LC_MESSAGES" / "django.po"
            with translation.override(lang):
                for e in polib.pofile(str(path)):
                    if e.obsolete or not e.msgid:
                        continue
                    tag = f"[{lang}] {e.msgid[:60]!r}"
                    if "fuzzy" in e.flags:
                        problems.append(f"{tag}: fuzzy")
                    forms = e.msgstr_plural.values() if e.msgid_plural else [e.msgstr]
                    if not all(f.strip() for f in forms):
                        problems.append(f"{tag}: пустой перевод")
                        continue
                    if e.msgid_plural or e.msgctxt:
                        continue
                    if gettext(e.msgid) != e.msgstr:
                        problems.append(f"{tag}: .mo не совпадает с .po (compilemessages?)")
                    elif (e.msgstr == e.msgid and has_cyr(e.msgid)
                          and e.msgid not in SAME_OK[lang]):
                        problems.append(f"{tag}: не переведено (совпадает с русским)")
        self.assertFalse(problems, "\n".join(problems))


TPL_STRIP = [re.compile(p, re.S | re.I) for p in (
    r"{#.*?#}",
    r"{%\s*comment\b.*?{%\s*endcomment\s*%}",
    r"<!--.*?-->",
    r"<(script|style)\b.*?</\1>",
    r"{%\s*blocktrans(?:late)?\b.*?{%\s*endblocktrans(?:late)?\s*%}",
    r"{%.*?%}",
    r"{{.*?}}",
)]

def py_problems(path):
    src = path.read_text(encoding="utf-8")
    tree, lines, skip = ast.parse(src), src.splitlines(), set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            name = f.id if isinstance(f, ast.Name) else getattr(f, "attr", "")
            is_log = (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
                      and f.value.id in LOGGERS)
            if name in GETTEXT or is_log:
                skip |= {id(x) for x in ast.walk(n)}
        elif isinstance(n, ast.Expr):
            skip.add(id(n.value))
    for n in ast.walk(tree):
        if (isinstance(n, ast.Constant) and isinstance(n.value, str)
                and id(n) not in skip and has_cyr(n.value)
                and "i18n-ignore" not in lines[n.lineno - 1]):
            yield f"{path.relative_to(BASE)}:{n.lineno}: {n.value[:60]!r}"


class HardcodedTextTests(SimpleTestCase):
    """Русский текст вне механизмов перевода.
    Осознанно русские строки (письма сотрудникам) помечайте `# i18n-ignore`
    в той же строке; management-команды пропускаются."""
    def test_templates(self):
        problems = []
        for p in files(".html"):
            text = p.read_text(encoding="utf-8")
            for rx in TPL_STRIP:
                text = rx.sub(lambda m: "\n" * m.group(0).count("\n"), text)
            problems += [f"{p.relative_to(BASE)}:{n}: {ln.strip()[:60]}"
                         for n, ln in enumerate(text.splitlines(), 1) if has_cyr(ln)]
        self.assertFalse(problems, "\n".join(problems))

    def test_python(self):
        problems = []
        for p in files(".py"):
            if p.name.startswith(SKIP_PY) or "management" in p.parts:
                continue
            problems += py_problems(p)
        self.assertFalse(problems, "\n".join(problems))


class PagesTests(TestCase):
    """Ключевые тексты страниц на KY/EN: переведены, русского оригинала нет."""
    def setUp(self):
        model = next((m for m in apps.get_models()
                      if m.__name__ == TEXT_BLOCK_MODEL), None)
        self.assertIsNotNone(model, f"Модель {TEXT_BLOCK_MODEL} не найдена: "
                             "поправьте TEXT_BLOCK_MODEL вверху файла")
        model.objects.all().delete()
        cache.clear()

    def test_pages(self):
        for lang in LANGS:
            self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = lang
            for name, query, msgids in PAGES:
                with self.subTest(lang=lang, page=name, q=query):
                    with translation.override(lang):
                        url = reverse(name)
                        expected = [gettext(m) for m in msgids]
                    resp = self.client.get(url, query, HTTP_ACCEPT_LANGUAGE=lang)
                    self.assertEqual(resp.status_code, 200)
                    body = resp.content.decode("utf-8")
                    bad = []
                    for msgid, tr in zip(msgids, expected):
                        if not (tr in body or escape(tr) in body):
                            bad.append(f"нет текста {tr!r}")
                        if tr != msgid and msgid in body:
                            bad.append(f"остался русский {msgid!r}")
                    if lang == "en":
                        visible = re.sub(r"<(script|style)\b.*?</\1>|<[^>]+>", " ",
                                         body, flags=re.S)
                        cyr = [ln.strip()[:80] for ln in visible.splitlines()
                               if has_cyr(ln)]
                        if cyr:
                            bad.append(f"кириллица на EN (контент из БД или "
                                       f"непереведённая строка): {cyr[:5]}")
                    self.assertFalse(bad, "\n".join(bad))