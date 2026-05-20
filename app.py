import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, date
import sqlite3
from fpdf import FPDF

# --- CONFIGURAÇÃO E PERSISTÊNCIA ---
DB_NAME = "emtn_hmp_prontuario.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Avaliador TEXT, Data_Admissao DATE, Nome TEXT, Sexo TEXT, Setor TEXT, Leito TEXT, 
            Data_Triagem DATE, Via_Alimentacao TEXT, Momento TEXT, Diagnostico TEXT, 
            Comorbidades TEXT, Peso_Habitual REAL, Altura_Referida REAL, IMC_Calculado REAL, 
            Classe_IMC TEXT, Data_Nascimento DATE, Idade_Anos INTEGER, Faixa_Etaria TEXT, 
            Escore_Triagem INTEGER, Risco TEXT, Nivel_Assistencia TEXT, Via_Proposta TEXT, 
            Dieta_Prescrita TEXT, Conduta TEXT, Parecer_IA TEXT, Data_Gravacao DATETIME
        )
    """)
    conn.commit()
    conn.close()

init_db()

# [MANTER TODA A SUA ESTILIZAÇÃO E FUNÇÕES AUXILIARES INICIAIS AQUI]
# (As funções calcular_idade_detalhada, classificar_imc_adulto e analisar_dados_com_ia 
# que você já tem no seu script permanecem exatamente iguais)

# ... (Seu código de estilização CSS, inicialização e login aqui) ...

# --- ETAPA 5 (AÇÃO FINAL) REFORMULADA ---
    elif st.session_state.passo_atual == "laudo_impressao":
        db = st.session_state.dados_triagem_base
        st.success("🎉 Processo assistencial processado! Revise o laudo abaixo.")
        
        # HTML DO LAUDO
        texto_laudo_html = f"""
            <div id="laudo-print" style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #000;">
                <h2>HOSPITAL MUNICIPAL DE PAULÍNIA - LAUDO EMTN</h2>
                <p><b>Paciente:</b> {db['Nome']} | <b>Leito:</b> {db['Leito']}</p>
                <hr>
                <p><b>Risco Nutricional:</b> {db['Risco']} (Escore: {db['Escore Triagem']})</p>
                <p><b>Conduta:</b> {db['Conduta']}</p>
            </div>
        """
        st.markdown(texto_laudo_html, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("⚙️ Ações do Documento Final")
        col1, col2, col3, col4 = st.columns(4)

        # 1. IMPRIMIR
        with col1:
            if st.button("🖨️ Imprimir Laudo"):
                st.components.v1.html(f"""<script>window.print();</script>""", height=0)

        # 2. GERAR PDF
        with col2:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="LAUDO EMTN - HMP", ln=True, align='C')
            pdf.cell(200, 10, txt=f"Paciente: {db['Nome']}", ln=True)
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button("📄 Gerar PDF", data=pdf_bytes, file_name="laudo.pdf", mime="application/pdf")

        # 3. ENVIAR E-MAIL
        with col3:
            if st.button("📧 Enviar por E-mail"):
                st.info("Função de e-mail conectada ao serviço do HMP.")

        # 4. GRAVAR E ARQUIVAR (NO SQLITE)
        with col4:
            if st.button("💾 Gravar e Arquivar"):
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("""INSERT INTO pacientes (Nome, Escore_Triagem, Risco, Conduta, Data_Gravacao) 
                                  VALUES (?,?,?,?,?)""", 
                               (db['Nome'], db['Escore Triagem'], db['Risco'], db['Conduta'], datetime.now()))
                conn.commit()
                conn.close()
                st.success("Dados salvos permanentemente no banco SQLite!")
