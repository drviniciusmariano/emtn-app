import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# CONFIGURAÇÕES DA PÁGINA
st.set_page_config(page_title="EMTN - HMP", page_icon="🏥", layout="wide")

# ESTILIZAÇÃO CUSTOMIZADA (IDENTIDADE VISUAL DA EMTN HMP)
st.markdown("""
    <style>
        .main { background-color: #FAFAFA; }
        .sidebar .sidebar-content { background-color: #E2E8F0; }
        h1, h2, h3 { color: #4D6452; font-family: 'Helvetica Neue', Arial, sans-serif; }
        .metric-card {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 5px solid #4D6452;
            margin-bottom: 10px;
        }
        .stButton>button {
            background-color: #4D6452;
            color: white;
            border-radius: 6px;
        }
    </style>
""", unsafe_allow_html=True)

# BANCO DE DADOS EM MEMÓRIA (INICIALIZAÇÃO DO ESTADO DA SESSÃO)
if 'banco_pacientes' not in st.session_state:
    st.session_state.banco_pacientes = pd.DataFrame(columns=[
        "Avaliador", "Data Admissão", "Nome", "Sexo", "Setor", "Leito", "Data Triagem", 
        "Via Alimentação", "Momento", "Diagnóstico", "Comorbidades", "Peso Habitual", 
        "Altura Referida", "Data Nascimento", "Idade", "Faixa Etária", "Escore Triagem", 
        "Risco", "Nível Assistência", "Via Proposta", "Dieta Prescrita", "Adequacao_Calorica"
    ])

# DICIONÁRIO DE USUÁRIOS PERMANECIDO CONFORME ACORDADO
CONTA_USUARIOS = {
    "vinicius.mariano": {"senha": "casa0904", "nome_completo": "Dr. Vinícius Mariano"},
    "priscila.emtn": {"senha": "hmp123", "nome_completo": "Dra. Priscila EMTN"},
    "julia.emtn": {"senha": "hmp123", "nome_completo": "Nutr. Júlia EMTN"}
}

# CONTROLE DE AUTENTICAÇÃO SIMPLES
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

# BARRA LATERAL DE NAVEGAÇÃO
st.sidebar.markdown(f"<h3 style='text-align: center; color: #4D6452;'>EMTN HMP</h3><p style='text-align: center;'>👤 {st.session_state.nome_avaliador}</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")
menu = st.sidebar.radio("Módulos do Sistema:", [
    "Módulo 1: Triagem e Admissão", 
    "Módulo 2: Prescrição e Evolução", 
    "Módulo 3: Passagem de Plantão", 
    "Módulo 4: Dashboard de Indicadores"
])
st.sidebar.markdown("---")
if st.sidebar.button("🔒 Sair do Sistema"):
    st.session_state.autenticado = False
    st.rerun()

