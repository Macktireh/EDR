import os
from collections.abc import Callable
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TypedDict

from django.conf import settings
from django.core.files import File
from django.core.files.uploadedfile import UploadedFile
from django.core.mail import EmailMultiAlternatives
from weasyprint import HTML


def save_file_temporarily(id: str, file: UploadedFile) -> None:
    folder = Path(settings.BASE_DIR) / "temp" / "identity_document" / str(id)
    folder.mkdir(parents=True, exist_ok=True)
    file_path = folder / file.name

    with open(file_path, "wb") as f:
        for chunk in file.chunks():
            f.write(chunk)


def attach_temp_document(reservation_data: dict, callback: Callable[[File, str], None]) -> None:
    temp_folder = (
        Path(settings.BASE_DIR) / "temp" / "identity_document" / str(reservation_data["id"])
    )
    temp_file_path = temp_folder / reservation_data["file_name"]

    if temp_file_path.exists():
        with open(temp_file_path, "rb") as f:
            callback(File(f), reservation_data["file_name"])


def delete_file_temporarily(id: str, file_name: str) -> None:
    folder = Path(settings.BASE_DIR) / "temp" / "identity_document" / str(id)
    file_path = folder / file_name

    if file_path.exists():
        try:
            file_path.unlink()
            if not any(folder.iterdir()):
                folder.rmdir()
        except Exception:
            pass


def generate_pdf(html_string: str) -> str:
    with NamedTemporaryFile(delete=False, suffix=".pdf") as result:
        html = HTML(string=html_string)
        html.write_pdf(target=result.name)
        return result.name


class PayloadEmail(TypedDict):
    from_email: str | None
    to: list[str]
    subject: str
    body: str
    html: str | None
    html_attach_file: str | None
    cc: list[str] | None
    bcc: list[str] | None
    reply_to: list[str] | None


def send_email(payload: PayloadEmail) -> None:
    try:
        email = EmailMultiAlternatives(
            subject=payload["subject"],
            body=payload["body"],
            to=payload["to"],
            from_email=payload.get("from_email"),
            cc=payload.get("cc"),
            bcc=payload.get("bcc"),
            reply_to=payload.get("reply_to"),
        )
        if payload["html_attach_file"]:
            pdf_path = generate_pdf(payload["html_attach_file"])
            email.attach_file(pdf_path)
        if payload["html"]:
            email.attach_alternative(payload["html"], "text/html")
        email.send()
    except Exception:
        raise
    finally:
        try:
            if pdf_path and os.path.exists(pdf_path):
                os.remove(pdf_path)
        except Exception:
            pass
