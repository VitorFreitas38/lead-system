import streamlit as st
from services.auth_service import check_login, create_user


def render_login_page():
    # Card central para login
    st.markdown('<div class="crm-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">🔐 Login / Cadastro</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        "Acesse o painel de leads da AgroSP Drones ou crie uma nova conta para começar."
        "</div>",
        unsafe_allow_html=True,
    )

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
                st.error(f"❌ {result.get('error')}")

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
                st.error(
                    "❌ Coloque uma senha com pelo menos 4 caracteres (para teste)."
                )
            else:
                ok, msg = create_user(email_cad, senha_cad, nome=nome_cad)
                if ok:
                    st.success(
                        "✅ Usuário criado! Agora faça login na aba 'Já tenho conta'."
                    )
                else:
                    st.error(f"❌ {msg}")

    st.markdown("</div>", unsafe_allow_html=True)
