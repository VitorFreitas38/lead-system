import streamlit as st
from services.leads_service import create_lead


def render_lead_create_page(user: dict):
    usuario_email = user.get("email", "")

    # Defaults (só inicializa uma vez)
    st.session_state.setdefault("lead_nome", "")
    st.session_state.setdefault("lead_email", "")
    st.session_state.setdefault("lead_telefone", "")
    st.session_state.setdefault("lead_origem", "")
    st.session_state.setdefault("lead_valor_previsto", 0.0)
    st.session_state.setdefault("lead_vendedor_email", usuario_email)
    st.session_state.setdefault("lead_observacoes", "")

    st.markdown('<div class="crm-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">➕ Cadastrar novo lead</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        "Preencha os dados do lead e escolha para qual vendedor ele será direcionado."
        "</div>",
        unsafe_allow_html=True,
    )

    # ✅ Sem clear_on_submit (pra não limpar em erro)
    with st.form("form_novo_lead_page"):
        col1, col2, col3 = st.columns(3)

        with col1:
            nome = st.text_input("Nome do lead", key="lead_nome")
            email = st.text_input("Email", key="lead_email")
        with col2:
            telefone = st.text_input("Telefone / WhatsApp", key="lead_telefone")
            origem = st.text_input("Origem (campanha, indicação, etc.)", key="lead_origem")
        with col3:
            valor_previsto = st.number_input(
                "Valor previsto (R$)", min_value=0.0, step=100.0, key="lead_valor_previsto"
            )

        st.markdown("### Vendedor responsável")
        vendedor_email = st.text_input(
            "Email do vendedor",
            key="lead_vendedor_email",
            help="Digite o email do vendedor que ficará responsável por este lead.",
        )

        observacoes = st.text_area("Observações", height=80, key="lead_observacoes")

        submitted = st.form_submit_button("Cadastrar lead")

    # ✅ Processa fora do form (padrão bom do Streamlit)
    if submitted:
        if not nome:
            st.error("Nome é obrigatório.")
        elif not vendedor_email:
            st.error("Informe o email do vendedor responsável.")
        else:
            ok, msg = create_lead(
                nome=nome,
                email=email,
                telefone=telefone,
                vendedor_email=vendedor_email,
                valor_previsto=valor_previsto,
                origem=origem,
                observacoes=observacoes,
            )
            if ok:
                st.success(msg)

                # ✅ Limpa SOMENTE no sucesso
                st.session_state["lead_nome"] = ""
                st.session_state["lead_email"] = ""
                st.session_state["lead_telefone"] = ""
                st.session_state["lead_origem"] = ""
                st.session_state["lead_valor_previsto"] = 0.0
                st.session_state["lead_observacoes"] = ""

                # Mantém vendedor como o usuário logado (pode mudar se quiser)
                st.session_state["lead_vendedor_email"] = usuario_email

                st.rerun()
            else:
                st.error(msg)

    st.markdown("</div>", unsafe_allow_html=True)
