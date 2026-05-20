import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, date

# CONFIGURAÇÕES DA PÁGINA
st.set_page_config(page_title="EMTN - Hospital Municipal de Paulínia", page_icon="🏥", layout="wide")

# ESTILIZAÇÃO CUSTOMIZADA E REGRAS DE IMPRESSÃO
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
        .ai-box {
            background-color: #F0F4F8;
            border-left: 6px solid #1E3A8A;
            color: #1E3A8A;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        
        /* Configuração de Impressão Otimizada para PDF */
        @media print {
            body * { visibility: hidden; }
            .secao-impressao, .secao-impressao * { visibility: visible; }
            .secao-impressao { 
                position: absolute; 
                left: 0; 
                top: 0; 
                width: 100%; 
                font-size: 12pt; 
                color: #000;
                background: white;
            }
            .no-print { display: none !important; }
        }
    </style>
""", unsafe_allow_html=True)

# BANCO DE DADOS EM MEMÓRIA (INICIALIZAÇÃO DO ESTADO SA SESSÃO)
if 'banco_pacientes' not in st.session_state:
    st.session_state.banco_pacientes = pd.DataFrame(columns=[
        "Avaliador", "Data Admissão", "Nome", "Sexo", "Setor", "Leito", "Data Triagem", 
        "Via Alimentação", "Momento", "Diagnóstico", "Comorbidades", "Peso Habitual", 
        "Altura Referida", "Data Nascimento", "Idade Anos", "Idade Meses", "Faixa Etária", 
        "Escore Triagem", "Risco", "Intervencao_Obrigatoria", "Nível Assistência", "Via Proposta", 
        "Dieta Prescrita", "Adequacao_Calorica", "Parecer_IA", "Notas_Plantao", "Ultima_Reavaliacao"
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

# FUNÇÃO DE INTELIGÊNCIA ARTIFICIAL CLÍNICA REVISADA (Conforme Manuais USP, HMP e Matrizes de Risco)
def analisar_dados_com_ia(dados):
    idade = dados.get("Idade Anos", 30)
    comorbidades = dados.get("Comorbidades", "")
    escore = dados.get("Escore Triagem", 0)
    risco = dados.get("Risco", "Baixo")
    via_atual = dados.get("Via Alimentação", "Oral")
    faixa_etaria = dados.get("Faixa Etária", "19-59")
    
    insights = []
    
    # Alerta de Realimentação baseado em critérios específicos e não em fórmulas genéricas de infusão
    if "Etilismo" in comorbidades or "Acamado(a)" in comorbidades or (faixa_etaria == "19-59" and escore >= 3) or (faixa_etaria == ">= 60" and escore < 12):
        insights.append("🛑 **Risco Clínico Intermediado (Síndrome de Realimentação):** Paciente com critérios de vulnerabilidade metabólica aguda. Recomenda-se acompanhamento rigoroso pela EMTN de eletrólitos extracelulares (Fósforo, Magnésio, Potássio) nas primeiras 72h e progressão escalonada obrigatória do aporte calórico total diário.")
    
    # Intervenção em Geriatria (Manual de Cuidados ao Idoso / MNA)
    if faixa_etaria == ">= 60" and (risco == "Risco de Desnutrição" or risco == "Desnutrido"):
        insights.append("👴 **Fragilidade Geriátrica Avançada:** Paciente idoso identificado em risco ou déficit nutricional evidente. Alerta para alta propensão à perda de massa muscular magra (sarcopenia) e queda da imunidade celular. Priorizar via oral qualificada ou terapia enteral precoce.")
        
    # Diabetes Mellitus
    if "Diabetes mellitus" in comorbidades:
        insights.append("📊 **Restrição Metabólica:** Paciente com distúrbio do metabolismo glicídico. Necessita de monitorização capilar frequente e formulações com menor índice de carboidratos simples.")

    # Alerta de Inconsistência Crítica (Jejum em Alto Risco)
    if via_atual == "Jejum" and risco in ["Alto", "Risco de Desnutrição", "Desnutrido"]:
        insights.append("🚨 **Alerta de Segurança do Paciente:** Paciente classificado com risco nutricional estabelecido e mantido em Jejum. Risco severo de depleção de glicogênio hepático e catabolismo muscular acelerado se ultrapassar 24 horas sem terapia nutricional ativa.")

    if not insights:
        insights.append("✅ **Parâmetros de Estabilidade:** Dados clínicos atuais sem alertas críticos imediatos. Seguir protocolo assistencial padrão conforme nível de atenção definido.")
        
    return "\n\n".join(insights)


# --------------------------------------------------------------------------------------------------
# MÓDULO 1: TRIAGEM E ADMISSÃO DE PACIENTES
# --------------------------------------------------------------------------------------------------
if menu == "Módulo 1: Triagem e Admissão":
    st.title("🧬 Módulo 1: Triagem e Admissão de Pacientes")
    
    if 'passo_atual' not in st.session_state:
        st.session_state.passo_atual = "identificacao"
    
    # Barra de ferramentas para controle e rastreabilidade do fluxo
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1:
        if st.session_state.passo_atual != "identificacao":
            if st.button("⬅️ Voltar Etapa", use_container_width=True):
                if st.session_state.passo_atual in ["triagem_<=18", "triagem_19-59", "triagem_>= 60"]:
                    st.session_state.passo_atual = "anamnese"
                elif st.session_state.passo_atual == "anamnese":
                    st.session_state.passo_atual = "identificacao"
                elif st.session_state.passo_atual == "conduta_final":
                    faixa = st.session_state.dados_triagem_base.get("Faixa Etária", "19-59")
                    st.session_state.passo_atual = f"triagem_{faixa}"
                elif st.session_state.passo_atual == "laudo_impressao":
                    st.session_state.passo_atual = "conduta_final"
                st.rerun()
    with col_nav2:
        if st.button("🔄 Reiniciar e Limpar Formulário", key="btn_reset"):
            st.session_state.passo_atual = "identificacao"
            if 'dados_triagem_base' in st.session_state: del st.session_state.dados_triagem_base
            st.rerun()

    st.markdown("---")

    # ETAPA 1: IDENTIFICAÇÃO DO PACIENTE
    if st.session_state.passo_atual == "identificacao":
        with st.form("form_passo_1"):
            st.subheader("Identificação Básica do Paciente")
            f_avaliador = st.text_input("1. Avaliador *", value=st.session_state.nome_avaliador, disabled=True)
            f_data_adm = st.date_input("2. Data de Admissão Hospitalar *", format="DD/MM/YYYY")
            f_nome = st.text_input("3. Nome Completo do Paciente *")
            f_sexo = st.radio("4. Gênero Biológico *", ["Masculino", "Feminino"])
            f_setor = st.selectbox("5. Setor de Internação *", ["Pronto Socorro Adulto", "Pronto Socorro Infantil", "Clinica Médica", "Clínica Cirúrgica", "Ginecologia e Obstetrícia", "Pediatria", "UTI"])
            f_leito = st.text_input("6. Identificação do Leito *")
            f_data_triagem = st.date_input("7. Data Real da Triagem EMTN", format="DD/MM/YYYY")
            f_via = st.selectbox("8. Via de Alimentação de Entrada *", ["Oral", "Sonda Nasoenteral", "Gastrostomia", "Jejunostomia", "Parenteral periférica", "Parenteral central", "Jejum"])
            
            st.markdown("---")
            f_momento = st.radio("9. Qual o momento da avaliação atual? *", ["Avaliação Inicial", "Reavaliação", "Evolução Nutricional"])
            
            btn_proximo_1 = st.form_submit_button("Avançar para Dados Clínicos e Idade ➔")
            
            if btn_proximo_1:
                if not f_nome or not f_leito:
                    st.error("Por favor, preencha os campos obrigatórios (*): Nome e Leito.")
                else:
                    st.session_state.dados_triagem_base = {
                        "Avaliador": f_avaliador, "Data Admissão": f_data_adm.strftime("%Y-%m-%d"), 
                        "Nome": f_nome, "Sexo": f_sexo, "Setor": f_setor, "Leito": f_leito, 
                        "Data Triagem": f_data_triagem.strftime("%Y-%m-%d"), "Via Alimentação": f_via, "Momento": f_momento,
                        "Notas_Plantao": "", "Ultima_Reavaliacao": "Não Reavaliado"
                    }
                    st.session_state.passo_atual = "anamnese"
                    st.rerun()

    # ETAPA 2: ANAMNESE E VALIDAÇÃO AUTOMÁTICA DA IDADE
    elif st.session_state.passo_atual == "anamnese":
        st.subheader("Anamnese Clínica e Perfil Antropométrico")
        st.markdown(f"**Paciente Selecionado:** {st.session_state.dados_triagem_base['Nome']} | **Leito:** {st.session_state.dados_triagem_base['Leito']}")
        
        with st.form("form_passo_2"):
            f_data_nasc = st.date_input("14. Data de Nascimento do Paciente *", value=date(1980, 1, 1), min_value=date(1900, 1, 1), max_value=date.today(), format="DD/MM/YYYY")
            
            # Cálculo imediato e demonstrativo pedagógico da idade na identificação
            anos, meses = calcular_idade_detalhada(f_data_nasc)
            st.success(f"📌 **Idade Calculada para Identificação:** {anos} anos e {meses} meses.")
            
            st.markdown("---")
            f_diag = st.text_area("10. Diagnóstico Médico de Admissão *")
            f_comorbidades = st.multiselect("11. Comorbidades Crônicas Associadas *", ["NÃO POSSUI COMORBIDADE", "Acamado(a)", "Diabetes mellitus", "Drogadição (SPA)", "Etilismo", "Hipertensão arterial sistêmica", "Infarto", "Insuficiência cardíaca", "Obesidade", "Tabagismo", "Doença autoimune", "Doença hematológica", "Doença hepática ou gastrointestinal", "Doença nefrológica", "Doença neoplásica", "Doença neurológica", "Doença psiquiátrica", "Doença respiratória", "Doença sexualmente transmissível", "Outra doença cardiovascular", "Outra doença endócrina", "Doença gestacional - Hipertensão arterial sistêmica", "Doença gestacional - Diabetes mellitus", "Doença gestacional - Outra doença endócrina", "Doença gestacional - Outra(s) doença(s)", "Outra(s) doença(s)"])
            f_peso_hab = st.number_input("12. Peso Habitual Referido (kg) *", min_value=0.0, step=0.1, format="%.2f")
            f_altura = st.number_input("13. Altura Estimada/Referida (m) *", min_value=0.0, step=0.01, format="%.2f")
            
            btn_proximo_2 = st.form_submit_button("Vincular e Chamar Questionário de Triagem Alvo ➔")
            
            if btn_proximo_2:
                faixa_calculada = "<=18" if anos < 19 else ("19-59" if 19 <= anos <= 59 else ">= 60")
                
                st.session_state.dados_triagem_base.update({
                    "Diagnóstico": f_diag, "Comorbidades": ", ".join(f_comorbidades),
                    "Peso Habitual": f_peso_hab, "Altura Referida": f_altura, 
                    "Data Nascimento": f_data_nasc.strftime("%Y-%m-%d"),
                    "Idade Anos": anos, "Idade Meses": meses, "Faixa Etária": faixa_calculada
                })
                
                if st.session_state.dados_triagem_base["Momento"] in ["Reavaliação", "Evolução Nutricional"]:
                    st.session_state.dados_triagem_base.update({"Escore Triagem": 0, "Risco": "Acompanhamento Continuado", "Intervencao_Obrigatoria": "Manutenção das condutas prévias e reavaliação de metas diárias."})
                    st.session_state.passo_atual = "conduta_final"
                else:
                    st.session_state.passo_atual = f"triagem_{faixa_calculada}"
                st.rerun()

    # ETAPA 3A: TRIAGEM PEDRIÁTRICA (STRONG KIDS) COM EXIBIÇÃO DA MATRIZ DE RISCO
    elif st.session_state.passo_atual == "triagem_<=18":
        st.subheader("🧬 Rastreamento de Risco Pediátrico: Ferramenta STRONG KIDS")
        
        st.info("""
        🔬 **Descritivo Explicativo HMP / USP:** A ferramenta STRONGkids avalia 4 domínios críticos para desnutrição infantil intrahospitalar: status subjetivo, gravidade da patologia de base, perdas/ingestão insatisfatória e variações recentes de peso. Aplicação obrigatória em pediatria.
        """)
        
        with st.form("form_strong"):
            q17_sel = st.radio("17. 1. Avaliação nutricional clínica subjetiva: A criança aparenta perda de tecido adiposo ou massa muscular subcutânea?", ["Não (0 ponto)", "Sim (1 ponto)"])
            q18_sel = st.radio("18. 2. Presença de patologia de base classificada em alto risco nutricional ou proposta de cirurgia de grande porte?", ["Não (0 ponto)", "Sim (2 pontos)"])
            q19_sel = st.radio("19. 3. Ingestão e perdas: Apresenta diarreia severa, vômitos reincidentes ou ingestão oral deficitária nos últimos dias?", ["Não (0 ponto)", "Sim (1 ponto)"])
            q20_sel = st.radio("20. 4. Evolução ponderal recente: Responsáveis referem perda de peso involuntária ou incapacidade de ganho estatural-ponderal?", ["Não (0 ponto)", "Sim (1 ponto)"])
            
            btn = st.form_submit_button("Computar Escore Pediátrico e Matriz de Ação ➔")
            if btn:
                escore = ("Sim" in q17_sel) + ("2 pontos" in q18_sel)*2 + ("Sim" in q19_sel) + ("Sim" in q20_sel)
                
                # Matriz Exclusiva Escore x Risco x Intervenção solicitada
                if escore >= 4:
                    risco = "Alto"
                    intervencao = (
                        "1. Consultar médico ou nutricionista para diagnóstico nutricional completo.\n"
                        "2. Orientação nutricional individualizada e seguimento restrito.\n"
                        "3. Iniciar suplementação oral imediata até conclusão do diagnóstico nutricional definitivo."
                    )
                elif 1 <= escore <= 3:
                    risco = "Médio"
                    intervencao = (
                        "1. Consultar médico assistente para diagnóstico completo.\n"
                        "2. Considerar início de intervenção nutricional precoce.\n"
                        "3. Checar peso corporal à beira-leito 2x/semana.\n"
                        "4. Reavaliar de forma compulsória o risco nutricional após 1 semana."
                    )
                else:
                    risco = "Baixo"
                    intervencao = (
                        "1. Checar peso corporal regulamente.\n"
                        "2. Reavaliar o risco nutricional global em 1 semana."
                    )
                    
                st.session_state.dados_triagem_base.update({"Escore Triagem": escore, "Risco": risco, "Intervencao_Obrigatoria": intervencao})
                st.session_state.passo_atual = "conduta_final"
                st.rerun()

    # ETAPA 3B: TRIAGEM ADULTO (NRS 2002)
    elif st.session_state.passo_atual == "triagem_19-59":
        st.subheader("🫁 Triagem de Risco no Adulto: Ferramenta NRS 2002")
        
        st.info("""
        🔬 **Descritivo Explicativo HMP / USP:** O Nutritional Risk Screening (NRS 2002) correlaciona o grau de desnutrição atual (baseado em IMC, ingestão e perda ponderal) com o estresse metabólico imposto pela gravidade da doença. Escore >= 3 define risco e necessidade de plano de cuidado imediato.
        """)
        
        with st.form("form_nrs"):
            nrs_q1 = st.checkbox("1) Índice de Massa Corporal (IMC) encontra-se abaixo de 20,5 kg/m²?")
            nrs_q2 = st.checkbox("2) O paciente manifestou perda ponderal involuntária ao longo dos últimos 3 meses?")
            nrs_q3 = st.checkbox("3) Houve redução expressiva da ingestão dietética alimentar na última semana?")
            nrs_q4 = st.checkbox("4) O paciente apresenta-se em estado clínico grave (ex: ventilação mecânica, sepse, trauma)?")
            
            btn = st.form_submit_button("Computar Escore Adulto ➔")
            if btn:
                escore = 3 if (nrs_q1 or nrs_q2 or nrs_q3 or nrs_q4) else 0
                risco = "Alto" if escore >= 3 else "Baixo"
                intervencao = "Prescrever terapia nutricional ativa e triagem continuada pela equipe." if risco == "Alto" else "Acompanhamento clínico regular e nova triagem em 7 dias."
                
                st.session_state.dados_triagem_base.update({"Escore Triagem": escore, "Risco": risco, "Intervencao_Obrigatoria": intervencao})
                st.session_state.passo_atual = "conduta_final"
                st.rerun()

    # ETAPA 3C: TRIAGEM GERIÁTRICA (MNA® COMPLETA)
    elif st.session_state.passo_atual == "triagem_>= 60":
        st.subheader("👴 Avaliação Geriátrica: Mini Avaliação Nutricional (MNA®)")
        
        st.info("""
        🔬 **Descritivo Explicativo HMP / USP:** A triagem MNA® é o padrão-ouro validado internacionalmente para idosos hospitalizados. Avalia perdas funcionais, cognitivas, restrições alimentares e biometria, visando intervenções precoces contra a desnutrição na senescência.
        """)
        
        with st.form("form_mna_completo"):
            mna_a = st.selectbox("A. Houve redução da ingesta alimentar nos últimos 3 meses devido a perda de apetite, problemas digestivos ou dificuldades de mastigação/deglutição?", 
                                 ["2 : Sem redução alimentar", "1 : Redução alimentar moderada", "0 : Redução alimentar severa"])
            mna_b = st.selectbox("B. Perda de peso involuntária ocorrida no período dos últimos 3 meses?", 
                                 ["3 : Sem perda ponderal", "2 : Perda entre 1 e 3 kg", "1 : Não sabe informar", "0 : Perda de peso maior que 3 kg"])
            mna_c = st.selectbox("C. Mobilidade e locomoção do paciente?", 
                                 ["2 : Deambula normalmente / sai de casa", "1 : Restrito ao leito/cadeira, mas consegue levantar", "0 : Restrito estritamente à cama ou cadeira de rodas"])
            mna_d = st.selectbox("D. Passou por situação de estresse psicológico agudo ou acometimento por doença aguda nos últimos 3 meses?", 
                                 ["2 : Não", "0 : Sim"])
            mna_e = st.selectbox("E. Diagnóstico ou sinais de problemas neuropsicológicos?", 
                                 ["2 : Sem alterações cognitivas", "1 : Demência moderada ou confusão mental leve", "0 : Demência grave ou quadro depressivo severo"])
            mna_f = st.selectbox("F. Janela do Índice de Massa Corporal (IMC) estabelecida?", 
                                 ["3 : IMC igual ou superior a 23 kg/m²", "2 : IMC entre 21 e 23 kg/m²", "1 : IMC entre 19 e 21 kg/m²", "0 : IMC menor que 19 kg/m²"])
            
            btn = st.form_submit_button("Computar Escore Geriátrico MNA® ➔")
            if btn:
                p_a = int(mna_a.split(" : ")[0])
                p_b = int(mna_b.split(" : ")[0])
                p_c = int(mna_c.split(" : ")[0])
                p_d = int(mna_d.split(" : ")[0])
                p_e = int(mna_e.split(" : ")[0])
                p_f = int(mna_f.split(" : ")[0])
                
                escore_total = p_a + p_b + p_c + p_d + p_e + p_f
                
                if escore_total >= 12:
                    risco = "Estado Nutricional Normal"
                    intervencao = "Manter rotina alimentar hospitalar padrão e monitorar aceitação da dieta."
                elif 8 <= escore_total <= 11:
                    risco = "Risco de Desnutrição"
                    intervencao = "Iniciar enriquecimento calórico-proteico na dieta e acompanhamento farmacológico."
                else:
                    risco = "Desnutrido"
                    intervencao = "Instalar terapia nutricional especializada (suplementos/enteral) e metas de reabilitação com a EMTN."
                    
                st.session_state.dados_triagem_base.update({"Escore Triagem": escore_total, "Risco": risco, "Intervencao_Obrigatoria": intervencao})
                st.session_state.passo_atual = "conduta_final"
                st.rerun()

    # ETAPA 4: DEFINIÇÃO DE CONDUTA BASEADA EM EVIDÊNCIAS
    elif st.session_state.passo_atual == "conduta_final":
        st.subheader("🏁 Definição da Conduta e Terapia Nutricional Proposta")
        db = st.session_state.dados_triagem_base
        parecer_ia_gerado = analisar_dados_com_ia(db)
        
        st.markdown(f'<div class="ai-box"><h4>🤖 Apoio Clínico EMTN - Diretrizes Baseadas em Evidências</h4><p style="white-space: pre-line;">{parecer_ia_gerado}</p></div>', unsafe_allow_html=True)
        
        with st.form("form_final"):
            st.markdown(f"### Identificação do Paciente no Laudo: **{db['Nome']}** ({db['Idade Anos']} anos e {db['Idade Meses']} meses)")
            st.warning(f"**Resultado Triagem:** Classificação de Risco: **{db['Risco']}** | Pontuação: **{db['Escore Triagem']}**")
            
            # Caixa informativa das diretrizes de intervenção obrigatória (Matriz Strong ou Protocolo HMP)
            st.info(f"📋 **Intervenção de Conduta Obrigatória Sugerida:**\n\n{db['Intervencao_Obrigatoria']}")
            
            f_nivel = st.selectbox("38. Classificação Definitiva do Nível de Assistência *", ["Primário", "Secundário A", "Secundário B", "Terciário"])
            f_conduta = st.text_area("83. Conduta Terapêutica Adotada da Equipe (Prescrição Clínica Completa) *", value=db['Intervencao_Obrigatoria'])
            f_via_prop = st.selectbox("84. Via de Alimentação Proposta Conforme Discussão *", ["Oral", "Sonda Nasoenteral", "Gastrostomia", "Jejunostomia", "Parenteral periférica", "Parenteral central", "Jejum"])
            f_dieta_prescrita = st.text_input("Dieta / Fórmula Específica Prescrita Hospitalar *")
            
            btn_salvar_banco = st.form_submit_button("Validar Parâmetros e Gerar Documento de Emissão ➔")
            if btn_salvar_banco:
                st.session_state.dados_triagem_base.update({
                    "Nível Assistência": f_nivel, "Via Proposta": f_via_prop, 
                    "Dieta Prescrita": f_dieta_prescrita, "Conduta": f_conduta, "Parecer_IA": parecer_ia_gerado
                })
                st.session_state.passo_atual = "laudo_impressao"
                st.rerun()

    # ETAPA 5: EMISSÃO E ARQUIVAMENTO HOSPITALAR
    elif st.session_state.passo_atual == "laudo_impressao":
        db = st.session_state.dados_triagem_base
        st.success("🎉 Processo assistencial concluído com sucesso!")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🖨️ Chamar Caixa de Impressão SOG / PDF"):
                st.components.v1.html("<script>window.print();</script>", height=0)
        with col_btn2:
            if st.button("💾 Chancelar Documento e Arquivar no Banco Definitivo"):
                novo_registro = {
                    "Avaliador": db["Avaliador"], "Data Admissão": db["Data Admissão"], "Nome": db["Nome"], 
                    "Sexo": db["Sexo"], "Setor": db["Setor"], "Leito": db["Leito"], "Data Triagem": db["Data Triagem"], 
                    "Via Alimentação": db["Via Alimentação"], "Momento": db["Momento"], "Diagnóstico": db.get("Diagnóstico", "N/A"), 
                    "Comorbidades": db.get("Comorbidades", "N/A"), "Peso Habitual": db.get("Peso Habitual", 0.0), 
                    "Altura Referida": db.get("Altura Referida", 0.0), "Data Nascimento": db.get("Data Nascimento", "N/A"), 
                    "Idade Anos": db.get("Idade Anos", 0), "Idade Meses": db.get("Idade Meses", 0), "Faixa Etária": db.get("Faixa Etária", "N/A"), 
                    "Escore Triagem": db["Escore Triagem"], "Risco": db["Risco"], "Intervencao_Obrigatoria": db["Intervencao_Obrigatoria"],
                    "Nível Assistência": db["Nível Assistência"], "Via Proposta": db["Via Proposta"], "Dieta Prescrita": db["Dieta Prescrita"], 
                    "Adequacao_Calorica": 100.0, "Parecer_IA": db["Parecer_IA"], "Notas_Plantao": "", "Ultima_Reavaliacao": "Não Reavaliado"
                }
                st.session_state.banco_pacientes = pd.concat([st.session_state.banco_pacientes, pd.DataFrame([novo_registro])], ignore_index=True)
                st.session_state.passo_atual = "identificacao"
                del st.session_state.dados_triagem_base
                st.rerun()

        st.markdown(f"""
            <div class="secao-impressao" style="padding: 30px; border: 1px solid #CCC; background-color: white;">
                <h2 style="text-align: center;">HOSPITAL MUNICIPAL DE PAULÍNIA - EMISSÃO LAUDO EMTN</h2>
                <hr>
                <p><b>Paciente:</b> {db['Nome']} | <b>Idade de Identificação:</b> {db['Idade Anos']} anos e {db['Idade Meses']} meses</p>
                <p><b>Leito de Destino:</b> {db['Leito']} - {db['Setor']} | <b>Data Tematização:</b> {db['Data Triagem']}</p>
                <p><b>Classificação Risco Nutricional:</b> {db['Risco']} (Escore: {db['Escore Triagem']}) | <b>Nível de Cuidado:</b> {db['Nível Assistência']}</p>
                <p><b>Via de Terapia Alimentar Proposta:</b> {db['Via Proposta']} | <b>Dieta / Fórmula Complexa:</b> {db['Dieta Prescrita']}</p>
                <p><b>Diretriz de Conduta Clinica Incorporada:</b><br>{db['Conduta'].replace('\n', '<br>')}</p>
                <p><b>Parecer Técnico EMTN:</b><br>{db['Parecer_IA'].replace('\n', '<br>')}</p>
            </div>
        """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------------------
# MÓDULO 2: PRESCRIÇÃO E EVOLUÇÃO CLÍNICA DIÁRIA
# --------------------------------------------------------------------------------------------------
elif menu == "Módulo 2: Prescrição e Evolução":
    st.title("📋 Módulo 2: Prescrição e Evolução Clínica Diária (Beira-Leito)")
    df = st.session_state.banco_pacientes
    if df.empty:
        st.info("Nenhum paciente cadastrado em leito ativo.")
    else:
        paciente_selecionado = st.selectbox("Selecione o Paciente para Check-in de Visita:", df["Nome"].unique())
        idx = df[df["Nome"] == paciente_selecionado].index[0]
        
        st.markdown(f"### Identificação do Paciente Selecionado: **{df.at[idx, 'Nome']}** ({df.at[idx, 'Idade Anos']} anos e {df.at[idx, 'Idade Meses']} meses)")
        
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
            st.success("Evolução registrada e arquivada com sucesso.")

# --------------------------------------------------------------------------------------------------
# MÓDULO 3: AVALIAÇÃO EMTN (VIGILÂNCIA SUPERVISIONADA)
# --------------------------------------------------------------------------------------------------
elif menu == "Módulo 3: Avaliação EMTN":
    st.title("🎯 Módulo 3: Painel de Vigilância e Avaliação Supervisionada da EMTN")
    
    df = st.session_state.banco_pacientes
    if df.empty:
        st.info("Nenhum paciente admitido no sistema até o momento.")
    else:
        criterio_nivel = df["Nível Assistência"].isin(["Secundário B", "Terciário"])
        criterio_via_admissao = df["Via Alimentação"].isin(["Sonda Nasoenteral", "Parenteral periférica", "Parenteral central"])
        criterio_via_proposta = df["Via Proposta"].isin(["Sonda Nasoenteral", "Parenteral periférica", "Parenteral central"])
        
        df_supervisionados = df[criterio_nivel | criterio_via_admissao | criterio_via_proposta]
        
        if df_supervisionados.empty:
            st.success("✅ Excelente! Nenhum paciente ativo em leito hospitalar preenche critérios de risco crítico/supervisionado hoje.")
        else:
            st.warning(f"⚠️ Atenção EMTN: Existem {len(df_supervisionados)} pacientes elegíveis para acompanhamento prioritário e reavaliação.")
            
            st.dataframe(
                df_supervisionados[["Leito", "Nome", "Idade Anos", "Setor", "Via Proposta", "Nível Assistência", "Risco", "Ultima_Reavaliacao"]],
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
# MÓDULO 4: PASSAGEM DE PLANTÃO COM EDIÇÃO RÁPIDA
# --------------------------------------------------------------------------------------------------
elif menu == "Módulo 4: Passagem de Plantão":
    st.title("📋 Módulo 4: Passagem de Plantão e Round da EMTN (Edição Rápida)")
    
    df = st.session_state.banco_pacientes
    if df.empty:
        st.info("Nenhum paciente ativo no hospital.")
    else:
        colunas_exibicao = ["Leito", "Nome", "Idade Anos", "Setor", "Via Proposta", "Dieta Prescrita", "Adequacao_Calorica", "Risco", "Notas_Plantao"]
        
        df_editado = st.data_editor(
            df[colunas_exibicao],
            column_config={
                "Nome": st.column_config.TextColumn("Paciente", disabled=True),
                "Idade Anos": st.column_config.NumberColumn("Idade", disabled=True, format="%d anos"),
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
# MÓDULO 5: DASHBOARD DE INDICADORES
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
