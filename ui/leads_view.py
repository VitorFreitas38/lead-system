import streamlit as st

from services.leads_service import (
    list_leads,
    update_lead_status,
    STATUS_PIPELINE,
)


def _proximo_status(status_atual: str):
    try:
        idx = STATUS_PIPELINE.index(status_atual)
        if idx < len(STATUS_PIPELINE) - 1:
            return STATUS_PIPELINE[idx + 1]
    except ValueError:
        return None
    return None


def render_leads_page(user: dict):
    role = user.get("role", "user")
    email_usuario = user.get("email")

    st.markdown('<div class="crm-card">', unsafe_allow_html=True)

    if role == "admin":
        st.markdown(
            '<div class="section-title">📊 Pipeline de leads (admin)</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-subtitle">'
            "Visualize o pipeline completo de todos os vendedores ou filtre por um vendedor específico."
            "</div>",
            unsafe_allow_html=True,
        )

        filtro_email = st.text_input(
            "Filtrar por email do vendedor (deixe em branco para ver todos):",
            value="",
        )
        vendedor_email = filtro_email or None
    else:
        st.markdown(
            '<div class="section-title">📊 Meu pipeline de leads</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-subtitle">'
            "Aqui você vê apenas os leads atribuídos ao seu usuário. "
            "Cada vendedor enxerga somente o próprio funil."
            "</div>",
            unsafe_allow_html=True,
        )
        vendedor_email = email_usuario

    st.markdown("---")
    st.subheader("📌 Pipeline")

    cols = st.columns(len(STATUS_PIPELINE))

    for idx, status in enumerate(STATUS_PIPELINE):
        with cols[idx]:
            st.markdown(f"### {status.capitalize()}")
            leads = list_leads(status=status, vendedor_email=vendedor_email)

            if not leads:
                st.caption("Nenhum lead aqui ainda.")
            else:
                for lead in leads:
                    with st.container():
                        st.markdown(
                            f"**{lead.get('nome', 'Sem nome')}**  \n"
                            f"{lead.get('email', '')}  \n"
                            f"{lead.get('telefone', '')}"
                        )

                        valor = lead.get("valor_previsto")
                        if valor:
                            st.caption(
                                "Valor previsto: R$ "
                                + f"{float(valor):,.2f}"
                                .replace(",", "X")
                                .replace(".", ",")
                                .replace("X", ".")
                            )

                        if role == "admin":
                            st.caption(
                                f"👤 Vendedor: {lead.get('vendedor_email', 'sem vendedor')}"
                            )

                        prox = _proximo_status(status)
                        if prox:
                            if st.button(
                                f"➡ Mover para {prox.capitalize()}",
                                key=f"move_{lead['id']}_{status}",
                            ):
                                ok, msg = update_lead_status(lead["id"], prox)
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)

                        st.markdown("---")

    st.markdown("</div>", unsafe_allow_html=True)