# --------------------------------------------------------------------------------------------------
# MÓDULO 1: TRIAGEM E ADMISSÃO DE PACIENTES
# --------------------------------------------------------------------------------------------------
if menu == "Módulo 1: Triagem e Admissão":
    st.title("🧬 Módulo 1: Triagem e Admissão de Pacientes")
    st.markdown("Ficha de admissão padronizada EMTN com aplicação imediata de algoritmos preditivos de risco.")
    
    with st.form("form_admissao"):
        st.subheader("Identificação e Dados Iniciais")
        # Sequência exata do formulário PDF fornecido
        f_avaliador = st.text_input("1. Avaliador *", value=st.session_state.nome_avaliador, disabled=True)
        f_data_adm = st.date_input("2. Data de Admissão *")
        f_nome = st.text_input("3. Nome *")
        f_sexo = st.radio("4. Sexo *", ["Masculino", "Feminino"])
        f_setor = st.selectbox("5. Setor *", ["Pronto Socorro Adulto", "Pronto Socorro Infantil", "Clinica Médica", "Clínica Cirúrgica", "Ginecologia e Obstetrícia", "Pediatria", "UTI"])
        f_leito = st.text_input("6. Leito *")
        f_data_triagem = st.date_input("7. Data da Triagem")
        f_via = st.selectbox("8. Via de alimentação *", ["Oral", "Sonda Nasoenteral", "Gastrostomia", "Jejunostomia", "Parenteral periférica", "Parenteral central", "Jejum"])
        f_momento = st.selectbox("9. Momento *", ["Avaliação Inicial", "Reavaliação", "Evolução Nutricional"])
        
        st.markdown("---")
        st.subheader("Anamnese")
        f_diag = st.text_area("10. Diagnóstico *")
        f_comorbidades = st.multiselect("11. Comorbidades *", ["NÃO POSSUI COMORBIDADE", "Acamado(a)", "Diabetes mellitus", "Drogadição (SPA)", "Etilismo", "Hipertensão arterial sistemica", "Infarto", "Insuficiência cardíaca", "Obesidade", "Tabagismo", "Doença autoimune", "Doença hematológica", "Doença hepática ou gastrointestinal", "Doença nefrológica", "Doença neoplásica", "Doença neurológica", "Doença psiquiátrica", "Doença respiratória", "Doença sexualmente transmissível"])
        f_peso_hab = st.number_input("12. Peso habitual (kg) *", min_value=0.0, step=0.1, format="%.2f")
        f_altura = st.number_input("13. Altura referida (m) *", min_value=0.0, step=0.01, format="%.2f")
        f_data_nasc = st.date_input("14. Data de Nascimento *")
        f_idade_texto = st.text_input("15. Idade * (Descreva sempre meses ou anos)")
        f_faixa = st.radio("16. Faixa Etária *", ["<=18", "19-59", ">= 60"])
        
        st.markdown("---")
        # DIRECIONAMENTO CONFORME FAIXA ETÁRIA DO PROTOCOLO ORIGINAL
        escore_calculado = 0
        risco_final = "Baixo"
        
        if f_faixa == "<=18":
            st.subheader("Screening Tool Risk Nutritional Status and Growth - STRONG KIDS")
            q17 = st.radio("17. 1. Avaliação nutricional subjetiva: a criança parece ter déficit nutricional?", ["Não (0 ponto)", "Sim (1 ponto)"])
            q18 = st.radio("18. 2. Doença (com alto risco nutricional) ou cirurgia de grande porte?", ["Não (0 ponto)", "Sim (2 ponto)"])
            q19 = st.radio("19. 3. Ingestão nutricional e/ou perda nos últimos dias?", ["Não (0 ponto)", "Sim (1 ponto)"])
            q20 = st.radio("20. 4. Refere perda de peso ou ganho insuficiente nas últimas semanas?", ["Não (0 ponto)", "Sim (1 ponto)"])
            escore_calculado = int(q17[5]) + int(q18[5]) + int(q19[5]) + int(q20[5])
            if escore_calculado >= 4: risco_final = "Alto"
            elif escore_calculado >= 1: risco_final = "Médio"
            
        elif f_faixa == "19-59":
            st.subheader("Triagem Nutricional - NRS 2002")
            st.info("Etapa 1. Triagem inicial")
            nrs_q1 = st.checkbox("O IMC é < 20,5 kg/m²?")
            nrs_q2 = st.checkbox("O paciente perdeu peso nos 3 últimos meses?")
            nrs_q3 = st.checkbox("O paciente teve sua ingestão dietética reduzida na última semana?")
            nrs_q4 = st.checkbox("O paciente é gravemente doente?")
            
            if nrs_q1 or nrs_q2 or nrs_q3 or nrs_q4:
                st.info("Etapa 2. Triagem final ativa")
                q27 = st.selectbox("27. Deterioração do estado nutricional", ["Ausente (0 ponto)", "Leve (1 ponto)", "Moderado (2 pontos)", "Grave (3 pontos)"])
                q28 = st.selectbox("28. Gravidade da doença (grau de estresse)", ["Ausente (0 ponto)", "Leve (1 ponto)", "Moderado (2 pontos)", "Grave (3 pontos)"])
                escore_calculado = int(q27[8]) + int(q28[8])
                if escore_calculado >= 3: risco_final = "Alto"
                else: risco_final = "Médio"
                
        elif f_faixa == ">= 60":
            st.subheader("Mini Nutritional Assessment - MNA®")
            mna_a = st.selectbox("A. Diminuição da ingesta alimentar nos últimos 3 meses por perda de apetite?", ["Sem diminuição (0 ponto)", "Diminuição moderada (1 ponto)", "Diminuição grave (2 pontos)"])
            mna_b = st.selectbox("B. Perda de peso nos últimos 3 meses?", ["Perda > 3kg (0 ponto)", "Não sabe (1 ponto)", "Perda entre 1 e 3kg (2 pontos)", "Sem perda de peso (3 pontos)"])
            mna_c = st.selectbox("C. Mobilidade *", ["Restrito ao leito ou cadeira (0 ponto)", "Deambula mas não sai de casa (1 ponto)", "Normal (2 pontos)"])
            mna_d = st.selectbox("D. Passou por algum estresse psicológico ou doença aguda?", ["Sim (0 ponto)", "Não (2 pontos)"])
            mna_e = st.selectbox("E. Problemas neuropsicológicos?", ["Demência ou depressão grave (0 ponto)", "Demência ligeira (1 ponto)", "Sem problemas (2 pontos)"])
            mna_f = st.selectbox("F. Índice de Massa Corporal - IMC", ["IMC < 19 (0 ponto)", "19 <= IMC < 21 (1 ponto)", "21 <= IMC < 23 (2 pontos)", "IMC >= 23 (3 pontos)"])
            escore_calculado = int(mna_a[-8]) + int(mna_b[-8]) + int(mna_c[-8]) + int(mna_d[-8]) + int(mna_e[-8]) + int(mna_f[-8])
            if escore_calculado <= 7: risco_final = "Alto"
            elif escore_calculado <= 11: risco_final = "Médio"
            else: risco_final = "Baixo"

        st.markdown("---")
        st.subheader("Terapia Nutricional Proposta")
        f_nivel = st.selectbox("38. Nível de Assistência *", ["Primário", "Secundário A", "Secundário B", "Terciário"])
        f_via_prop = st.selectbox("84. Via de alimentação proposta *", ["Oral", "Sonda Nasoenteral", "Gastrostomia", "Jejunostomia", "Parenteral periférica", "Parenteral central", "Jejum"])
        f_dieta_prescrita = st.text_input("Dieta / Fórmula Específica Prescrita *")
        
        btn_admitir = st.form_submit_button("Salvar Admissão e Processar Alertas")
        
        if btn_admitir:
            # Cálculo Automatizado de IMC
            imc_calculado = 0.0
            if f_altura > 0:
                imc_calculado = f_peso_hab / (f_altura ** 2)
            
            # Cálculo de Meta Calórica Dinâmica Padrão do Manual do HMP
            meta_calorica_sugerida = f_peso_hab * 25.0 if f_peso_hab > 0 else 0.0
            
            novo_paciente = {
                "Avaliador": st.session_state.nome_avaliador, "Data Admissão": str(f_data_adm), "Nome": f_nome, 
                "Sexo": f_sexo, "Setor": f_setor, "Leito": f_leito, "Data Triagem": str(f_data_triagem), 
                "Via Alimentação": f_via, "Momento": f_momento, "Diagnóstico": f_diag, "Comorbidades": ", ".join(f_comorbidades), 
                "Peso Habitual": f_peso_hab, "Altura Referida": f_altura, "Data Nascimento": str(f_data_nasc), 
                "Idade": f_idade_texto, "Faixa Etária": f_faixa, "Escore Triagem": escore_calculado, "Risco": risco_final, 
                "Nível Assistência": f_nivel, "Via Proposta": f_via_prop, "Dieta Prescrita": f_dieta_prescrita, "Adequacao_Calorica": 100.0
            }
            
            st.session_state.banco_pacientes = pd.concat([st.session_state.banco_pacientes, pd.DataFrame([novo_paciente])], ignore_index=True)
            st.success(f"Paciente {f_nome} admitido com sucesso no sistema!")
            
            # ALERTA VISUAL SE FOR TERCIÁRIO / RISCO ALTO
            if f_nivel == "Terciário" or risco_final == "Alto":
                st.markdown(f"<div style='padding:20px; background-color:#F8D7DA; color:#721C24; border-radius:8px; font-weight:bold; border-left:8px solid #DC3545;'>🛑 ALERTA DE RISCO CRÍTICO (NÍVEL TERCIÁRIO): Paciente {f_nome} classificado em Alto Risco. Priorizar avaliação clínica em até 24 horas!</div>", unsafe_allow_html=True)

