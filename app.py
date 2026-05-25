import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime, date

# ==================================================================================================
# CONFIGURAÇÕES DA PÁGINA
# ==================================================================================================
st.set_page_config(page_title="EMTN - Hospital Municipal de Paulínia", page_icon="🏥", layout="wide")

# ==================================================================================================
# BANCO DE DADOS — SQLite (persiste após fechar o app)
# ==================================================================================================
DB_NAME = "emtn_hmp.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pacientes_ativos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Avaliador TEXT, Data_Admissao TEXT, Nome TEXT UNIQUE, Sexo TEXT,
        Setor TEXT, Leito TEXT, Data_Triagem TEXT, Via_Alimentacao TEXT,
        Momento TEXT, Diagnostico TEXT, Comorbidades TEXT,
        Peso_Habitual REAL, Altura_Referida REAL, IMC_Calculado REAL, Classe_IMC TEXT,
        Data_Nascimento TEXT, Idade_Anos INTEGER, Idade_Meses INTEGER, Faixa_Etaria TEXT,
        Escore_Triagem INTEGER, Risco TEXT, Intervencao_Obrigatoria TEXT,
        Nivel_Assistencia TEXT, Via_Proposta TEXT, Dieta_Prescrita TEXT, Conduta TEXT,
        Adequacao_Calorica REAL DEFAULT 100.0, Parecer_IA TEXT,
        Notas_Plantao TEXT, Ultima_Reavaliacao TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS historico_alta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Avaliador TEXT, Data_Admissao TEXT, Nome TEXT, Sexo TEXT,
        Setor TEXT, Leito TEXT, Data_Triagem TEXT, Via_Alimentacao TEXT,
        Momento TEXT, Diagnostico TEXT, Comorbidades TEXT,
        Peso_Habitual REAL, Altura_Referida REAL, IMC_Calculado REAL, Classe_IMC TEXT,
        Data_Nascimento TEXT, Idade_Anos INTEGER, Idade_Meses INTEGER, Faixa_Etaria TEXT,
        Escore_Triagem INTEGER, Risco TEXT, Intervencao_Obrigatoria TEXT,
        Nivel_Assistencia TEXT, Via_Proposta TEXT, Dieta_Prescrita TEXT, Conduta TEXT,
        Adequacao_Calorica REAL, Parecer_IA TEXT,
        Notas_Plantao TEXT, Ultima_Reavaliacao TEXT, Data_Alta TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# Mapa de nomes do formulário (com espaços/acentos) para colunas do banco (com underscore)
MAPA_COLUNAS = {
    "Avaliador": "Avaliador", "Data Admissão": "Data_Admissao", "Nome": "Nome",
    "Sexo": "Sexo", "Setor": "Setor", "Leito": "Leito",
    "Data Triagem": "Data_Triagem", "Via Alimentação": "Via_Alimentacao",
    "Momento": "Momento", "Diagnóstico": "Diagnostico", "Comorbidades": "Comorbidades",
    "Peso Habitual": "Peso_Habitual", "Altura Referida": "Altura_Referida",
    "IMC Calculado": "IMC_Calculado", "Classe IMC": "Classe_IMC",
    "Data Nascimento": "Data_Nascimento", "Idade Anos": "Idade_Anos",
    "Idade Meses": "Idade_Meses", "Faixa Etária": "Faixa_Etaria",
    "Escore Triagem": "Escore_Triagem", "Risco": "Risco",
    "Intervencao_Obrigatoria": "Intervencao_Obrigatoria",
    "Nível Assistência": "Nivel_Assistencia", "Via Proposta": "Via_Proposta",
    "Dieta Prescrita": "Dieta_Prescrita", "Conduta": "Conduta",
    "Adequacao_Calorica": "Adequacao_Calorica", "Parecer_IA": "Parecer_IA",
    "Notas_Plantao": "Notas_Plantao", "Ultima_Reavaliacao": "Ultima_Reavaliacao",
}

def load_pacientes():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM pacientes_ativos", conn)
    conn.close()
    return df

def load_historico():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM historico_alta", conn)
    conn.close()
    return df

def salvar_paciente(dados: dict):
    dados_db = {}
    for chave, valor in dados.items():
        col = MAPA_COLUNAS.get(chave, chave)
        dados_db[col] = valor
    # Remove colunas que não existem na tabela
    colunas_validas = [
        "Avaliador","Data_Admissao","Nome","Sexo","Setor","Leito","Data_Triagem",
        "Via_Alimentacao","Momento","Diagnostico","Comorbidades","Peso_Habitual",
        "Altura_Referida","IMC_Calculado","Classe_IMC","Data_Nascimento","Idade_Anos",
        "Idade_Meses","Faixa_Etaria","Escore_Triagem","Risco","Intervencao_Obrigatoria",
        "Nivel_Assistencia","Via_Proposta","Dieta_Prescrita","Conduta","Adequacao_Calorica",
        "Parecer_IA","Notas_Plantao","Ultima_Reavaliacao"
    ]
    dados_db = {k: v for k, v in dados_db.items() if k in colunas_validas}
    conn = get_connection()
    c = conn.cursor()
    cols = ", ".join(dados_db.keys())
    placeholders = ", ".join(["?"] * len(dados_db))
    c.execute(f"INSERT OR REPLACE INTO pacientes_ativos ({cols}) VALUES ({placeholders})", tuple(dados_db.values()))
    conn.commit()
    conn.close()

def atualizar_paciente(nome: str, campo_db: str, valor):
    conn = get_connection()
    c = conn.cursor()
    c.execute(f"UPDATE pacientes_ativos SET {campo_db} = ? WHERE Nome = ?", (valor, nome))
    conn.commit()
    conn.close()

