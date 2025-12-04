import streamlit as st
from services.leads_service import create_lead


def render_lead_create_page(user: dict):
    usuario_email = user.get("email", "")

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

    with st.form("form_novo_lead_page"):
        col1, col2, col3 = st.columns(3)

        with col1:
            nome = st.text_input("Nome do lead")
            email = st.text_input("Email")
        with col2:
            telefone = st.text_input("Telefone / WhatsApp")
            origem = st.text_input("Origem (campanha, indicação, etc.)")
        with col3:
            valor_previsto = st.number_input(
                "Valor previsto (R$)", min_value=0.0, step=100.0
            )

        st.markdown("### Vendedor responsável")
        vendedor_email = st.text_input(
            "Email do vendedor",
            value=usuario_email,
            help="Digite o email do vendedor que ficará responsável por este lead.",
        )

        observacoes = st.text_area("Observações", height=80)

        submitted = st.form_submit_button("Cadastrar lead")
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
                    st.rerun()
                else:
                    st.error(msg)

    st.markdown("</div>", unsafe_allow_html=True)
