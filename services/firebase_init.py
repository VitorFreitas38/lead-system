# services/firebase_init.py
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

try:
    import streamlit as st
except ImportError:
    st = None  # permite rodar sem streamlit (ex.: testes)
    

def _load_cred_dict():
    # 1) Tenta via variável de ambiente FIREBASE_CREDENTIALS (produção / Docker / Render)
    cred_json = os.getenv("FIREBASE_CREDENTIALS")
    if cred_json:
        return json.loads(cred_json)

    # 2) Tenta via st.secrets (local ou Streamlit Cloud)
    if st is not None:
        try:
            raw = st.secrets.get("FIREBASE_CREDENTIALS", None)
        except Exception:
            raw = None

        if raw:
            # Se veio como string (caso do ''' {...} ''')
            if isinstance(raw, str):
                return json.loads(raw)
            # Se vier como dict (outro formato de secrets), já está ok
            return dict(raw)

    # 3) Fallback: arquivo local (dev)
    path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_key.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# Inicializa o Firebase uma única vez
if not firebase_admin._apps:
    cred_dict = _load_cred_dict()
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()
