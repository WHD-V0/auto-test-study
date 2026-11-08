import pytest
from src.user_service import User, UserService


@pytest.fixture
def service():
    print("prepare service")
    return UserService()


def test_add_user(service):
    user = User("Learner", "learner@example.com", 20)
    service.add_user(user)
    assert service.get_user("learner@example.com") is user


def test_service_starts_empty(service):
    assert service.list_users() == []