# --------------------------------------------------------------------------------------------------
# MÓDULO 2: PRESCRIÇÃO E EVOLUÇÃO CLÍNICA DIÁRIA
# --------------------------------------------------------------------------------------------------
elif menu == "Módulo 2: Prescrição e Evolução":
    st.title("📋 Módulo 2: Prescrição e Evolução Clínica Diária (Beira-Leito)")
    df = st.session_state.banco_pacientes
    
    if df.empty:
        st.info("Nenhum paciente cadastrado para evolução. Realize a admissão no Módulo 1.")
    else:
        paciente_selecionado = st.selectbox("Selecione o Paciente para Check-in de Visita:", df["Nome"].unique())
        idx = df[df["Nome"] == paciente_selecionado].index[0]
        
        st.markdown(f"### Guia Rápido de Visita Diária: **{paciente_selecionado}**")
        
        col_ev1, col_ev2 = st.columns(2)
        with col_ev1:
            st.markdown("#### Parâmetros de Tolerância Gastrointestinal")
            distensao = st.radio("Presença de Distensão Abdominal?", ["Não", "Sim"])
            evacuacao = st.radio("Padrão de Evacuações Preservado?", ["Sim, normal", "Não, constipação", "Não, diarreia"])
            residuo = st.number_input("Volume de Resíduo Gástrico Aferido (mL):", min_value=0, value=0)
            
        with col_ev2:
            st.markdown("#### Painel Laboratorial Crítico (Vigilância de Realimentação)")
            fosforo = st.number_input("Fósforo Sérico (mg/dL) - Valor de referência: 2.5 - 4.5", min_value=0.0, value=3.0, step=0.1)
            magnesio = st.number_input("Magnésio Sérico (mg/dL) - Valor de referência: 1.6 - 2.6", min_value=0.0, value=2.0, step=0.1)
            potassio = st.number_input("Potássio Sérico (mEq/L) - Valor de referência: 3.5 - 5.0", min_value=0.0, value=4.0, step=0.1)
            
            # Disparadores de segurança de eletrólitos
            if fosforo < 2.5 or magnesio < 1.6 or potassio < 3.5:
                st.markdown("<div style='background-color:#FFF3CD; padding:10px; border-left:4px solid #FFC107; color:#856404; font-weight:bold;'>⚠️ RISCO DE SÍNDROME DE REALIMENTAÇÃO: Níveis críticos de eletrólitos identificados. Monitorar infusão de calorias com moderação!</div>", unsafe_allow_html=True)
                
        st.markdown("---")
        st.markdown("#### Evolução de Metas")
        vol_prescrito = st.number_input("Volume de Dieta Prescrito (mL/dia):", min_value=1, value=1000)
        vol_infundido = st.number_input("Volume de Dieta Efetivamente Infundido Real (mL/dia):", min_value=0, value=1000)
        
        if st.button("Salvar Evolução Diária"):
            adequacao = (vol_infundido / vol_prescrito) * 100
            st.session_state.banco_pacientes.at[idx, "Adequacao_Calorica"] = adequacao
            st.success(f"Evolução registrada. Taxa de adequação do paciente atualizada para {adequacao:.1f}%")

