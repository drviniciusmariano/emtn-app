import streamlit as st
import pandas as pd
import datetime

# 1. CONFIGURAÇÃO DA PÁGINA & IDENTIDADE VISUAL
st.set_page_config(
    page_title="EMTN - Hospital Municipal de Paulínia",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeção de CSS para customização completa das cores do Logotipo
st.markdown("""
    <style>
        /* Fundo do App */
        .stApp {
            background-color: #FCFBF7;
            color: #334155;
        }
        /* Títulos */
        h1, h2, h3 {
            color: #4D6452 !important;
            font-family: 'Montserrat', sans-serif;
        }
        /* Customização de Botões */
        div.stButton > button:first-child {
            background-color: #4D6452;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 24px;
            font-weight: bold;
        }
        div.stButton > button:first-child:hover {
            background-color: #D97E3A;
            color: white;
        }
        /* Estilização dos blocos/cards */
        .metric-card {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            border-left: 5px solid #D97E3A;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 15px;
        }
    </style>
""", unsafe_gradient=True)

# 2. BANCO DE DADOS EM MEMÓRIA (Simulação para visualização de indicadores e listagem)
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
        },
        {
            "Avaliador": "Dra. Juliana Costa", "Data Admissão": "2026-05-18", "Nome": "Ana Júlia Bento", 
            "Sexo": "Feminino", "Setor": "Pediatria", "Leito": "Ped 03", "Faixa Etária": "< ou = 18", 
            "Via Alimentação": "Oral", "Risco": "Baixo", "Adequacao_Calorica": 100.0
        }
    ])

# 3. BARRA LATERAL (Navegação e Identidade)
st.sidebar.markdown(
    "<h2 style='text-align: center; color: #4D6452; margin-bottom: 0;'>EMTN</h2>"
    "<p style='text-align: center; color: #D97E3A; font-weight: bold; margin-top: 0;'>HMP Paulínia - SP</p>", 
    unsafe_allow_html=True
)
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navegação do Plantão:", ["📊 Dashboard de Indicadores", "📋 Listagem por Unidade", "📝 Novo Protocolo de Avaliação"])

# SEÇÃO 1: DASHBOARD DE INDICADORES (Agrupados por Unidade/Setor)
if menu == "📊 Dashboard de Indicadores":
    st.title("📊 Indicadores de Qualidade Nutricional")
    st.markdown("Monitoramento em tempo real estratificado por unidade de internação hospitalar.")
    
    df = st.session_state.banco_pacientes
    
    # [span_3](start_span)KPIs Gerais de Cuidado[span_3](end_span)
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.markdown(f"<div class='metric-card'><h4>Total de Pacientes em TN</h4><h1>{len(df)}</h1></div>", unsafe_allow_html=True)
    with kpi2:
        alto_risco = len(df[df['Risco'] == 'Alto'])
        st.markdown(f"<div class='metric-card' style='border-left-color: #D97E3A;'><h4>Pacientes em Alto Risco</h4><h1>{alto_risco}</h1></div>", unsafe_allow_html=True)
    with kpi3:
        media_adequacao = df['Adequacao_Calorica'].mean()
        st.markdown(f"<div class='metric-card' style='border-left-color: #4D6452;'><h4>Média de Adequação Calórica</h4><h1>{media_adequacao:.1f}%</h1></div>", unsafe_allow_html=True)
        
    st.markdown("### Adequação Calórica Média por Setor")
    chart_data = df.groupby('Setor')['Adequacao_Calorica'].mean().reset_index()
    st.bar_chart(data=chart_data, x='Setor', y='Adequacao_Calorica', color="#4D6452")

