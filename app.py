import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime, date

# CONFIGURAÇÕES DA PÁGINA
st.set_page_config(page_title="EMTN - Hospital Municipal de Paulínia", page_icon="🏥", layout="wide")

# CONFIGURAÇÃO DO BANCO DE DADOS SQLite
DB_NAME = "emtn_hmp.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # Tabela de pacientes ativos
    cursor.execute('''CREATE TABLE IF NOT EXISTS pacientes_ativos (
                        Avaliador TEXT, Data_Admissao TEXT, Nome TEXT PRIMARY KEY, Sexo TEXT, 
                        Setor TEXT, Leito TEXT, Data_Triagem TEXT, Via_Alimentacao TEXT, 
                        Momento TEXT, Diagnostico TEXT, Comorbidades TEXT, Peso_Habitual REAL, 
                        Altura_Referida REAL, IMC_Calculado REAL, Classe_IMC TEXT, 
                        Data_Nascimento TEXT, Idade_Anos INTEGER, Idade_Meses INTEGER, 
                        Faixa_Etaria TEXT, Escore_Triagem INTEGER, Risco TEXT, 
                        Intervencao_Obrigatoria TEXT, Nivel_Assistencia TEXT, Via_Proposta TEXT, 
                        Dieta_Prescrita TEXT, Adequacao_Calorica REAL, Parecer_IA TEXT, 
                        Notas_Plantao TEXT, Ultima_Reavaliacao TEXT)''')
    # Tabela de histórico de alta
    cursor.execute('''CREATE TABLE IF NOT EXISTS historico_alta (
                        Avaliador TEXT, Data_Admissão TEXT, Nome TEXT, Sexo TEXT, 
                        Setor TEXT, Leito TEXT, Data_Triagem TEXT, Via_Alimentação TEXT, 
                        Momento TEXT, Diagnóstico TEXT, Comorbidades TEXT, Peso_Habitual REAL, 
                        Altura_Referida REAL, IMC_Calculado REAL, Classe_IMC TEXT, 
                        Data_Nascimento TEXT, Idade_Anos INTEGER, Idade_Meses INTEGER, 
                        Faixa_Etária TEXT, Escore_Triagem INTEGER, Risco TEXT, 
                        Intervencao_Obrigatoria TEXT, Nível_Assistencia TEXT, Via_Proposta TEXT, 
                        Dieta_Prescrita TEXT, Adequacao_Calorica REAL, Parecer_IA TEXT, 
                        Notas_Plantao TEXT, Ultima_Reavaliacao TEXT, Data_Alta TEXT)''')
    conn.commit()
    conn.close()

init_db()

def load_pacientes():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM pacientes_ativos", conn)
    conn.close()
    return df

def salvar_paciente(dados):
    conn = get_connection()
    cursor = conn.cursor()
    cols = ",".join(dados.keys())
    placeholders = ",".join(["?"] * len(dados))
    cursor.execute(f"INSERT OR REPLACE INTO pacientes_ativos ({cols}) VALUES ({placeholders})", tuple(dados.values()))
    conn.commit()
    conn.close()

def atualizar_paciente(nome, campo, valor):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE pacientes_ativos SET {campo} = ? WHERE Nome = ?", (valor, nome))
    conn.commit()
    conn.close()

def registrar_alta(nome):
    conn = get_connection()
    cursor = conn.cursor()
    # Copia para histórico
    cursor.execute("SELECT * FROM pacientes_ativos WHERE Nome = ?", (nome,))
    p = cursor.fetchone()
    if p:
        campos = [d[0] for d in cursor.description]
        valores = list(p) + [date.today().strftime("%Y-%m-%d")]
        query = f"INSERT INTO historico_alta ({','.join(campos)}, Data_Alta) VALUES ({','.join(['?'] * len(valores))})"
        cursor.execute(query, valores)
        # Deleta do ativo
        cursor.execute("DELETE FROM pacientes_ativos WHERE Nome = ?", (nome,))
    conn.commit()
    conn.close()

