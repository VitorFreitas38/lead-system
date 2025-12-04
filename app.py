# app.py
import streamlit as st
from ui.login_view import render_login_page
from ui.home_view import render_home_page
from ui.lead_create_view import render_lead_create_page
from ui.leads_view import render_leads_page

# ==============================
# CONFIG GERAL
# ==============================
st.set_page_config(
    page_title="AgroSP Drones - Gestão de Leads",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",  # sempre começa com sidebar aberta
)

# ==============================
# ESTADO INICIAL DA SESSÃO
# ==============================
if "logged" not in st.session_state:
    st.session_state.logged = False
    st.session_state.user = None

if "pagina" not in st.session_state:
    st.session_state.pagina = "Home"


def change_page(page: str):
    st.session_state.pagina = page


# ==============================
# CSS GLOBAL (VISUAL TIPO CRM + SIDEBAR FIXA)
# ==============================
custom_css = """
<style>

/* Remove menu e footer padrão do Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
/* Mantemos o header do Streamlit escondido para ficar mais “limpo” */
header {visibility: hidden;}

/* Fundo geral da aplicação */
.stApp {
    background-color: #f5f7fb;
}

/* Container principal mais estreito, estilo “app SaaS” */
.main .block-container {
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Top bar escura tipo CRM */
.top-bar {
    background: #0f172a;
    color: white;
    padding: 0.9rem 1.5rem;
    border-radius: 0 0 18px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 24px rgba(15,23,42,0.35);
}

/* Título do sistema */
.top-bar .title {
    font-size: 1.3rem;
    font-weight: 600;
}

/* Subtítulo */
.top-bar .subtitle {
    font-size: 0.85rem;
    opacity: 0.8;
}

/* Usuário no topo */
.top-bar .user-box {
    text-align: right;
    font-size: 0.9rem;
}
.top-bar .user-box span {
    display: block;
    font-size: 0.75rem;
    opacity: 0.8;
}

/* ===== SIDEBAR FIXA SEMPRE VISÍVEL ===== */
[data-testid="stSidebar"] {
    background: #0b1220 !important;
    color: #e5e7eb !important;

    /* Largura fixa para parecer app mesmo */
    min-width: 260px !important;
    max-width: 260px !important;
    width: 260px !important;

    visibility: visible !important;
}

/* Força a sidebar a continuar visível mesmo se o estado estiver "recolhido" */
[data-testid="stSidebar"][aria-expanded="false"] {
    transform: translateX(0) !important;
    visibility: visible !important;
}

/* Cores internas da sidebar */
[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* Esconde o botão padrão de recolher/expandir (pra galera não sumir com a barra) */
button[data-testid="baseButton-header"] {
    display: none !important;
}

/* Título do menu */
.sidebar-title {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.3rem;
}

/* Descrição pequena na sidebar */
.sidebar-subtitle {
    font-size: 0.75rem;
    opacity: 0.8;
    margin-bottom: 0.8rem;
}

/* Cards padrão para usar nas páginas internas */
.crm-card {
    background: white;
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 4px 16px rgba(15,23,42,0.06);
    margin-bottom: 1rem;
}

.section-title {
    font-size: 1.05rem;
    font-weight: 600;
    margin-bottom: 0.4rem;
    color: #111827;
}

.section-subtitle {
    font-size: 0.85rem;
    color: #6b7280;
    margin-bottom: 0.8rem;
}

/* Tabela com hover */
.dataframe tbody tr:hover {
    background-color: #eef2ff !important;
}

/* Botões mais arredondados */
.stButton button {
    border-radius: 999px;
    font-weight: 500;
}

/* Badge genérica */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    background: #ecfdf3;
    color: #166534;
}

</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==============================
# TOPO (SÓ QUANDO ESTIVER LOGADO)
# ==============================
if st.session_state.logged:
    user_email = (
        st.session_state.user.get("email", "")
        if st.session_state.user
        else ""
    )

    with st.container():
        st.markdown(
            f"""
            <div class="top-bar">
                <div>
                    <div class="title">AgroSP Drones - Gestão de Leads</div>
                    <div class="subtitle">
                        CRM para controle de oportunidades e serviços com drones agrícolas
                    </div>
                </div>
                <div class="user-box">
                    {user_email if user_email else "Usuário logado"}
                    <span>Ambiente seguro de gestão de leads</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

# ==============================
# SIDEBAR (MENU) - SÓ SE LOGADO
# ==============================
if st.session_state.logged:
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-title">💼 Lead System</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="sidebar-subtitle">Navegue entre as telas do CRM.</div>',
            unsafe_allow_html=True,
        )

        menu = st.radio(
            "Navegação",
            ["Home", "Cadastrar Lead", "Leads (Pipeline)"],
            index=["Home", "Cadastrar Lead", "Leads (Pipeline)"].index(
                st.session_state.pagina
            ),
        )

        if menu != st.session_state.pagina:
            change_page(menu)

        st.markdown("---")
        st.caption("Clique em 'Sair' para encerrar a sessão.")

        if st.button("Sair"):
            st.session_state.logged = False
            st.session_state.user = None
            change_page("Home")
            st.rerun()

# ==============================
# ROTEAMENTO DAS PÁGINAS
# ==============================
if not st.session_state.logged:
    render_login_page()
else:
    pagina_atual = st.session_state.pagina

    if pagina_atual == "Home":
        render_home_page(st.session_state.user)
    elif pagina_atual == "Cadastrar Lead":
        render_lead_create_page(st.session_state.user)
    elif pagina_atual == "Leads (Pipeline)":
        render_leads_page(st.session_state.user)
