import re

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.postgres.search import TrigramSimilarity
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from utils.cache import invalidate_profile_cache


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email.lower())
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def search(self, text):
        username_similarity = TrigramSimilarity("username", text)
        queryset = (
            self.get_queryset()
            .annotate(similarity=username_similarity)
            .filter(similarity__gt=0.25)
            .order_by("-similarity")
        )
        return queryset


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email"), max_length=255, unique=True, db_index=True)
    username = models.CharField(
        _("username"),
        max_length=255,
        unique=True,
        validators=[
            validators.RegexValidator(
                re.compile(r"^[\w.-]+$"),
                _("Username must contain alphanumeric characters"),
                "invalid",
            )
        ],
    )
    full_name = models.CharField(_("full name"), max_length=256, blank=True)
    date_of_birth = models.DateField(_("date of birth"))
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into the admin " "site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as "
            "active. Unselect this instead of deleting accounts."
        ),
    )
    country = CountryField()
    date_joined = models.DateTimeField(_("date joined"), auto_now_add=True)
    bio = models.TextField(_("biography"), null=False, blank=True, default="")
    phone = models.CharField(
        _("phone number"),
        validators=[
            validators.RegexValidator(
                r"^\+?1?\d{9,15}$",
                _(
                    "The number must be entered in the format: '+999999999' with up to 15 digits."
                ),
                "invalid",
            )
        ],
        max_length=16,
        blank=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "date_of_birth"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.username

    def get_full_name(self):
        return self.full_name or self.username or self.email

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        invalidate_profile_cache(self.id)