# --------------------------------------------------------------------------------------------------
# MÓDULO 3: PASSAGEM DE PLANTÃO (MURAL DIGITAL DE SEGURANÇA)
# --------------------------------------------------------------------------------------------------
elif menu == "Módulo 3: Passagem de Plantão":
    st.title("📋 Módulo 3: Passagem de Plantão (Mural Digital)")
    df = st.session_state.banco_pacientes
    
    setores_oficiais = ["Pronto Socorro Adulto", "Pronto Socorro Infantil", "Clinica Médica", "Clínica Cirúrgica", "Ginecologia e Obstetrícia", "Pediatria", "UTI"]
    abas = st.tabs(setores_oficiais)
    
    for i, setor in enumerate(setores_oficiais):
        with abas[i]:
            df_filtrado = df[df['Setor'] == setor]
            st.markdown(f"### Ala: {setor} <span style='color:#D97E3A;'>({len(df_filtrado)} sob cuidados)</span>", unsafe_allow_html=True)
            
            if df_filtrado.empty:
                st.info("Nenhum paciente ativo nesta unidade.")
            else:
                # Barreiras críticas de monitoramento à beira-leito
                pacientes_criticos = df_filtrado[df_filtrado['Risco'] == 'Alto']
                pacientes_jejum = df_filtrado[df_filtrado['Via Alimentação'] == 'Jejum']
                
                if not pacientes_criticos.empty:
                    st.warning(f"⚠️ **Aviso Amarelo:** Há {len(pacientes_criticos)} paciente(s) com Alto Risco detectado pelas triagens. Avaliação prioritária necessária.")
                if not pacientes_jejum.empty:
                    st.error(f"🛑 **Aviso Vermelho:** Há {len(pacientes_jejum)} paciente(s) registrado(s) em JEJUM nesta ala. Risco de catabolismo severo!")
                
                # Tabela ordenada automaticamente por Leito/Box
                st.dataframe(
                    df_filtrado[["Leito", "Nome", "Sexo", "Faixa Etária", "Via Alimentação", "Risco", "Adequacao_Calorica", "Avaliador"]].sort_values(by="Leito"),
                    use_container_width=True, hide_index=True,
                    column_config={
                        "Adequacao_Calorica": st.column_config.NumberColumn("Adequação (%)", format="%.1f%%")
                    }
                )
                
                # Rodapé estatístico da ala
                c1, c2, c3 = st.columns(3)
                c1.metric("Adequação Média da Ala", f"{df_filtrado['Adequacao_Calorica'].mean():.1f}%")
                c2.metric("Via Predominante", df_filtrado['Via Alimentação'].mode()[0] if not df_filtrado.empty else "Nenhuma")
                c3.metric("Total de Casos Graves", len(pacientes_criticos))

