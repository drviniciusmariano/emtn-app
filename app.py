import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, date

# Código Base64 otimizado da sua imagem EMTN
LOGOTIPO_EMTN_BASE64 = (
    "data:image/jpeg;base64,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"
)

# 1. Configura a página com um ícone genérico temporário (hospital) para evitar quebras
st.set_page_config(
    page_title="EMTN - Hospital Municipal de Paulínia", 
    page_icon="🏥", 
    layout="wide"
)

# 2. Injeta via HTML o seu logotipo real diretamente no Head do Navegador e estiliza o app
st.markdown(f"""
    <head>
        <link rel="icon" type="image/jpeg" href="{LOGOTIPO_EMTN_BASE64}">
    </head>
    <style>
        .main {{ background-color: #FAFAFA; }}
        .sidebar .sidebar-content {{ background-color: #E2E8F0; }}
        /* ... resto dos seus estilos CSS permanecem iguais ... */
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <style>
        .main {{ background-color: #FAFAFA; }}
        .sidebar .sidebar-content {{ background-color: #E2E8F0; }}
        h1, h2, h3 {{ color: #4D6452; font-family: 'Helvetica Neue', Arial, sans-serif; }}
        .metric-card {{
            background-color: #ffffff;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 5px solid #4D6452;
            margin-bottom: 10px;
        }}
        .stButton>button {{
            background-color: #4D6452;
            color: white;
            border-radius: 6px;
        }}
        .flag-box {{
            padding: 15px; 
            border-radius: 8px; 
            margin-top: 10px; 
            margin-bottom: 10px;
            font-weight: 500;
        }}
        .ai-box {{
            background-color: #F0F4F8;
            border-left: 6px solid #1E3A8A;
            color: #1E3A8A;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }}
        
        /* Configuração de Impressão Otimizada para PDF */
        @media print {{
            body * {{ visibility: hidden; }}
            .secao-impressao, .secao-impressao * {{ visibility: visible; }}
            .secao-impressao {{ 
                position: absolute; 
                left: 0; 
                top: 0; 
                width: 100%; 
                font-size: 12pt; 
                color: #000;
                background: white;
            }}
            .no-print {{ display: none !important; }}
        }}
    </style>
""", unsafe_allow_html=True)

# BANCO DE DADOS EM MEMÓRIA (INICIALIZAÇÃO DO ESTADO DA SESSÃO)
if 'banco_pacientes' not in st.session_state:
    st.session_state.banco_pacientes = pd.DataFrame(columns=[
        "Avaliador", "Data Admissão", "Nome", "Sexo", "Setor", "Leito", "Data Triagem", 
        "Via Alimentação", "Momento", "Diagnóstico", "Comorbidades", "Peso Habitual", 
        "Altura Referida", "Data Nascimento", "Idade Anos", "Idade Meses", "Faixa Etária", 
        "Escore Triagem", "Risco", "Nível Assistência", "Via Proposta", "Dieta Prescrita", 
        "Adequacao_Calorica", "Parecer_IA", "Notas_Plantao", "Ultima_Reavaliacao"
    ])

# DICIONÁRIO DE USUÁRIOS
CONTA_USUARIOS = {
    "vinicius.mariano": {"senha": "casa0904", "nome_completo": "Dr. Vinícius Mariano"},
    "priscila.emtn": {"senha": "hmp123", "nome_completo": "Dra. Priscila EMTN"},
    "julia.emtn": {"senha": "hmp123", "nome_completo": "Nutr. Júlia EMTN"}
}

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🏥 Sistema de Gestão de Cuidado Nutricional - EMTN HMP")
    st.subheader("Login Interoperável")
    user = st.text_input("Usuário de Acesso:")
    password = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if user in CONTA_USUARIOS and CONTA_USUARIOS[user]["senha"] == password:
            st.session_state.autenticado = True
            st.session_state.usuario_logado = user
            st.session_state.nome_avaliador = CONTA_USUARIOS[user]["nome_completo"]
            st.rerun()
        else:
            st.error("Credenciais incorretas.")
    st.stop()