def registrar_alta(nome: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM pacientes_ativos WHERE Nome = ?", (nome,))
    row = c.fetchone()
    if row:
        colunas = [d[0] for d in c.description if d[0] != "id"]
        valores = [row[col] for col in colunas] + [date.today().strftime("%Y-%m-%d")]
        cols_str = ", ".join(colunas) + ", Data_Alta"
        placeholders = ", ".join(["?"] * len(valores))
        c.execute(f"INSERT INTO historico_alta ({cols_str}) VALUES ({placeholders})", valores)
        c.execute("DELETE FROM pacientes_ativos WHERE Nome = ?", (nome,))
    conn.commit()
    conn.close()

# ==================================================================================================
# ESTILIZAÇÃO
# ==================================================================================================
st.markdown("""
    <style>
        .main { background-color: #FAFAFA; }
        .sidebar .sidebar-content { background-color: #E2E8F0; }
        h1, h2, h3 { color: #4D6452; font-family: 'Helvetica Neue', Arial, sans-serif; }
        .metric-card {
            background-color: #ffffff; padding: 15px; border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 5px solid #4D6452; margin-bottom: 10px;
        }
        .stButton>button { background-color: #4D6452; color: white; border-radius: 6px; }
        .flag-box { padding: 15px; border-radius: 8px; margin-top: 10px; margin-bottom: 10px; font-weight: 500; }
        .ai-box {
            background-color: #F0F4F8; border-left: 6px solid #1E3A8A;
            color: #1E3A8A; padding: 15px; border-radius: 8px; margin-top: 15px;
        }
        @media print {
            body * { visibility: hidden; }
            .secao-impressao, .secao-impressao * { visibility: visible; }
            .secao-impressao {
                position: absolute; left: 0; top: 0; width: 100%;
                font-size: 12pt; color: #000; background: white;
            }
            .no-print { display: none !important; }
        }
    </style>
""", unsafe_allow_html=True)

# ==================================================================================================
# AUTENTICAÇÃO COM LOGIN PERSISTENTE (sobrevive ao F5 via query param)
# ==================================================================================================
CONTA_USUARIOS = {
    "vinicius.mariano": {"senha": "casa0904", "nome_completo": "Dr. Vinícius Mariano"},
    "priscila.nutri":   {"senha": "nutri1234", "nome_completo": "Nutri. Priscila"},
    "resilda.enfermeira": {"senha": "enf1234", "nome_completo": "Enf. Resilda"},
    "julia.lopes":      {"senha": "julia1234", "nome_completo": "Júlia Lopes"},
    "amanda.snd":       {"senha": "snd1234",   "nome_completo": "Amanda SND"},
    "carol.geriatria":  {"senha": "geriatria1234", "nome_completo": "Carol Geriatria"},
    "matheus.soberana": {"senha": "matheus1234", "nome_completo": "Matheus Soberana"},
    "rafael.soberana":  {"senha": "rafael1234", "nome_completo": "Rafael Soberana"},
    "caren.soberana":   {"senha": "caren1234",  "nome_completo": "Caren Soberana"},
    "vanessa.soberana": {"senha": "vanessa1234","nome_completo": "Vanessa Soberana"},
}

# Inicializa flags de sessão
for _k, _v in [("autenticado", False), ("usuario_logado", ""), ("nome_avaliador", "")]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# Tenta restaurar sessão via query param (sobrevive ao F5 dentro da mesma aba)
if not st.session_state.autenticado:
    _u = st.query_params.get("u", "")
    if _u and _u in CONTA_USUARIOS:
        st.session_state.autenticado = True
        st.session_state.usuario_logado = _u
        st.session_state.nome_avaliador = CONTA_USUARIOS[_u]["nome_completo"]

# Tela de login
if not st.session_state.autenticado:
    st.title("🏥 Sistema de Gestão de Cuidado Nutricional - EMTN HMP")
    st.subheader("Login Interoperável")
    _user = st.text_input("Usuário de Acesso:")
    _pwd  = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if _user in CONTA_USUARIOS and CONTA_USUARIOS[_user]["senha"] == _pwd:
            st.session_state.autenticado    = True
            st.session_state.usuario_logado = _user
            st.session_state.nome_avaliador = CONTA_USUARIOS[_user]["nome_completo"]
            st.query_params["u"] = _user   # persiste na URL
            st.rerun()
        else:
            st.error("Credenciais incorretas.")
    st.stop()

# ==================================================================================================
# BARRA LATERAL — navegação + botão Sair
# ==================================================================================================
st.sidebar.markdown(
    f"<h3 style='text-align:center;color:#4D6452;'>EMTN HMP</h3>"
    f"<p style='text-align:center;'>👤 {st.session_state.nome_avaliador}</p>",
    unsafe_allow_html=True
)
st.sidebar.markdown("---")

_opcoes_menu = [
    "🏠 Início",
    "Módulo 1: Triagem e Admissão",
    "Módulo 2: Prescrição e Evolução",
    "Módulo 3: Avaliação EMTN",
    "Módulo 4: Passagem de Plantão",
    "Módulo 5: Indicadores",
]
# Após concluir uma avaliação ou evolução, o app volta para o módulo correto automaticamente
_default_menu = st.session_state.get("menu_ativo", "🏠 Início")
_idx = _opcoes_menu.index(_default_menu) if _default_menu in _opcoes_menu else 0
menu = st.sidebar.radio("Módulos do Sistema:", _opcoes_menu, index=_idx)
st.session_state.menu_ativo = menu  # sincroniza seleção manual

st.sidebar.markdown("---")

# Botão Sair — limpa tudo e volta para o login
if st.sidebar.button("🔒 Sair do Sistema"):
    for _chave in ["autenticado","usuario_logado","nome_avaliador","passo_atual",
                   "dados_triagem_base","p_ativo","menu_ativo"]:
        st.session_state.pop(_chave, None)
    st.session_state.autenticado = False
    st.query_params.clear()
    st.rerun()

# ==================================================================================================
# FUNÇÕES CLÍNICAS AUXILIARES
# ==================================================================================================
def calcular_idade_detalhada(data_nasc):
    if isinstance(data_nasc, str):
        try:    data_nasc = datetime.strptime(data_nasc, "%Y-%m-%d").date()
        except: data_nasc = datetime.strptime(data_nasc, "%d/%m/%Y").date()
    hoje  = date.today()
    anos  = hoje.year  - data_nasc.year
    meses = hoje.month - data_nasc.month
    if hoje.day < data_nasc.day: meses -= 1
    if meses < 0: anos -= 1; meses += 12
    return anos, meses

def classificar_imc_adulto(imc):
    if imc < 18.5:              return "Baixo Peso"
    elif 18.5 <= imc < 25.0:   return "Eutrofia"
    elif 25.0 <= imc < 30.0:   return "Sobrepeso"
    else:                       return "Obesidade"

def analisar_dados_com_ia(dados):
    idade        = dados.get("Idade Anos", 30)
    comorbidades = dados.get("Comorbidades", "")
    escore       = dados.get("Escore Triagem", 0)
    risco        = dados.get("Risco", "Baixo")
    via_atual    = dados.get("Via Alimentação", "Oral")
    faixa_etaria = dados.get("Faixa Etária", "19-59")
    insights = []
    if "Etilismo" in comorbidades or "Acamado(a)" in comorbidades \
            or (faixa_etaria == "19-59" and escore >= 3) \
            or (faixa_etaria == ">= 60" and escore < 12):
        insights.append("🛑 **Risco Clínico Intermediado (Síndrome de Realimentação):** Paciente com critérios de vulnerabilidade metabólica aguda. Recomenda-se acompanhamento rigoroso pela EMTN de eletrólitos extracelulares (Fósforo, Magnésio, Potássio) nas primeiras 72h e progressão escalonada obrigatória do aporte calórico total diário.")
    if (faixa_etaria == ">= 60" or idade >= 60) and \
            (risco == "Risco de Desnutrição" or risco == "Desnutrido" or "risco" in risco.lower()):
        insights.append("👴 **Fragilidade Geriátrica Avançada:** Paciente idoso identificado em risco ou déficit nutricional evidente. Alerta para alta propensão à perda de massa muscular magra (sarcopenia) e queda da imunidade celular. Priorizar via oral qualificada ou terapia enteral precoce.")
    if "Diabetes mellitus" in comorbidades:
        insights.append("📊 **Restrição Metabólica:** Paciente com distúrbio do metabolismo glicídico. Necessita de monitorização capilar frequente e formulações com menor índice de carboidratos simples.")
    if via_atual == "Jejum" and (escore >= 3 or "risco" in risco.lower()):
        insights.append("🚨 **Alerta de Segurança do Paciente:** Paciente classificado com risco nutricional estabelecido e mantido em Jejum. Risco severo de depleção de glicogênio hepático e catabolismo muscular acelerado se ultrapassar 24 horas sem terapia nutricional activa.")
    if not insights:
        insights.append("✅ **Parâmetros de Estabilidade:** Dados clínicos atuais sem alertas críticos imediatos. Seguir protocolo assistencial padrão conforme nível de atenção definido.")
    return "\n\n".join(insights)

# ==================================================================================================
# TELA INICIAL — BRIEFING E SELEÇÃO DE MÓDULO
# ==================================================================================================
if menu == "🏠 Início":
    df_home = load_pacientes()
    df_alta_home = load_historico()

    # ---- Cabeçalho institucional ----
    st.markdown("""
        <div style="background: linear-gradient(135deg, #4D6452 0%, #2E3D30 100%);
                    padding: 40px 36px 32px 36px; border-radius: 14px; margin-bottom: 28px;">
            <h1 style="color:#FFFFFF; margin:0; font-size:2.1rem; font-family:'Helvetica Neue',Arial,sans-serif;">
                🏥 Sistema EMTN — Hospital Municipal de Paulínia
            </h1>
            <p style="color:#C8D8CA; margin:10px 0 0 0; font-size:1.05rem;">
                Equipe Multiprofissional de Terapia Nutricional &nbsp;|&nbsp; Gestão Integrada do Cuidado Nutricional Hospitalar
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ---- Métricas rápidas ----
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👤 Pacientes Ativos",          len(df_home))
    m2.metric("✅ Altas Registradas",          len(df_alta_home))
    m3.metric("📋 Total de Fichas Emitidas",   len(df_home) + len(df_alta_home))
    risco_count = len(df_home[df_home["Nivel_Assistencia"].isin(["Secundário B","Terciário"])]) if not df_home.empty and "Nivel_Assistencia" in df_home.columns else 0
    m4.metric("⚠️ Em Vigilância EMTN",         risco_count)

    st.markdown("---")

    # ---- Briefing institucional ----
    col_brief, col_nav = st.columns([3, 2], gap="large")

    with col_brief:
        st.markdown("### Sobre o Sistema")
        st.markdown("""
        Este sistema foi desenvolvido para **organizar, registrar e acompanhar o cuidado nutricional**
        de todos os pacientes internados no Hospital Municipal de Paulínia, integrando a atuação da
        **Equipe Multiprofissional de Terapia Nutricional (EMTN)** em tempo real.

        ---

        #### Por que o preenchimento correto importa?

        A desnutrição hospitalar afeta entre **30% e 50% dos pacientes internados** e está diretamente
        associada a maior tempo de internação, complicações cirúrgicas, queda da imunidade e aumento
        da mortalidade. Ela é, em grande parte, **silenciosa e subdiagnosticada**.

        O registro sistemático realizado por esta equipe permite:

        - **Identificar precocemente** pacientes em risco nutricional antes que o quadro se agrave
        - **Direcionar a conduta correta** para cada perfil: oral qualificada, suplementação, terapia enteral ou parenteral
        - **Monitorar a adequação calórico-proteica** diária e intervir quando a meta não é atingida
        - **Gerar indicadores de qualidade** auditáveis pela gestão hospitalar e órgãos reguladores
        - **Proteger juridicamente** a equipe com registros clínicos completos e rastreáveis

        > *"Nutrir é tratar. O registro é o que transforma a intenção em cuidado documentado."*

        ---

        #### Responsabilidade de cada membro da EMTN

        Cada profissional que acessa este sistema tem um papel insubstituível. A triagem feita pelo
        enfermeiro na admissão, a evolução diária do nutricionista à beira-leito, a prescrição médica
        e as notas do plantão formam juntas o **prontuário nutricional completo** — que orienta decisões,
        garante continuidade do cuidado e sustenta os indicadores assistenciais do hospital.

        **Preencher com atenção não é burocracia. É parte do tratamento.**
        """)

    with col_nav:
        st.markdown("### Acesse um Módulo")
        st.markdown(f"Bem-vindo, **{st.session_state.nome_avaliador}**. Por onde deseja começar?")
        st.markdown("")

        _modulos = {
            "🧬 Triagem e Admissão":      "Módulo 1: Triagem e Admissão",
            "📋 Prescrição e Evolução":    "Módulo 2: Prescrição e Evolução",
            "🎯 Avaliação EMTN":           "Módulo 3: Avaliação EMTN",
            "📝 Passagem de Plantão":      "Módulo 4: Passagem de Plantão",
            "📊 Indicadores":              "Módulo 5: Indicadores",
        }
        for _label, _destino in _modulos.items():
            if st.button(_label, use_container_width=True, key=f"btn_home_{_destino}"):
                st.session_state.menu_ativo = _destino
                st.rerun()

        st.markdown("---")
        st.markdown("""
        <div style="background:#FFF8E1; border-left:4px solid #F9A825;
                    padding:14px; border-radius:8px; font-size:0.88rem; color:#5D4037;">
            <b>⚠️ Lembrete de Qualidade</b><br>
            Triagens devem ser realizadas em até <b>48h após a admissão</b>.<br>
            Evoluções devem ser registradas <b>diariamente</b> para pacientes em risco.<br>
            Reavaliações de pacientes Terciários: <b>mínimo 2x por semana</b>.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ---- Painel de situação atual dos leitos ----
    if not df_home.empty:
        st.markdown("### 📍 Situação Atual dos Leitos")
        cols_home = [c for c in ["Leito","Nome","Setor","Risco","Via_Proposta","Nivel_Assistencia","Ultima_Reavaliacao"] if c in df_home.columns]
        st.dataframe(
            df_home[cols_home].sort_values("Setor") if "Setor" in df_home.columns else df_home[cols_home],
            use_container_width=True, hide_index=True
        )
    else:
        st.info("Nenhum paciente ativo no momento. Realize a primeira admissão no Módulo 1.")

# ==================================================================================================
# MÓDULO 1 — TRIAGEM E ADMISSÃO
# ==================================================================================================
elif menu == "Módulo 1: Triagem e Admissão":
    st.title("🧬 Módulo 1: Triagem e Admissão de Pacientes")

    if "passo_atual" not in st.session_state:
        st.session_state.passo_atual = "identificacao"

    # Botões de navegação
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1:
        if st.session_state.passo_atual != "identificacao":
            if st.button("⬅️ Voltar Etapa", use_container_width=True):
                if st.session_state.passo_atual in ["triagem_<=18","triagem_19-59","triagem_>= 60"]:
                    st.session_state.passo_atual = "anamnese"
                elif st.session_state.passo_atual == "anamnese":
                    st.session_state.passo_atual = "identificacao"
                elif st.session_state.passo_atual == "conduta_final":
                    faixa = st.session_state.dados_triagem_base.get("Faixa Etária","19-59")
                    st.session_state.passo_atual = f"triagem_{faixa}"
                st.rerun()
    with col_nav2:
        if st.button("🔄 Reiniciar e Limpar Formulário", key="btn_reset"):
            st.session_state.passo_atual = "identificacao"
            st.session_state.pop("dados_triagem_base", None)
            st.rerun()

    st.markdown("---")

    # ------------------------------------------------------------------
    # ETAPA 1 — Identificação
    # ------------------------------------------------------------------
    if st.session_state.passo_atual == "identificacao":
        with st.form("form_passo_1"):
            st.subheader("Identificação Básica do Paciente")
            f_avaliador    = st.text_input("1. Avaliador *", value=st.session_state.nome_avaliador, disabled=True)
            f_data_adm     = st.date_input("2. Data de Admissão Hospitalar *", format="DD/MM/YYYY")
            f_nome         = st.text_input("3. Nome Completo do Paciente *")
            f_sexo         = st.radio("4. Gênero Biológico *", ["Masculino","Feminino"])
            f_setor        = st.selectbox("5. Setor de Internação *", ["Pronto Socorro Adulto","Pronto Socorro Infantil","Clinica Médica","Clínica Cirúrgica","Ginecologia e Obstetrícia","Pediatria","UTI"])
            f_leito        = st.text_input("6. Identificação do Leito *")
            f_data_triagem = st.date_input("7. Data Real da Triagem EMTN", format="DD/MM/YYYY")
            f_via          = st.selectbox("8. Via de Alimentação de Entrada *", ["Oral","Sonda Nasoenteral","Gastrostomia","Jejunostomia","Parenteral periférica","Parenteral central","Jejum"])
            if st.form_submit_button("Avançar para Dados Clínicos e Idade ➔"):
                if not f_nome or not f_leito:
                    st.error("Preencha os campos obrigatórios: Nome e Leito.")
                else:
                    st.session_state.dados_triagem_base = {
                        "Avaliador": f_avaliador,
                        "Data Admissão": f_data_adm.strftime("%Y-%m-%d"),
                        "Nome": f_nome, "Sexo": f_sexo, "Setor": f_setor, "Leito": f_leito,
                        "Data Triagem": f_data_triagem.strftime("%Y-%m-%d"),
                        "Via Alimentação": f_via, "Momento": "Avaliação Inicial",
                        "Notas_Plantao": "", "Ultima_Reavaliacao": "Não Reavaliado",
                    }
                    st.session_state.passo_atual = "anamnese"
                    st.rerun()

    # ------------------------------------------------------------------
    # ETAPA 2 — Anamnese + IMC reativo
    # ------------------------------------------------------------------
    elif st.session_state.passo_atual == "anamnese":
        st.subheader("Anamnese Clínica e Perfil Antropométrico")
        st.markdown(f"**Paciente:** {st.session_state.dados_triagem_base['Nome']} | **Leito:** {st.session_state.dados_triagem_base['Leito']}")

        f_data_nasc = st.date_input("14. Data de Nascimento *", value=date(1980,1,1),
                                    min_value=date(1900,1,1), max_value=date.today(), format="DD/MM/YYYY")
        anos, meses = calcular_idade_detalhada(f_data_nasc)

        col_a1, col_a2 = st.columns(2)
        with col_a1: f_peso_hab = st.number_input("12. Peso Habitual (kg) *", min_value=0.0, max_value=300.0, value=70.0, step=0.1, format="%.2f")
        with col_a2: f_altura   = st.number_input("13. Altura (m) *", min_value=0.10, max_value=2.50, value=1.70, step=0.01, format="%.2f")

        st.success(f"📌 Idade calculada: {anos} anos e {meses} meses.")

        imc_real  = 0.0
        classe_imc = "N/A"
        if f_altura > 0:
            imc_real = f_peso_hab / (f_altura ** 2)
            if anos >= 19:
                classe_imc = classificar_imc_adulto(imc_real)
                st.info(f"⚖️ IMC: {imc_real:.2f} kg/m² ({classe_imc})")
            else:
                classe_imc = "Percentil Pediátrico"
                st.info(f"⚖️ IMC: {imc_real:.2f} kg/m² (Avaliar por Curva de Crescimento)")

        with st.form("form_passo_2"):
            f_diag = st.text_area("10. Diagnóstico Médico de Admissão *")
            f_comorbidades = st.multiselect("11. Comorbidades Crônicas Associadas *", [
                "NÃO POSSUI COMORBIDADE","Acamado(a)","Diabetes mellitus","Drogadição (SPA)",
                "Etilismo","Hipertensão arterial sistêmica","Infarto","Insuficiência cardíaca",
                "Obesidade","Tabagismo","Doença autoimune","Doença hematológica",
                "Doença hepática ou gastrointestinal","Doença nefrológica","Doença neoplásica",
                "Doença neurológica","Doença psiquiátrica","Doença respiratória",
                "Doença sexualmente transmissível","Outra doença cardiovascular","Outra doença endócrina",
                "Doença gestacional - Hipertensão arterial sistêmica","Doença gestacional - Diabetes mellitus",
                "Doença gestacional - Outra doença endócrina","Doença gestacional - Outra(s) doença(s)",
                "Outra(s) doença(s)"
            ])
            if st.form_submit_button("Vincular e Chamar Questionário de Triagem ➔"):
                faixa_calculada = "<=18" if anos < 19 else ("19-59" if anos <= 59 else ">= 60")
                st.session_state.dados_triagem_base.update({
                    "Diagnóstico": f_diag, "Comorbidades": ", ".join(f_comorbidades),
                    "Peso Habitual": f_peso_hab, "Altura Referida": f_altura,
                    "IMC Calculado": round(imc_real, 2), "Classe IMC": classe_imc,
                    "Data Nascimento": f_data_nasc.strftime("%Y-%m-%d"),
                    "Idade Anos": anos, "Idade Meses": meses, "Faixa Etária": faixa_calculada,
                })
                st.session_state.passo_atual = f"triagem_{faixa_calculada}"
                st.rerun()

    # ------------------------------------------------------------------
    # ETAPA 3A — STRONG KIDS (pediátrico)
    # ------------------------------------------------------------------
    elif st.session_state.passo_atual == "triagem_<=18":
        st.subheader("🧬 Rastreamento de Risco Pediátrico: Ferramenta STRONG KIDS")
        st.info("🔬 **HMP / USP:** A ferramenta STRONGkids avalia 4 domínios críticos para desnutrição infantil intrahospitalar.")
        with st.form("form_strong"):
            q1 = st.radio("17. A criança aparenta perda de tecido adiposo ou massa muscular?", ["Não (0 ponto)","Sim (1 ponto)"])
            q2 = st.radio("18. Patologia de base em alto risco nutricional ou cirurgia de grande porte?", ["Não (0 ponto)","Sim (2 pontos)"])
            q3 = st.radio("19. Diarreia severa, vômitos reincidentes ou ingestão oral deficitária?", ["Não (0 ponto)","Sim (1 ponto)"])
            q4 = st.radio("20. Perda de peso involuntária ou incapacidade de ganho estatural?", ["Não (0 ponto)","Sim (1 ponto)"])
            if st.form_submit_button("Computar Escore Pediátrico ➔"):
                escore = ("Sim" in q1) + ("2 pontos" in q2)*2 + ("Sim" in q3) + ("Sim" in q4)
                if escore >= 4:
                    risco = "Alto Risco Nutricional"
                    interv = "1. Consultar médico ou nutricionista\n2. Orientação individualizada\n3. Iniciar suplementação oral"
                elif 1 <= escore <= 3:
                    risco = "Médio Risco Nutricional"
                    interv = "1. Consultar médico\n2. Considerar intervenção nutricional\n3. Checar peso 2x/semana\n4. Reavaliar em 1 semana"
                else:
                    risco = "Baixo Risco Nutricional"
                    interv = "1. Checar peso regularmente\n2. Reavaliar risco em 1 semana"
                st.session_state.dados_triagem_base.update({"Escore Triagem": escore, "Risco": risco, "Intervencao_Obrigatoria": interv})
                st.session_state.passo_atual = "conduta_final"
                st.rerun()

    # ------------------------------------------------------------------
    # ETAPA 3B — NRS 2002 (adulto)
    # ------------------------------------------------------------------
    elif st.session_state.passo_atual == "triagem_19-59":
        st.subheader("🫁 Triagem de Risco no Adulto: Ferramenta NRS 2002")
        st.info("🔬 **HMP / USP:** O NRS 2002 correlaciona desnutrição atual com estresse metabólico da doença. Escore ≥ 3 indica risco.")
        with st.form("form_nrs_completo"):
            st.markdown("### Pré-Rastreamento")
            st.checkbox("IMC abaixo de 20,5 kg/m²?")
            st.checkbox("Perda ponderal involuntária nos últimos 3 meses?")
            st.checkbox("Redução expressiva da ingestão na última semana?")
            st.checkbox("Estado clínico grave?")
            st.markdown("---")
            f_det = st.radio("27. Deterioração do Estado Nutricional *", [
                "0 : Ausente - Estado nutricional normal",
                "1 : Leve - Perda > 5% em 3 meses OU aceitação 50-75% há 1 semana",
                "2 : Moderado - Perda > 5% em 2 meses OU IMC 18,5-20,5 + piora OU aceitação 25-50% há 1 semana",
                "3 : Grave - Perda > 5% em 1 mês (>15% em 3 meses) OU IMC < 18,5 + piora OU aceitação 0-25%",
            ])
            f_grav = st.radio("28. Gravidade da Doença *", [
                "0 : Ausente - Requerimento nutricional normal",
                "1 : Leve - Fratura quadril, cirrose, DPOC, hemodiálise, diabetes, oncologia",
                "2 : Moderado - Cirurgia abdominal grande porte, AVC, pneumonia grave, leucemia",
                "3 : Grave - TCE, transplante medula óssea, pacientes críticos (APACHE II > 10)",
            ])
            if st.form_submit_button("Computar Escore NRS 2002 ➔"):
                p_det   = int(f_det.split(" : ")[0])
                p_grav  = int(f_grav.split(" : ")[0])
                idade_p = st.session_state.dados_triagem_base.get("Idade Anos", 0)
                escore  = p_det + p_grav + (1 if idade_p >= 70 else 0)
                if escore >= 3:
                    risco = f"Escore ≥ 3 ({escore} pontos) — Risco Nutricional"
                    if escore == 3:   interv = "Escore 3: indicação de dieta enteral se aceitação oral < 50%."
                    elif escore == 4: interv = "Escore 4: indicação formal de Terapia Nutricional Enteral (TNE)."
                    else:             interv = f"Escore {escore}: hipercatabolismo severo. Suporte enteral/parenteral precoce mandatório."
                else:
                    risco = f"Escore < 3 ({escore} pontos) — Sem risco atual"
                    if escore == 1:   interv = "Escore 1: monitorar semanalmente. Suplemento VO se necessário."
                    elif escore == 2: interv = "Escore 2: suplemento VO. Reavaliar em 7 dias."
                    else:             interv = "Escore 0: sem risco. Reavaliar semanalmente."
                st.session_state.dados_triagem_base.update({"Escore Triagem": escore, "Risco": risco, "Intervencao_Obrigatoria": interv})
                st.session_state.passo_atual = "conduta_final"
                st.rerun()

    # ------------------------------------------------------------------
    # ETAPA 3C — MNA® (geriátrico)
    # ------------------------------------------------------------------
    elif st.session_state.passo_atual == "triagem_>= 60":
        st.subheader("👴 Avaliação Geriátrica: Mini Avaliação Nutricional (MNA®)")
        st.info("🔬 **HMP / USP:** A MNA® é o padrão-ouro validado internacionalmente para idosos hospitalizados.")
        with st.form("form_mna_completo"):
            mna_a = st.selectbox("A. Redução da ingesta alimentar nos últimos 3 meses?",["2 : Sem redução alimentar","1 : Redução moderada","0 : Redução severa"])
            mna_b = st.selectbox("B. Perda de peso involuntária nos últimos 3 meses?",["3 : Sem perda ponderal","2 : Perda entre 1 e 3 kg","1 : Não sabe informar","0 : Perda > 3 kg"])
            mna_c = st.selectbox("C. Mobilidade e locomoção?",["2 : Deambula normalmente","1 : Restrito ao leito/cadeira, mas levanta","0 : Restrito à cama ou cadeira de rodas"])
            mna_d = st.selectbox("D. Estresse psicológico agudo ou doença aguda nos últimos 3 meses?",["2 : Não","0 : Sim"])
            mna_e = st.selectbox("E. Problemas neuropsicológicos?",["2 : Sem alterações cognitivas","1 : Demência moderada ou confusão leve","0 : Demência grave ou depressão severa"])
            mna_f = st.selectbox("F. IMC atual?",["3 : IMC ≥ 23 kg/m²","2 : IMC 21-23 kg/m²","1 : IMC 19-21 kg/m²","0 : IMC < 19 kg/m²"])
            if st.form_submit_button("Computar Escore MNA® ➔"):
                escore = int(mna_a[0])+int(mna_b[0])+int(mna_c[0])+int(mna_d[0])+int(mna_e[0])+int(mna_f[0])
                if escore >= 12:
                    risco = "Estado Nutricional Normal"
                    interv = "Manter rotina hospitalar padrão e monitorar aceitação da dieta."
                elif 8 <= escore <= 11:
                    risco = "Risco de Desnutrição"
                    interv = "Iniciar enriquecimento calórico-proteico e acompanhamento farmacológico."
                else:
                    risco = "Desnutrido"
                    interv = "Terapia nutricional especializada (suplementos/enteral) e metas de reabilitação com a EMTN."
                st.session_state.dados_triagem_base.update({"Escore Triagem": escore, "Risco": risco, "Intervencao_Obrigatoria": interv})
                st.session_state.passo_atual = "conduta_final"
                st.rerun()

    # ------------------------------------------------------------------
    # ETAPA 4 — Conduta final + salva no SQLite
    # ------------------------------------------------------------------
    elif st.session_state.passo_atual == "conduta_final":
        st.subheader("🏁 Definição da Conduta e Terapia Nutricional Proposta")
        db = st.session_state.dados_triagem_base
        parecer_ia = analisar_dados_com_ia(db)

        st.markdown(f'<div class="ai-box"><h4>🤖 Apoio Clínico EMTN</h4><p style="white-space:pre-line;">{parecer_ia}</p></div>', unsafe_allow_html=True)
        st.info("""
        📋 **Níveis de Assistência (HMP/USP)**
        - **Primário:** sem risco e sem dieta específica
        - **Secundário A:** dieta específica, sem risco nutricional
        - **Secundário B:** sem dieta específica, com risco nutricional
        - **Terciário:** com risco nutricional ou dieta especializada
        """)

        with st.form("form_final"):
            st.markdown(f"**Paciente:** {db['Nome']} | **Idade:** {db.get('Idade Anos','?')} anos e {db.get('Idade Meses','?')} meses")
            st.warning(f"Risco: **{db.get('Risco','N/A')}** | Escore: **{db.get('Escore Triagem',0)}** | IMC: {db.get('IMC Calculado',0.0)} ({db.get('Classe IMC','N/A')})")
            st.markdown(f"📋 **Intervenção sugerida:**\n\n{db.get('Intervencao_Obrigatoria','')}")

            f_nivel    = st.selectbox("38. Nível de Assistência *", ["Primário","Secundário A","Secundário B","Terciário"])
            f_conduta  = st.text_area("83. Conduta Terapêutica Adotada *", placeholder="Insira a conduta oficial...")
            f_via_prop = st.selectbox("84. Via de Alimentação Proposta *", ["Oral","Sonda Nasoenteral","Gastrostomia","Jejunostomia","Parenteral periférica","Parenteral central","Jejum"])
            f_dieta    = st.text_input("Dieta / Fórmula Prescrita *")

            if st.form_submit_button("✅ Finalizar Admissão e Salvar no Banco de Dados"):
                db.update({
                    "Nível Assistência": f_nivel, "Via Proposta": f_via_prop,
                    "Dieta Prescrita": f_dieta,
                    "Conduta": f_conduta if f_conduta else "Conduta padrão conforme protocolo.",
                    "Parecer_IA": parecer_ia, "Adequacao_Calorica": 100.0,
                })
                salvar_paciente(db)
                st.success("✅ Paciente admitido e salvo no banco de dados!")
                # Volta para a tela inicial do módulo
                st.session_state.pop("dados_triagem_base", None)
                st.session_state.passo_atual = "identificacao"
                st.session_state.menu_ativo  = "Módulo 1: Triagem e Admissão"
                st.rerun()

# ==================================================================================================
# MÓDULO 2 — PRESCRIÇÃO E EVOLUÇÃO
# ==================================================================================================
elif menu == "Módulo 2: Prescrição e Evolução":
    st.title("📋 Módulo 2: Prescrição e Evolução Clínica Diária (Beira-Leito)")
    st.info("🔬 **HMP/USP:** Monitorar eficácia da via alimentar, adequação volumétrica e sintomas de intolerância.")

    df = load_pacientes()
    if df.empty:
        st.info("Nenhum paciente cadastrado. Realize a admissão no Módulo 1.")
    else:
        setores = df["Setor"].dropna().unique().tolist()
        setor_sel = st.selectbox("Filtrar por Setor:", setores)
        df_setor  = df[df["Setor"] == setor_sel]
        nome_sel  = st.selectbox("Selecione o paciente:", df_setor["Nome"].unique())

        if st.button("Carregar Prontuário"):
            st.session_state.p_ativo = df[df["Nome"] == nome_sel].iloc[0].to_dict()

        if "p_ativo" in st.session_state:
            p = st.session_state.p_ativo
            via = p.get("Via_Proposta","Oral")

            st.markdown(f"### Paciente: **{p['Nome']}** ({p.get('Idade_Anos','?')} anos)")
            st.info(f"📍 Via: {via} | Dieta: {p.get('Dieta_Prescrita','N/A')} | IMC: {p.get('IMC_Calculado',0.0)} ({p.get('Classe_IMC','N/A')})")

            with st.form("form_evolucao_diaria"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 🩺 Sinais Clínicos")
                    f_nausea    = st.radio("Náuseas / Vômitos?", ["Não","Sim"])
                    f_evacuacao = st.selectbox("Padrão de Evacuações (24h):", ["Sim, normal","Não, constipação","Não, diarreia"])
                    f_intercorr = st.text_input("Outras queixas:", placeholder="Ex: xerostomia, dor ao engolir")
                with col2:
                    st.markdown("#### 🧪 Exames e Peso")
                    f_peso_atual = st.number_input("Peso atual (kg):", min_value=0.0, value=float(p.get("Peso_Habitual",70.0)), step=0.1, format="%.2f")
                    f_fosforo    = st.number_input("Fósforo sérico (mg/dL):", min_value=0.0, value=3.5, step=0.1)

                st.markdown("---")
                st.markdown("#### 🍽️ Monitoramento de Ingestão")

                if via in ["Oral","Transição para Oral","Oral Plena"]:
                    st.success("📝 Via Oral Ativa")
                    f_consist   = st.selectbox("Consistência da dieta:", ["Livre / Geral","Branda","Pastosa","Leve","Líquida","Líquida Pastosa"])
                    f_aceitacao = st.select_slider("Aceitação estimada (24h):", options=["0%","25%","50%","75%","100%"], value="100%")
                    adequacao   = int(f_aceitacao.replace("%",""))
                    f_sno       = st.radio("Uso de Suplemento Nutricional Oral (SNO)?", ["Não","Sim — Boa aceitação","Sim — Recusa parcial","Sim — Recusa total"])
                else:
                    st.warning("⚡ Terapia Enteral/Parenteral ou Jejum")
                    f_distensao   = st.radio("Distensão abdominal ou resíduo gástrico?", ["Não","Sim"])
                    vol_prescrito = st.number_input("Volume prescrito (mL/dia):", min_value=1, value=1000)
                    vol_infundido = st.number_input("Volume infundido (mL/dia):", min_value=0, value=1000)
                    adequacao     = (vol_infundido / vol_prescrito) * 100
                    f_consist     = "N/A — Enteral/Parenteral"
                    f_sno         = "Não"

                st.markdown("---")
                f_evolucao = st.text_area("Evolução de Prontuário (Notas Clínicas do Dia):")

                if st.form_submit_button("💾 Gravar Evolução Diária"):
                    hoje_str = date.today().strftime("%d/%m/%Y")
                    nota = (
                        f"[{hoje_str}] Via: {via} | Consistência: {f_consist} | "
                        f"Adequação: {adequacao:.0f}% | Evacuação: {f_evacuacao} | "
                        f"Notas: {f_evolucao if f_evolucao else 'Sem observações.'}"
                    )
                    atualizar_paciente(p["Nome"], "Adequacao_Calorica", float(adequacao))
                    atualizar_paciente(p["Nome"], "Notas_Plantao", nota)
                    atualizar_paciente(p["Nome"], "Ultima_Reavaliacao", f"Evoluído em {hoje_str}")
                    st.success(f"✅ Evolução de {p['Nome']} salva no banco de dados!")
                    st.session_state.pop("p_ativo", None)
                    # Volta para tela inicial do módulo 2
                    st.session_state.menu_ativo = "Módulo 2: Prescrição e Evolução"
                    st.rerun()

            st.markdown("---")
            if st.button("🚨 Registrar Alta Hospitalar"):
                registrar_alta(p["Nome"])
                st.session_state.pop("p_ativo", None)
                st.success(f"Alta de {p['Nome']} registrada! Dados movidos para o histórico.")
                st.session_state.menu_ativo = "Módulo 2: Prescrição e Evolução"
                st.rerun()

# ==================================================================================================
# MÓDULO 3 — AVALIAÇÃO EMTN
# ==================================================================================================
elif menu == "Módulo 3: Avaliação EMTN":
    st.title("🎯 Módulo 3: Painel de Vigilância e Avaliação Supervisionada da EMTN")
    df = load_pacientes()
    if df.empty:
        st.info("Nenhum paciente admitido no sistema.")
    else:
        crit_nivel    = df["Nivel_Assistencia"].isin(["Secundário B","Terciário"])
        crit_via_adm  = df["Via_Alimentacao"].isin(["Sonda Nasoenteral","Parenteral periférica","Parenteral central"])
        crit_via_prop = df["Via_Proposta"].isin(["Sonda Nasoenteral","Parenteral periférica","Parenteral central"])
        df_sup = df[crit_nivel | crit_via_adm | crit_via_prop]

        if df_sup.empty:
            st.success("✅ Nenhum paciente preenche critérios de risco crítico hoje.")
        else:
            st.warning(f"⚠️ {len(df_sup)} paciente(s) em acompanhamento prioritário.")
            cols_exib = [c for c in ["Leito","Nome","Idade_Anos","Setor","IMC_Calculado","Classe_IMC","Via_Proposta","Nivel_Assistencia","Risco","Ultima_Reavaliacao"] if c in df_sup.columns]
            st.dataframe(df_sup[cols_exib], use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("🔄 Registrar Reavaliação Supervisionada")
            pac_reav = st.selectbox("Paciente para reavaliação:", df_sup["Nome"].unique())
            with st.form("form_reaval_emtn"):
                col1, col2 = st.columns(2)
                with col1:
                    nova_via   = st.selectbox("Nova via proposta:", ["Sonda Nasoenteral","Parenteral central","Parenteral periférica","Transição para Oral","Oral Plena","Gastrostomia","Jejum"])
                    novo_nivel = st.selectbox("Reclassificar Nível:", ["Terciário","Secundário B","Secundário A","Primário"])
                with col2:
                    nova_conduta = st.text_area("Evolução EMTN / Ajustes de metas:")
                if st.form_submit_button("Submeter e Atualizar Grade de Vigilância"):
                    hoje_str = date.today().strftime("%d/%m/%Y")
                    atualizar_paciente(pac_reav, "Via_Proposta", nova_via)
                    atualizar_paciente(pac_reav, "Nivel_Assistencia", novo_nivel)
                    atualizar_paciente(pac_reav, "Conduta", nova_conduta)
                    atualizar_paciente(pac_reav, "Ultima_Reavaliacao", f"Reavaliado em {hoje_str}")
                    st.success(f"Ficha de {pac_reav} atualizada com sucesso!")
                    st.rerun()

# ==================================================================================================
# MÓDULO 4 — PASSAGEM DE PLANTÃO
# ==================================================================================================
elif menu == "Módulo 4: Passagem de Plantão":
    st.title("📋 Módulo 4: Passagem de Plantão e Round da EMTN")
    df = load_pacientes()
    if df.empty:
        st.info("Nenhum paciente ativo no hospital.")
    else:
        cols_plantao = [c for c in ["Leito","Nome","Idade_Anos","Setor","IMC_Calculado","Via_Proposta","Dieta_Prescrita","Adequacao_Calorica","Risco","Notas_Plantao"] if c in df.columns]
        df_edit = st.data_editor(
            df[cols_plantao],
            column_config={
                "Nome":             st.column_config.TextColumn("Paciente", disabled=True),
                "Idade_Anos":       st.column_config.NumberColumn("Idade", disabled=True, format="%d anos"),
                "Setor":            st.column_config.TextColumn("Setor", disabled=True),
                "IMC_Calculado":    st.column_config.NumberColumn("IMC", disabled=True, format="%.2f kg/m²"),
                "Via_Proposta":     st.column_config.TextColumn("Via", disabled=True),
                "Risco":            st.column_config.TextColumn("Risco", disabled=True),
                "Adequacao_Calorica": st.column_config.NumberColumn("Adequação (%)", disabled=True, format="%.1f%%"),
                "Leito":            st.column_config.TextColumn("Leito (Editar)"),
                "Dieta_Prescrita":  st.column_config.TextColumn("Dieta (Editar)"),
                "Notas_Plantao":    st.column_config.TextColumn("Notas do Round ✏️", width="medium"),
            },
            hide_index=True, use_container_width=True
        )
        if st.button("💾 Consolidar Alterações do Round"):
            for _, row in df_edit.iterrows():
                atualizar_paciente(row["Nome"], "Leito",           row["Leito"])
                atualizar_paciente(row["Nome"], "Dieta_Prescrita", row["Dieta_Prescrita"])
                atualizar_paciente(row["Nome"], "Notas_Plantao",   row["Notas_Plantao"])
            st.success("✅ Alterações salvas no banco de dados!")
            st.rerun()

# ==================================================================================================
# MÓDULO 5 — INDICADORES
# ==================================================================================================
elif menu == "Módulo 5: Indicadores":
    st.title("📊 Módulo 5: Dashboard de Indicadores Epidemiológicos e de Qualidade")
    df      = load_pacientes()
    df_alta = load_historico()

    if df.empty and df_alta.empty:
        st.info("Base de dados vazia. Insira registros no Módulo 1.")
    else:
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Pacientes Ativos",         len(df))
        col_m2.metric("Total de Altas Registradas", len(df_alta))
        col_m3.metric("Total de Fichas Emitidas",  len(df) + len(df_alta))
        st.markdown("---")

        if not df.empty:
            g1, g2, g3 = st.columns(3)
            with g1:
                if "Setor" in df.columns:
                    st.plotly_chart(px.bar(df, x="Setor", color="Setor", title="Distribuição por Setor"), use_container_width=True)
            with g2:
                if "Sexo" in df.columns:
                    st.plotly_chart(px.pie(df, names="Sexo", title="Distribuição por Gênero"), use_container_width=True)
            with g3:
                if "Faixa_Etaria" in df.columns:
                    st.plotly_chart(px.histogram(df, x="Faixa_Etaria", title="Pacientes por Faixa Etária"), use_container_width=True)

        st.markdown("---")
        st.subheader("📋 Histórico de Altas")
        if df_alta.empty:
            st.info("Nenhuma alta registrada ainda.")
        else:
            cols_alta = [c for c in ["Nome","Setor","Leito","Risco","Via_Proposta","Data_Alta"] if c in df_alta.columns]
            st.dataframe(df_alta[cols_alta], use_container_width=True, hide_index=True)
