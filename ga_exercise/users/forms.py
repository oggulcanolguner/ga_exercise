from django import forms
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from users.models import User


class UserCreationForm(DjangoUserCreationForm):
    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages["duplicate_username"])

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "country",
            "is_staff",
            "is_superuser",
            "country",
            "bio",
            "date_of_birth",
            "phone",
        )


class UserChangeForm(DjangoUserChangeForm):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "country",
            "is_staff",
            "is_superuser",
            "country",
            "bio",
            "date_of_birth",
            "phone",
        )