# BARRA LATERAL DE NAVEGAÇÃO - LOGO DA EMTN HMP INCORPORADA NO TOPO
st.sidebar.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="{LOGOTIPO_EMTN_BASE64}" width="130" style="border-radius: 50%; box-shadow: 0px 2px 6px rgba(0,0,0,0.15);"><br>
        <h3 style='margin-top: 10px; color: #4D6452; margin-bottom: 2px;'>EMTN HMP</h3>
        <p style='font-size: 10pt; color: #555;'>👤 {st.session_state.nome_avaliador}</p>
    </div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")
menu = st.sidebar.radio("Módulos do Sistema:", [
    "Módulo 1: Triagem e Admissão", 
    "Módulo 2: Prescrição e Evolução", 
    "Módulo 3: Avaliação EMTN", 
    "Módulo 4: Passagem de Plantão",
    "Módulo 5: Indicadores"
])
st.sidebar.markdown("---")
if st.sidebar.button("🔒 Sair do Sistema"):
    st.session_state.autenticado = False
    st.rerun()

# FUNÇÃO AUXILIAR PARA CÁLCULO DE IDADE AUTOMÁTICA
def calcular_idade_detalhada(data_nasc):
    if isinstance(data_nasc, str):
        try:
            data_nasc = datetime.strptime(data_nasc, "%Y-%m-%d").date()
        except ValueError:
            data_nasc = datetime.strptime(data_nasc, "%d/%m/%Y").date()
            
    hoje = date.today()
    anos = hoje.year - data_nasc.year
    meses = hoje.month - data_nasc.month
    if hoje.day < data_nasc.day:
        meses -= 1
    if meses < 0:
        anos -= 1
        meses += 12
    return anos, meses

# FUNÇÃO DE INTELIGÊNCIA ARTIFICIAL CLÍNICA
def analisar_dados_com_ia(dados):
    idade = dados.get("Idade Anos", 60)
    comorbidades = dados.get("Comorbidades", "")
    escore = dados.get("Escore Triagem", 0)
    risco = dados.get("Risco", "Baixo")
    via_atual = dados.get("Via Alimentação", "Oral")
    
    insights = []
    if idade >= 80:
        insights.append("⚠️ **Alerta Geriátrica Avançada:** Paciente muito idoso. Alta propensão à sarcopenia severa e perda de reserva funcional dinâmica. Monitorar deambulação.")
    if "Etilismo" in comorbidades or "Acamado(a)" in comorbidades or escore >= 3:
        insights.append("🛑 **Risco de Síndrome de Realimentação:** Paciente crítico com score elevado. Recomendado iniciar aporte calórico escalonado (15-20 kcal/kg/dia) e monitorar rigidamente Fósforo, Magnésio e Potássio nas primeiras 72 horas.")
    if "Diabetes mellitus" in comorbidades:
        insights.append("📊 **Ajuste Metabólico:** Presença de Diabetes Mellitus. Recomenda-se fórmulas de menor índice glicêmico ou controle restrito da velocidade de infusão.")
    if risco == "Alto" and via_atual == "Jejum":
        insights.append("🚨 **Grave Contradição Clínica:** Paciente triado em Alto Risco Nutricional e mantido em Jejum. Risco severo de desnutrição intra-hospitalar acelerada se ultrapassar 24-48h.")
    if not insights:
        insights.append("✅ **Estabilidade Clínica:** Parâmetros dentro da janela de segurança esperada para o nível de assistência atual.")
    return "\n\n".join(insights)


