import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime, date
from fpdf import FPDF

# --- CONFIGURAÇÃO DO BANCO DE DADOS (SQLITE) ---
DB_NAME = "emtn_hmp_prontuario.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, idade_anos INTEGER, data_admissao DATE, setor TEXT, 
            leito TEXT, escore_triagem INTEGER, risco TEXT, via_proposta TEXT, 
            nivel_assistencia TEXT, comorbidades TEXT, data_gravacao DATETIME
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- INTERFACE E AUTENTICAÇÃO ---
st.set_page_config(page_title="Gestão EMTN HMP", layout="wide")
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🏥 Sistema de Gestão EMTN - HMP")
    if st.text_input("Senha de Acesso", type="password") == "hmp2026":
        st.session_state.autenticado = True
        st.rerun()
    st.stop()

# --- MENU LATERAL ---
menu = st.sidebar.radio("Navegação do Sistema", [
    "Módulo 1: Triagem", "Módulo 2: Evolução", "Módulo 3: Avaliação EMTN", 
    "Módulo 4: Passagem de Plantão", "Módulo 5: Indicadores"
])

# --- LÓGICA DOS MÓDULOS ---

if menu == "Módulo 1: Triagem":
    st.title("🧬 Módulo 1: Admissão e Triagem (NRS 2002)")
    with st.form("form_triagem"):
        nome = st.text_input("Nome do Paciente")
        idade = st.number_input("Idade", 0, 120)
        setor = st.selectbox("Setor", ["UTI", "Clínica Médica", "Cirúrgica"])
        
        st.subheader("27. Deterioração Nutricional (0-3 pontos)")
        det = st.selectbox("Grau", [0, 1, 2, 3])
        
        st.subheader("28. Gravidade da Doença (0-3 pontos)")
        grav = st.selectbox("Grau", [0, 1, 2, 3])
        
        if st.form_submit_button("Salvar e Arquivar"):
            escore = det + grav + (1 if idade >= 70 else 0)
            risco = "Risco Nutricional (Escore >= 3)" if escore >= 3 else "Sem Risco"
            
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO pacientes (nome, idade_anos, setor, escore_triagem, risco, data_gravacao) VALUES (?,?,?,?,?,?)",
                           (nome, idade, setor, escore, risco, datetime.now()))
            conn.commit()
            conn.close()
            st.success(f"Paciente {nome} arquivado com sucesso!")

elif menu == "Módulo 5: Indicadores":
    st.title("📊 Painel de Indicadores e Gestão")
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM pacientes", conn)
    conn.close()
    
    if not df.empty:
        # Gráficos
        col1, col2 = st.columns(2)
        col1.plotly_chart(px.pie(df, names='setor', title="Distribuição por Setor"))
        col2.plotly_chart(px.histogram(df, x='idade_anos', title="Faixa Etária"))
        
        # Ações de Exportação
        st.subheader("⚙️ Ações de Relatório Mensal")
        c1, c2 = st.columns(2)
        
        csv = df.to_csv(index=False).encode('utf-8')
        c1.download_button("📥 Exportar Banco de Dados (CSV)", csv, "banco_completo.csv", "text/csv")
        
        if c2.button("📄 Gerar Relatório Consolidado"):
            relatorio = f"RELATÓRIO MENSAL EMTN\nTotal Pacientes: {len(df)}\nMédia de Score: {df['escore_triagem'].mean():.1f}"
            st.text_area("Relatório de Indicadores:", value=relatorio, height=150)
    else:
        st.info("Nenhum registro encontrado no banco de dados.")

else:
    st.title(f"{menu}")
    st.info("Funcionalidade em desenvolvimento / Módulo operacional.")

# --- INSTRUÇÃO DE USO ---
st.sidebar.markdown("---")
st.sidebar.caption("Sistema interno Hospital Municipal de Paulínia (HMP).")
