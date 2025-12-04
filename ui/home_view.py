import streamlit as st
from services.leads_service import get_leads_stats, STATUS_PIPELINE


def render_home_page(user: dict):
    role = user.get("role", "user")
    vendedor_email = user.get("email")

    # ==============================
    # BUSCA DOS DADOS
    # ==============================
    if role == "admin":
        # Admin pode ver geral ou filtrar por email
        st.markdown('<div class="crm-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-title">🏠 Dashboard geral</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-subtitle">'
            "Visualize os KPIs gerais de leads ou filtre pelos leads de um vendedor específico."
            "</div>",
            unsafe_allow_html=True,
        )

        filtro_email = st.text_input(
            "Filtrar KPIs por email de vendedor (deixe em branco para visão geral):",
            value="",
        )
        email_filtro = filtro_email or None

        stats = get_leads_stats(vendedor_email=email_filtro)

        if email_filtro:
            st.markdown(f"**📈 KPIs do vendedor:** `{email_filtro}`")
        else:
            st.markdown("**📈 KPIs gerais (todos os leads)**")

    else:
        # Vendedor vê apenas seus próprios KPIs
        st.markdown('<div class="crm-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-title">🏠 Meu Dashboard</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-subtitle">'
            "Este painel mostra apenas os números dos <b>seus leads</b>. "
            "Cada vendedor enxerga somente seus próprios resultados."
            "</div>",
            unsafe_allow_html=True,
        )

        stats = get_leads_stats(vendedor_email=vendedor_email)
        st.markdown(f"**📈 Meus KPIs ({vendedor_email})**")

    # ==============================
    # CÁLCULOS DE KPI
    # ==============================
    total_leads = stats["total"]
    total_valor = stats["total_valor_previsto"]

    # normaliza chaves de status pra minúsculo
    por_status_raw = stats.get("por_status", {})
    por_status = {str(k).lower(): v for k, v in por_status_raw.items()}

    leads_faturados = por_status.get("faturado", por_status.get("fechado", 0))
    leads_abertos = total_leads - leads_faturados if total_leads else 0

    taxa_conversao = (
        round((leads_faturados / total_leads) * 100.0, 1) if total_leads > 0 else 0.0
    )
    ticket_medio = (
        total_valor / total_leads if total_leads > 0 else 0.0
    )  # valor médio por lead

    # ==============================
    # BLOCO DE KPIs PRINCIPAIS
    # ==============================
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Leads no funil", total_leads)

    with col2:
        st.metric("Leads em aberto", leads_abertos)

    with col3:
        st.metric("Leads faturados", leads_faturados)

    with col4:
        st.metric(
            "Ticket médio (R$)",
            "R$ "
            + f"{ticket_medio:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
        )

    st.markdown("---")

    # Taxa de conversão com barra
    st.markdown("#### 🎯 Taxa de conversão do funil")
    conv_col1, conv_col2 = st.columns([3, 1])
    with conv_col1:
        st.progress(min(taxa_conversao / 100, 1.0))
    with conv_col2:
        st.markdown(f"<h4 style='text-align:right'>{taxa_conversao:.1f}%</h4>",
                    unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ==============================
    # BLOCO DE LEADS POR STATUS
    # ==============================
    st.markdown('<div class="crm-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">📊 Leads por status</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        "Distribuição dos leads ao longo das etapas do funil de vendas."
        "</div>",
        unsafe_allow_html=True,
    )

    cols_status = st.columns(len(STATUS_PIPELINE))

    for idx, status in enumerate(STATUS_PIPELINE):
        qtd = por_status.get(status.lower(), 0)
        with cols_status[idx]:
            st.markdown(
                f"<p style='font-size:0.8rem; text-transform:uppercase; "
                f"letter-spacing:0.05em; color:#6b7280; margin-bottom:0.1rem;'>"
                f"{status}</p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<h2 style='margin-top:0; margin-bottom:0.2rem;'>{qtd}</h2>",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    if role == "admin":
        st.caption(
            "Use a aba **'Leads (Pipeline)'** para acompanhar o funil global "
            "e mover os leads entre os estágios."
        )
    else:
        st.caption(
            "Use a aba **'Cadastrar Lead'** para registrar novas oportunidades "
            "e **'Leads (Pipeline)'** para movimentar os seus leads ao longo do funil."
        )

    st.markdown("</div>", unsafe_allow_html=True)
