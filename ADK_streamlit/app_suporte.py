"""
Assistente de Suporte Técnico Multi-Agente
Variação própria do projeto de viagens (Atividade 11 - FastCamp)
Demonstra aplicação do padrão Google ADK em outro domínio.
"""

import os
import asyncio
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Configure GOOGLE_API_KEY no arquivo .env")
    st.stop()

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

MODEL = "gemini-3.6-flash"

# ======================#
# AGENTES ESPECIALIZADOS

bug_agent = Agent(
    name="bug_agent",
    model=MODEL,
    mode="single_turn",
    description="Especialista em diagnosticar bugs e erros técnicos.",
    instruction=(
        "Você é um engenheiro de software especialista em debugging. "
        "Com base na descrição do problema, sugira causas prováveis, "
        "passos de diagnóstico e uma solução provável. "
        "Responda em português, de forma técnica mas acessível."
    ),
)

feature_agent = Agent(
    name="feature_agent",
    model=MODEL,
    mode="single_turn",
    description="Especialista em avaliar solicitações de novas funcionalidades.",
    instruction=(
        "Você é um product manager. Com base na solicitação do cliente, "
        "avalie a viabilidade, sugira alternativas e estime complexidade "
        "(baixa/média/alta). Responda em português, de forma concisa."
    ),
)

billing_agent = Agent(
    name="billing_agent",
    model=MODEL,
    mode="single_turn",
    description="Especialista em dúvidas de cobrança e planos.",
    instruction=(
        "Você é um especialista em billing. Com base na dúvida do cliente, "
        "explique políticas, prazos e opções de plano. "
        "Responda em português, de forma clara e objetiva."
    ),
)

# ===================#
# AGENTE ORQUESTRADOR

support_orchestrator = Agent(
    name="support_orchestrator",
    model=MODEL,
    description="Coordenador de suporte técnico.",
    instruction=(
        "Você é um coordenador de suporte. Analise a solicitação do cliente "
        "e delegue para os especialistas relevantes:\n"
        "- bug_agent para erros, bugs e problemas técnicos\n"
        "- feature_agent para solicitações de novas funcionalidades\n"
        "- billing_agent para cobrança, planos e pagamentos\n\n"
        "Se a solicitação envolver múltiplas áreas, delegue para TODOS os "
        "especialistas relevantes antes de sintetizar a resposta final.\n"
        "Ao final, produza uma resposta unificada e priorizada em português."
    ),
    sub_agents=[bug_agent, feature_agent, billing_agent],
)

# =========#
# EXECUÇÃO

async def atender_cliente(mensagem_cliente):
    session_service = InMemorySessionService()
    runner = Runner(
        agent=support_orchestrator,
        app_name="tech_support",
        session_service=session_service,
    )

    user_id = "cliente_1"
    session_id = "sessao_suporte"

    await session_service.create_session(
        app_name="tech_support",
        user_id=user_id,
        session_id=session_id,
    )

    message = types.Content(role="user", parts=[types.Part(text=mensagem_cliente)])

    resposta = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                resposta = event.content.parts[0].text

    return resposta


# ===================#
# INTERFACE STREAMLIT

st.set_page_config(page_title="Suporte Técnico Multi-Agente", page_icon="🛠️", layout="wide")

st.title("🛠️ Suporte Técnico Multi-Agente")
st.caption("Variação própria — Google ADK + Gemini + Streamlit | Atividade 11")

st.markdown("""
Este sistema usa três agentes especializados que colaboram para atender solicitações:
- **support_orchestrator** — coordena e sintetiza
- **bug_agent** — diagnostica erros técnicos
- **feature_agent** — avalia pedidos de funcionalidade
- **billing_agent** — responde dúvidas de cobrança
""")

with st.form("form_suporte"):
    mensagem = st.text_area(
        "Descreva sua solicitação",
        value=(
            "Estou com dois problemas:\n"
            "1) O relatório de vendas está demorando mais de 30 segundos para carregar.\n"
            "2) Quero saber se o plano Pro inclui integração com API externa, "
            "e se não incluir, quanto custaria para adicionar."
        ),
        height=150,
    )
    enviado = st.form_submit_button("Enviar solicitação")

if enviado:
    if not mensagem.strip():
        st.warning("Digite sua solicitação.")
    else:
        with st.spinner("Os agentes estão analisando sua solicitação..."):
            try:
                resultado = asyncio.run(atender_cliente(mensagem))
                if resultado:
                    st.success("Resposta gerada!")
                    st.markdown("---")
                    st.markdown(resultado)
                    st.download_button(
                        "Baixar resposta (.md)",
                        data=resultado,
                        file_name="resposta_suporte.md",
                        mime="text/markdown",
                    )
                else:
                    st.error("Sem resposta dos agentes. Tente novamente.")
            except Exception as e:
                st.error(f"Erro: {e}")

st.markdown("---")
st.caption("FastCamp Agentes Inteligentes — Atividade 11")