# --------------------------------------------------------------------------------------------------
# MÓDULO 4: DASHBOARD DE INDICADORES DE QUALIDADE (GOVERNANÇA E DIRETORIA)
# --------------------------------------------------------------------------------------------------
elif menu == "Módulo 4: Dashboard de Indicadores":
    st.title("📊 Módulo 4: Dashboard de Indicadores Epidemiológicos e de Qualidade")
    st.markdown("Visões gerenciais consolidadas baseadas na base real de formulários aplicados.")
    
    df = st.session_state.banco_pacientes
    
    if df.empty:
        st.info("Base de dados vazia. Insira registros no Módulo 1 para consolidar os gráficos do painel de governança.")
    else:
        # Métricas de Auditoria Superior
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-card'><h4>Total de Fichas Emitidas</h4><h1>{len(df)}</h1></div>", unsafe_allow_html=True)
        with m2:
            taxa_jejum_ind = (len(df[df['Via Alimentação'] == 'Jejum']) / len(df)) * 100
            st.markdown(f"<div class='metric-card' style='border-left-color: #D97E3A;'><h4>Índice de Jejum Geral</h4><h1>{taxa_jejum_ind:.1f}%</h1></div>", unsafe_allow_html=True)
        with m3:
            # Score de Dietas Prescritas
            total_dietas = len(df[df['Dieta Prescrita'] != ""])
            st.markdown(f"<div class='metric-card' style='border-left-color: #3182CE;'><h4>Fórmulas Prescritas Ativas</h4><h1>{total_dietas}</h1></div>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Gráficos de Distribuição Populacional e Triagem")
        
        # Grid de Gráficos 1
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown("##### Casos Cadastrados por Setor")
            fig_setor = px.bar(df, x='Setor', color='Setor', color_discrete_sequence=px.colors.qualitative.Dark2)
            st.plotly_chart(fig_setor, use_container_width=True)
            
        with g2:
            st.markdown("##### Prevalência por Sexo")
            fig_sexo = px.pie(df, names='Sexo', color_discrete_sequence=['#4D6452', '#D97E3A'])
            st.plotly_chart(fig_sexo, use_container_width=True)
            
        with g3:
            st.markdown("##### Divisão por Faixa Etária")
            fig_faixa = px.histogram(df, x='Faixa Etária', color_discrete_sequence=['#3182CE'])
            st.plotly_chart(fig_faixa, use_container_width=True)

        st.markdown("---")
        st.subheader("Análise Avançada de Comorbidades e Suporte Nutricional")

        # Grid de Gráficos 2
        g4, g5, g6 = st.columns(3)
        with g4:
            st.markdown("##### Perfil do Risco Nutricional")
            fig_risco = px.bar(df, x='Risco', color='Risco', color_discrete_map={'Alto': '#DC3545', 'Médio': '#FFC107', 'Baixo': '#28A745'})
            st.plotly_chart(fig_risco, use_container_width=True)
            
        with g5:
            st.markdown("##### Distribuição de Vias de Alimentação")
            fig_vias = px.pie(df, names='Via Alimentação', color_discrete_sequence=px.colors.sequential.YlGnBu)
            st.plotly_chart(fig_vias, use_container_width=True)
            
        with g6:
            st.markdown("##### Score Clínico de Fórmulas e Dietas")
            # Agrupamento nominal de dietas prescritas para controle e rastreamento de estoque/custos
            df_dietas_score = df['Dieta Prescrita'].value_counts().reset_index()
            df_dietas_score.columns = ['Fórmula / Dieta', 'Quantidade']
            st.dataframe(df_dietas_score, use_container_width=True, hide_index=True)

        st.markdown("---")
        # RELATÓRIO DE IMPACTO FINANCEIRO E AUDITORIA DE CUSTO-BENEFÍCIO
        st.subheader("📉 Auditoria Orçamentária e Impacto Financeiro da EMTN")
        col_fin1, col_fin2 = st.columns([1, 2])
        with col_fin1:
            st.write("")
            st.write("")
            st.info("""
                **Análise de Desperdício Oculto:**
                O gráfico ao lado cruza a volumetria de fórmulas enterais imunomoduladoras ou renais de alto custo que foram efetivamente infundidas versus o planejado em prescrição. 
                Diferenças acentuadas apontam falhas operacionais na administração pelas alas.
            """)
        with col_fin2:
            df_financeiro = df.groupby('Setor')['Adequacao_Calorica'].mean().reset_index()
            fig_fin = px.line(df_financeiro, x='Setor', y='Adequacao_Calorica', title="Adesão ao Volume Prescrito (%) por Setor do HMP", markers=True, color_discrete_sequence=['#DC3545'])
            fig_fin.update_yaxes(range=[0, 110])
            st.plotly_chart(fig_fin, use_container_width=True)