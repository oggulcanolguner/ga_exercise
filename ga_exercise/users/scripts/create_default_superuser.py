from users import models


def create_default_superuser():
    username = "admin@ga.com"
    password = "awesome123"
    models.User.objects.create_superuser(
        username, password, date_of_birth="1970-01-01", username="admin"
    )
    print(
        f"Super user was created successfully! Username = {username} Password = {password}"
    )


def run():
    create_default_superuser()
