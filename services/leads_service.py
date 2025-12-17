# services/leads_service.py
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re

from config.firebase import get_db
from google.cloud.firestore_v1.base_query import FieldFilter

db = get_db()

LEADS_COLLECTION = "leads"
USUARIOS_COLLECTION = "usuarios"

STATUS_PIPELINE = ["novo", "atendimento", "negociacao", "faturado", "perdido"]


def _leads_ref():
    return db.collection(LEADS_COLLECTION)


def _usuarios_ref():
    return db.collection(USUARIOS_COLLECTION)


def _norm_email(email: str) -> str:
    return (email or "").strip().lower()


def _norm_phone(telefone: str) -> str:
    # Mantém só dígitos: "(19) 98162-0565" -> "19981620565"
    return re.sub(r"\D+", "", telefone or "")


def _exists_by_field(collection_ref, field_name: str, value: str) -> bool:
    """
    Retorna True se existir algum documento na collection com field_name == value.
    Usa limit(1) para ser rápido.
    """
    if not value:
        return False
    q = collection_ref.where(filter=FieldFilter(field_name, "==", value)).limit(1)
    return any(True for _ in q.stream())


def _lead_exists_by_field(field_name: str, value: str) -> bool:
    return _exists_by_field(_leads_ref(), field_name, value)


def _vendedor_existe(email: str) -> bool:
    """
    Verifica se existe um usuário cadastrado com este email na collection 'usuarios'.
    """
    email_norm = _norm_email(email)
    return _exists_by_field(_usuarios_ref(), "email", email_norm)


def create_lead(
    nome: str,
    email: str,
    telefone: str,
    vendedor_email: str,
    valor_previsto: Optional[float] = None,
    origem: Optional[str] = None,
    observacoes: Optional[str] = None,
    status: str = "novo",
) -> Tuple[bool, str]:
    """
    Cria lead com:
    - bloqueio de duplicidade (email e telefone) via campos normalizados
    - validação de vendedor_email existente em 'usuarios'
    """
    try:
        if status not in STATUS_PIPELINE:
            status = "novo"

        nome = (nome or "").strip()
        vendedor_email = _norm_email(vendedor_email)
        email_raw = (email or "").strip()
        telefone_raw = (telefone or "").strip()

        if not nome:
            return False, "Nome é obrigatório."
        if not vendedor_email:
            return False, "Informe o email do vendedor responsável."

        # ✅ valida vendedor
        if not _vendedor_existe(vendedor_email):
            return False, "Email do vendedor não encontrado. Verifique e tente novamente."

        # ✅ normaliza para bloquear duplicidade (independente de formatação)
        email_norm = _norm_email(email_raw)
        telefone_norm = _norm_phone(telefone_raw)

        # ✅ bloqueio de duplicidade (se preenchido)
        if email_norm and _lead_exists_by_field("email_norm", email_norm):
            return False, "Já existe um lead cadastrado com este email."

        if telefone_norm and _lead_exists_by_field("telefone_norm", telefone_norm):
            return False, "Já existe um lead cadastrado com este telefone/WhatsApp."

        now = datetime.utcnow()

        doc_ref = _leads_ref().document()
        doc_ref.set(
            {
                "nome": nome,
                "email": email_raw,
                "email_norm": email_norm,
                "telefone": telefone_raw,
                "telefone_norm": telefone_norm,
                "vendedor_email": vendedor_email,
                "valor_previsto": valor_previsto,
                "origem": origem,
                "observacoes": observacoes,
                "status": status,
                "created_at": now,
                "updated_at": now,
            }
        )

        return True, "Lead criado com sucesso."

    except Exception as e:
        return False, f"Erro ao criar lead: {e}"


def list_leads(
    status: Optional[str] = None,
    vendedor_email: Optional[str] = None,
) -> List[Dict]:
    """
    Lista leads (opcionalmente filtrando por status e/ou vendedor_email).
    """
    ref = _leads_ref()

    if status:
        ref = ref.where(filter=FieldFilter("status", "==", status))

    if vendedor_email:
        ref = ref.where(filter=FieldFilter("vendedor_email", "==", _norm_email(vendedor_email)))

    docs = ref.stream()

    leads: List[Dict] = []
    for d in docs:
        data = d.to_dict() or {}
        data["id"] = d.id
        leads.append(data)

    return leads


def update_lead_status(lead_id: str, new_status: str) -> Tuple[bool, str]:
    if new_status not in STATUS_PIPELINE:
        return False, "Status inválido."

    ref = _leads_ref().document(lead_id)
    snap = ref.get()

    if not snap.exists:
        return False, "Lead não encontrado."

    ref.update(
        {
            "status": new_status,
            "updated_at": datetime.utcnow(),
        }
    )
    return True, "Status atualizado com sucesso."


def update_lead_fields(lead_id: str, campos: dict) -> Tuple[bool, str]:
    """
    Atualiza campos genéricos de um lead.
    Se atualizar email/telefone, atualiza também os campos normalizados.
    Se atualizar vendedor_email, valida se existe em 'usuarios'.
    """
    try:
        if not isinstance(campos, dict) or not campos:
            return False, "Campos inválidos."

        # Se mexer em vendedor_email, valida existência
        if "vendedor_email" in campos:
            ve = _norm_email(campos.get("vendedor_email"))
            if not ve:
                return False, "Informe o email do vendedor responsável."
            if not _vendedor_existe(ve):
                return False, "Email do vendedor não encontrado. Verifique e tente novamente."
            campos["vendedor_email"] = ve

        # Normaliza email/telefone se vierem no update
        if "email" in campos:
            email_raw = (campos.get("email") or "").strip()
            campos["email"] = email_raw
            campos["email_norm"] = _norm_email(email_raw)

        if "telefone" in campos:
            tel_raw = (campos.get("telefone") or "").strip()
            campos["telefone"] = tel_raw
            campos["telefone_norm"] = _norm_phone(tel_raw)

        campos["updated_at"] = datetime.utcnow()

        _leads_ref().document(lead_id).update(campos)
        return True, "Lead atualizado com sucesso."

    except Exception as e:
        return False, f"Erro ao atualizar lead: {e}"


def get_leads_stats(vendedor_email: Optional[str] = None) -> Dict:
    """
    Estatísticas para dashboard.
    """
    ref = _leads_ref()

    if vendedor_email:
        ref = ref.where(filter=FieldFilter("vendedor_email", "==", _norm_email(vendedor_email)))

    docs = ref.stream()

    stats = {
        "total": 0,
        "por_status": {s: 0 for s in STATUS_PIPELINE},
        "total_valor_previsto": 0.0,
    }

    for d in docs:
        data = d.to_dict() or {}
        stats["total"] += 1

        stt = data.get("status", "novo")
        if stt in stats["por_status"]:
            stats["por_status"][stt] += 1

        valor = data.get("valor_previsto") or 0
        try:
            stats["total_valor_previsto"] += float(valor)
        except Exception:
            pass

    return stats
