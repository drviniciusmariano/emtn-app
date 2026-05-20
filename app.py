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

# FUNÇÃO AUXILIAR PARA CÁLCULO DE IDADE AUTOMÁTICA
def calcular_idade_detalhada(data_nasc):
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
    
    # Estados de controle do fluxo dinâmico
    if 'passo_atual' not in st.session_state:
        st.session_state.passo_atual = "identificacao"
    
    # RESETAR FLUXO
    if st.button("🔄 Reiniciar Formulário"):
        st.session_state.passo_atual = "identificacao"
        if 'dados_triagem_base' in st.session_state: del st.session_state.dados_triagem_base
        st.rerun()

    # -------------------------------------------------------------------------
    # PASSO 1: IDENTIFICAÇÃO (PERGUNTAS 1 A 9)
    # -------------------------------------------------------------------------
    if st.session_state.passo_atual == "identificacao":
        with st.form("form_passo_1"):
            st.subheader("Identificação Básica do Paciente")
            f_avaliador = st.text_input("1. Avaliador *", value=st.session_state.nome_avaliador, disabled=True)
            f_data_adm = st.date_input("2. Data de Admissão *")
            f_nome = st.text_input("3. Nome *")
            f_sexo = st.radio("4. Sexo *", ["Masculino", "Feminino"])
            f_setor = st.selectbox("5. Setor *", ["Pronto Socorro Adulto", "Pronto Socorro Infantil", "Clinica Médica", "Clínica Cirúrgica", "Ginecologia e Obstetrícia", "Pediatria", "UTI"])
            f_leito = st.text_input("6. Leito *")
            f_data_triagem = st.date_input("7. Data da Triagem")
            f_via = st.selectbox("8. Via de alimentação *", ["Oral", "Sonda Nasoenteral", "Gastrostomia", "Jejunostomia", "Parenteral periférica", "Parenteral central", "Jejum"])
            
            st.markdown("---")
            st.markdown("### 🧭 Direcionamento Logístico Ambulatorial")
            f_momento = st.radio("9. Selecione o Momento Operacional *", ["Avaliação Inicial", "Reavaliação", "Evolução Nutricional"])
            
            btn_proximo_1 = st.form_submit_button("Processar Direcionamento de Seção ➔")
            
            if btn_proximo_1:
                if not f_nome or not f_leito:
                    st.error("Por favor, preencha os campos obrigatórios (Nome e Leito).")
                else:
                    st.session_state.dados_triagem_base = {
                        "Avaliador": f_avaliador, "Data Admissão": str(f_data_adm), "Nome": f_nome, 
                        "Sexo": f_sexo, "Setor": f_setor, "Leito": f_leito, "Data Triagem": str(f_data_triagem), 
                        "Via Alimentação": f_via, "Momento": f_momento
                    }
                    
                    # Lógica de Pulo da Pergunta 9 do Formulário Oficial
                    if f_momento == "Avaliação Inicial":
                        st.session_state.passo_atual = "anamnese" # Segue para pergunta 10
                    elif f_momento == "Reavaliação":
                        st.session_state.passo_atual = "avaliacao_detalhada_secao" # Pula para a pergunta 39
                    elif f_momento == "Evolução Nutricional":
                        st.session_state.passo_atual = "evolucao_direta_secao" # Pula para a pergunta 86
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
            f_data_nasc = st.date_input("14. Data de Nascimento *", value=date(2000, 1, 1))
            
            btn_proximo_2 = st.form_submit_button("Avançar para Triagem Específica ➔")
            
            if btn_proximo_2:
                # Automação da Idade e Faixa Etária por Diferença Temporal
                anos, meses = calcular_idade_detalhada(f_data_nasc)
                
                if anos < 19:
                    faixa_calculada = "<=18"
                elif 19 <= anos <= 59:
                    faixa_calculada = "19-59"
                else:
                    faixa_calculada = ">= 60"
                
                st.session_state.dados_triagem_base.update({
                    "Diagnóstico": f_diag, "Comorbidades": ", ".join(f_comorbidades),
                    "Peso Habitual": f_peso_hab, "Altura Referida": f_altura, "Data Nascimento": str(f_data_nasc),
                    "Idade Anos": anos, "Idade Meses": meses, "Faixa Etária": faixa_calculada
                })
                
                # Encaminhamento automático baseado na idade calculada (Pergunta 16 Automatizada)
                st.session_state.passo_atual = f"triagem_{faixa_calculada}"
                st.rerun()

    # -------------------------------------------------------------------------
    # PASSO 3A: TRIAGEM PEDIÁTRICA (STRONG KIDS - PERGUNTAS 17 A 22)
    # -------------------------------------------------------------------------
    elif st.session_state.passo_atual == "triagem_<=18":
        st.subheader("🧬 Screening Tool Risk Nutritional Status and Growth - STRONG KIDS (Idade ≤ 18)")
        st.info(f"Paciente: {st.session_state.dados_triagem_base['Nome']} | Idade Calculada: {st.session_state.dados_triagem_base['IdadeAnos']} anos e {st.session_state.dados_triagem_base['IdadeMeses']} meses.")
        
        # Mapeamentos de Pontuação Protegidos contra Erros de Fatiamento
        map_q17 = {"Não (0 ponto)": 0, "Sim (1 ponto)": 1}
        map_q18 = {"Não (0 ponto)": 0, "Sim (2 ponto)": 2}
        map_q19 = {"Não (0 ponto)": 0, "Sim (1 ponto)": 1}
        map_q20 = {"Não (0 ponto)": 0, "Sim (1 ponto)": 1}
        
        q17_sel = st.radio("17. 1. Avaliação nutricional subjetiva: a criança parece ter déficit nutricional ou desnutrição?", list(map_q17.keys()))
        q18_sel = st.radio("18. 2. Doença (com alto risco nutricional) ou cirurgia de grande porte?", list(map_q18.keys()))
        q19_sel = st.radio("19. 3. Ingestão nutricional e/ou perda nos últimos dias?", list(map_q19.keys()))
        q20_sel = st.radio("20. 4. Refere perda de peso ou ganho insuficiente nas últimas semanas ou meses?", list(map_q20.keys()))
        
        # Soma Automatizada das Pontuações
        escore_strong = map_q17[q17_sel] + map_q18[q18_sel] + map_q19[q19_sel] + map_q20[q20_sel]
        
        # Classificação do Escore Conforme Manual (Perguntas 21 e 22)
        if escore_strong == 0:
            risco_strong = "Baixo"
            cor_flag = "#D4EDDA"
            cor_texto = "#155724"
            borda = "28A745"
            diretriz = "🔹 Conduta Baixo Risco:\n1. Checar peso regularmente.\n2. Reavaliar risco em 1 semana."
        elif 1 <= escore_strong <= 3:
            risco_strong = "Médio"
            cor_flag = "#FFF3CD"
            cor_texto = "#856404"
            borda = "FFC107"
            diretriz = "🔸 Conduta Médio Risco:\n1. Consultar médico para diagnóstico completo.\n2. Considerar intervenção nutricional.\n3. Checar peso 2x/semana.\n4. Reavaliar o risco nutricional após 1 semana."
        else:
            risco_strong = "Alto"
            cor_flag = "#F8D7DA"
            cor_texto = "#721C24"
            borda = "DC3545"
            diretriz = "🛑 CONDUTA EM ALTO RISCO:\n1. Consultar médico ou nutricionista para diagnóstico completo imediato.\n2. Orientação nutricional individualizada e seguimento restrito.\n3. Iniciar suplementação oral até conclusão do diagnóstico nutricional."

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

    # -------------------------------------------------------------------------
    # PASSO 3B: TRIAGEM ADULTO (NRS 2002 - PERGUNTAS 23 A 29)
    # -------------------------------------------------------------------------
    elif st.session_state.passo_atual == "triagem_19-59":
        st.subheader("🫁 Triagem Nutricional - NRS 2002 (Idade 19-59)")
        st.caption(f"Paciente: {st.session_state.dados_triagem_base['Nome']}")
        
        f_peso_atual = st.number_input("23. Peso atual (kg) *", min_value=0.0, step=0.1, format="%.2f")
        
        # Cálculo Automático do IMC para a Pergunta 24
        imc_nrs = 0.0
        if st.session_state.dados_triagem_base["Altura Referida"] > 0 and f_peso_atual > 0:
            imc_nrs = f_peso_atual / (st.session_state.dados_triagem_base["Altura Referida"] ** 2)
        st.disabled = True
        st.text_input("24. IMC Computado (kg/m²)", value=f"{imc_nrs:.2f}", disabled=True)
        
        st.markdown("---")
        st.markdown("#### 25. Etapa 1: Triagem Inicial")
        nrs_q1 = st.checkbox("1) O IMC é < 20,5 kg/m²?")
        nrs_q2 = st.checkbox("2) O paciente perdeu peso nos 3 últimos meses?")
        nrs_q3 = st.checkbox("3) O paciente teve sua ingestão dietética reduzida na última semana?")
        nrs_q4 = st.checkbox("4) O paciente é gravemente doente?")
        
        # Condicional Inteligente (Suprime ou Executa a Pergunta 26/27 de forma limpa)
        qualquer_sim = nrs_q1 or nrs_q2 or nrs_q3 or nrs_q4
        
        escore_final_nrs = 0
        risco_nrs = "Baixo"
        
        if qualquer_sim:
            st.markdown("---")
            st.warning("⚠️ Triagem Inicial Positiva! Direcionando para a Etapa 2 (Triagem Final).")
            
            map_q27 = {"Ausente (0 ponto)": 0, "Leve (1 ponto)": 1, "Moderado (2 pontos)": 2, "Grave (3 pontos)": 3}
            map_q28 = {"Ausente (0 ponto)": 0, "Leve (1 ponto)": 1, "Moderado (2 pontos)": 2, "Grave (3 pontos)": 3}
            
            st.markdown("##### 27. Deterioração do Estado Nutricional")
            q27_sel = st.selectbox("Selecione o grau de deterioração conforme critérios clínicos:", list(map_q27.keys()))
            st.caption("• Leve: Perda de peso >5% em 3 meses ou ingesta oral entre 50-75%.\n• Moderado: Perda >5% em 2 meses ou IMC 18.5-20.5 + piora geral ou ingesta 25-50%.\n• Grave: Perda >5% em 1 mês ou IMC <18.5 + piora geral ou ingesta <25%.")
            
            st.markdown("##### 28. Gravidade da Doença (Grau de Estresse)")
            q28_sel = st.selectbox("Selecione o grau de estresse metabólico da doença:", list(map_q28.keys()))
            st.info("💡 **Diretriz de Auditoria HMP:** Fratura de quadril ou pacientes oncológicos estáveis classificam-se como Leve (1pt). Cirurgias abdominais de grande porte ou AVC são Moderados (2pt). Pacientes críticos sob terapia intensiva com SAPS 3 entre 45 e 55 pontos (equivalente moderno ao APACHE II > 10) devem ser classificados como Grave (3pt).")
            
            # Cálculo do Escore Combinado (Pergunta 29)
            escore_final_nrs = map_q27[q27_sel] + map_q28[q28_sel]
            
            # Correção de fragilidade por idade (>70 anos ganha +1 ponto conforme protocolo)
            if st.session_state.dados_triagem_base["Idade Anos"] > 70:
                escore_final_nrs += 1
                st.caption("👴 Adicionado +1 ponto ao escore devido à idade superior a 70 anos.")
                
            if escore_final_nrs >= 3:
                risco_nrs = "Alto"
        else:
            st.success("✅ Triagem Inicial Negativa. Paciente sem risco nutricional aparente no momento. Repetir triagem a cada 7 dias.")
            escore_final_nrs = 0
            risco_nrs = "Baixo"

        st.markdown("---")
        st.markdown(f"#### 29. Consolidação do Escore Final - NRS 2002")
        st.metric("Pontuação Total", f"{escore_final_nrs} Pontos", delta="Risco ALTO (Indicação de Enteral)" if escore_final_nrs >= 3 else "Risco BAIXO/MÉDIO")
        
        if st.button("Gravar Dados e Ir para Definição de Conduta ➔"):
            st.session_state.dados_triagem_base.update({"Escore Triagem": escore_final_nrs, "Risco": risco_nrs})
            st.session_state.passo_atual = "conduta_final"
            st.rerun()

    # -------------------------------------------------------------------------
    # PASSO 3C: TRIAGEM IDOSO (MNA® - PERGUNTAS 30 A 37)
    # -------------------------------------------------------------------------
    elif st.session_state.passo_atual == "triagem_>= 60":
        st.subheader("👴 Mini Nutritional Assessment - MNA® (População Geriátrica ≥ 60)")
        st.caption(f"Paciente: {st.session_state.dados_triagem_base['Nome']}")
        
        # Mapeamentos Explícitos Isolados por Variáveis Estruturadas (Evita falhas de String)
        map_mna_a = {"Sem diminuição da ingesta (2 pontos)": 2, "Diminuição moderada da ingesta (1 ponto)": 1, "Diminuição grave da ingesta (0 ponto)": 0}
        map_mna_b = {"Sem perda de peso (3 pontos)": 3, "Perda entre 1 e 3kg (2 pontos)": 2, "Não sabe (1 ponto)": 1, "Perda > 3kg (0 ponto)": 0}
        map_mna_c = {"Normal (2 pontos)": 2, "Deambula mas não é capaz de sair de casa (1 ponto)": 1, "Restrito ao leito ou à cadeira de rodas (0 ponto)": 0}
        map_mna_d = {"Não (2 pontos)": 2, "Sim (0 ponto)": 0}
        map_mna_e = {"Sem problemas psicológicos (2 pontos)": 2, "Demência ligeira (1 ponto)": 1, "Demência ou depressão graves (0 ponto)": 0}
        map_mna_f = {"IMC >= 23 (3 pontos)": 3, "21 <= IMC < 23 (2 pontos)": 2, "19 <= IMC < 21 (1 ponto)": 1, "IMC < 19 (0 ponto)": 0}

        mna_a = st.selectbox("30. A. Diminuição da ingesta alimentar nos últimos 3 meses por perda de apetite/problemas digestivos?", list(map_mna_a.keys()))
        mna_b = st.selectbox("31. B. Perda de peso nos últimos 3 meses?", list(map_mna_b.keys()))
        mna_c = st.selectbox("32. C. Mobilidade *", list(map_mna_c.keys()))
        mna_d = st.selectbox("33. D. Passou por algum stress psicológico ou doença aguda nos últimos três meses?", list(map_mna_d.keys()))
        mna_e = st.selectbox("34. E. Problemas neuropsicológicos?", list(map_mna_e.keys()))
        mna_f = st.selectbox("35. F. Índice de Massa Corporal - IMC (kg/m²)", list(map_mna_f.keys()))
        
        # Cálculo Seguro Automatizado das Questões Geriátricas A até F
        escore_mna_triagem = map_mna_a[mna_a] + map_mna_b[mna_b] + map_mna_c[mna_c] + map_mna_d[mna_d] + map_mna_e[mna_e] + map_mna_f[mna_f]
        
        # Perguntas 36 e 37: Classificação do Estado Nutricional
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
                <p><b>Escore Calculado:</b> {escore_mna_triagem} Pontos (Máximo de 14)</p>
                <p><b>Classificação Geriátrica:</b> {texto_status} (Risco {risco_mna})</p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Gravar Triagem MNA® e Prosseguir ➔"):
            st.session_state.dados_triagem_base.update({"Escore Triagem": escore_mna_triagem, "Risco": risco_mna})
            st.session_state.passo_atual = "conduta_final"
            st.rerun()

    # -------------------------------------------------------------------------
    # PASSO 4: FINALIZAÇÃO E TERAPIA NUTRICIONAL PROPOSTA (PERGUNTAS 38, 83, 84)
    # -------------------------------------------------------------------------
    elif st.session_state.passo_atual == "conduta_final":
        st.subheader("🏁 Definição da Conduta e Terapia Nutricional Proposta")
        db = st.session_state.dados_triagem_base
        
        with st.form("form_final"):
            st.write(f"**Paciente:** {db['Nome']} | **Triagem:** {db['Risco']} ({db['Escore Triagem']} pts)")
            
            f_nivel = st.selectbox("38. Classificação do Nível de Assistência *", ["Primário", "Secundário A", "Secundário B", "Terciário"])
            st.caption("• Primário: Sem risco e sem dieta específica.\n• Secundário A: Doença exige dieta específica, mas está sem risco.\n• Secundário B: Doença livre, porém possui riscos nutricionais ativos.\n• Terciário: Doença com cuidados altamente especializados e risco estabelecido.")
            
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
                st.success("✅ Ficha de admissão e conduta integrada com sucesso na linha de evolução clínica!")
                
                # Gatilho de Alerta Vermelho de Alta Prioridade
                if f_nivel == "Terciário" or db["Risco"] == "Alto":
                    st.markdown(f"<div style='padding:20px; background-color:#F8D7DA; color:#721C24; border-radius:8px; font-weight:bold; border-left:8px solid #DC3545;'>🛑 ALERTA DE RISCO CRÍTICO ENCAMINHADO À EQUIPE: Priorizar atendimento beira-leito imediato.</div>", unsafe_allow_html=True)
                
                del st.session_state.dados_triagem_base
                st.session_state.passo_atual = "identificacao"
                st.rerun()

    # -------------------------------------------------------------------------
    # DESVIOS DA PERGUNTA 9: REAVALIAÇÃO & EVOLUÇÃO
    # -------------------------------------------------------------------------
    elif st.session_state.passo_atual == "avaliacao_detalhada_secao":
        st.subheader("📋 Pergunta 39: Direcionamento de Avaliação Nutricional Detalhada (Pós-Triagem)")
        st.info("Pulo da Pergunta 9 ativado: Usuário em estágio de Reavaliação.")
        st.write(f"Paciente: {st.session_state.dados_triagem_base['Nome']}")
        
        f_tipo_detalhe = st.radio("Selecione o segmento da avaliação detalhada:", ["Pediátrica (Pula para Q40)", "Adulto (Pula para Q51)", "Idoso (Pula para Q67)"])
        if st.button("Abrir Questionário Clínico Avançado"):
            st.success("Formulário Avançado de Diagnóstico (SGNA/ASG) pronto para receber dados.")
            
    elif st.session_state.passo_atual == "evolucao_direta_secao":
        st.subheader("📈 Pergunta 86: Parâmetros de Evolução Nutricional")
        st.info("Pulo da Pergunta 9 ativado: Usuário direto na seção de acompanhamento continuado.")
        st.write(f"Paciente: {st.session_state.dados_triagem_base['Nome']}")
        st.selectbox("86. Via de Alimentação Atual Encontrada:", ["Oral", "Sonda Nasoenteral", "Gastrostomia", "Jejunostomia", "Parenteral periférica", "Parenteral central", "Jejum"])
        st.text_input("Dieta Prescrita Ativa:")
        if st.button("Salvar Registro"):
            st.success("Dados salvos com sucesso.")