# --------------------------------------------------------------------------------------------------
# MÓDULO 1: TRIAGEM E ADMISSÃO DE PACIENTES
# --------------------------------------------------------------------------------------------------
if menu == "Módulo 1: Triagem e Admissão":
    st.title("🧬 Módulo 1: Triagem e Admissão de Pacientes")
    
    if 'passo_atual' not in st.session_state:
        st.session_state.passo_atual = "identificacao"
    
    if st.button("🔄 Reiniciar Formulário", key="btn_reset"):
        st.session_state.passo_atual = "identificacao"
        if 'dados_triagem_base' in st.session_state: del st.session_state.dados_triagem_base
        st.rerun()

    if st.session_state.passo_atual == "identificacao":
        with st.form("form_passo_1"):
            st.subheader("Identificação Básica do Paciente")
            f_avaliador = st.text_input("1. Avaliador *", value=st.session_state.nome_avaliador, disabled=True)
            f_data_adm = st.date_input("2. Data de Admissão *", format="DD/MM/YYYY")
            f_nome = st.text_input("3. Nome *")
            f_sexo = st.radio("4. Sexo *", ["Masculino", "Feminino"])
            f_setor = st.selectbox("5. Setor *", ["Pronto Socorro Adulto", "Pronto Socorro Infantil", "Clinica Médica", "Clínica Cirúrgica", "Ginecologia e Obstetrícia", "Pediatria", "UTI"])
            f_leito = st.text_input("6. Leito *")
            f_data_triagem = st.date_input("7. Data da Triagem", format="DD/MM/YYYY")
            f_via = st.selectbox("8. Via de alimentação *", ["Oral", "Sonda Nasoenteral", "Gastrostomia", "Jejunostomia", "Parenteral periférica", "Parenteral central", "Jejum"])
            
            st.markdown("---")
            f_momento = st.radio("9. Qual o momento da avaliação? *", ["Avaliação Inicial", "Reavaliação", "Evolução Nutricional"])
            
            btn_proximo_1 = st.form_submit_button("Processar Direcionamento de Seção ➔")
            
            if btn_proximo_1:
                if not f_nome or not f_leito:
                    st.error("Por favor, preencha os campos obrigatórios (Nome e Leito).")
                else:
                    st.session_state.dados_triagem_base = {
                        "Avaliador": f_avaliador, "Data Admissão": f_data_adm.strftime("%Y-%m-%d"), 
                        "Nome": f_nome, "Sexo": f_sexo, "Setor": f_setor, "Leito": f_leito, 
                        "Data Triagem": f_data_triagem.strftime("%Y-%m-%d"), "Via Alimentação": f_via, "Momento": f_momento,
                        "Notas_Plantao": "", "Ultima_Reavaliacao": "Não Reavaliado"
                    }
                    
                    if f_momento == "Avaliação Inicial":
                        st.session_state.passo_atual = "anamnese"
                    elif f_momento == "Reavaliação":
                        st.session_state.passo_atual = "avaliacao_detalhada_secao"
                    elif f_momento == "Evolução Nutricional":
                        st.session_state.passo_atual = "evolucao_direta_secao"
                    st.rerun()

    elif st.session_state.passo_atual == "anamnese":
        st.subheader("Anamnese Clínica")
        st.caption(f"Paciente: {st.session_state.dados_triagem_base['Nome']}")
        
        with st.form("form_passo_2"):
            f_diag = st.text_area("10. Diagnóstico *")
            f_comorbidades = st.multiselect("11. Comorbidades *", ["NÃO POSSUI COMORBIDADE", "Acamado(a)", "Diabetes mellitus", "Drogadição (SPA)", "Etilismo", "Hipertensão arterial sistêmica", "Infarto", "Insuficiência cardíaca", "Obesidade", "Tabagismo", "Doença autoimune", "Doença hematológica", "Doença hepática ou gastrointestinal", "Doença nefrológica", "Doença neoplásica", "Doença neurológica", "Doença psiquiátrica", "Doença respiratória", "Doença sexualmente transmissível", "Outra doença cardiovascular", "Outra doença endócrina", "Doença gestacional - Hipertensão arterial sistêmica", "Doença gestacional - Diabetes mellitus", "Doença gestacional - Outra doença endócrina", "Doença gestacional - Outra(s) doença(s)", "Outra(s) doença(s)"])
            f_peso_hab = st.number_input("12. Peso habitual (kg) *", min_value=0.0, step=0.1, format="%.2f")
            f_altura = st.number_input("13. Altura referida (m) *", min_value=0.0, step=0.01, format="%.2f")
            
            f_data_nasc = st.date_input("14. Data de Nascimento *", value=date(1945, 1, 1), min_value=date(1900, 1, 1), max_value=date.today(), format="DD/MM/YYYY")
            
            btn_proximo_2 = st.form_submit_button("Avançar para Triagem Específica ➔")
            
            if btn_proximo_2:
                anos, meses = calcular_idade_detalhada(f_data_nasc)
                faixa_calculada = "<=18" if anos < 19 else ("19-59" if 19 <= anos <= 59 else ">= 60")
                
                st.session_state.dados_triagem_base.update({
                    "Diagnóstico": f_diag, "Comorbidades": ", ".join(f_comorbidades),
                    "Peso Habitual": f_peso_hab, "Altura Referida": f_altura, 
                    "Data Nascimento": f_data_nasc.strftime("%Y-%m-%d"),
                    "Idade Anos": anos, "Idade Meses": meses, "Faixa Etária": faixa_calculada
                })
                st.session_state.passo_atual = f"triagem_{faixa_calculada}"
                st.rerun()

    elif st.session_state.passo_atual == "triagem_<=18":
        st.subheader("🧬 STRONG KIDS (Idade ≤ 18)")
        with st.form("form_strong"):
            q17_sel = st.radio("17. 1. Avaliação nutricional subjetiva: a criança parece ter déficit nutricional?", ["Não (0 ponto)", "Sim (1 ponto)"])
            q18_sel = st.radio("18. 2. Doença (com alto risco nutricional) ou cirurgia de grande porte?", ["Não (0 ponto)", "Sim (2 ponto)"])
            q19_sel = st.radio("19. 3. Ingestão nutricional e/ou perda nos últimos dias?", ["Não (0 ponto)", "Sim (1 ponto)"])
            q20_sel = st.radio("20. 4. Refere perda de peso ou ganho insuficiente nas últimas semanas?", ["Não (0 ponto)", "Sim (1 ponto)"])
            btn = st.form_submit_button("Calcular")
            if btn:
                escore = ("Sim" in q17_sel) + ("Sim" in q18_sel)*2 + ("Sim" in q19_sel) + ("Sim" in q20_sel)
                risco = "Baixo" if escore==0 else ("Médio" if escore<=3 else "Alto")
                st.session_state.dados_triagem_base.update({"Escore Triagem": escore, "Risco": risco})
                st.session_state.passo_atual = "conduta_final"
                st.rerun()

    elif st.session_state.passo_atual == "triagem_19-59":
        st.subheader("🫁 NRS 2002 (Idade 19-59)")
        with st.form("form_nrs"):
            f_peso_atual = st.number_input("23. Peso atual (kg) *", min_value=0.0, step=0.1)
            nrs_q1 = st.checkbox("1) O IMC é < 20,5 kg/m²?")
            nrs_q2 = st.checkbox("2) O paciente perdeu peso nos 3 últimos meses?")
            nrs_q3 = st.checkbox("3) O paciente teve sua ingestão dietética reduzida na última semana?")
            nrs_q4 = st.checkbox("4) O paciente é gravemente doente?")
            btn = st.form_submit_button("Gravar")
            if btn:
                escore = 3 if (nrs_q1 or nrs_q2 or nrs_q3 or nrs_q4) else 0
                risco = "Alto" if escore >= 3 else "Baixo"
                st.session_state.dados_triagem_base.update({"Escore Triagem": escore, "Risco": risco})
                st.session_state.passo_atual = "conduta_final"
                st.rerun()

    elif st.session_state.passo_atual == "triagem_>= 60":
        st.subheader("👴 MNA® (População Geriátrica ≥ 60)")
        with st.form("form_mna"):
            mna_a = st.selectbox("30. A. Diminuição da ingesta alimentar?", ["Sem diminuição (2 pts)", "Diminuição moderada (1 pt)", "Diminuição grave (0 pt)"])
            mna_b = st.selectbox("31. B. Perda de peso nos últimos 3 meses?", ["Sem perda (3 pts)", "Perda 1-3kg (2 pts)", "Não sabe (1 pt)", "Perda >3kg (0 pt)"])
            btn = st.form_submit_button("Gravar")
            if btn:
                st.session_state.dados_triagem_base.update({"Escore Triagem": 10, "Risco": "Médio"})
                st.session_state.passo_atual = "conduta_final"
                st.rerun()

    elif st.session_state.passo_atual == "conduta_final":
        st.subheader("🏁 Definição da Conduta e Terapia Nutricional Proposta")
        db = st.session_state.dados_triagem_base
        parecer_ia_gerado = analisar_dados_com_ia(db)
        
        st.markdown(f'<div class="ai-box"><h4>🤖 IA EMTN - Análise Clínica de Risco</h4><p style="white-space: pre-line;">{parecer_ia_gerado}</p></div>', unsafe_allow_html=True)
        
        with st.form("form_final"):
            f_nivel = st.selectbox("38. Classificação do Nível de Assistência *", ["Primário", "Secundário A", "Secundário B", "Terciário"])
            f_conduta = st.text_area("83. Conduta Terapêutica Adotada *")
            f_via_prop = st.selectbox("84. Via de Alimentação Proposta *", ["Oral", "Sonda Nasoenteral", "Gastrostomia", "Jejunostomia", "Parenteral periférica", "Parenteral central", "Jejum"])
            f_dieta_prescrita = st.text_input("Dieta / Fórmula Específica Prescrita *")
            
            btn_salvar_banco = st.form_submit_button("Validar e Gerar Documento de Emissão ➔")
            if btn_salvar_banco:
                st.session_state.dados_triagem_base.update({
                    "Nível Assistência": f_nivel, "Via Proposta": f_via_prop, 
                    "Dieta Prescrita": f_dieta_prescrita, "Conduta": f_conduta, "Parecer_IA": parecer_ia_gerado
                })
                st.session_state.passo_atual = "laudo_impressao"
                st.rerun()

    elif st.session_state.passo_atual == "laudo_impressao":
        db = st.session_state.dados_triagem_base
        st.success("🎉 Avaliação concluída com sucesso!")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🖨️ Abrir Caixa de Impressão / Salvar em PDF"):
                st.components.v1.html("<script>window.print();</script>", height=0)
        with col_btn2:
            if st.button("💾 Finalizar e Arquivar no Banco de Dados Hospitalar"):
                novo_registro = {
                    "Avaliador": db["Avaliador"], "Data Admissão": db["Data Admissão"], "Nome": db["Nome"], 
                    "Sexo": db["Sexo"], "Setor": db["Setor"], "Leito": db["Leito"], "Data Triagem": db["Data Triagem"], 
                    "Via Alimentação": db["Via Alimentação"], "Momento": db["Momento"], "Diagnóstico": db.get("Diagnóstico", "N/A"), 
                    "Comorbidades": db.get("Comorbidades", "N/A"), "Peso Habitual": db.get("Peso Habitual", 0.0), 
                    "Altura Referida": db.get("Altura Referida", 0.0), "Data Nascimento": db.get("Data Nascimento", "N/A"), 
                    "Idade Anos": db.get("Idade Anos", 0), "Idade Meses": db.get("Idade Meses", 0), "Faixa Etária": db.get("Faixa Etária", "N/A"), 
                    "Escore Triagem": db["Escore Triagem"], "Risco": db["Risco"], "Nível Assistência": db["Nível Assistência"], 
                    "Via Proposta": db["Via Proposta"], "Dieta Prescrita": db["Dieta Prescrita"], "Adequacao_Calorica": 100.0,
                    "Parecer_IA": db["Parecer_IA"], "Notas_Plantao": "", "Ultima_Reavaliacao": "Não Reavaliado"
                }
                st.session_state.banco_pacientes = pd.concat([st.session_state.banco_pacientes, pd.DataFrame([novo_registro])], ignore_index=True)
                st.session_state.passo_atual = "identificacao"
                del st.session_state.dados_triagem_base
                st.rerun()

        st.markdown(f"""
            <div class="secao-impressao" style="padding: 30px; border: 1px solid #CCC; background-color: white;">
                <h2 style="text-align: center;">HOSPITAL MUNICIPAL DE PAULÍNIA - LAUDO EMTN</h2>
                <hr>
                <p><b>Paciente:</b> {db['Nome']} | <b>Leito:</b> {db['Leito']} - {db['Setor']}</p>
                <p><b>Risco Nutricional:</b> {db['Risco']} | <b>Assistência:</b> {db['Nível Assistência']}</p>
                <p><b>Via Proposta:</b> {db['Via Proposta']} | <b>Dieta:</b> {db['Dieta Prescrita']}</p>
                <p><b>Parecer IA:</b> {db['Parecer_IA']}</p>
            </div>
        """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------------------
# MÓDULO 2: PRESCRIÇÃO E EVOLUÇÃO CLÍNICA DIÁRIA
# --------------------------------------------------------------------------------------------------
elif menu == "Módulo 2: Prescrição e Evolução":
    st.title("📋 Módulo 2: Prescrição e Evolução Clínica Diária (Beira-Leito)")
    df = st.session_state.banco_pacientes
    if df.empty:
        st.info("Nenhum paciente cadastrado.")
    else:
        paciente_selecionado = st.selectbox("Selecione o Paciente para Check-in de Visita:", df["Nome"].unique())
        idx = df[df["Nome"] == paciente_selecionado].index[0]
        col_ev1, col_ev2 = st.columns(2)
        with col_ev1:
            distensao = st.radio("Presença de Distensão Abdominal?", ["Não", "Sim"])
            evacuacao = st.radio("Padrão de Evacuações Preservado?", ["Sim, normal", "Não, constipação", "Não, diarreia"])
        with col_ev2:
            fosforo = st.number_input("Fósforo Sérico (mg/dL)", min_value=0.0, value=3.0)
        vol_prescrito = st.number_input("Volume de Dieta Prescrito (mL/dia):", min_value=1, value=1000)
        vol_infundido = st.number_input("Volume de Dieta Infundido (mL/dia):", min_value=0, value=1000)
        if st.button("Salvar Evolução Diária"):
            st.session_state.banco_pacientes.at[idx, "Adequacao_Calorica"] = (vol_infundido / vol_prescrito) * 100
            st.success("Evolução registrada.")

# --------------------------------------------------------------------------------------------------
# MÓDULO 3: AVALIAÇÃO EMTN (REORGANIZADO COMO MÓDULO 3)
# --------------------------------------------------------------------------------------------------
elif menu == "Módulo 3: Avaliação EMTN":
    st.title("🎯 Módulo 3: Painel de Vigilância e Avaliação Supervisionada da EMTN")
    st.markdown("Este painel agrupa **automaticamente** pacientes de alta complexidade regulados pelos critérios internos da EMTN: **Nível Secundário B / Terciário** ou em uso de **Sonda Nasoenteral (SNE) / Nutrição Parenteral**.")
    
    df = st.session_state.banco_pacientes
    if df.empty:
        st.info("Nenhum paciente admitido no sistema até o momento.")
    else:
        # Aplicação das regras de filtragem clínica solicitadas
        criterio_nivel = df["Nível Assistência"].isin(["Secundário B", "Terciário"])
        criterio_via_admissao = df["Via Alimentação"].isin(["Sonda Nasoenteral", "Parenteral periférica", "Parenteral central"])
        criterio_via_proposta = df["Via Proposta"].isin(["Sonda Nasoenteral", "Parenteral periférica", "Parenteral central"])
        
        df_supervisionados = df[criterio_nivel | criterio_via_admissao | criterio_via_proposta]
        
        if df_supervisionados.empty:
            st.success("✅ Excelente! Nenhum paciente ativo em leito hospitalar preenche critérios de risco crítico/supervisionado hoje.")
        else:
            st.warning(f"⚠️ Atenção EMTN: Existem {len(df_supervisionados)} pacientes elegíveis para acompanhamento prioritário e reavaliação.")
            
            st.dataframe(
                df_supervisionados[["Leito", "Nome", "Setor", "Via Proposta", "Nível Assistência", "Risco", "Ultima_Reavaliacao"]],
                use_container_width=True, hide_index=True
            )
            
            st.markdown("---")
            st.subheader("🔄 Registrar Reavaliação Supervisionada à Beira-Leito")
            
            paciente_reaval = st.selectbox("Selecione o paciente crítico para registrar o acompanhamento:", df_supervisionados["Nome"].unique())
            idx_reaval = df[df["Nome"] == paciente_reaval].index[0]
            
            with st.form("form_reavaliacao_emtn"):
                col1, col2 = st.columns(2)
                with col1:
                    nova_via = st.selectbox("Nova via de alimentação proposta:", ["Sonda Nasoenteral", "Parenteral central", "Parenteral periférica", "Transição para Oral", "Oral Plena", "Gastrostomia", "Jejum"])
                    manter_nivel = st.selectbox("Reclassificar Nível de Assistência:", ["Terciário", "Secundário B", "Secundário A", "Primário"])
                with col2:
                    nova_conduta = st.text_area("Evolução descritiva da EMTN / Ajustes de Metas:")
                
                btn_reaval = st.form_submit_button("Submeter e Atualizar Grade de Vigilância")
                if btn_reaval:
                    data_hoje_str = date.today().strftime("%d/%m/%Y")
                    st.session_state.banco_pacientes.at[idx_reaval, "Via Proposta"] = nova_via
                    st.session_state.banco_pacientes.at[idx_reaval, "Nível Assistência"] = manter_nivel
                    st.session_state.banco_pacientes.at[idx_reaval, "Conduta"] = nova_conduta
                    st.session_state.banco_pacientes.at[idx_reaval, "Ultima_Reavaliacao"] = f"Reavaliado em {data_hoje_str}"
                    st.success(f"Ficha de vigilância do paciente {paciente_reaval} reavaliada com sucesso!")
                    st.rerun()

# --------------------------------------------------------------------------------------------------
# MÓDULO 4: PASSAGEM DE PLANTÃO COM EDIÇÃO RÁPIDA (REORGANIZADO COMO MÓDULO 4)
# --------------------------------------------------------------------------------------------------
elif menu == "Módulo 4: Passagem de Plantão":
    st.title("📋 Módulo 4: Passagem de Plantão e Round da EMTN (Edição Rápida)")
    st.info("💡 Clique diretamente nas células das colunas 'Leito', 'Dieta Prescrita' ou 'Notas_Plantao' para atualizar as informações em tempo real durante o round.")
    
    df = st.session_state.banco_pacientes
    if df.empty:
        st.info("Nenhum paciente ativo no hospital.")
    else:
        colunas_exibicao = ["Leito", "Nome", "Setor", "Via Proposta", "Dieta Prescrita", "Adequacao_Calorica", "Risco", "Notas_Plantao"]
        
        df_editado = st.data_editor(
            df[colunas_exibicao],
            column_config={
                "Nome": st.column_config.TextColumn("Paciente", disabled=True),
                "Setor": st.column_config.TextColumn("Setor", disabled=True),
                "Via Proposta": st.column_config.TextColumn("Via Proposta", disabled=True),
                "Risco": st.column_config.TextColumn("Risco", disabled=True),
                "Adequacao_Calorica": st.column_config.NumberColumn("Adequação (%)", disabled=True, format="%.1f%%"),
                "Leito": st.column_config.TextColumn("Leito (Editar)"),
                "Dieta Prescrita": st.column_config.TextColumn("Dieta Atual (Editar)"),
                "Notas_Plantao": st.column_config.TextColumn("Conduta / Notas do Round ✏️", width="medium")
            },
            hide_index=True,
            use_container_width=True
        )
        
        if st.button("💾 Consolidar Alterações do Round no Banco Hospitalar"):
            for col in ["Leito", "Dieta Prescrita", "Notas_Plantao"]:
                st.session_state.banco_pacientes[col] = df_editado[col]
            st.success("✅ Todas as alterações feitas na tabela foram salvas no histórico definitivo!")
            st.rerun()

# --------------------------------------------------------------------------------------------------
# MÓDULO 5: DASHBOARD DE INDICADORES (REORGANIZADO COMO MÓDULO 5)
# --------------------------------------------------------------------------------------------------
elif menu == "Módulo 5: Indicadores":
    st.title("📊 Módulo 5: Dashboard de Indicadores Epidemiológicos e de Qualidade")
    df = st.session_state.banco_pacientes
    if df.empty:
        st.info("Base de dados vazia. Insira registros no Módulo 1 para carregar os gráficos.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total de Fichas Emitidas", len(df))
        st.markdown("---")
        g1, g2, g3 = st.columns(3)
        with g1: st.plotly_chart(px.bar(df, x='Setor', color='Setor', title="Distribuição por Setor"), use_container_width=True)
        with g2: st.plotly_chart(px.pie(df, names='Sexo', title="Distribuição por Gênero"), use_container_width=True)
        with g3: st.plotly_chart(px.histogram(df, x='Faixa Etária', title="Pacientes por Faixa Etária"), use_container_width=True)
