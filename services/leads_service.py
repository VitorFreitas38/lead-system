# services/leads_service.py
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config.firebase import get_db
from google.cloud.firestore_v1.base_query import FieldFilter
from services.firebase_init import db

db = get_db()

LEADS_COLLECTION = "leads"

STATUS_PIPELINE = ["novo", "atendimento", "negociacao", "faturado"]


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

    if status not in STATUS_PIPELINE:
        status = "novo"

    doc_ref = db.collection(LEADS_COLLECTION).document()
    doc_ref.set(
        {
            "nome": nome,
            "email": email,
            "telefone": telefone,
            "vendedor_email": vendedor_email,
            "valor_previsto": valor_previsto,
            "origem": origem,
            "observacoes": observacoes,
            "status": status,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
    )

    return True, "Lead criado com sucesso."


def list_leads(
    status: Optional[str] = None,
    vendedor_email: Optional[str] = None,
) -> List[Dict]:

    ref = db.collection(LEADS_COLLECTION)

    if status:
        ref = ref.where(filter=FieldFilter("status", "==", status))

    if vendedor_email:
        ref = ref.where(filter=FieldFilter("vendedor_email", "==", vendedor_email))

    docs = ref.stream()

    leads = []
    for d in docs:
        data = d.to_dict()
        data["id"] = d.id
        leads.append(data)

    return leads


def update_lead_status(lead_id: str, new_status: str) -> Tuple[bool, str]:
    if new_status not in STATUS_PIPELINE:
        return False, "Status inválido."

    ref = db.collection(LEADS_COLLECTION).document(lead_id)

    if not ref.get().exists:
        return False, "Lead não encontrado."

    ref.update(
        {
            "status": new_status,
            "updated_at": datetime.utcnow(),
        }
    )

    return True, "Status atualizado com sucesso."


def get_leads_stats(vendedor_email: Optional[str] = None) -> Dict:
    ref = db.collection(LEADS_COLLECTION)

    if vendedor_email:
        ref = ref.where(filter=FieldFilter("vendedor_email", "==", vendedor_email))

    docs = ref.stream()

    stats = {
        "total": 0,
        "por_status": {s: 0 for s in STATUS_PIPELINE},
        "total_valor_previsto": 0.0,
    }

    for d in docs:
        data = d.to_dict()
        stats["total"] += 1

        st = data.get("status", "novo")
        if st in stats["por_status"]:
            stats["por_status"][st] += 1

        valor = data.get("valor_previsto") or 0
        try:
            stats["total_valor_previsto"] += float(valor)
        except:
            pass

    return stats
