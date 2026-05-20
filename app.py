import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
DB_NAME = "emtn_hmp_prontuario.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Tabela com todos os dados solicitados anteriormente
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, idade_anos INTEGER, setor TEXT, leito TEXT,
            escore_triagem INTEGER, risco TEXT, diagnostico TEXT, 
            comorbidades TEXT, via_alimentacao TEXT, data_gravacao DATETIME
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- LOGIN ---
st.set_page_config(page_title="Gestão EMTN HMP", layout="wide")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🏥 Sistema de Gestão EMTN - HMP")
    senha = st.text_input("Senha de Acesso", type="password")
    if st.button("Entrar"):
        if senha == "hmp2026":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# --- MENU E ESTRUTURA ---
menu = st.sidebar.radio("Navegação", [
    "Módulo 1: Triagem", "Módulo 2: Evolução", "Módulo 3: Avaliação", 
    "Módulo 4: Plantão", "Módulo 5: Indicadores"
])

# --- MÓDULO 1: TRIAGEM ---
if menu == "Módulo 1: Triagem":
    st.title("🧬 Módulo 1: Triagem de Risco (NRS 2002)")
    with st.form("form_triagem"):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome do Paciente")
        idade = col2.number_input("Idade", 0, 120)
        setor = col1.text_input("Setor")
        leito = col2.text_input("Leito")
        
        st.write("---")
        det = st.slider("Deterioração Nutricional (0-3)", 0, 3, 0)
        grav = st.slider("Gravidade da Doença (0-3)", 0, 3, 0)
        
        if st.form_submit_button("Salvar e Arquivar"):
            escore = det + grav + (1 if idade >= 70 else 0)
            risco = "Risco Nutricional" if escore >= 3 else "Sem Risco"
            
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO pacientes (nome, idade_anos, setor, leito, escore_triagem, risco, data_gravacao) 
                              VALUES (?,?,?,?,?,?,?)""", (nome, idade, setor, leito, escore, risco, datetime.now()))
            conn.commit()
            conn.close()
            st.success(f"Paciente {nome} arquivado com sucesso!")

# --- MÓDULO 5: INDICADORES E RELATÓRIOS ---
elif menu == "Módulo 5: Indicadores":
    st.title("📊 Painel de Indicadores")
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM pacientes", conn)
    conn.close()
    
    if not df.empty:
        # Gráficos
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.pie(df, names='setor', title="Pacientes por Setor"))
        c2.plotly_chart(px.histogram(df, x='idade_anos', title="Distribuição por Idade"))
        
        st.markdown("---")
        # Exportação
        col_exp1, col_exp2 = st.columns(2)
        
        # Download CSV
        csv = df.to_csv(index=False).encode('utf-8')
        col_exp1.download_button("📥 Baixar Base Completa (CSV)", csv, "banco_emtn.csv", "text/csv")
        
        # Relatório
        if col_exp2.button("📄 Gerar Relatório Mensal"):
            resumo = f"Relatório Gerencial - {datetime.now().strftime('%m/%Y')}\nTotal de Pacientes: {len(df)}\nEscore Médio: {df['escore_triagem'].mean():.1f}"
            st.text_area("Resumo Mensal:", value=resumo)
    else:
        st.info("Nenhum dado cadastrado ainda.")

else:
    st.title(f"{menu}")
    st.info("Módulo em operação. Utilize a barra lateral para navegar.")
