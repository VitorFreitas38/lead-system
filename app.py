# app.py
import streamlit as st

from ui.login_view import render_login_page
from ui.home_view import render_home_page
from ui.lead_create_view import render_lead_create_page
from ui.leads_view import render_leads_page


st.set_page_config(
    page_title="Lead System - CRM",
    page_icon="📋",
    layout="wide",
)

custom_css = """
<style>
html, body, [class*="block-container"] {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text",
                 "Segoe UI", sans-serif;
}

/* ===== LAYOUT PRINCIPAL ===== */
.main-container {
    max-width: 1400px;
    margin: 0 auto;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: #020617;
}

.sidebar-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #E5E7EB;
    margin-bottom: 0.25rem;
}

.sidebar-subtitle {
    font-size: 0.8rem;
    color: #9CA3AF;
    margin-bottom: 1rem;
}

/* ===== HEADER SUPERIOR ===== */
.top-bar {
    background: #020617;
    border-radius: 24px;
    padding: 0.85rem 1.8rem;
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 16px 40px rgba(15,23,42,0.4);
    color: #E5E7EB;
}

.top-bar .brand-title {
    font-size: 1.05rem;
    font-weight: 600;
}

.top-bar .brand-subtitle {
    font-size: 0.8rem;
    color: #9CA3AF;
}

.top-bar .user-info {
    text-align: right;
    font-size: 0.8rem;
}

/* ===== CARDS GENÉRICOS ===== */
.crm-card {
    background: #FFFFFF;
    border-radius: 24px;
    padding: 1.4rem 1.5rem;
    box-shadow: 0 20px 55px rgba(15,23,42,0.12);
    border: 1px solid rgba(226,232,240,0.9);
    margin-bottom: 1.5rem;
}

/* ===== TÍTULOS DE SEÇÃO ===== */
.section-title {
    font-size: 1.1rem;
    font-weight: 650;
    margin-bottom: 0.3rem;
    display: flex;
    align-items: center;
    gap: 0.45rem;
}

.section-title::before {
    content: "";
    display: inline-block;
    width: 4px;
    height: 18px;
    border-radius: 999px;
    background: linear-gradient(180deg,#0ea5e9,#22c55e);
}

.section-subtitle {
    font-size: 0.85rem;
    color: #6B7280;
    margin-bottom: 1rem;
}

/* ===== MÉTRICAS ===== */
[data-testid="stMetric"] {
    background: #F9FAFB;
    padding: 0.9rem 1rem;
    border-radius: 16px;
    border: 1px solid #E5E7EB;
}

/* ===== KANBAN PIPELINE ===== */
.kanban-board {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}

/* Coluna bem leve, sem retângulo gigante */
.kanban-column {
    padding: 0.25rem 0.25rem 0.75rem;
}

/* Cabeçalho da coluna */
.kanban-column-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.kanban-column-title {
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #4b5563;
}

.kanban-column-badge {
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 999px;
    background: #e5e7eb;
    color: #111827;
}

/* Card do lead */
.kanban-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 0.6rem 0.75rem;
    margin-bottom: 0.6rem;
    box-shadow: 0 4px 12px rgba(15,23,42,0.08);
    border: 1px solid rgba(209,213,219,0.7);
}

/* Card de lead perdido */
.kanban-card-lost {
    border-color: #fecaca;
    background: #fef2f2;
}

.kanban-card-lost .kanban-card-title {
    color: #b91c1c;
}

.kanban-card-title {
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 0.1rem;
    color: #111827;
}

.kanban-card-sub {
    font-size: 0.78rem;
    color: #6b7280;
    margin-bottom: 0.15rem;
}

.kanban-card-meta {
    font-size: 0.78rem;
    color: #4b5563;
    display: flex;
    justify-content: space-between;
    margin-top: 0.2rem;
}

.kanban-chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 999px;
    background: #eff6ff;
    color: #1d4ed8;
}

.kanban-chip-small {
    font-size: 0.7rem;
    padding: 1px 6px;
    border-radius: 999px;
    background: #f9fafb;
    color: #6b7280;
    border: 1px solid #e5e7eb;
}


/* Botão "Sair" na sidebar */
.sidebar-logout {
    margin-top: 2rem;
    font-size: 0.8rem;
    color: #9CA3AF;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Home"


def render_shell():
    user = st.session_state.user
    user_email = user.get("email", "") if user else ""
    user_role = user.get("role", "user") if user else "user"

    # SIDEBAR
    with st.sidebar:
        st.markdown('<div class="sidebar-title">📋 Lead System</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sidebar-subtitle">Navegue entre as telas do CRM.</div>',
            unsafe_allow_html=True,
        )

        page = st.radio(
            "Navegação",
            ["Home", "Cadastrar Lead", "Leads (Pipeline)"],
            index=["Home", "Cadastrar Lead", "Leads (Pipeline)"].index(st.session_state.page),
            label_visibility="collapsed",
        )
        st.session_state.page = page

        st.markdown('<div class="sidebar-logout">Clique em \'Sair\' para encerrar a sessão.</div>', unsafe_allow_html=True)
        if st.button("Sair"):
            st.session_state.user = None
            st.session_state.page = "Home"
            st.experimental_rerun()

    # HEADER
    st.markdown(
        f"""
        <div class="top-bar">
            <div>
                <div class="brand-title">AgroSP Drones - Gestão de Leads</div>
                <div class="brand-subtitle">
                    CRM para controle de oportunidades e serviços com drones agrícolas
                </div>
            </div>
            <div class="user-info">
                <div>{user_email}</div>
                <div>{"Administrador" if user_role == "admin" else "Vendedor"}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # CONTEÚDO
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    if st.session_state.page == "Home":
        render_home_page(user)
    elif st.session_state.page == "Cadastrar Lead":
        render_lead_create_page(user)
    elif st.session_state.page == "Leads (Pipeline)":
        render_leads_page(user)

    st.markdown("</div>", unsafe_allow_html=True)


def main():
    user = st.session_state.user
    if user is None:
        render_login_page()
    else:
        render_shell()


if __name__ == "__main__":
    main()
