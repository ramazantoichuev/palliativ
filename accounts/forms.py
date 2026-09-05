from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class BaseRegistrationForm(forms.ModelForm):
    PLACEHOLDERS = {
        "first_name": _("Айгуль"),
        "last_name": _("Токтосунова"),
        "email": _("example@gmail.com"),
        "phone": _("+996 700 123 456"),
        "password1": _("Минимум 8 символов"),
        "password2": _("Повторите пароль"),
    }
    password1 = forms.CharField(label=_("Пароль"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Подтверждение пароля"), widget=forms.PasswordInput)

    role = None

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            attrs = {"class": "form-control"}
            if name in self.PLACEHOLDERS:
                attrs["placeholder"] = self.PLACEHOLDERS[name]
            field.widget.attrs.update(attrs)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", _("Пароли не совпадают."))
        return cleaned_data

    def _generate_username(self, email):
        base = email.split("@")[0]
        username = base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self._generate_username(self.cleaned_data["email"])
        user.role = self.role
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class PatientRegistrationForm(BaseRegistrationForm):
    role = User.Role.PATIENT

    class Meta(BaseRegistrationForm.Meta):
        fields = BaseRegistrationForm.Meta.fields + ["phone"]

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if User.objects.filter(phone=phone).exists():
            raise ValidationError(_("Пользователь с таким номером телефона уже зарегистрирован."))
        return phone


class DoctorApplicationForm(BaseRegistrationForm):
    role = User.Role.DOCTOR

    class Meta(BaseRegistrationForm.Meta):
        fields = BaseRegistrationForm.Meta.fields + ["phone"]

    education = forms.CharField(label=_("Образование или место учебы"), max_length=255)
    skills = forms.CharField(label=_("Профессиональные навыки"), widget=forms.Textarea)

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.doctor_profile.education = self.cleaned_data["education"]
            user.doctor_profile.skills = self.cleaned_data["skills"]
            user.doctor_profile.save()
        return user



class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Введите email"),
            }
        )
    )

    password = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Введите пароль"),
            }
        )
    )