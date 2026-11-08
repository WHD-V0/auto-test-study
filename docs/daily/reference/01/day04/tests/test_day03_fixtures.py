@pytest.fixture
def prepared_file(tmp_path):
    path = tmp_path / "lesson.txt"
    path.write_text("hello", encoding="utf-8")
    try:
        yield path
    finally:
        path.unlink(missing_ok=True)
        assert not path.exists()
        print("cleaned:", path)


def test_read_prepared_file(prepared_file):
    assert prepared_file.read_text(encoding="utf-8") == "hello"


def test_save_and_load(service, tmp_path):
    service.add_user(User("Learner", "learner@example.com", 20))
    path = tmp_path / "users.json"
    service.save_to_file(str(path))
    restored = UserService()
    restored.load_from_file(str(path))
    user = restored.get_user("learner@example.com")
    assert user is not None
    assert user.name == "Learner"
    assert user.email == "learner@example.com"
