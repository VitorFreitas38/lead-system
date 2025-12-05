import streamlit as st
from services.leads_service import (
    list_leads,
    update_lead_status,
    update_lead_fields,  # função que atualiza valor/observações
    STATUS_PIPELINE,
)


def _proximo_status(status_atual: str):
    """Retorna o próximo status do funil, se existir."""
    try:
        idx = STATUS_PIPELINE.index(status_atual)
        if idx < len(STATUS_PIPELINE) - 1:
            return STATUS_PIPELINE[idx + 1]
    except ValueError:
        return None
    return None


def _status_anterior(status_atual: str):
    """Retorna o status anterior no funil, se existir."""
    try:
        idx = STATUS_PIPELINE.index(status_atual)
        if idx > 0:
            return STATUS_PIPELINE[idx - 1]
    except ValueError:
        return None
    return None


def _ensure_state_keys():
    if "current_lead" not in st.session_state:
        st.session_state["current_lead"] = None


# ===== MODAL NATIVO DO STREAMLIT =====
@st.dialog("✏️ Detalhes do lead")
def show_lead_details_dialog():
    """Modal central para editar valor e observações do lead selecionado."""
    lead = st.session_state.get("current_lead")
    if not lead:
        st.write("Nenhum lead selecionado.")
        return

    lead_id = lead.get("id")
    nome = lead.get("nome", "Sem nome")
    email = lead.get("email", "")
    telefone = lead.get("telefone", "")
    valor = lead.get("valor_previsto", "")
    observacoes = lead.get("observacoes", "")

    st.subheader(nome)
    if email:
        st.caption(email)
    if telefone:
        st.caption(telefone)

    with st.form(f"lead_edit_form_{lead_id}"):
        novo_valor = st.text_input(
            "Valor previsto (R$)", value=str(valor or "")
        )
        novas_obs = st.text_area(
            "Observações", value=str(observacoes or ""), height=120
        )

        col1, col2 = st.columns(2)
        with col1:
            salvar = st.form_submit_button("💾 Salvar")
        with col2:
            fechar = st.form_submit_button("Fechar")

    if salvar:
        campos = {
            "valor_previsto": novo_valor,
            "observacoes": novas_obs,
        }
        ok, msg = update_lead_fields(lead_id, campos)
        if ok:
            st.success(msg)
        else:
            st.error(msg)
        st.session_state.current_lead = None
        st.rerun()

    elif fechar:
        st.session_state.current_lead = None
        st.rerun()


# ===== PÁGINA PRINCIPAL DO PIPELINE =====
def render_leads_page(user: dict):
    _ensure_state_keys()

    role = user.get("role", "user")
    email_usuario = user.get("email")

    #st.markdown('<div class="crm-card">', unsafe_allow_html=True)

    # Cabeçalho
    if role == "admin":
        st.markdown(
            '<div class="section-title">📊 Pipeline de leads (Kanban - Admin)</div>',
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
            '<div class="section-title">📊 Meu pipeline de leads (Kanban)</div>',
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
    st.subheader("📌 Pipeline Kanban")

    cols = st.columns(len(STATUS_PIPELINE))

    for idx, status in enumerate(STATUS_PIPELINE):
        with cols[idx]:
            st.markdown('<div class="kanban-column">', unsafe_allow_html=True)

            leads_col = list_leads(status=status, vendedor_email=vendedor_email)
            qtd = len(leads_col)

            # Cabeçalho da coluna
            st.markdown(
                f"""
                <div class="kanban-column-header">
                    <div class="kanban-column-title">{status}</div>
                    <div class="kanban-column-badge">{qtd}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if not leads_col:
                st.caption("Nenhum lead aqui ainda.")
            else:
                for lead in leads_col:
                    nome = lead.get("nome", "Sem nome")
                    email = lead.get("email", "")
                    telefone = lead.get("telefone", "")
                    valor = lead.get("valor_previsto")
                    vendedor = lead.get("vendedor_email", "")

                    # Formatação do valor
                    valor_str = ""
                    if valor not in (None, ""):
                        try:
                            valor_float = float(valor)
                            valor_str = (
                                "R$ "
                                + f"{valor_float:,.2f}"
                                .replace(",", "X")
                                .replace(".", ",")
                                .replace("X", ".")
                            )
                        except Exception:
                            valor_str = str(valor)

                    # Chips opcionais
                    if valor_str:
                        valor_html = f"<span class='kanban-chip'>💰 {valor_str}</span>"
                    else:
                        valor_html = ""

                    if role == "admin" and vendedor:
                        vendedor_html = (
                            f"<span class='kanban-chip-small'>👤 {vendedor}</span>"
                        )
                    else:
                        vendedor_html = ""

                    # Classe extra para leads perdidos
                    card_class = "kanban-card"
                    if status == "perdido":
                        card_class += " kanban-card-lost"

                    # Card visual
                    card_html = f"""
                        <div class="{card_class}">
                            <div class="kanban-card-header">
                                <div class="kanban-card-title">{nome}</div>
                            </div>
                            <div class="kanban-card-sub">{email or ""}</div>
                            <div class="kanban-card-sub">{telefone or ""}</div>
                            <div class="kanban-card-meta">
                                <div>{valor_html}</div>
                                <div>{vendedor_html}</div>
                            </div>
                        </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

                    # Linha de botões icon-only, coladinhos no card
                    status_anterior = _status_anterior(status)
                    proximo = _proximo_status(status)

                    col_prev, col_perdido, col_next, col_details = st.columns(4)

                    # Voltar uma etapa
                    if status_anterior:
                        with col_prev:
                            if st.button(
                                "⬅",
                                key=f"back_{lead['id']}_{status}",
                                help=f"Voltar para {status_anterior}",
                            ):
                                ok, msg = update_lead_status(
                                    lead["id"], status_anterior
                                )
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)

                    # Marcar como perdido (se ainda não estiver perdido)
                    if status != "perdido":
                        with col_perdido:
                            if st.button(
                                "❌",
                                key=f"lost_{lead['id']}_{status}",
                                help="Marcar lead como perdido",
                            ):
                                ok, msg = update_lead_status(lead["id"], "perdido")
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)

                    # Avançar uma etapa
                    if proximo:
                        with col_next:
                            if st.button(
                                "➡",
                                key=f"next_{lead['id']}_{status}",
                                help=f"Avançar para {proximo}",
                            ):
                                ok, msg = update_lead_status(lead["id"], proximo)
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)

                    # Detalhes do lead (ícone ⋯) -> abre modal nativo
                    with col_details:
                        if st.button(
                            "⋯",
                            key=f"details_{lead['id']}_{status}",
                            help="Ver/editar detalhes do lead",
                        ):
                            st.session_state.current_lead = lead
                            show_lead_details_dialog()

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
