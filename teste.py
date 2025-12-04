import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import bcrypt
from datetime import datetime

# -----------------------------------------
# INICIALIZA FIREBASE ADMIN (FIRESTORE)
# -----------------------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("lead-system/teste.json") # caminho do seu JSON
    firebase_admin.initialize_app(cred)

db = firestore.client()

# -----------------------------------------
# FUNÇÕES AUXILIARES (USUÁRIOS)
# -----------------------------------------
def get_user_by_email(email: str):
    """Busca usuário pelo email (usando o email como ID do doc)."""
    doc_ref = db.collection("usuarios").document(email)
    doc = doc_ref.get()
    if doc.exists:
        return doc_ref, doc.to_dict()
    return None, None


def create_user(email: str, password: str, nome: str = ""):
    """Cria usuário com senha hasheada no Firestore."""
    # Verifica se já existe
    doc_ref, existing = get_user_by_email(email)
    if existing:
        return False, "Usuário já cadastrado."

    # Gera hash da senha
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    # Cria documento
    if not doc_ref:
        doc_ref = db.collection("usuarios").document(email)

    doc_ref.set({
        "email": email,
        "nome": nome,
        "password_hash": password_hash,
        "role": "user",
        "created_at": datetime.utcnow()
    })

    return True, "Usuário criado com sucesso."


def check_login(email: str, password: str):
    """Verifica se email/senha conferem com o hash salvo no Firestore."""
    _, user_data = get_user_by_email(email)
    if not user_data:
        return False, "Usuário não encontrado."

    stored_hash = user_data.get("password_hash")
    if not stored_hash:
        return False, "Usuário sem senha configurada."

    # Compara senha com hash
    if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        return True, user_data
    else:
        return False, "Senha incorreta."


# -----------------------------------------
# CONFIG STREAMLIT
# -----------------------------------------
st.set_page_config(page_title="Sistema de Leads", layout="wide")

if "logged" not in st.session_state:
    st.session_state.logged = False
    st.session_state.user = None

# -----------------------------------------
# INTERFACE
# -----------------------------------------

if not st.session_state.logged:
    st.title("🔐 Login / Cadastro")

    aba_login, aba_cadastro = st.tabs(["Já tenho conta", "Criar conta"])

    with aba_login:
        st.subheader("Entrar")
        email_login = st.text_input("Email (login)", key="email_login")
        senha_login = st.text_input("Senha", type="password", key="senha_login")

        if st.button("Entrar", key="btn_login"):
            ok, result = check_login(email_login, senha_login)
            if ok:
                st.session_state.logged = True
                st.session_state.user = result
                st.success("✅ Login realizado com sucesso!")
                st.rerun()
            else:
                st.error(f"❌ {result}")

    with aba_cadastro:
        st.subheader("Criar nova conta")
        nome_cad = st.text_input("Nome", key="nome_cad")
        email_cad = st.text_input("Email", key="email_cad")
        senha_cad = st.text_input("Senha", type="password", key="senha_cad")
        senha_conf = st.text_input("Confirmar senha", type="password", key="senha_conf")

        if st.button("Cadastrar", key="btn_cadastrar"):
            if senha_cad != senha_conf:
                st.error("❌ As senhas não conferem.")
            elif len(senha_cad) < 4:
                st.error("❌ Coloque uma senha com pelo menos 4 caracteres (para teste).")
            else:
                ok, msg = create_user(email_cad, senha_cad, nome=nome_cad)
                if ok:
                    st.success("✅ Usuário criado! Agora faça login na aba 'Já tenho conta'.")
                else:
                    st.error(f"❌ {msg}")

else:
    # -----------------------------------------
    # PÁGINA INTERNA (APÓS LOGIN)
    # -----------------------------------------
    user = st.session_state.user
    st.sidebar.success(f"Logado como: {user.get('email')}")
    if st.sidebar.button("Sair"):
        st.session_state.logged = False
        st.session_state.user = None
        st.rerun()

    st.title("🏠 Página Inicial - Sistema de Leads")
    st.write(f"Bem-vindo, **{user.get('nome') or user.get('email')}**!")

    st.write("Aqui depois você coloca:")
    st.markdown("""
    - 📋 Lista de leads  
    - ➕ Formulário para cadastrar lead  
    - 📊 Relatórios de conversão  
    - 👥 Filtro por vendedor / status  
    """)

    st.info("Autenticação atual usando Firestore + hash de senha (bcrypt).")
