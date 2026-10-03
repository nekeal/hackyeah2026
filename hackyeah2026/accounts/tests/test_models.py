from django.contrib.auth.models import AbstractUser

from hackyeah2026.accounts.factories import UserFactory
from hackyeah2026.accounts.models import CustomUser


class TestCustomUser:
    def test_custom_user_inherits_from_abstract(self):
        assert issubclass(CustomUser, AbstractUser)

    def test_factory_builds_user(self):
        user = UserFactory.build(password="password")  # noqa: S106
        assert user.password != "password"