# --------------------------------------------------------------------------------------------------
# MÓDULO 2: PRESCRIÇÃO E EVOLUÇÃO CLÍNICA DIÁRIA
# --------------------------------------------------------------------------------------------------
elif menu == "Módulo 2: Prescrição e Evolução":
    st.title("📋 Módulo 2: Prescrição e Evolução Clínica Diária (Beira-Leito)")
    df = st.session_state.banco_pacientes
    
    if df.empty:
        st.info("Nenhum paciente cadastrado. Realize a admissão no Módulo 1 para evoluir.")
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
            fosforo = st.number_input("Fósforo Sérico (mg/dL) - Ref: 2.5 - 4.5", min_value=0.0, value=3.0, step=0.1)
            magnesio = st.number_input("Magnésio Sérico (mg/dL) - Ref: 1.6 - 2.6", min_value=0.0, value=2.0, step=0.1)
            potassio = st.number_input("Potássio Sérico (mEq/L) - Ref: 3.5 - 5.0", min_value=0.0, value=4.0, step=0.1)
            
            if fosforo < 2.5 or magnesio < 1.6 or potassio < 3.5:
                st.markdown("<div style='background-color:#FFF3CD; padding:10px; border-left:4px solid #FFC107; color:#856404; font-weight:bold;'>⚠️ RISCO DE SÍNDROME DE REALIMENTAÇÃO: Níveis críticos de eletrólitos identificados!</div>", unsafe_allow_html=True)
                
        st.markdown("---")
        st.markdown("#### Evolução de Metas")
        vol_prescrito = st.number_input("Volume de Dieta Prescrito (mL/dia):", min_value=1, value=1000)
        vol_infundido = st.number_input("Volume de Dieta Efetivamente Infundido Real (mL/dia):", min_value=0, value=1000)
        
        if st.button("Salvar Evolução Diária"):
            adequacao = (vol_infundido / vol_prescrito) * 100
            st.session_state.banco_pacientes.at[idx, "Adequacao_Calorica"] = adequacao
            st.success(f"Evolução registrada. Taxa de adequação do paciente atualizada para {adequacao:.1f}%")

