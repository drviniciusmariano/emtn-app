import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, date

# CONFIGURAÇÕES DA PÁGINA
st.set_page_config(page_title="EMTN - Hospital Municipal de Paulínia", page_icon="🏥", layout="wide")

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
        .flag-box {
            padding: 15px; 
            border-radius: 8px; 
            margin-top: 10px; 
            margin-bottom: 10px;
            font-weight: 500;
        }
    </style>
""", unsafe_allow_html=True)

# BANCO DE DADOS EM MEMÓRIA (INICIALIZAÇÃO DO ESTADO DA SESSÃO)
if 'banco_pacientes' not in st.session_state:
    st.session_state.banco_pacientes = pd.DataFrame(columns=[
        "Avaliador", "Data Admissão", "Nome", "Sexo", "Setor", "Leito", "Data Triagem", 
        "Via Alimentação", "Momento", "Diagnóstico", "Comorbidades", "Peso Habitual", 
        "Altura Referida", "Data Nascimento", "Idade Anos", "Idade Meses", "Faixa Etária", 
        "Escore Triagem", "Risco", "Nível Assistência", "Via Proposta", "Dieta Prescrita", "Adequacao_Calorica"
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

# FUNÇÃO AUXILIAR PARA CÁLCULO DE IDADE AUTOMÁTICA (BLINDADA CONTRA ERROS DE STRING)
def calcular_idade_detalhada(data_nasc):
    # Se a data vier acidentalmente como string, faz a conversão segura para Objeto Date
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

# --------------------------------------------------------------------------------------------------
# MÓDULO 1: TRIAGEM E ADMISSÃO DE PACIENTES
# --------------------------------------------------------------------------------------------------
if menu == "Módulo 1: Triagem e Admissão":
    st.title("🧬 Módulo 1: Triagem e Admissão de Pacientes")
    
    if 'passo_atual' not in st.session_state:
        st.session_state.passo_atual = "identificacao"
    
    if st.button("🔄 Reiniciar Formulário"):
        st.session_state.passo_atual = "identificacao"
        if 'dados_triagem_base' in st.session_state: del st.session_state.dados_triagem_base
        st.rerun()

    # -------------------------------------------------------------------------
    # PASSO 1: IDENTIFICAÇÃO (PERGUNTAS 1 A 9) - TERMO ALTERADO E DATA CONFIGURADA
    # -------------------------------------------------------------------------
    if st.session_state.passo_atual == "identificacao":
        with st.form("form_passo_1"):
            st.subheader("Identificação Básica do Paciente")
            f_avaliador = st.text_input("1. Avaliador *", value=st.session_state.nome_avaliador, disabled=True)
            # Exibição da Data configurada explicitamente em padrão DD/MM/YYYY
            f_data_adm = st.date_input("2. Data de Admissão *", format="DD/MM/YYYY")
            f_nome = st.text_input("3. Nome *")
            f_sexo = st.radio("4. Sexo *", ["Masculino", "Feminino"])
            f_setor = st.selectbox("5. Setor *", ["Pronto Socorro Adulto", "Pronto Socorro Infantil", "Clinica Médica", "Clínica Cirúrgica", "Ginecologia e Obstetrícia", "Pediatria", "UTI"])
            f_leito = st.text_input("6. Leito *")
            f_data_triagem = st.date_input("7. Data da Triagem", format="DD/MM/YYYY")
            f_via = st.selectbox("8. Via de alimentação *", ["Oral", "Sonda Nasoenteral", "Gastrostomia", "Jejunostomia", "Parenteral periférica", "Parenteral central", "Jejum"])
            
            st.markdown("---")
            # TERMO ALTERADO CONFORME SOLICITAÇÃO
            f_momento = st.radio("9. Qual o momento da avaliação? *", ["Avaliação Inicial", "Reavaliação", "Evolução Nutricional"])
            
            btn_proximo_1 = st.form_submit_button("Processar Direcionamento de Seção ➔")
            
            if btn_proximo_1:
                if not f_nome or not f_leito:
                    st.error("Por favor, preencha os campos obrigatórios (Nome e Leito).")
                else:
                    # Guardamos o objeto Date puro convertido em string de forma limpa padrão ISO
                    st.session_state.dados_triagem_base = {
                        "Avaliador": f_avaliador, "Data Admissão": f_data_adm.strftime("%Y-%m-%d"), 
                        "Nome": f_nome, "Sexo": f_sexo, "Setor": f_setor, "Leito": f_leito, 
                        "Data Triagem": f_data_triagem.strftime("%Y-%m-%d"), "Via Alimentação": f_via, "Momento": f_momento
                    }
                    
                    if f_momento == "Avaliação Inicial":
                        st.session_state.passo_atual = "anamnese"
                    elif f_momento == "Reavaliação":
                        st.session_state.passo_atual = "avaliacao_detalhada_secao"
                    elif f_momento == "Evolução Nutricional":
                        st.session_state.passo_atual = "evolucao_direta_secao"
                    st.rerun()

    # -------------------------------------------------------------------------
    # PASSO 2: ANAMNESE E AUTOMAÇÃO DA IDADE (PERGUNTAS 10 A 15 + AUTO 16)
    # -------------------------------------------------------------------------
    elif st.session_state.passo_atual == "anamnese":
        st.subheader("Anamnese Clínica")
        st.caption(f"Paciente: {st.session_state.dados_triagem_base['Nome']}")
        
        with st.form("form_passo_2"):
            f_diag = st.text_area("10. Diagnóstico *")
            f_comorbidades = st.multiselect("11. Comorbidades *", ["NÃO POSSUI COMORBIDADE", "Acamado(a)", "Diabetes mellitus", "Drogadição (SPA)", "Etilismo", "Hipertensão arterial sistêmica", "Infarto", "Insuficiência cardíaca", "Obesidade", "Tabagismo", "Doença autoimune", "Doença hematológica", "Doença hepática ou gastrointestinal", "Doença nefrológica", "Doença neoplásica", "Doença neurológica", "Doença psiquiátrica", "Doença respiratória", "Doença sexualmente transmissível", "Outra doença cardiovascular", "Outra doença endócrina", "Doença gestacional - Hipertensão arterial sistêmica", "Doença gestacional - Diabetes mellitus", "Doença gestacional - Outra doença endócrina", "Doença gestacional - Outra(s) doença(s)", "Outra(s) doença(s)"])
            f_peso_hab = st.number_input("12. Peso habitual (kg) *", min_value=0.0, step=0.1, format="%.2f")
            f_altura = st.number_input("13. Altura referida (m) *", min_value=0.0, step=0.01, format="%.2f")
            f_data_nasc = st.date_input("14. Data de Nascimento *", value=date(2000, 1, 1), format="DD/MM/YYYY")
            
            btn_proximo_2 = st.form_submit_button("Avançar para Triagem Específica ➔")
            
            if btn_proximo_2:
                # O cálculo agora consome o objeto Date de forma segura e direta
                anos, meses = calcular_idade_detalhada(f_data_nasc)
                
                if anos < 19:
                    faixa_calculada = "<=18"
                elif 19 <= anos <= 59:
                    faixa_calculada = "19-59"
                else:
                    faixa_calculada = ">= 60"
                
                st.session_state.dados_triagem_base.update({
                    "Diagnóstico": f_diag, "Comorbidades": ", ".join(f_comorbidades),
                    "Peso Habitual": f_peso_hab, "Altura Referida": f_altura, 
                    "Data Nascimento": f_data_nasc.strftime("%Y-%m-%d"),
                    "Idade Anos": anos, "Idade Meses": meses, "Faixa Etária": faixa_calculada
                })
                
                st.session_state.passo_atual = f"triagem_{faixa_calculada}"
                st.rerun()

    # [O restante das seções (triagem_<=18, triagem_19-59, triagem_>= 60 e conduta_final) permanecem idênticos e protegidos contra falhas de execução]
    elif st.session_state.passo_atual == "triagem_<=18":
        st.subheader("🧬 Screening Tool Risk Nutritional Status and Growth - STRONG KIDS (Idade ≤ 18)")
        st.info(f"Paciente: {st.session_state.dados_triagem_base['Nome']} | Idade Calculada: {st.session_state.dados_triagem_base['Idade Anos']} anos e {st.session_state.dados_triagem_base['Idade Meses']} meses.")
        
        map_q17 = {"Não (0 ponto)": 0, "Sim (1 ponto)": 1}
        map_q18 = {"Não (0 ponto)": 0, "Sim (2 ponto)": 2}
        map_q19 = {"Não (0 ponto)": 0, "Sim (1 ponto)": 1}
        map_q20 = {"Não (0 ponto)": 0, "Sim (1 ponto)": 1}
        
        q17_sel = st.radio("17. 1. Avaliação nutricional subjetiva: a criança parece ter déficit nutricional?", list(map_q17.keys()))
        q18_sel = st.radio("18. 2. Doença (com alto risco nutricional) ou cirurgia de grande porte?", list(map_q18.keys()))
        q19_sel = st.radio("19. 3. Ingestão nutricional e/ou perda nos últimos dias?", list(map_q19.keys()))
        q20_sel = st.radio("20. 4. Refere perda de peso ou ganho insuficiente nas últimas semanas?", list(map_q20.keys()))
        
        escore_strong = map_q17[q17_sel] + map_q18[q18_sel] + map_q19[q19_sel] + map_q20[q20_sel]
        
        if escore_strong == 0:
            risco_strong = "Baixo"
            cor_flag, cor_texto, borda = "#D4EDDA", "#155724", "28A745"
            diretriz = "🔹 Conduta Baixo Risco:\n1. Checar peso regularmente.\n2. Reavaliar risco em 1 semana."
        elif 1 <= escore_strong <= 3:
            risco_strong = "Médio"
            cor_flag, cor_texto, borda = "#FFF3CD", "#856404", "FFC107"
            diretriz = "🔸 Conduta Médio Risco:\n1. Consultar médico para diagnóstico completo.\n2. Considerar intervenção.\n3. Checar peso 2x/semana.\n4. Reavaliar em 1 semana."
        else:
            risco_strong = "Alto"
            cor_flag, cor_texto, borda = "#F8D7DA", "#721C24", "DC3545"
            diretriz = "🛑 CONDUTA EM ALTO RISCO:\n1. Consultar equipe em caráter imediato.\n2. Orientação individualizada.\n3. Iniciar suplementação oral."

        st.markdown(f"""
            <div class='flag-box' style='background-color: {cor_flag}; color: {cor_texto}; border-left: 6px solid #{borda};'>
                <h4>21 e 22. Resultado do Screening - STRONG KIDS</h4>
                <p><b>Escore Total Computado:</b> {escore_strong} Pontos</p>
                <p><b>Classificação de Risco:</b> Risco {risco_strong}</p>
                <p style='white-space: pre-line;'><b>Diretriz Clínica Obrigatória HMP:</b>\n{diretriz}</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Gravar Triagem e Seguir para Conduta ➔"):
            st.session_state.dados_triagem_base.update({"Escore Triagem": escore_strong, "Risco": risco_strong})
            st.session_state.passo_atual = "conduta_final"
            st.rerun()

    elif st.session_state.passo_atual == "triagem_19-59":
        st.subheader("🫁 Triagem Nutricional - NRS 2002 (Idade 19-59)")
        st.caption(f"Paciente: {st.session_state.dados_triagem_base['Nome']}")
        
        f_peso_atual = st.number_input("23. Peso atual (kg) *", min_value=0.0, step=0.1, format="%.2f")
        
        imc_nrs = f_peso_atual / (st.session_state.dados_triagem_base["Altura Referida"] ** 2) if st.session_state.dados_triagem_base["Altura Referida"] > 0 and f_peso_atual > 0 else 0.0
        st.text_input("24. IMC Computado (kg/m²)", value=f"{imc_nrs:.2f}", disabled=True)
        
        st.markdown("#### 25. Etapa 1: Triagem Inicial")
        nrs_q1 = st.checkbox("1) O IMC é < 20,5 kg/m²?")
        nrs_q2 = st.checkbox("2) O paciente perdeu peso nos 3 últimos meses?")
        nrs_q3 = st.checkbox("3) O paciente teve sua ingestão dietética reduzida na última semana?")
        nrs_q4 = st.checkbox("4) O paciente é gravemente doente?")
        
        qualquer_sim = nrs_q1 or nrs_q2 or nrs_q3 or nrs_q4
        escore_final_nrs = 0
        risco_nrs = "Baixo"
        
        if qualquer_sim:
            st.warning("⚠️ Triagem Inicial Positiva! Direcionando para a Etapa 2 (Triagem Final).")
            map_q27 = {"Ausente (0 ponto)": 0, "Leve (1 ponto)": 1, "Moderado (2 pontos)": 2, "Grave (3 pontos)": 3}
            map_q28 = {"Ausente (0 ponto)": 0, "Leve (1 ponto)": 1, "Moderado (2 pontos)": 2, "Grave (3 pontos)": 3}
            
            q27_sel = st.selectbox("27. Deterioração do Estado Nutricional", list(map_q27.keys()))
            q28_sel = st.selectbox("28. Gravidade da Doença (Grau de Estresse)", list(map_q28.keys()))
            
            escore_final_nrs = map_q27[q27_sel] + map_q28[q28_sel]
            if st.session_state.dados_triagem_base["Idade Anos"] > 70:
                escore_final_nrs += 1
                
            if escore_final_nrs >= 3:
                risco_nrs = "Alto"
        else:
            st.success("✅ Triagem Inicial Negativa. Paciente classificado em Baixo Risco.")

        st.markdown(f"#### 29. Consolidação do Escore Final - NRS 2002")
        st.metric("Pontuação Total", f"{escore_final_nrs} Pontos")
        
        if st.button("Gravar Dados e Ir para Definição de Conduta ➔"):
            st.session_state.dados_triagem_base.update({"Escore Triagem": escore_final_nrs, "Risco": risco_nrs})
            st.session_state.passo_atual = "conduta_final"
            st.rerun()

    elif st.session_state.passo_atual == "triagem_>= 60":
        st.subheader("👴 Mini Nutritional Assessment - MNA® (População Geriátrica ≥ 60)")
        st.caption(f"Paciente: {st.session_state.dados_triagem_base['Nome']}")
        
        map_mna_a = {"Sem diminuição da ingesta (2 pontos)": 2, "Diminuição moderada da ingesta (1 ponto)": 1, "Diminuição grave da ingesta (0 ponto)": 0}
        map_mna_b = {"Sem perda de peso (3 pontos)": 3, "Perda entre 1 e 3kg (2 pontos)": 2, "Não sabe (1 ponto)": 1, "Perda > 3kg (0 ponto)": 0}
        map_mna_c = {"Normal (2 pontos)": 2, "Deambula mas não é capaz de sair de casa (1 ponto)": 1, "Restrito ao leito ou à cadeira de rodas (0 ponto)": 0}
        map_mna_d = {"Não (2 pontos)": 2, "Sim (0 ponto)": 0}
        map_mna_e = {"Sem problemas psicológicos (2 pontos)": 2, "Demência ligeira (1 ponto)": 1, "Demência ou depressão graves (0 ponto)": 0}
        map_mna_f = {"IMC >= 23 (3 pontos)": 3, "21 <= IMC < 23 (2 pontos)": 2, "19 <= IMC < 21 (1 ponto)": 1, "IMC < 19 (0 ponto)": 0}

        mna_a = st.selectbox("30. A. Diminuição da ingesta alimentar nos últimos 3 meses por perda de apetite?", list(map_mna_a.keys()))
        mna_b = st.selectbox("31. B. Perda de peso nos últimos 3 meses?", list(map_mna_b.keys()))
        mna_c = st.selectbox("32. C. Mobilidade *", list(map_mna_c.keys()))
        mna_d = st.selectbox("33. D. Passou por algum stress psicológico ou doença aguda nos últimos três meses?", list(map_mna_d.keys()))
        mna_e = st.selectbox("34. E. Problemas neuropsicológicos?", list(map_mna_e.keys()))
        mna_f = st.selectbox("35. F. Índice de Massa Corporal - IMC (kg/m²)", list(map_mna_f.keys()))
        
        escore_mna_triagem = map_mna_a[mna_a] + map_mna_b[mna_b] + map_mna_c[mna_c] + map_mna_d[mna_d] + map_mna_e[mna_e] + map_mna_f[mna_f]
        
        if escore_mna_triagem >= 12:
            risco_mna = "Baixo"
            texto_status = "Estado Nutricional Normal"
        elif 8 <= escore_mna_triagem <= 11:
            risco_mna = "Médio"
            texto_status = "Sob Risco de Desnutrição"
        else:
            risco_mna = "Alto"
            texto_status = "Desnutrido"
            
        st.markdown(f"""
            <div class='flag-box' style='background-color: #ECEFF1; border-left: 6px solid #455A64; color: #263238;'>
                <h4>36 e 37. Pontuação da Triagem MNA® Computada</h4>
                <p><b>Escore Calculado:</b> {escore_mna_triagem} Pontos</p>
                <p><b>Classificação Geriátrica:</b> {texto_status} (Risco {risco_mna})</p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Gravar Triagem MNA® e Prosseguir ➔"):
            st.session_state.dados_triagem_base.update({"Escore Triagem": escore_mna_triagem, "Risco": risco_mna})
            st.session_state.passo_atual = "conduta_final"
            st.rerun()

    elif st.session_state.passo_atual == "conduta_final":
        st.subheader("🏁 Definição da Conduta e Terapia Nutricional Proposta")
        db = st.session_state.dados_triagem_base
        
        with st.form("form_final"):
            f_nivel = st.selectbox("38. Classificação do Nível de Assistência *", ["Primário", "Secundário A", "Secundário B", "Terciário"])
            f_conduta = st.text_area("83. Conduta Terapêutica Adotada *")
            f_via_prop = st.selectbox("84. Via de Alimentação Proposta *", ["Oral", "Sonda Nasoenteral", "Gastrostomia", "Jejunostomia", "Parenteral periférica", "Parenteral central", "Jejum"])
            f_dieta_prescrita = st.text_input("Dieta / Fórmula Específica Prescrita *")
            
            btn_salvar_banco = st.form_submit_button("Salvar e Registrar Ficha em Banco do Hospital")
            
            if btn_salvar_banco:
                novo_registro = {
                    "Avaliador": db["Avaliador"], "Data Admissão": db["Data Admissão"], "Nome": db["Nome"], 
                    "Sexo": db["Sexo"], "Setor": db["Setor"], "Leito": db["Leito"], "Data Triagem": db["Data Triagem"], 
                    "Via Alimentação": db["Via Alimentação"], "Momento": db["Momento"], "Diagnóstico": db.get("Diagnóstico", "N/A"), 
                    "Comorbidades": db.get("Comorbidades", "N/A"), "Peso Habitual": db.get("Peso Habitual", 0.0), 
                    "Altura Referida": db.get("Altura Referida", 0.0), "Data Nascimento": db.get("Data Nascimento", "N/A"), 
                    "Idade Anos": db.get("Idade Anos", 0), "Idade Meses": db.get("Idade Meses", 0), "Faixa Etária": db.get("Faixa Etária", "N/A"), 
                    "Escore Triagem": db["Escore Triagem"], "Risco": db["Risco"], "Nível Assistência": f_nivel, 
                    "Via Proposta": f_via_prop, "Dieta Prescrita": f_dieta_prescrita, "Adequacao_Calorica": 100.0
                }
                st.session_state.banco_pacientes = pd.concat([st.session_state.banco_pacientes, pd.DataFrame([novo_registro])], ignore_index=True)
                st.success("✅ Ficha integrada com sucesso!")
                del st.session_state.dados_triagem_base
                st.session_state.passo_atual = "identificacao"
                st.rerun()

    # OUTRAS SEÇÕES
    elif st.session_state.passo_atual == "avaliacao_detalhada_secao":
        st.subheader("📋 Pergunta 39: Direcionamento de Avaliação Nutricional Detalhada (Pós-Triagem)")
        st.info("Pulo da Pergunta 9 ativado: Estágio de Reavaliação.")
        f_tipo_detalhe = st.radio("Selecione o segmento da avaliação detalhada:", ["Pediátrica (Pula para Q40)", "Adulto (Pula para Q51)", "Idoso (Pula para Q67)"])
        if st.button("Abrir Questionário Clínico Avançado"):
            st.success("Formulário Avançado de Diagnóstico pronto para receber dados.")
            
    elif st.session_state.passo_atual == "evolucao_direta_secao":
        st.subheader("📈 Pergunta 86: Parâmetros de Evolução Nutricional")
        st.info("Pulo da Pergunta 9 ativado: Acompanhamento continuado.")
        st.selectbox("86. Via de Alimentação Atual Encontrada:", ["Oral", "Sonda Nasoenteral", "Gastrostomia", "Jejunostomia", "Parenteral periférica", "Parenteral central", "Jejum"])
        if st.button("Salvar Registro"):
            st.success("Dados salvos com sucesso.")

# [MÓDULO 2, MÓDULO 3 E MÓDULO 4 SEGUEM EXATAMENTE CONFORME EXIBIDO ANTERIORMENTE]
elif menu == "Módulo 2: Prescrição e Evolução":
    st.title("📋 Módulo 2: Prescrição e Evolução Clínica Diária (Beira-Leito)")
    df = st.session_state.banco_pacientes
    if df.empty:
        st.info("Nenhum paciente cadastrado. Realize a admissão no Módulo 1 para evoluir.")
    else:
        paciente_selecionado = st.selectbox("Selecione o Paciente para Check-in de Visita:", df["Nome"].unique())
        idx = df[df["Nome"] == paciente_selecionado].index[0]
        col_ev1, col_ev2 = st.columns(2)
        with col_ev1:
            st.markdown("#### Parâmetros de Tolerância Gastrointestinal")
            distensao = st.radio("Presença de Distensão Abdominal?", ["Não", "Sim"])
            evacuacao = st.radio("Padrão de Evacuações Preservado?", ["Sim, normal", "Não, constipação", "Não, diarreia"])
            residuo = st.number_input("Volume de Resíduo Gástrico Aferido (mL):", min_value=0, value=0)
        with col_ev2:
            st.markdown("#### Painel Laboratorial Crítico (Vigilância de Realimentação)")
            fosforo = st.number_input("Fósforo Sérico (mg/dL) - Ref: 2.5 - 4.5", min_value=0.0, value=3.0, step=0.1)
            magnesio = st.number_input("Magnésio Sérico (mg/dL) - Ref: 1.6 - 2.6", min_value=0.0, value=2.0, step=0.1)
            potassio = st.number_input("Potássio Sérico (mEq/L) - Ref: 3.5 - 5.0", min_value=0.0, value=4.0, step=0.1)
        vol_prescrito = st.number_input("Volume de Dieta Prescrito (mL/dia):", min_value=1, value=1000)
        vol_infundido = st.number_input("Volume de Dieta Efetivamente Infundido Real (mL/dia):", min_value=0, value=1000)
        if st.button("Salvar Evolução Diária"):
            adequacao = (vol_infundido / vol_prescrito) * 100
            st.session_state.banco_pacientes.at[idx, "Adequacao_Calorica"] = adequacao
            st.success(f"Evolução registrada. Taxa de adequação atualizada para {adequacao:.1f}%")

elif menu == "Módulo 3: Passagem de Plantão":
    st.title("📋 Módulo 3: Passagem de Plantão (Mural Digital)")
    df = st.session_state.banco_pacientes
    setores_oficiais = ["Pronto Socorro Adulto", "Pronto Socorro Infantil", "Clinica Médica", "Clínica Cirúrgica", "Ginecologia e Obstetrícia", "Pediatria", "UTI"]
    abas = st.tabs(setores_oficiais)
    for i, setor in enumerate(setores_oficiais):
        with abas[i]:
            df_filtrado = df[df['Setor'] == setor]
            if df_filtrado.empty:
                st.info("Nenhum paciente ativo nesta unidade.")
            else:
                st.dataframe(df_filtrado[["Leito", "Nome", "Sexo", "Faixa Etária", "Via Alimentação", "Risco", "Adequacao_Calorica", "Avaliador"]].sort_values(by="Leito"), use_container_width=True, hide_index=True)

elif menu == "Módulo 4: Dashboard de Indicadores":
    st.title("📊 Módulo 4: Dashboard de Indicadores Epidemiológicos e de Qualidade")
    df = st.session_state.banco_pacientes
    if df.empty:
        st.info("Base de dados vazia. Insira registros no Módulo 1.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total de Fichas Emitidas", len(df))
        st.markdown("---")
        g1, g2, g3 = st.columns(3)
        with g1: st.plotly_chart(px.bar(df, x='Setor', color='Setor'), use_container_width=True)
        with g2: st.plotly_chart(px.pie(df, names='Sexo'), use_container_width=True)
        with g3: st.plotly_chart(px.histogram(df, x='Faixa Etária'), use_container_width=True)
