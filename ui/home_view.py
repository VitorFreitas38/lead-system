# ui/home_view.py

import streamlit as st
import pandas as pd

from services.leads_service import (
    get_leads_stats,
    list_leads,
    STATUS_PIPELINE,
)


# ================== HELPERS GERAIS ==================


def _format_currency(valor):
    try:
        v = float(valor or 0)
    except (TypeError, ValueError):
        return "R$ 0,00"
    return (
        "R$ "
        + f"{v:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def _sum_valor_por_status(status, vendedor_email=None) -> float:
    """Soma o valor previsto dos leads em um determinado status."""
    total = 0.0
    try:
        leads = list_leads(status=status, vendedor_email=vendedor_email)
    except TypeError:
        leads = list_leads(status, vendedor_email)
    for lead in leads:
        try:
            total += float(lead.get("valor_previsto") or 0)
        except (TypeError, ValueError):
            continue
    return total


def _count_por_status(vendedor_email=None) -> dict:
    """Conta quantos leads existem em cada status, usando list_leads (fonte confiável)."""
    counts = {}
    for status in STATUS_PIPELINE:
        try:
            leads = list_leads(status=status, vendedor_email=vendedor_email)
        except TypeError:
            leads = list_leads(status, vendedor_email)
        counts[status] = len(leads)
    return counts


def _compute_status_metrics(vendedor_email=None):
    """
    Retorna:
    - por_status (dict)
    - total
    - faturados
    - perdidos
    - abertos
    tudo calculado em cima do list_leads.
    """
    por_status = _count_por_status(vendedor_email)
    total = sum(por_status.values())
    faturados = por_status.get("faturado", 0)
    perdidos = por_status.get("perdido", 0)
    abertos = total - faturados - perdidos  # tudo que não é fechado nem perdido
    return por_status, total, faturados, perdidos, abertos


def _load_all_leads():
    """Carrega todos os leads (de todos os status). Usado no dashboard de admin."""
    all_leads = []
    for status in STATUS_PIPELINE:
        try:
            all_leads.extend(list_leads(status=status, vendedor_email=None))
        except TypeError:
            all_leads.extend(list_leads(status, None))
    return all_leads


def _build_status_dataframe(stats_por_status: dict) -> pd.DataFrame:
    data = {
        "Status": [],
        "Leads": [],
    }
    for status in STATUS_PIPELINE:
        data["Status"].append(status)
        data["Leads"].append(int(stats_por_status.get(status, 0)))
    return pd.DataFrame(data)


def _build_valor_status_dataframe(vendedor_email=None) -> pd.DataFrame:
    data = {"Status": [], "Valor_previsto": []}
    for status in STATUS_PIPELINE:
        v = _sum_valor_por_status(status, vendedor_email)
        data["Status"].append(status)
        data["Valor_previsto"].append(v)
    return pd.DataFrame(data)


# ================== HOME VENDEDOR ==================


def _render_vendedor_home(user: dict):
    vendedor_email = user.get("email")

    # Ticket médio continua vindo da função de stats (se ela estiver correta)
    stats = get_leads_stats(vendedor_email=vendedor_email)
    ticket_medio = stats.get("ticket_medio", 0.0)

    # Todo o resto (por status, total, abertos etc) calculamos com list_leads
    por_status, total, faturados, perdidos, abertos = _compute_status_metrics(
        vendedor_email=vendedor_email
    )

    conversao = (faturados / total) * 100 if total else 0.0
    valor_negociacao = _sum_valor_por_status("negociacao", vendedor_email)
    valor_faturado = _sum_valor_por_status("faturado", vendedor_email)

    st.markdown(
        '<div class="section-title">🏡 Meu Dashboard - Sistema de Leads</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        "Este painel mostra apenas os números dos <strong>seus leads</strong>. "
        "Use estas métricas para acompanhar seu funil e priorizar ações."
        "</div>",
        unsafe_allow_html=True,
    )

    # Linha de KPIs principais
    st.markdown("### 📌 Meus KPIs")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Leads no funil", total)
    with col2:
        st.metric("Leads em aberto", abertos)
    with col3:
        st.metric("Leads faturados", faturados)
    with col4:
        st.metric("Ticket médio (R$)", _format_currency(ticket_medio))

    st.markdown("---")

    # Conversão e valores
    st.markdown("### 🎯 Visão rápida do funil")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.caption("Distribuição dos leads por etapa do funil (apenas seus leads).")
        df_status = _build_status_dataframe(por_status)
        st.bar_chart(df_status, x="Status", y="Leads", use_container_width=True)

    with col2:
        st.metric("Taxa de conversão", f"{conversao:.1f}%")
        st.metric("Valor em negociação", _format_currency(valor_negociacao))
        st.metric("Valor faturado", _format_currency(valor_faturado))
        st.metric("Leads perdidos", perdidos)

    st.markdown("---")

    # Atividades pendentes simples (sem campo de datas)
    st.markdown("### 📝 Atividades sugeridas")

    leads_novo = list_leads(status="novo", vendedor_email=vendedor_email)
    leads_negociacao = list_leads(status="negociacao", vendedor_email=vendedor_email)

    # Leads em negociação sem valor preenchido
    neg_sem_valor = [l for l in leads_negociacao if not l.get("valor_previsto")]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📞 Leads para primeiro contato")
        if not leads_novo:
            st.caption("Nenhum lead novo aguardando contato.")
        else:
            for lead in leads_novo[:5]:
                nome = lead.get("nome", "Sem nome")
                email = lead.get("email", "")
                st.write(f"• **{nome}**  —  {email}")

    with col2:
        st.subheader("💼 Negociações sem valor definido")
        if not neg_sem_valor:
            st.caption("Todas as negociações possuem valor previsto.")
        else:
            for lead in neg_sem_valor[:5]:
                nome = lead.get("nome", "Sem nome")
                email = lead.get("email", "")
                st.write(f"• **{nome}**  —  {email}")

    st.markdown("---")
    st.caption(
        "Use a aba **'Cadastrar Lead'** para registrar novas oportunidades e "
        "**'Leads (Pipeline)'** para movimentar seus leads ao longo do funil."
    )


# ================== HOME ADMIN ==================


def _render_admin_home(user: dict):
    st.markdown(
        '<div class="section-title">🏢 Dashboard (Admin) - Visão da operação</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        "Você está logado como <strong>admin</strong>. Este painel traz a visão consolidada "
        "dos leads da empresa e permite acompanhar a performance dos vendedores."
        "</div>",
        unsafe_allow_html=True,
    )

    filtro_email = st.text_input(
        "Filtrar métricas por email de vendedor (opcional):",
        value="",
        placeholder="ex: vendedor@empresa.com",
    ).strip() or None

    # Ticket médio global ainda vindo da função de stats (se estiver correta)
    stats_global = get_leads_stats(vendedor_email=None)
    ticket_medio = stats_global.get("ticket_medio", 0.0)

    # Por status, total, abertos, faturados, perdidos calculados via list_leads
    por_status, total, faturados, perdidos, abertos = _compute_status_metrics(
        vendedor_email=None
    )
    conversao = (faturados / total) * 100 if total else 0.0

    # KPIs gerais da operação
    st.markdown("### 📊 Visão geral da operação")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Leads no funil (empresa)", total)
    with col2:
        st.metric("Leads em aberto", abertos)
    with col3:
        st.metric("Leads faturados", faturados)
    with col4:
        st.metric("Ticket médio (R$)", _format_currency(ticket_medio))

    st.markdown("---")

    # Gráficos de status e valor global
    st.markdown("### 📈 Funil global de leads")
    col1, col2 = st.columns(2)

    with col1:
        st.caption("Quantidade de leads por etapa do funil (toda a empresa).")
        df_status = _build_status_dataframe(por_status)
        st.bar_chart(df_status, x="Status", y="Leads", use_container_width=True)

    with col2:
        st.caption("Valor previsto total por etapa do funil.")
        df_valor_status = _build_valor_status_dataframe(vendedor_email=None)
        st.bar_chart(
            df_valor_status,
            x="Status",
            y="Valor_previsto",
            use_container_width=True,
        )
        st.metric("Taxa de conversão global", f"{conversao:.1f}%")
        st.metric("Leads perdidos", perdidos)

    st.markdown("---")

    # Ranking de vendedores (usando todos os leads)
    st.markdown("### 🏅 Ranking de vendedores")

    all_leads = _load_all_leads()
    ranking = {}
    for lead in all_leads:
        vend = lead.get("vendedor_email") or "Não atribuído"
        status = lead.get("status") or lead.get("status_lead")
        try:
            valor = float(lead.get("valor_previsto") or 0)
        except (TypeError, ValueError):
            valor = 0.0

        data = ranking.setdefault(
            vend,
            {
                "leads_total": 0,
                "valor_total": 0.0,
                "leads_faturados": 0,
                "valor_faturado": 0.0,
            },
        )
        data["leads_total"] += 1
        data["valor_total"] += valor
        if status == "faturado":
            data["leads_faturados"] += 1
            data["valor_faturado"] += valor

    if not ranking:
        st.caption("Nenhum lead encontrado para montar o ranking.")
    else:
        df_rank = pd.DataFrame(
            [
                {
                    "Vendedor": vend,
                    "Leads": info["leads_total"],
                    "Leads faturados": info["leads_faturados"],
                    "Valor faturado": info["valor_faturado"],
                    "Valor total": info["valor_total"],
                }
                for vend, info in ranking.items()
            ]
        )
        df_rank = df_rank.sort_values(by="Valor faturado", ascending=False)
        st.dataframe(
            df_rank,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")

    # Se admin filtrou um vendedor específico, mostrar um resumo comparativo
    if filtro_email:
        st.markdown(f"### 👤 Resumo do vendedor: `{filtro_email}`")
        stats_vend = get_leads_stats(vendedor_email=filtro_email)

        # Por status calculado via list_leads também
        por_status_v, total_v, faturados_v, perdidos_v, abertos_v = _compute_status_metrics(
            vendedor_email=filtro_email
        )
        ticket_v = stats_vend.get("ticket_medio", 0.0)
        conv_v = (faturados_v / total_v) * 100 if total_v else 0.0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Leads no funil", total_v)
        with c2:
            st.metric("Leads em aberto", abertos_v)
        with c3:
            st.metric("Leads faturados", faturados_v)
        with c4:
            st.metric("Ticket médio (R$)", _format_currency(ticket_v))

        c5, c6 = st.columns(2)
        with c5:
            st.metric("Taxa de conversão", f"{conv_v:.1f}%")
        with c6:
            st.metric("Leads perdidos", perdidos_v)

    st.markdown("---")
    st.caption(
        "Use a aba **'Leads (Pipeline)'** para acompanhar o funil global e o filtro "
        "de vendedor para analisar o pipeline individual de cada membro da equipe."
    )


# ================== ROUTER ==================


def render_home_page(user: dict):
    role = user.get("role", "user")

    if role == "admin":
        _render_admin_home(user)
    else:
        _render_vendedor_home(user)
