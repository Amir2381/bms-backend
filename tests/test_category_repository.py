from app.models.category import Category
from app.repositories import category_repository
from tests.database import TestingSessionLocal


def test_create_and_get_category():
    db = TestingSessionLocal()
    try:
        new_category = Category(name="Electronics")
        created = category_repository.create_category(db, new_category)
        assert created.id is not None
        assert created.name == "Electronics"

        fetched = category_repository.get_category(db, created.id)
        assert fetched is not None
        assert fetched.name == "Electronics"
    finally:
        db.close()


def test_get_category_by_name():
    db = TestingSessionLocal()
    try:
        new_category = Category(name="Books")
        category_repository.create_category(db, new_category)

        fetched = category_repository.get_category_by_name(db, "Books")
        assert fetched is not None
        assert fetched.name == "Books"
    finally:
        db.close()


def test_get_all_categories():
    db = TestingSessionLocal()
    try:
        cat1 = Category(name="Home")
        cat2 = Category(name="Toys")
        category_repository.create_category(db, cat1)
        category_repository.create_category(db, cat2)

        categories = category_repository.get_all_categories(db)
        names = [c.name for c in categories]
        assert "Home" in names
        assert "Toys" in names
    finally:
        db.close()


def test_update_category():
    db = TestingSessionLocal()
    try:
        cat = Category(name="Old Name")
        created = category_repository.create_category(db, cat)

        created.name = "New Name"
        updated = category_repository.update_category(db, created)

        assert updated.name == "New Name"
        fetched = category_repository.get_category(db, created.id)
        assert fetched.name == "New Name"
    finally:
        db.close()


def test_delete_category():
    db = TestingSessionLocal()
    try:
        cat = Category(name="To Delete")
        created = category_repository.create_category(db, cat)

        category_repository.delete_category(db, created)

        fetched = category_repository.get_category(db, created.id)
        assert fetched is None
    finally:
        db.close()
