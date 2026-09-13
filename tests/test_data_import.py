from io import BytesIO


def test_upload_csv_file(client):
    response = client.post(
        "/import/sales",
        files={
            "file": (
                "sales.csv",
                BytesIO(b"date,product,quantity,unit_price\n"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "sales.csv"


def test_reject_unsupported_file_type(client):
    response = client.post(
        "/import/sales",
        files={
            "file": (
                "sales.txt",
                BytesIO(b"test"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 400


def test_reject_empty_file(client):
    response = client.post(
        "/import/sales",
        files={
            "file": (
                "sales.csv",
                BytesIO(b""),
                "text/csv",
            )
        },
    )

    assert response.status_code == 400


def test_reject_file_larger_than_max_size(client, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "import_max_file_size", 10)

    response = client.post(
        "/import/sales",
        files={
            "file": (
                "sales.csv",
                BytesIO(b"12345678901"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 413