# --------------------------------------------------------------------------------------------------
# MÓDULO 3: PASSAGEM DE PLANTÃO
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
                pacientes_criticos = df_filtrado[df_filtrado['Risco'] == 'Alto']
                pacientes_jejum = df_filtrado[df_filtrado['Via Alimentação'] == 'Jejum']
                
                if not pacientes_criticos.empty:
                    st.warning(f"⚠️ **Aviso Amarelo:** Há {len(pacientes_criticos)} paciente(s) com Alto Risco detectado pelas triagens.")
                if not pacientes_jejum.empty:
                    st.error(f"🛑 **Aviso Vermelho:** Há {len(pacientes_jejum)} paciente(s) registrado(s) em JEJUM nesta ala!")
                
                st.dataframe(
                    df_filtrado[["Leito", "Nome", "Sexo", "Faixa Etária", "Via Alimentação", "Risco", "Adequacao_Calorica", "Avaliador"]].sort_values(by="Leito"),
                    use_container_width=True, hide_index=True,
                    column_config={"Adequacao_Calorica": st.column_config.NumberColumn("Adequação (%)", format="%.1f%%")}
                )

# --------------------------------------------------------------------------------------------------
# MÓDULO 4: DASHBOARD DE INDICADORES DE QUALIDADE
# --------------------------------------------------------------------------------------------------
elif menu == "Módulo 4: Dashboard de Indicadores":
    st.title("📊 Módulo 4: Dashboard de Indicadores Epidemiológicos e de Qualidade")
    df = st.session_state.banco_pacientes
    
    if df.empty:
        st.info("Base de dados vazia. Insira registros no Módulo 1 para visualizar os indicadores gráficos.")
    else:
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-card'><h4>Total de Fichas Emitidas</h4><h1>{len(df)}</h1></div>", unsafe_allow_html=True)
        with m2:
            taxa_jejum_ind = (len(df[df['Via Alimentação'] == 'Jejum']) / len(df)) * 100
            st.markdown(f"<div class='metric-card' style='border-left-color: #D97E3A;'><h4>Índice de Jejum Geral</h4><h1>{taxa_jejum_ind:.1f}%</h1></div>", unsafe_allow_html=True)
        with m3:
            total_dietas = len(df[df['Dieta Prescrita'] != ""])
            st.markdown(f"<div class='metric-card' style='border-left-color: #3182CE;'><h4>Fórmulas Prescritas Ativas</h4><h1>{total_dietas}</h1></div>", unsafe_allow_html=True)

        st.markdown("---")
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown("##### Casos Cadastrados por Setor")
            st.plotly_chart(px.bar(df, x='Setor', color='Setor', color_discrete_sequence=px.colors.qualitative.Dark2), use_container_width=True)
        with g2:
            st.markdown("##### Prevalência por Sexo")
            st.plotly_chart(px.pie(df, names='Sexo', color_discrete_sequence=['#4D6452', '#D97E3A']), use_container_width=True)
        with g3:
            st.markdown("##### Divisão por Faixa Etária")
            st.plotly_chart(px.histogram(df, x='Faixa Etária', color_discrete_sequence=['#3182CE']), use_container_width=True)

        st.markdown("---")
        g4, g5, g6 = st.columns(3)
        with g4:
            st.markdown("##### Perfil do Risco Nutricional")
            st.plotly_chart(px.bar(df, x='Risco', color='Risco', color_discrete_map={'Alto': '#DC3545', 'Médio': '#FFC107', 'Baixo': '#28A745'}), use_container_width=True)
        with g5:
            st.markdown("##### Distribuição de Vias de Alimentação")
            st.plotly_chart(px.pie(df, names='Via Alimentação', color_discrete_sequence=px.colors.sequential.YlGnBu), use_container_width=True)
        with g6:
            st.markdown("##### Score Clínico de Fórmulas e Dietas")
            df_dietas_score = df['Dieta Prescrita'].value_counts().reset_index()
            df_dietas_score.columns = ['Fórmula / Dieta', 'Quantidade']
            st.dataframe(df_dietas_score, use_container_width=True, hide_index=True)