# SEÇÃO 2: LISTAGEM DE PACIENTES COM FILTRO DE SETOR (Passagem de Plantão)
elif menu == "📋 Listagem por Unidade":
    st.title("📋 Passagem de Plantão por Unidade de Internação")
    st.markdown("Selecione a ala para visualizar a listagem nominal e vias de alimentação ativas.")
    
    df = st.session_state.banco_pacientes
    
    # [span_4](start_span)Lista de setores dinâmicos conforme mapeado no formulário[span_4](end_span)
    setores_disponiveis = ["Pronto Socorro Adulto", "Pronto Socorro Infantil", "Clinica Médica", "Clínica Cirúrgica", "Ginecologia e Obstetrícia", "Pediatria", "UTI"]
    
    # Criando abas dinâmicas baseadas nos setores preenchidos ou existentes
    abas = st.tabs(setores_disponiveis)
    
    for i, setor in enumerate(setores_disponiveis):
        with abas[i]:
            df_filtrado = df[df['Setor'] == setor]
            st.subheader(f"Ala: {setor} ({len(df_filtrado)} pacientes)")
            
            if not df_filtrado.empty:
                st.dataframe(
                    df_filtrado[["Nome", "Leito", "Sexo", "Faixa Etária", "Via Alimentação", "Risco", "Avaliador"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info(f"Nenhum paciente sob acompanhamento da EMTN no(a) {setor} atualmente.")

# SEÇÃO 3: NOVO PROTOCOLO DE AVALIAÇÃO (Dinamizado por Idade/Protocolo correspondente)
elif menu == "📝 Novo Protocolo de Avaliação":
    st.title("📝 Protocolo de Avaliação Nutricional")
    [span_5](start_span)st.markdown("Formulário oficial para padronização e otimização do processo assistencial da EMTN[span_5](end_span).")
    
    with st.form("formulario_emtn"):
        st.markdown("### 1. Identificação Geral")
        col1, col2 = st.columns(2)
        with col1:
            [span_6](start_span)avaliador = st.text_input("Avaliador *", placeholder="Nome do profissional da EMTN")[span_6](end_span)
            [span_7](start_span)nome_paciente = st.text_input("Nome do Paciente *")[span_7](end_span)
            [span_8](start_span)sexo = st.selectbox("Sexo *", ["Masculino", "Feminino"])[span_8](end_span)
        with col2:
            [span_9](start_span)data_admissao = st.date_input("Data de Admissão *", datetime.date.today())[span_9](end_span)
            [span_10](start_span)setor = st.selectbox("Setor / Unidade de Internação *", ["Pronto Socorro Adulto", "Pronto Socorro Infantil", "Clinica Médica", "Clínica Cirúrgica", "Ginecologia e Obstetrícia", "Pediatria", "UTI"])[span_10](end_span)
            [span_11](start_span)leito = st.text_input("Leito *")[span_11](end_span)
            
        st.markdown("---")
        st.markdown("### 2. Triagem e Antropometria Inicial")
        col3, col4 = st.columns(2)
        with col3:
            [span_12](start_span)via_alimentacao = st.multiselect("Via de Alimentação Atual *", ["Oral", "Sonda Nasoenteral", "Gastrostomia", "Jejunostomia", "Parenteral periférica", "Parenteral central", "Jejum"])[span_12](end_span)
            [span_13](start_span)momento = st.radio("Momento da Avaliação *", ["Avaliação Inicial", "Reavaliação", "Evolução Nutricional"], horizontal=True)[span_13](end_span)
        with col4:
            faixa_etaria = st.selectbox(
                "Faixa Etária (Define o Protocolo de Screening) *", 
                ["< ou = 18 (Pediatria)", "19-59 (Adulto)", "> ou = 60 (Idoso)"]
            [span_14](start_span))
            
        # BLOCOS DE PROTOCOLO DINÂMICO CONFORME A FAIXA ETÁRIA SELECIONADA[span_14](end_span)
        st.markdown("---")
        if "< ou = 18" in faixa_etaria:
            [span_15](start_span)st.markdown("### 🧬 Protocolo STRONG KIDS (Triagem Pediátrica)")[span_15](end_span)
            [span_16](start_span)st.info("Ferramenta para avaliação de risco de desnutrição em crianças de 1 mês a 18 anos[span_16](end_span).")
            [span_17](start_span)[span_18](start_span)sk1 = st.checkbox("1. A criança parece ter déficit nutricional ou desnutrição subjetiva? (1 pt)")[span_17](end_span)[span_18](end_span)
            [span_19](start_span)[span_20](start_span)sk2 = st.checkbox("2. Há presença de doença de alto risco nutricional ou cirurgia de grande porte? (2 pts)")[span_19](end_span)[span_20](end_span)
            [span_21](start_span)[span_22](start_span)sk3 = st.checkbox("3. Ingestão nutricional reduzida ou perdas gastrointestinais significativas nos últimos dias? (1 pt)")[span_21](end_span)[span_22](end_span)
            [span_23](start_span)[span_24](start_span)sk4 = st.checkbox("4. Houve perda de peso ou ganho insuficiente nas últimas semanas? (1 pt)")[span_23](end_span)[span_24](end_span)
            
            # [span_25](start_span)Cálculo rápido do score do formulário[span_25](end_span)
            score_sk = sum([sk1, sk2*2, sk3, sk4])
            [span_26](start_span)[span_27](start_span)risco_final = "Baixo" if score_sk == 0 else "Médio" if score_sk <= 3 else "Alto"[span_26](end_span)[span_27](end_span)
            [span_28](start_span)[span_29](start_span)st.metric("Escore Total STRONG KIDS", f"{score_sk} pontos", f"Risco: {risco_final}")[span_28](end_span)[span_29](end_span)

        elif "19-59" in faixa_etaria:
            [span_30](start_span)st.markdown("### 🫁 Protocolo NRS 2002 (Triagem Adulto)")[span_30](end_span)
            [span_31](start_span)st.info("Instrumento internacional recomendado para avaliar ingestão dietética e gravidade da doença[span_31](end_span).")
            [span_32](start_span)[span_33](start_span)nrs1 = st.checkbox("IMC < 20,5 kg/m²?")[span_32](end_span)[span_33](end_span)
            [span_34](start_span)[span_35](start_span)nrs2 = st.checkbox("Paciente perdeu peso nos últimos 3 meses?")[span_34](end_span)[span_35](end_span)
            [span_36](start_span)[span_37](start_span)nrs3 = st.checkbox("Paciente teve sua ingestão dietética reduzida na última semana?")[span_36](end_span)[span_37](end_span)
            [span_38](start_span)[span_39](start_span)nrs4 = st.checkbox("O paciente é gravemente doente / crítico?")[span_38](end_span)[span_39](end_span)
            
            score_nrs = sum([nrs1, nrs2, nrs3, nrs4])
            risco_final = "Alto" if score_nrs >= 2 else "Médio" if score_nrs == 1 else "Baixo"
            st.metric("Escore Triagem Inicial NRS", f"{score_nrs} itens positivos", f"Risco Recomendado: {risco_final}")

        else:
            [span_40](start_span)st.markdown("### 👴 Protocolo MNA® (Mini Nutritional Assessment - Idoso)")[span_40](end_span)
            [span_41](start_span)[span_42](start_span)st.info("Detecção precoce do risco de desnutrição e funcionalidade motora do paciente idoso[span_41](end_span)[span_42](end_span).")
            [span_43](start_span)mna1 = st.selectbox("A. Diminuição da ingesta alimentar nos últimos 3 meses?", ["Sem diminuição", "Diminuição moderada", "Diminuição grave"])[span_43](end_span)
            [span_44](start_span)mna2 = st.selectbox("C. Mobilidade atual:", ["Normal", "Deambula mas não sai de casa", "Restrito ao leito/cadeira"])[span_44](end_span)
            [span_45](start_span)mna3 = st.checkbox("D. Passou por estresse psicológico ou doença aguda recente?")[span_45](end_span)
            [span_46](start_span)mna4 = st.selectbox("E. Problemas neuropsicológicos:", ["Sem problemas", "Demência ligeira", "Demência ou depressão grave"])[span_46](end_span)
            
            risco_final = "Alto" if mna3 else "Médio"

        st.markdown("---")
        st.markdown("### 3. Planejamento Terapêutico Proposto")
        [span_47](start_span)conduta_proposta = st.text_area("Conduta e Metas Calórico-Proteicas de Beira-Leito[span_47](end_span)")
        adequacao_estimada = st.slider("Meta Estimada de Adequação Nutricional (%)", 0, 100, 85)
        
        # Botão de envio
        enviar = st.form_submit_button("Salvar Registro e Atualizar Plantão")
        
        if enviar:
            # Estruturando nova linha para acoplamento no dataframe global
            novo_paciente = {
                "Avaliador": avaliador,
                "Data Admissão": str(data_admissao),
                "Nome": nome_paciente,
                "Sexo": sexo,
                "Setor": setor,
                "Leito": leito,
                "Faixa Etária": faixa_etaria.split(" ")[0],
                "Via Alimentação": ", ".join(via_alimentacao) if via_alimentacao else "Jejum",
                "Risco": risco_final,
                "Adequacao_Calorica": float(adequacao_estimada)
            }
            
            # Adiciona ao dataframe da sessão
            st.session_state.banco_pacientes = pd.concat([st.session_state.banco_pacientes, pd.DataFrame([novo_paciente])], ignore_index=True)
            st.success(f"Sucesso! O prontuário de {nome_paciente} foi processado e agrupado no setor {setor}!")
