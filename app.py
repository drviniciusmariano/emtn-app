import streamlit as st
import pandas as pd
import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="EMTN - Hospital Municipal de Paulínia",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. BANCO DE DADOS DE USUÁRIOS (Crie aqui os logins da equipe)
# Dica: O "Nome Completo" será usado automaticamente como o Avaliador no formulário
CONTA_USUARIOS = {
    "vinicius.mariano": {"senha": "casa0904", "nome_completo": "Dr. Vinícius Mariano"},
    "priscila.nutri": {"senha": "nutri1234", "nome_completo": "Nutricionista EMTN"},
    "resilda.enfermeira": {"senha": "enf1234", "nome_completo": "Enfermeira EMTN"},
    "julia.lopes": {"senha": "julia1234", "nome completo": "Dra. Julia Lopes"},
    "amanda.snd": {"senha": "snd1234", "nome completo": "Nutricionista SND"},
    "carol.geriatria": {"senha": "geriatria1234", "nome completo": "Nutricionista Geriatria"},
    "matheus.soberana": {"senha": "matheus1234", "nome completo": "Nutricionista - Soberana"},
    "rafael.soberana": {"senha": "rafael1234", "nome completo": "Nutricionista - Soberana"},
    "caren.soberana": {"senha": "caren1234", "nome completo": "Nutricionista - Soberana"},
    "vanessa.soberana": {"senha": "vanessa1234", "nome completo": "Nutricionista - Soberana"}
    
# Controle de sessão para autenticação
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None
if 'nome_avaliador' not in st.session_state:
    st.session_state.nome_avaliador = ""

# Função de validação de login
def efetuar_login():
    u_input = st.session_state.usuario_input.strip().lower()
    s_input = st.session_state.senha_input
    
    if u_input in CONTA_USUARIOS and CONTA_USUARIOS[u_input]["senha"] == s_input:
        st.session_state.autenticado = True
        st.session_state.usuario_logado = u_input
        st.session_state.nome_avaliador = CONTA_USUARIOS[u_input]["nome_completo"]
        st.success("Acesso autorizado!")
    else:
        st.error("Usuário ou senha incorretos para a equipe EMTN.")

# Interface da Tela de Login
if not st.session_state.autenticado:
    st.markdown("""
        <style>
            .stApp { background-color: #FCFBF7; }
            .login-box {
                background-color: white; padding: 40px; border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 5px solid #4D6452;
                max-width: 500px; margin: 80px auto;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; color: #4D6452;'>🩺 EMTN - Hospital Municipal de Paulínia</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #D97E3A; font-weight: bold;'>Controle de Acesso Individual</p>", unsafe_allow_html=True)
    
    with st.form("Visual_Login"):
        st.text_input("Usuário (Ex: nome.sobrenome)", key="usuario_input")
        st.text_input("Senha Individual", type="password", key="senha_input")
        st.form_submit_button("Entrar no Sistema", on_click=efetuar_login)
        
    st.stop() # Trava o aplicativo aqui caso não esteja logado

# -------------------------------------------------------------------------
# APÓS O LOGIN: SEGUMENTO DO APLICATIVO COM IDENTIDADE VISUAL E REGRAS
# -------------------------------------------------------------------------

# Injeção de CSS para customização das cores do Logotipo (Verde e Terracota)
st.markdown("""
    <style>
        .stApp { background-color: #FCFBF7; color: #334155; }
        h1, h2, h3 { color: #4D6452 !important; font-family: 'Montserrat', sans-serif; }
        div.stButton > button:first-child {
            background-color: #4D6452; color: white; border-radius: 8px;
            border: none; padding: 10px 24px; font-weight: bold; width: 100%;
        }
        div.stButton > button:first-child:hover { background-color: #D97E3A; color: white; }
        .metric-card {
            background-color: white; padding: 20px; border-radius: 12px;
            border-left: 5px solid #D97E3A; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# BANCO DE DADOS EM MEMÓRIA
if 'banco_pacientes' not in st.session_state:
    st.session_state.banco_pacientes = pd.DataFrame([
        {
            "Avaliador": "Dr. Vinícius Mariano", "Data Admissão": "2026-05-10", "Nome": "Carlos Silva", 
            "Sexo": "Masculino", "Setor": "UTI", "Leito": "102-A", "Faixa Etária": "19-59", 
            "Via Alimentação": "Sonda Nasoenteral", "Risco": "Alto", "Adequacao_Calorica": 88.0
        },
        {
            "Avaliador": "Dra. Juliana Costa", "Data Admissão": "2026-05-14", "Nome": "Maria Oliveira", 
            "Sexo": "Feminino", "Setor": "UTI", "Leito": "105-B", "Faixa Etária": "> ou = 60", 
            "Via Alimentação": "Parenteral central", "Risco": "Alto", "Adequacao_Calorica": 92.0
        },
        {
            "Avaliador": "Dr. Vinícius Mariano", "Data Admissão": "2026-05-15", "Nome": "Pedro Rocha", 
            "Sexo": "Masculino", "Setor": "Clinica Médica", "Leito": "204", "Faixa Etária": "19-59", 
            "Via Alimentação": "Oral", "Risco": "Médio", "Adequacao_Calorica": 75.0
        }
    ])

# BARRA LATERAL (Navegação, Usuário Logado e Logout)
st.sidebar.markdown(
    f"<h3 style='text-align: center; color: #4D6452; margin-bottom: 0;'>EMTN HMP</h3>"
    f"<p style='text-align: center; color: #334155; font-size: 14px; margin-top: 5px;'>👤 {st.session_state.nome_avaliador}</p>", 
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
menu = st.sidebar.radio("Menu do Plantão:", ["📊 Indicadores Gerais", "📋 Passagem por Unidade", "📝 Novo Protocolo"])
st.sidebar.markdown("---")

# Botão de Logout
if st.sidebar.button("🔒 Sair do Sistema"):
    st.session_state.autenticado = False
    st.session_state.usuario_logado = None
    st.session_state.nome_avaliador = ""
    st.rerun()

# --- SEÇÃO 1: DASHBOARD ---
if menu == "📊 Indicadores Gerais":
    st.title("📊 Indicadores de Qualidade Nutricional")
    df = st.session_state.banco_pacientes
    
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.markdown(f"<div class='metric-card'><h4>Total sob Cuidados</h4><h1>{len(df)}</h1></div>", unsafe_allow_html=True)
    with kpi2:
        alto_risco = len(df[df['Risco'] == 'Alto'])
        st.markdown(f"<div class='metric-card' style='border-left-color: #D97E3A;'><h4>Alto Risco Nutricional</h4><h1>{alto_risco}</h1></div>", unsafe_allow_html=True)
    with kpi3:
        media_adequacao = df['Adequacao_Calorica'].mean() if not df.empty else 0
        st.markdown(f"<div class='metric-card' style='border-left-color: #4D6452;'><h4>Média de Adequação</h4><h1>{media_adequacao:.1f}%</h1></div>", unsafe_allow_html=True)
        
    st.markdown("### Adequação Calórica por Setor do Hospital")
    if not df.empty:
        chart_data = df.groupby('Setor')['Adequacao_Calorica'].mean().reset_index()
        st.bar_chart(data=chart_data, x='Setor', y='Adequacao_Calorica', color="#4D6452")

# --- SEÇÃO 2: LISTAGEM NOMINAL POR UNIDADE ---
elif menu == "📋 Passagem por Unidade":
    st.title("📋 Listagem Nominativa para Passagem de Plantão")
    df = st.session_state.banco_pacientes
    
    setores_oficiais = ["Pronto Socorro Adulto", "Pronto Socorro Infantil", "Clinica Médica", "Clínica Cirúrgica", "Ginecologia e Obstetrícia", "Pediatria", "UTI"]
    abas = st.tabs(setores_oficiais)
    
    for i, setor in enumerate(setores_oficiais):
        with abas[i]:
            df_filtrado = df[df['Setor'] == setor]
            st.subheader(f"Ala: {setor} ({len(df_filtrado)} ativos)")
            if not df_filtrado.empty:
                st.dataframe(
                    df_filtrado[["Nome", "Leito", "Sexo", "Faixa Etária", "Via Alimentação", "Risco", "Avaliador"]],
                    use_container_width=True, hide_index=True
                )
            else:
                st.info(f"Sem pacientes da EMTN mapeados nesta ala no momento.")

# --- SEÇÃO 3: FORMULÁRIO COM TRIAGENS DINÂMICAS ---
elif menu == "📝 Novo Protocolo":
    st.title("📝 Protocolo Assistencial Multidisciplinar")
    
    with st.form("form_registro"):
        st.markdown("### 1. Dados Iniciais do Paciente")
        col1, col2 = st.columns(2)
        with col1:
            # Trava o campo de avaliador com o nome de quem fez o login!
            st.text_input("Avaliador Responsável", value=st.session_state.nome_avaliador, disabled=True)
            nome_paciente = st.text_input("Nome Completo do Paciente *")
            sexo = st.selectbox("Sexo Biológico *", ["Masculino", "Feminino"])
        with col2:
            data_admissao = st.date_input("Data de Admissão Hospitalar", datetime.date.today())
            setor = st.selectbox("Setor / Unidade de Internação *", ["Pronto Socorro Adulto", "Pronto Socorro Infantil", "Clinica Médica", "Clínica Cirúrgica", "Ginecologia e Obstetrícia", "Pediatria", "UTI"])
            leito = st.text_input("Leito/Box *")
            
        st.markdown("---")
        st.markdown("### 2. Triagem de Risco por Faixa Etária")
        faixa_etaria = st.selectbox("Classificação Etária *", ["< ou = 18 (Pediatria)", "19-59 (Adulto)", "> ou = 60 (Idoso)"])
        
        # LÓGICA DE TRIAGEM CONDICIONAL DO FORMULÁRIO
        if "< ou = 18" in faixa_etaria:
            st.markdown("#### 🧬 Protocolo STRONG KIDS (Triagem Pediátrica)")
            sk1 = st.checkbox("A criança apresenta desnutrição clínica evidente ou perda ponderal severa? (+1)")
            sk2 = st.checkbox("Possui patologia de alto risco associada (Ex: Cardiopatia, Nefropatia, Oncologia)? (+2)")
            sk3 = st.checkbox("Houve diminuição drástica da ingestão de alimentos ou vômitos/diarreia recentes? (+1)")
            score_final = sum([sk1, sk2*2, sk3])
            risco_final = "Baixo" if score_final == 0 else "Médio" if score_final <= 2 else "Alto"
            st.warning(f"Score Obtido: {score_final} ponto(s) | Classificação: Risco {risco_final}")
            
        elif "19-59" in faixa_etaria:
            st.markdown("#### 🫁 Protocolo NRS 2002 (Triagem Adulto)")
            nrs1 = st.checkbox("Índice de Massa Corporal (IMC) inferior a 20,5 kg/m²?")
            nrs2 = st.checkbox("Perda de peso involuntária observada nos últimos 3 meses?")
            nrs3 = st.checkbox("Redução de ingesta calórica acentuada na última semana?")
            score_final = sum([nrs1, nrs2, nrs3])
            risco_final = "Alto" if score_final >= 2 else "Médio" if score_final == 1 else "Baixo"
            st.warning(f"Classificação de Risco Base: Risco {risco_final}")
            
        else:
            st.markdown("#### 👴 Protocolo MNA® (Mini Nutritional Assessment - Idoso)")
            mna1 = st.selectbox("Houve perda de apetite ou problemas digestivos severos no trimestre?", ["Não", "Moderadamento", "Severamente"])
            mna2 = st.checkbox("Paciente apresenta quadro clínico de estresse psicológico agudo?")
            risco_final = "Alto" if mna2 or "Severamente" in mna1 else "Médio"
            st.warning(f"Classificação de Risco Base: Risco {risco_final}")

        st.markdown("---")
        st.markdown("### 3. Vias e Plano de Cuidado")
        via_alimentacao = st.multiselect("Vias de Alimentação Ativas *", ["Oral", "Sonda Nasoenteral", "Gastrostomia", "Jejunostomia", "Parenteral periférica", "Parenteral central", "Jejum"])
        adequacao_estimada = st.slider("Meta de Adequação Calórico-Proteica Programada (%)", 0, 100, 85)
        
        salvar = st.form_submit_button("Salvar e Enviar para a Passagem de Plantão")
        
        if salvar:
            if not nome_paciente or not leito or not via_alimentacao:
                st.error("Por favor, preencha todos os campos obrigatórios (*).")
            else:
                novo_registro = {
                    "Avaliador": st.session_state.nome_avaliador,
                    "Data Admissão": str(data_admissao),
                    "Nome": nome_paciente,
                    "Sexo": sexo,
                    "Setor": setor,
                    "Leito": leito,
                    "Faixa Etária": faixa_etaria.split(" ")[0],
                    "Via Alimentação": ", ".join(via_alimentacao),
                    "Risco": risco_final,
                    "Adequacao_Calorica": float(adequacao_estimada)
                }
                st.session_state.banco_pacientes = pd.concat([st.session_state.banco_pacientes, pd.DataFrame([novo_registro])], ignore_index=True)
                st.success(f"Prontuário de {nome_paciente} salvo e integrado à ala {setor}!")