# ESTILIZAÇÃO CUSTOMIZADA
st.markdown("""
    <style>
        .main { background-color: #FAFAFA; }
        .sidebar .sidebar-content { background-color: #E2E8F0; }
        h1, h2, h3 { color: #4D6452; font-family: 'Helvetica Neue', Arial, sans-serif; }
        .ai-box { background-color: #F0F4F8; border-left: 6px solid #1E3A8A; color: #1E3A8A; padding: 15px; border-radius: 8px; margin-top: 15px; }
        @media print { body * { visibility: hidden; } .secao-impressao, .secao-impressao * { visibility: visible; } }
    </style>
""", unsafe_allow_html=True)

# DICIONÁRIO DE USUÁRIOS
CONTA_USUARIOS = {
    "vinicius.mariano": {"senha": "casa0904", "nome_completo": "Dr. Vinícius Mariano"},
    "priscila.nutri": {"senha": "nutri1234", "nome_completo": "Nutri. Priscila"},
    "resilda.enfermeira": {"senha": "enf1234", "nome_completo": "Enf. Resilda"},
    "julia.lopes": {"senha": "julia1234", "nome_completo": "Júlia Lopes"},
    "amanda.snd": {"senha": "snd1234", "nome_completo": "Amanda SND"},
    "carol.geriatria": {"senha": "geriatria1234", "nome_completo": "Carol Geriatria"},
    "matheus.soberana": {"senha": "matheus1234", "nome_completo": "Matheus Soberana"},
    "rafael.soberana": {"senha": "rafael1234", "nome_completo": "Rafael Soberana"},
    "caren.soberana": {"senha": "caren1234", "nome_completo": "Caren Soberana"},
    "vanessa.soberana": {"senha": "vanessa1234", "nome_completo": "Vanessa Soberana"}
}

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🏥 Sistema de Gestão de Cuidado Nutricional - EMTN HMP")
    user = st.text_input("Usuário de Acesso:")
    password = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if user in CONTA_USUARIOS and CONTA_USUARIOS[user]["senha"] == password:
            st.session_state.autenticado = True
            st.session_state.nome_avaliador = CONTA_USUARIOS[user]["nome_completo"]
            st.rerun()
        else: st.error("Credenciais incorretas.")
    st.stop()

# BARRA LATERAL
st.sidebar.markdown(f"<h3 style='text-align: center; color: #4D6452;'>EMTN HMP</h3><p style='text-align: center;'>👤 {st.session_state.nome_avaliador}</p>", unsafe_allow_html=True)
menu = st.sidebar.radio("Módulos do Sistema:", ["Módulo 1: Triagem e Admissão", "Módulo 2: Prescrição e Evolução", "Módulo 3: Avaliação EMTN", "Módulo 4: Passagem de Plantão", "Módulo 5: Indicadores"])
if st.sidebar.button("🔒 Sair"): st.session_state.autenticado = False; st.rerun()

def calcular_idade_detalhada(data_nasc):
    if isinstance(data_nasc, str): data_nasc = datetime.strptime(data_nasc, "%Y-%m-%d").date()
    hoje = date.today()
    anos = hoje.year - data_nasc.year
    meses = hoje.month - data_nasc.month
    if hoje.day < data_nasc.day: meses -= 1
    if meses < 0: anos -= 1; meses += 12
    return anos, meses

def classificar_imc_adulto(imc):
    if imc < 18.5: return "Baixo Peso"
    elif 18.5 <= imc < 25.0: return "Eutrofia"
    elif 25.0 <= imc < 30.0: return "Sobrepeso"
    else: return "Obesidade"

def analisar_dados_com_ia(dados):
    insights = []
    if "Etilismo" in dados.get("Comorbidades", "") or (dados.get("Faixa_Etaria") == "19-59" and dados.get("Escore_Triagem", 0) >= 3):
        insights.append("🛑 Risco de Síndrome de Realimentação.")
    return "\n\n".join(insights) if insights else "✅ Parâmetros de Estabilidade."

