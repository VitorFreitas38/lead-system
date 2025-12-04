# services/auth_service.py
from datetime import datetime
import bcrypt
from typing import Tuple, Optional, Dict
from services.firebase_init import db

from config.firebase import get_db

db = get_db()


def get_user_by_email(email: str):
    """Busca usuário pelo email (ID do documento)."""
    doc_ref = db.collection("usuarios").document(email)
    doc = doc_ref.get()
    if doc.exists:
        return doc_ref, doc.to_dict()
    return None, None


def create_user(email: str, password: str, nome: str = "") -> Tuple[bool, str]:
    """Cria usuário com senha hasheada."""
    doc_ref, existing = get_user_by_email(email)
    if existing:
        return False, "Usuário já cadastrado."

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    if not doc_ref:
        doc_ref = db.collection("usuarios").document(email)

    doc_ref.set({
        "email": email,
        "nome": nome,
        "password_hash": password_hash,
        "role": "user",
        "created_at": datetime.utcnow(),
    })

    return True, "Usuário criado com sucesso."


def check_login(email: str, password: str) -> Tuple[bool, Optional[Dict]]:
    """Valida email/senha."""
    _, user_data = get_user_by_email(email)
    if not user_data:
        return False, {"error": "Usuário não encontrado."}

    stored_hash = user_data.get("password_hash")
    if not stored_hash:
        return False, {"error": "Usuário sem senha configurada."}

    if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        return True, user_data

    return False, {"error": "Senha incorreta."}
