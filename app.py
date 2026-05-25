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

# BANCO DE DADOS EM MEMÓRIA (INICIALIZAÇÃO DO ESTADO DA SESSÃO)
if 'banco_pacientes' not in st.session_state:
    st.session_state.banco_pacientes = pd.DataFrame(columns=[
        "Avaliador", "Data Admissão", "Nome", "Sexo", "Setor", "Leito", "Data Triagem", 
        "Via Alimentação", "Momento", "Diagnóstico", "Comorbidades", "Peso Habitual", 
        "Altura Referida", "IMC Calculado", "Classe IMC", "Data Nascimento", "Idade Anos", "Idade Meses", "Faixa Etária", 
        "Escore Triagem", "Risco", "Intervencao_Obrigatoria", "Nível Assistência", "Via Proposta", 
        "Dieta Prescrita", "Adequacao_Calorica", "Parecer_IA", "Notas_Plantao", "Ultima_Reavaliacao"
    ])

if 'banco_historico_alta' not in st.session_state:
    st.session_state.banco_historico_alta = pd.DataFrame(columns=st.session_state.banco_pacientes.columns.tolist() + ["Data_Alta"])

# DICIONÁRIO DE USUÁRIOS
CONTA_USUARIOS = {
    "vinicius.mariano": {"senha": "casa0904", "nome_completo": "Dr. Vinícius Mariano"},
    "priscila.nutri": {"senha": "nutri1234", "nome_completo": "Nutri. Priscila"},
    "resilda.enfermeira": {"senha": "enf1234", "nome_completo": "Enf. Resilda"},
    "julia.lopes": {"senha": "julia1234", "nome_completo": "Júlia Lopes"},
    "amanda.snd": {"senha": "snd1234", "nome_completo": "Amanda SND"},
    "carol.geriatria": {"senha": "geriatria1234", "nome_completo": "Carol Geriatria"},
    "matheus.soberana": {"senha": "matheus1234", "nome_completo": "Matheus Soberana"},
    "rafael.soberana": {"senha": "rafael1234", "nome_completo": "Rafael Soberana"},
    "caren.soberana": {"senha": "caren1234", "nome_completo": "Caren Soberana"},
    "vanessa.soberana": {"senha": "vanessa1234", "nome_completo": "Vanessa Soberana"}
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

# FUNÇÃO AUXILIAR PARA CLASSIFICAR IMC ADULTO
def classificar_imc_adulto(imc):
    if imc < 18.5: return "Baixo Peso"
    elif 18.5 <= imc < 25.0: return "Eutrofia"
    elif 25.0 <= imc < 30.0: return "Sobrepeso"
    else: return "Obesidade"

# FUNÇÃO DE INTELIGÊNCIA ARTIFICIAL CLÍNICA REVISADA
def analisar_dados_com_ia(dados):
    idade = dados.get("Idade Anos", 30)
    comorbidades = dados.get("Comorbidades", "")
    escore = dados.get("Escore Triagem", 0)
    risco = dados.get("Risco", "Baixo")
    via_atual = dados.get("Via Alimentação", "Oral")
    faixa_etaria = dados.get("Faixa Etária", "19-59")
    
    insights = []
    
    if "Etilismo" in comorbidades or "Acamado(a)" in comorbidades or (faixa_etaria == "19-59" and escore >= 3) or (faixa_etaria == ">= 60" and escore < 12):
        insights.append("🛑 **Risco Clínico Intermediado (Síndrome de Realimentação):** Paciente com critérios de vulnerabilidade metabólica aguda. Recomenda-se acompanhamento rigoroso pela EMTN de eletrólitos extracelulares (Fósforo, Magnésio, Potássio) nas primeiras 72h e progressão escalonada obrigatória do aporte calórico total diário.")
    
    if (faixa_etaria == ">= 60" or idade >= 60) and (risco == "Risco de Desnutrição" or risco == "Desnutrido" or "risco" in risco.lower()):
        insights.append("👴 **Fragilidade Geriátrica Avançada:** Paciente idoso identificado em risco ou déficit nutricional evidente. Alerta para alta propensão à perda de massa muscular magra (sarcopenia) e queda da imunidade celular. Priorizar via oral qualificada ou terapia enteral precoce.")
        
    if "Diabetes mellitus" in comorbidades:
        insights.append("📊 **Restrição Metabólica:** Paciente com distúrbio do metabolismo glicídico. Necessita de monitorização capilar frequente e formulações com menor índice de carboidratos simples.")

    if via_atual == "Jejum" and (escore >= 3 or "risco" in risco.lower()):
        insights.append("🚨 **Alerta de Segurança do Paciente:** Paciente classificado com risco nutricional estabelecido e mantido em Jejum. Risco severo de depleção de glicogênio hepático e catabolismo muscular acelerado se ultrapassar 24 horas sem terapia nutricional activa.")

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
            f_avaliador = st.text_input("Avaliador *", value=st.session_state.nome_avaliador, disabled=True)
            f_data_adm = st.date_input("Data de Admissão Hospitalar *", format="DD/MM/YYYY")
            f_nome = st.text_input("Nome Completo do Paciente *")
            f_sexo = st.radio("Gênero Biológico *", ["Masculino", "Feminino"])
            f_setor = st.selectbox("Setor de Internação *", ["Pronto Socorro Adulto", "Pronto Socorro Infantil", "Clinica Médica", "Clínica Cirúrgica", "Ginecologia e Obstetrícia", "Pediatria", "UTI"])
            f_leito = st.text_input("Identificação do Leito *")
            f_data_triagem = st.date_input("Data Real da Triagem EMTN", format="DD/MM/YYYY")
            f_via = st.selectbox("Via de Alimentação de Entrada *", ["Oral", "Sonda Nasoenteral", "Gastrostomia", "Jejunostomia", "Parenteral periférica", "Parenteral central", "Jejum"])
            
            btn_proximo_1 = st.form_submit_button("Avançar para Dados Clínicos e Idade ➔")
            
            if btn_proximo_1:
                if not f_nome or not f_leito:
                    st.error("Por favor, preencha os campos obrigatórios (*): Nome e Leito.")
                else:
                    st.session_state.dados_triagem_base = {
                        "Avaliador": f_avaliador, "Data Admissão": f_data_adm.strftime("%Y-%m-%d"), 
                        "Nome": f_nome, "Sexo": f_sexo, "Setor": f_setor, "Leito": f_leito, 
                        "Data Triagem": f_data_triagem.strftime("%Y-%m-%d"), "Via Alimentação": f_via,
                        "Notas_Plantao": "", "Ultima_Reavaliacao": "Não Reavaliado"
                    }
                    st.session_state.passo_atual = "anamnese"
                    st.rerun()

    # ETAPA 2: ANAMNESE E VALIDAÇÃO DA IDADE + IMC REATIVOS
    elif st.session_state.passo_atual == "anamnese":
        st.subheader("Anamnese Clínica e Perfil Antropométrico")
        
        f_data_nasc = st.date_input("Data de Nascimento do Paciente *", value=date(1980, 1, 1), min_value=date(1900, 1, 1), max_value=date.today(), format="DD/MM/YYYY")
        anos, meses = calcular_idade_detalhada(f_data_nasc)
        
        col_ant1, col_ant2 = st.columns(2)
        with col_ant1:
            f_peso_hab = st.number_input("Peso Habitual Referido (kg) *", min_value=0.0, max_value=300.0, value=70.0, step=0.1, format="%.2f")
        with col_ant2:
            f_altura = st.number_input("Altura Estimada/Referida (m) *", min_value=0.10, max_value=2.50, value=1.70, step=0.01, format="%.2f")
        
        st.success(f"📌 **Idade Calculada para Identificação:** {anos} anos e {meses} meses.")
        
        imc_real = 0.0
        classe_imc = "N/A"
        if f_altura > 0:
            imc_real = f_peso_hab / (f_altura ** 2)
            if anos >= 19:
                classe_imc = classificar_imc_adulto(imc_real)
                st.info(f"⚖️ **Índice de Massa Corporal (IMC) Calculado:** {imc_real:.2f} kg/m² ({classe_imc})")
            else:
                classe_imc = "Percentil Pediátrico"
                st.info(f"⚖️ **Índice de Massa Corporal (IMC) Calculado:** {imc_real:.2f} kg/m² (Avaliar por Curva de Crescimento)")

        with st.form("form_passo_2"):
            f_diag = st.text_area("Diagnóstico Médico de Admissão *")
            f_comorbidades = st.multiselect("Comorbidades Crônicas Associadas *", ["NÃO POSSUI COMORBIDADE", "Acamado(a)", "Diabetes mellitus", "Drogadição (SPA)", "Etilismo", "Hipertensão arterial sistêmica", "Infarto", "Insuficiência cardíaca", "Obesidade", "Tabagismo", "Doença autoimune", "Doença hematológica", "Doença hepática ou gastrointestinal", "Doença nefrológica", "Doença neoplásica", "Doença neurológica", "Doença psiquiátrica", "Doença respiratória", "Doença sexualmente transmissível", "Outra doença cardiovascular", "Outra doença endócrina", "Doença gestacional - Hipertensão arterial sistêmica", "Doença gestacional - Diabetes mellitus", "Doença gestacional - Outra doença endócrina", "Doença gestacional - Outra(s) doença(s)", "Outra(s) doença(s)"])
            
            btn_proximo_2 = st.form_submit_button("Vincular e Chamar Questionário de Triagem Alvo ➔")
            
            if btn_proximo_2:
                faixa_calculada = "<=18" if anos < 19 else ("19-59" if 19 <= anos <= 59 else ">= 60")
                
                st.session_state.dados_triagem_base.update({
                    "Diagnóstico": f_diag, "Comorbidades": ", ".join(f_comorbidades),
                    "Peso Habitual": f_peso_hab, "Altura Referida": f_altura,
                    "IMC Calculado": round(imc_real, 2), "Classe IMC": classe_imc,
                    "Data Nascimento": f_data_nasc.strftime("%Y-%m-%d"),
                    "Idade Anos": anos, "Idade Meses": meses, "Faixa Etária": faixa_calculada
                })
                st.session_state.passo_atual = f"triagem_{faixa_calculada}"
                st.rerun()

    # ETAPA 3A: TRIAGEM PEDIÁTRICA (STRONG KIDS)
    elif st.session_state.passo_atual == "triagem_<=18":
        st.subheader("🧬 Rastreamento de Risco Pediátrico: Ferramenta STRONG KIDS")
        with st.form("form_strong"):
            q17_sel = st.radio("Avaliação nutricional clinical subjetiva: A criança aparenta perda de tecido adiposo ou massa muscular subcutânea?", ["Não (0 ponto)", "Sim (1 ponto)"])
            q18_sel = st.radio("Presença de patologia de base classificada em alto risco nutricional ou proposta de cirurgia de grande porte?", ["Não (0 ponto)", "Sim (2 pontos)"])
            q19_sel = st.radio("Ingestão e perdas: Apresenta diarreia severa, vômitos reincidentes ou ingestão oral deficitária nos últimos dias?", ["Não (0 ponto)", "Sim (1 ponto)"])
            q20_sel = st.radio("Evolução ponderal recente: Responsáveis referem perda de peso involuntária ou incapacidade de ganho estatural-ponderal?", ["Não (0 ponto)", "Sim (1 ponto)"])
            
            btn = st.form_submit_button("Computar Escore Pediátrico e Matriz de Ação ➔")
            if btn:
                escore = ("Sim" in q17_sel) + ("2 pontos" in q18_sel)*2 + ("Sim" in q19_sel) + ("Sim" in q20_sel)
                if escore >= 4:
                    risco = "Alto Risco Nutricional"
                    intervencao = "1. Consultar médico ou nutricionista para diagnóstico nutricional completo\n2. Orientação nutricional individualizada e seguimento\n3. Iniciar suplementação oral até conclusão do diagnóstico nutricional"
                elif 1 <= escore <= 3:
                    risco = "Médio Risco Nutricional"
                    intervencao = "1. Consultar médico para diagnóstico completo\n2. Considerar intervenção nutricional\n3. Checar peso 2x/semana\n4. Reavaliar o risco nutricional após 1 semana"
                else:
                    risco = "Baixo Risco Nutricional"
                    intervencao = "1. Checar peso regularmente\n2. Reavaliar risco em 1 semana"
                    
                st.session_state.dados_triagem_base.update({"Escore Triagem": escore, "Risco": risco, "Intervencao_Obrigatoria": intervencao})
                st.session_state.passo_atual = "conduta_final"
                st.rerun()

    # ETAPA 3B: TRIAGEM ADULTO (NRS 2002)
    elif st.session_state.passo_atual == "triagem_19-59":
        st.subheader("🫁 Triagem de Risco no Adulto: Ferramenta NRS 2002")
        with st.form("form_nrs_completo"):
            f_deterioracao = st.radio("Selecione o grau de deterioração do estado nutricional *",
                ["0 : Ausente", "1 : Leve", "2 : Moderado", "3 : Grave"])
            f_gravidade = st.radio("Selecione o grau de gravidade da doença *",
                ["0 : Ausente", "1 : Leve", "2 : Moderado", "3 : Grave"])
            
            btn_calcular_nrs = st.form_submit_button("Computar Escore Adulto NRS 2002 ➔")
            if btn_calcular_nrs:
                p_det = int(f_deterioracao.split(" : ")[0])
                p_grav = int(f_gravidade.split(" : ")[0])
                escore_final = p_det + p_grav + (1 if st.session_state.dados_triagem_base.get("Idade Anos", 0) >= 70 else 0)
                risco_status = f"Escore total {escore_final} pontos"
                st.session_state.dados_triagem_base.update({"Escore Triagem": escore_final, "Risco": risco_status, "Intervencao_Obrigatoria": "Ajustar conforme escore."})
                st.session_state.passo_atual = "conduta_final"
                st.rerun()

    # ETAPA 3C: TRIAGEM GERIÁTRICA (MNA®)
    elif st.session_state.passo_atual == "triagem_>= 60":
        st.subheader("👴 Avaliação Geriátrica: Mini Avaliação Nutricional (MNA®)")
        with st.form("form_mna_completo"):
            mna_a = st.selectbox("A. Redução da ingesta?", ["2 : Sem redução", "1 : Redução moderada", "0 : Redução severa"])
            mna_b = st.selectbox("B. Perda de peso?", ["3 : Sem perda", "2 : 1-3kg", "1 : Não sabe", "0 : >3kg"])
            mna_c = st.selectbox("C. Mobilidade?", ["2 : Deambula", "1 : Restrito leito", "0 : Cadeira"])
            mna_d = st.selectbox("D. Estresse agudo?", ["2 : Não", "0 : Sim"])
            mna_e = st.selectbox("E. Neuropsicológico?", ["2 : Sem alteração", "1 : Leve", "0 : Grave"])
            mna_f = st.selectbox("F. IMC?", ["3 : >= 23", "2 : 21-23", "1 : 19-21", "0 : < 19"])
            btn = st.form_submit_button("Computar MNA® ➔")
            if btn:
                escore_total = int(mna_a[0]) + int(mna_b[0]) + int(mna_c[0]) + int(mna_d[0]) + int(mna_e[0]) + int(mna_f[0])
                risco = "Normal" if escore_total >= 12 else ("Risco" if 8 <= escore_total <= 11 else "Desnutrido")
                st.session_state.dados_triagem_base.update({"Escore Triagem": escore_total, "Risco": risco, "Intervencao_Obrigatoria": "Monitorar conforme score."})
                st.session_state.passo_atual = "conduta_final"
                st.rerun()

    # ETAPA 4: CONDUTA FINAL
    elif st.session_state.passo_atual == "conduta_final":
        st.subheader("🏁 Definição da Conduta")
        db = st.session_state.dados_triagem_base
        parecer_ia = analisar_dados_com_ia(db)
        with st.form("form_final"):
            f_nivel = st.selectbox("Nível de Assistência *", ["Primário", "Secundário A", "Secundário B", "Terciário"])
            f_conduta = st.text_area("Conduta Terapêutica Adotada *")
            f_via_prop = st.selectbox("Via de Alimentação Proposta *", ["Oral", "Sonda Nasoenteral", "Gastrostomia", "Jejunostomia", "Parenteral periférica", "Parenteral central", "Jejum"])
            f_dieta = st.text_input("Dieta / Fórmula Prescrita *")
            
            btn_salvar_banco = st.form_submit_button("Finalizar Admissão e Arquivar")
            if btn_salvar_banco:
                novo_registro = db.copy()
                novo_registro.update({"Nível Assistência": f_nivel, "Via Proposta": f_via_prop, "Dieta Prescrita": f_dieta, "Conduta": f_conduta, "Parecer_IA": parecer_ia})
                st.session_state.banco_pacientes = pd.concat([st.session_state.banco_pacientes, pd.DataFrame([novo_registro])], ignore_index=True)
                st.success("Admissão finalizada e paciente integrado!")
                del st.session_state.dados_triagem_base
                st.session_state.passo_atual = "identificacao"
                st.rerun()

# --------------------------------------------------------------------------------------------------
# MÓDULO 2: PRESCRIÇÃO E EVOLUÇÃO
# --------------------------------------------------------------------------------------------------
elif menu == "Módulo 2: Prescrição e Evolução":
    st.title("📋 Módulo 2: Prescrição e Evolução")
    if st.session_state.banco_pacientes.empty:
        st.info("Nenhum paciente cadastrado. Realize a admissão no Módulo 1.")
    else:
        setor_sel = st.selectbox("Filtrar por Setor:", st.session_state.banco_pacientes['Setor'].unique())
        pacientes_setor = st.session_state.banco_pacientes[st.session_state.banco_pacientes['Setor'] == setor_sel]
        nome_sel = st.selectbox("Selecione o paciente:", pacientes_setor['Nome'].unique())
        
        if st.button("Carregar Prontuário"):
            st.session_state.p_ativo = st.session_state.banco_pacientes[st.session_state.banco_pacientes['Nome'] == nome_sel].iloc[0]
            
        if 'p_ativo' in st.session_state:
            p = st.session_state.p_ativo
            st.info(f"Paciente: {p['Nome']} | Leito: {p['Leito']}")
            with st.form("form_evolucao"):
                evolucao = st.text_area("Evolução Nutricional:")
                btn_evolucao = st.form_submit_button("Salvar Evolução")
                if btn_evolucao:
                    st.success("Evolução salva!")
            
            if st.button("🚨 Registrar Alta Hospitalar"):
                p_alta = p.copy()
                p_alta['Data_Alta'] = date.today()
                st.session_state.banco_historico_alta = pd.concat([st.session_state.banco_historico_alta, pd.DataFrame([p_alta])], ignore_index=True)
                st.session_state.banco_pacientes = st.session_state.banco_pacientes[st.session_state.banco_pacientes['Nome'] != p['Nome']]
                del st.session_state.p_ativo
                st.success("Alta registrada com sucesso!")
                st.rerun()

# --------------------------------------------------------------------------------------------------
# MÓDULO 3: AVALIAÇÃO EMTN
# --------------------------------------------------------------------------------------------------
elif menu == "Módulo 3: Avaliação EMTN":
    st.title("🎯 Módulo 3: Avaliação EMTN e Auditoria")
    st.write("Funcionalidade de monitoramento avançado e auditoria de leitos.")
    if not st.session_state.banco_pacientes.empty:
        st.dataframe(st.session_state.banco_pacientes)
    else:
        st.warning("Sem dados para exibir.")

# --------------------------------------------------------------------------------------------------
# MÓDULO 4: PASSAGEM DE PLANTÃO
# --------------------------------------------------------------------------------------------------
elif menu == "Módulo 4: Passagem de Plantão":
    st.title("📋 Módulo 4: Passagem de Plantão")
    st.write("Interface para resumo de transferências e intercorrências do turno.")
    if not st.session_state.banco_pacientes.empty:
        df_editado = st.data_editor(
            st.session_state.banco_pacientes[["Nome", "Leito", "Dieta Prescrita", "Notas_Plantao"]],
            column_config={
                "Notas_Plantao": st.column_config.TextColumn("Conduta / Notas do Round ✏️", width="medium")
            },
            hide_index=True, use_container_width=True
        )
        if st.button("💾 Consolidar Alterações do Round no Banco Hospitalar"):
            for col in ["Leito", "Dieta Prescrita", "Notas_Plantao"]:
                st.session_state.banco_pacientes[col] = df_editado[col]
            st.success("✅ Todas as alterações feitas na tabela foram salvas!")
            st.rerun()

# --------------------------------------------------------------------------------------------------
# MÓDULO 5: INDICADORES
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
