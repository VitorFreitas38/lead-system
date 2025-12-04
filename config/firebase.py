# config/firebase.py
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Opcional: pegar caminho do JSON de secrets do Streamlit ou variáveis de ambiente
def _get_credentials_path() -> str:
    # 1) Tenta pegar do secrets.toml
    try:
        import streamlit as st
        path = st.secrets.get("FIREBASE_CREDENTIALS_PATH", "")
        if path:
            return path
    except Exception:
        pass

    # 2) Fallback: variável de ambiente
    env_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if env_path:
        return env_path

    # 3) Fallback final: caminho padrão (ajusta para o seu)
    return "lead-system/teste.json"


def initialize_firebase():
    if not firebase_admin._apps:
        cred_path = _get_credentials_path()
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)


def get_db():
    initialize_firebase()
    return firestore.client()