# MÓDULO 1
if menu == "Módulo 1: Triagem e Admissão":
    st.title("🧬 Módulo 1: Triagem e Admissão")
    if 'passo_atual' not in st.session_state: st.session_state.passo_atual = "identificacao"
    
    if st.session_state.passo_atual == "identificacao":
        with st.form("form_1"):
            f_nome = st.text_input("Nome *")
            f_leito = st.text_input("Leito *")
            f_sexo = st.radio("Gênero", ["Masculino", "Feminino"])
            f_setor = st.selectbox("Setor", ["Clinica Médica", "UTI", "Pronto Socorro"])
            f_via = st.selectbox("Via", ["Oral", "Sonda", "Jejum"])
            f_momento = st.radio("Momento", ["Avaliação Inicial", "Reavaliação"])
            if st.form_submit_button("Avançar"):
                st.session_state.dados_triagem_base = {"Nome": f_nome, "Leito": f_leito, "Sexo": f_sexo, "Setor": f_setor, "Via_Alimentacao": f_via, "Momento": f_momento, "Avaliador": st.session_state.nome_avaliador}
                st.session_state.passo_atual = "anamnese"; st.rerun()
    
    elif st.session_state.passo_atual == "anamnese":
        f_nasc = st.date_input("Nascimento")
        f_peso = st.number_input("Peso", value=70.0)
        f_alt = st.number_input("Altura", value=1.70)
        if st.button("Vincular"):
            anos, meses = calcular_idade_detalhada(f_nasc)
            st.session_state.dados_triagem_base.update({"Data_Nascimento": str(f_nasc), "Idade_Anos": anos, "Idade_Meses": meses, "Peso_Habitual": f_peso, "Altura_Referida": f_alt, "IMC_Calculado": round(f_peso/(f_alt**2), 2)})
            st.session_state.passo_atual = "conduta_final"; st.rerun()
            
    elif st.session_state.passo_atual == "conduta_final":
        with st.form("final"):
            f_conduta = st.text_area("Conduta")
            if st.form_submit_button("Salvar"):
                st.session_state.dados_triagem_base.update({"Conduta": f_conduta, "Risco": "Baixo", "Escore_Triagem": 0, "Nivel_Assistencia": "Primário", "Via_Proposta": "Oral", "Dieta_Prescrita": "Livre", "Parecer_IA": "Normal"})
                salvar_paciente(st.session_state.dados_triagem_base)
                st.session_state.passo_atual = "identificacao"
                st.success("Salvo no SQLite!"); st.rerun()

# MÓDULO 2
elif menu == "Módulo 2: Prescrição e Evolução":
    df = load_pacientes()
    if df.empty: st.info("Sem pacientes.")
    else:
        nome = st.selectbox("Paciente", df["Nome"].unique())
        evol = st.text_area("Evolução")
        if st.button("Salvar"):
            atualizar_paciente(nome, "Notas_Plantao", evol)
            st.success("Atualizado!")
        if st.button("Alta"):
            registrar_alta(nome)
            st.success("Alta registrada!")

# MÓDULO 3
elif menu == "Módulo 3: Avaliação EMTN":
    df = load_pacientes()
    st.dataframe(df)

# MÓDULO 4
elif menu == "Módulo 4: Passagem de Plantão":
    df = load_pacientes()
    edited_df = st.data_editor(df)
    if st.button("Sincronizar"):
        for _, row in edited_df.iterrows():
            atualizar_paciente(row["Nome"], "Notas_Plantao", row["Notas_Plantao"])

# MÓDULO 5
elif menu == "Módulo 5: Indicadores":
    df = load_pacientes()
    if not df.empty:
        st.plotly_chart(px.pie(df, names='Sexo'))
