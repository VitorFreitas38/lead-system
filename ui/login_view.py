# ui/login_view.py

import streamlit as st
from services.auth_service import check_login, create_user


# ================== AÇÕES DE LOGIN / CADASTRO ==================


def _do_login(email: str, password: str):
    """Tenta logar o usuário usando o auth_service."""
    if not email or not password:
        st.error("Informe email e senha para entrar.")
        return

    # check_login retorna (ok, result)
    ok, result = check_login(email, password)

    if not ok:
        # result deve ser um dict com {"error": "..."} no seu código antigo
        msg = ""
        if isinstance(result, dict):
            msg = result.get("error") or result.get("message") or ""
        else:
            msg = str(result)
        st.error(f"Usuário ou senha inválidos. {msg}")
        return

    # Aqui result é o dict com os dados do usuário (como antes)
    st.session_state["logged"] = True
    st.session_state["user"] = result

    st.success("Login realizado com sucesso! Redirecionando…")
    st.rerun()


def _do_register(nome: str, email: str, password: str, password2: str):
    """Criação de novo usuário (simples)."""

    if not nome or not email or not password:
        st.error("Preencha nome, email e senha para criar o usuário.")
        return

    if password != password2:
        st.error("As senhas não coincidem.")
        return

    # create_user retorna (ok, msg) no seu código antigo
    ok, msg = create_user(email, password, nome=nome)

    if not ok:
        st.error(f"Não foi possível criar o usuário. {msg}")
        return

    st.success("Usuário criado com sucesso! Você já pode fazer login.")


# ================== ESTILO GLOBAL ==================


def _inject_global_styles():
    st.markdown(
        """
        <style>
        /* Fundo geral mais clean */
        .stApp {
            background: radial-gradient(circle at top left, #e0f2fe 0, #eff6ff 35%, #f9fafb 70%);
        }

        /* Remover um pouco do padding padrão para centralizar melhor */
        .main > div {
            padding-top: 5vh;
            padding-bottom: 5vh;
        }

        /* Card de login */

        .login-title {
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 0.35rem;
        }

        .login-subtitle {
            font-size: 0.85rem;
            color: #6b7280;
            margin-bottom: 1.2rem;
        }

        .product-title {
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            margin-bottom: 0.5rem;
        }

        .product-subtitle {
            font-size: 0.95rem;
            color: #4b5563;
            max-width: 520px;
        }

        .product-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            border-radius: 999px;
            background: rgba(8, 47, 73, 0.06);
            padding: 0.30rem 0.75rem;
            font-size: 0.78rem;
            color: #0f172a;
            margin-bottom: 0.75rem;
        }

        .product-metric {
            font-size: 0.8rem;
            color: #6b7280;
        }

        .product-metric strong {
            color: #111827;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ================== TELA DE LOGIN ==================


def render_login_page():
    # Garante que não tem usuário antigo em sessão
    st.session_state.pop("user", None)
    st.session_state.pop("logged", None)

    _inject_global_styles()

    # Layout em duas colunas: esquerda branding, direita card de login
    col_left, col_right = st.columns([3, 2], gap="large")

    # ---------- Coluna esquerda: branding / descrição ----------
    with col_left:
        st.markdown(
            """
            <div class="product-chip">
                <span style="font-size:0.9rem;">🔒</span>
                <span>Ambiente seguro de gestão de leads</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="product-title">
                Lead System – Gestão de Leads
            </div>
            <div class="product-subtitle">
                Controle o funil de vendas da sua operação com uma visão simples,
                focada em resultados e pensada para equipes comerciais enxutas.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                """
                <div class="product-metric">
                    <strong>Pipeline visual</strong><br/>
                    Arraste os leads pelas etapas do funil.
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                """
                <div class="product-metric">
                    <strong>Dashboard por usuário</strong><br/>
                    KPIs separados para vendedores e admin.
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ---------- Coluna direita: card de autenticação ----------
    with col_right:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="login-title">Acesso ao painel</div>
            <div class="login-subtitle">
                Entre com suas credenciais ou cadastre um novo usuário vendedor.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Switch entre Entrar / Criar conta
        mode = st.radio(
            "Escolha uma opção",
            options=("Entrar", "Criar conta"),
            horizontal=True,
            label_visibility="collapsed",
        )

        if mode == "Entrar":
            with st.form("login_form"):
                email = st.text_input(
                    "Email",
                    key="login_email",
                    placeholder="seuemail@empresa.com",
                )
                password = st.text_input(
                    "Senha",
                    type="password",
                    key="login_password",
                )
                lembrar = st.checkbox("Continuar conectado", value=False)
                st.caption("")  # só para dar respiro visual

                submitted = st.form_submit_button("Entrar", width="stretch")
                if submitted:
                    # 'lembrar' pode ser usado futuramente (cookies / token)
                    _do_login(email.strip(), password.strip())

        else:  # Criar conta
            with st.form("register_form"):
                nome = st.text_input("Nome completo", key="reg_nome")
                email = st.text_input(
                    "Email",
                    key="reg_email",
                    placeholder="vendedor@empresa.com",
                )
                col1, col2 = st.columns(2)
                with col1:
                    password = st.text_input(
                        "Senha",
                        type="password",
                        key="reg_password",
                    )
                with col2:
                    password2 = st.text_input(
                        "Confirmar senha",
                        type="password",
                        key="reg_password2",
                    )

                criar = st.form_submit_button("Criar usuário", width="stretch")
                if criar:
                    _do_register(
                        nome.strip(),
                        email.strip(),
                        password.strip(),
                        password2.strip(),
                    )

        st.markdown("</div>", unsafe_allow_html=True)
