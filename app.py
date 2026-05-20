import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO GERAL DO APP
st.set_page_config(page_title="EMTN - Hospital Municipal de Paulínia", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size:30px; font-weight:bold; color:#0C4A60; text-align:center; margin-bottom:5px; }
    .subtitle { font-size:15px; color:#4A5568; text-align:center; margin-bottom:25px; }
    .section-header { font-size:20px; font-weight:bold; color:#111827; border-bottom: 2px solid #E5E7EB; padding-bottom:5px; margin-top:15px; margin-bottom:15px; }
    .card-alerta { border-left: 6px solid #DC2626; padding: 12px; background-color: #FEF2F2; margin-bottom: 10px; border-radius: 4px; }
    .card-alerta-aviso { border-left: 6px solid #F59E0B; padding: 12px; background-color: #FFFBEB; margin-bottom: 10px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏥 Sistema de Gestão de Terapia Nutricional - HMP</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Conformidade: Regimento/Manual HMP | Guia Rápido | Manual USP | Manual de Nutrição Clínica</div>', unsafe_allow_html=True)

# 2. BANCO DE DADOS EM MEMÓRIA SIMULADO (A ser conectado ao Sheets no próximo passo)
if "banco_central" not in st.session_state:
    st.session_state.banco_central = [
        {
            "Unidade": "UTI Geral", "Leito": "Leito 01", "Nome": "Carlos Bento de Souza", "Idade": 68, 
            "Data Internação": "10/05/2026", "Diagnóstico": "AVC Isquêmico + Pneumonia Aspirativa", 
            "Nível Assistencial": "Terciário (Risco Alto)", "Via Alimentação": "TNE (Sonda Nasoentérica)", 
            "Jejum": "Não", "Dieta Prescrita": "Polimérica Hiperproteica 1.5 kcal/ml", 
            "Peso": 72.0, "Altura": 1.70, "IMC": 24.9, "NET": 1800, "Meta Calórica": "1440 - 1800 kcal", 
            "Meta Proteica": "108 - 144 g", "Suplemento": "Nenhum", 
            "Evolução Clínica": "Paciente estável, tolerando dieta enteral em bomba de infusão a 60ml/h.", 
            "Intercorrências": "Nenhuma nas últimas 24h.", "Status_EMTN": "Pendente Visita"
        },
        {
            "Unidade": "Clínica Médica", "Leito": "Quarto 204-A", "Nome": "Maria das Dores", "Idade": 74, 
            "Data Internação": "14/05/2026", "Diagnóstico": "Fratura de Fêmur + Desnutrição Grave", 
            "Nível Assistencial": "Secundário B (Risco)", "Via Alimentação": "Oral + Suplementação", 
            "Jejum": "Não", "Dieta Prescrita": "Dieta Branda Hiperproteica", 
            "Peso": 45.0, "Altura": 1.55, "IMC": 18.7, "NET": 1350, "Meta Calórica": "1125 - 1350 kcal", 
            "Meta Proteica": "67 - 90 g", "Suplemento": "Suplemento Hipercalórico Pó", 
            "Evolução Clínica": "Baixa aceitação da dieta hospitalar via oral (<50%). Iniciado suplemento.", 
            "Intercorrências": "Recusa parcial do suplemento no período da tarde.", "Status_EMTN": "Pendente Visita"
        }
    ]

# 3. CRIAÇÃO DAS ABAS DE FLUXO DE TRABALHO
aba_terceirizada, aba_painel_emtn, aba_plantao = st.tabs([
    "📋 1. Entrada de Dados (Equipe Terceirizada)", 
    "🚨 2. Central de Alertas (Painel EMTN)",
    "📝 3. PASSAGEM DE PLANTÃO AUTOMÁTICA"
])

# ==========================================
# ABA 1: ENTRADA DE DADOS (EQUIPE TERCEIRIZADA)
# ==========================================
with aba_terceirizada:
    st.markdown('<div class="section-header">Formulário de Avaliação Inicial e Evolução de Rotina</div>', unsafe_allow_html=True)
    st.caption("A equipe terceirizada utiliza este espaço para cadastrar novas triagens e registrar as evoluções clínicas diárias.")
    
    with st.form("registro_paciente"):
        c1, c2, c3 = st.columns(3)
        with c1:
            u_int = st.selectbox("Unidade de Internação", ["UTI Geral", "Clínica Médica", "Clínica Cirúrgica", "Pediatria", "Maternidade"])
            leito_int = st.text_input("Leito / Quarto")
            nome_int = st.text_input("Nome Completo do Paciente")
            idade_int = st.number_input("Idade", min_value=0, max_value=120, step=1)
            dt_int = st.date_input("Data da Internação Hospitalar").strftime('%d/%m/%Y')
        
        with c2:
            diag_int = st.text_area("Diretriz / Diagnóstico Principal")
            nivel_int = st.selectbox("Nível Assistencial (Triagem)", ["Sem Risco", "Secundário B (Risco)", "Terciário (Risco Alto)"])
            via_int = st.selectbox("Via de Alimentação Atual", ["Oral", "Oral + Suplemento", "TNE (Sonda Nasoentérica)", "GTT / JTM", "TNP (Parenteral)", "Jejum Absoluto"])
            jejum_int = st.radio("Paciente em Jejum no Momento?", ["Não", "Sim"])
            dieta_int = st.text_input("Dieta Prescrita Atual")
            
        with c3:
            p_int = st.number_input("Peso para Cálculo (kg)", min_value=0.0, step=0.1)
            a_int = st.number_input("Altura (m)", min_value=0.0, step=0.01)
            suple_int = st.text_input("Suplemento Prescrito (Se houver)", value="Nenhum")
            evol_int = st.text_area("Resumo da Evolução Clínica")
            interc_int = st.text_area("Intercorrências registradas", value="Nenhuma nas últimas 24h.")
            
        enviar_dados = st.form_submit_button("Salvar e Processar Dados")
        
        if enviar_dados:
            if nome_int and leito_int:
                # Cálculos automáticos baseados nas diretrizes do Guia Rápido HMP
                imc_calc = p_int / (a_int ** 2) if p_int > 0 and a_int > 0 else 0
                net_calc = p_int * 25 # Regra de bolso padrão
                
                # Definição das metas conforme o Guia Rápido HMP
                if "Terciário" in nivel_int:
                    m_cal = f"{p_int*20:.0f} - {p_int*25:.0f} kcal" # Fase Aguda
                else:
                    m_cal = f"{p_int*25:.0f} - {p_int*30:.0f} kcal" # Anabolismo/Recuperação
                m_prot = f"{p_int*1.2:.1f} - {p_int*1.5:.1f} g"
                
                # GATILHO DA LINHA DE CUIDADO: Define se vai gerar alerta para a EMTN central
                if nivel_int in ["Secundário B (Risco)", "Terciário (Risco Alto)"] or via_int in ["TNE (Sonda Nasoentérica)", "TNP (Parenteral)", "Jejum Absoluto"]:
                    status_emtn = "Pendente Visita"
                else:
                    status_emtn = "Acompanhamento Terceirizada"
                
                novo_registro = {
                    "Unidade": u_int, "Leito": leito_int, "Nome": nome_int, "Idade": idade_int, "Data Internação": dt_int,
                    "Diagnóstico": diag_int, "Nível Assistencial": nivel_int, "Via Alimentação": via_int, "Jejum": jejum_int,
                    "Dieta Prescrita": dieta_int, "Peso": p_int, "Altura": a_int, "IMC": round(imc_calc, 1),
                    "NET": round(net_calc), "Meta Calórica": m_cal, "Meta Proteica": m_prot, "Suplemento": suple_int,
                    "Evolução Clínica": evol_int, "Intercorrências": interc_int, "Status_EMTN": status_emtn
                }
                st.session_state.banco_central.append(novo_registro)
                st.success("✅ Avaliação salva com sucesso! O Mural de Passagem de Plantão e a Central de Alertas foram atualizados.")
            else:
                st.error("❌ Por favor, preencha os campos obrigatórios: Nome e Leito.")

# ==========================================
# ABA 2: CENTRAL DE ALERTAS (EQUIPE CENTRAL EMTN)
# ==========================================
with aba_painel_emtn:
    st.markdown('<div class="section-header">Central de Gatilhos Assistenciais Ativos (Supervisão EMTN)</div>', unsafe_allow_html=True)
    st.caption("Filtro automático de pacientes elegíveis para visita prioritária da equipe central da EMTN conforme o Guia Rápido.")
    
    df_atual = pd.DataFrame(st.session_state.banco_central)
    alertas = df_atual[df_atual["Status_EMTN"] == "Pendente Visita"]
    
    if alertas.empty:
        st.success("✅ Excelente! Nenhum paciente crítico aguardando avaliação ou parecer da EMTN no momento.")
    else:
        st.warning(f"Atenção: Existem {len(alertas)} pacientes com critérios de risco pendentes de visita pela EMTN.")
        
        for idx, row in alertas.iterrows():
            estilo_card = "card-alerta" if row["Nível Assistencial"] == "Terciário (Risco Alto)" else "card-alerta-aviso"
            
            st.markdown(f"""
                <div class="{estilo_card}">
                    <strong>📍 Unidade: {row['Unidade']} — Leito: {row['Leito']}</strong><br>
                    <b>Paciente:</b> {row['Nome']} ({row['Idade']} anos) | <b>Data de Admissão:</b> {row['Data Internação']}<br>
                    <b>Risco Nutricional:</b> {row['Nível Assistencial']} | <b>Via Selecionada:</b> {row['Via Alimentação']} | <b>Em Jejum:</b> {row['Jejum']}<br>
                    <b>Diagnóstico/Conduta da Terceirizada:</b> {row['Diagnóstico']}
                </div>
            """, unsafe_allow_html=True)
            
            # Botão de Ação para a EMTN registrar que visitou e mudou a prescrição
            if st.button(f"🩺 Registrar Visita EMTN / Carimbar Validação: {row['Nome']}", key=f"btn_emtn_{idx}"):
                st.session_state.banco_central[idx]["Status_EMTN"] = "Validado e Monitorado pela EMTN"
                st.toast(f"Caso de {row['Nome']} assumido pela equipe central da EMTN!", icon="📝")
                st.rerun()

# ==========================================
# ABA 3: PASSAGEM DE PLANTÃO AUTOMÁTICA
# ==========================================
with aba_plantao:
    st.markdown('<div class="section-header">Mural Dinâmico de Passagem de Plantão da Terapia Nutricional</div>', unsafe_allow_html=True)
    st.caption("Visão macro e atualizada em tempo real para a passagem de turnos ou round multidisciplinar.")
    
    df_plantao = pd.DataFrame(st.session_state.banco_central)
    
    # Filtro rápido por setor para agilizar o round beira-leito
    setores = ["Todos os Setores"] + list(df_plantao["Unidade"].unique())
    filtro_setor = st.selectbox("Filtrar visualização por setor:", setores)
    
    if filtro_setor != "Todos os Setores":
        df_plantao = df_plantao[df_plantao["Unidade"] == filtro_setor]
        
    # Colunas ordenadas exatamente segundo a sua solicitação técnica
    colunas_especificadas = [
        "Unidade", "Leito", "Nome", "Idade", "Data Internação", "Diagnóstico", 
        "Nível Assistencial", "Via Alimentação", "Jejum", "Dieta Prescrita", 
        "Peso", "Altura", "IMC", "NET", "Meta Calórica", "Meta Proteica", 
        "Suplemento", "Evolução Clínica", "Intercorrências"
    ]
    
    # Apresenta a tabela unificada
    st.dataframe(df_plantao[colunas_especificadas], use_container_width=True, hide_index=True)
    
    # Exportador em formato amigável para contingência em papel ou envio por e-mail institucional
    st.markdown("### 🖨️ Exportação do Plantão")
    csv = df_plantao[colunas_especificadas].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Dados de Passagem de Plantão (.CSV para Excel)",
        data=csv,
        file_name=f"plantao_emtn_hmp_{datetime.now().strftime('%d_%m_%Y')}.csv",
        mime="text/csv",
    )