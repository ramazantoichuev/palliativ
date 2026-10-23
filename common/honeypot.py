from django import forms

HONEYPOT_FIELD = "company_site"


class HoneypotFormMixin:
    """Скрытое поле-ловушка. Люди его не видят, боты заполняют."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[HONEYPOT_FIELD] = forms.CharField(
            required=False,
            label="",
            widget=forms.TextInput(
                attrs={
                    "tabindex": "-1",
                    "autocomplete": "off",
                    "aria-hidden": "true",
                    "style": "position:absolute;left:-9999px;height:0;width:0;opacity:0;",
                }
            ),
        )


def honeypot_filled(request):
    return bool(request.POST.get(HONEYPOT_FIELD, "").strip())