"""
Assistente de Viagens Multi-Agente com Google ADK + Gemini + Streamlit
Atividade 11 - FastCamp Agentes Inteligentes
"""

import os
import re
import json
import asyncio
import streamlit as st
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Configura a chave do Google
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Configure GOOGLE_API_KEY no arquivo .env")
    st.stop()

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

# Imports do ADK
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

#=====================#
# DEFINIÇÃO DOS AGENTES

MODEL = "gemini-3.5-flash-lite"

flight_agent = Agent(
    name="flight_agent",
    model=MODEL,
    mode="single_turn",
    description="Especialista em sugerir opções de voos.",
    instruction=(
        "Dado um destino, datas e orçamento, sugira 1-2 opções de voos realistas. "
        "Inclua nome da companhia aérea, preço aproximado e horário de partida. "
        "Garanta que os voos caibam no orçamento. Responda em português, de forma concisa."
    ),
)

stay_agent = Agent(
    name="stay_agent",
    model=MODEL,
    mode="single_turn",
    description="Especialista em sugerir hospedagem.",
    instruction=(
        "Dado um destino, datas e orçamento, sugira 2-3 opções de hotéis ou pousadas. "
        "Inclua nome, preço por noite e localização. Responda em português, de forma concisa."
    ),
)

activities_agent = Agent(
    name="activities_agent",
    model=MODEL,
    mode="single_turn",
    description="Especialista em sugerir atividades turísticas.",
    instruction=(
        "Dado um destino, datas e orçamento, sugira 3-4 atividades turísticas ou culturais. "
        "Para cada atividade, forneça nome, descrição curta, estimativa de preço e duração em horas. "
        "Responda em português, de forma concisa."
    ),
)

host_agent = Agent(
    name="host_agent",
    model=MODEL,
    description="Coordenador de planejamento de viagens.",
    instruction=(
        "Coordenador de viagens. Você DEVE consultar os três especialistas em sequência:\n"
        "1. flight_agent → depois volte para host_agent\n"
        "2. stay_agent → depois volte para host_agent\n"
        "3. activities_agent → depois volte para host_agent\n"
        "Só depois de consultar os três, monte o itinerário final em português."
    ),
    sub_agents=[flight_agent, stay_agent, activities_agent],
)

#==============================#
# FUNÇÃO DE EXECUÇÃO DOS AGENTES

async def planejar_viagem(destino, data_ida, data_volta, orcamento):
    """Executa o host_agent e retorna o itinerário final como texto."""

    session_service = InMemorySessionService()
    runner = Runner(
        agent=host_agent,
        app_name="travel_planner",
        session_service=session_service,
    )

    user_id = "usuario_streamlit"
    session_id = "sessao_unica"

    await session_service.create_session(
        app_name="travel_planner",
        user_id=user_id,
        session_id=session_id,
    )

    prompt = (
        f"Quero viajar para {destino} de {data_ida} a {data_volta}, "
        f"com orçamento total de {orcamento}. "
        f"Sugira voos, hospedagem e atividades. Responda em português."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    resposta_final = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                resposta_final = event.content.parts[0].text

    return resposta_final


# ===================#
# INTERFACE STREAMLIT

st.set_page_config(
    page_title="Assistente de Viagens ADK",
    page_icon="✈️",
    layout="wide",
)

st.title("✈️ Planejador de Viagens Multi-Agente")
st.caption("Google ADK + Gemini + Streamlit | Atividade 11 - FastCamp")

st.markdown("""
Este assistente usa **quatro agentes especializados** que trabalham em equipe:
- **host_agent** — coordena o planejamento
- **flight_agent** — sugere voos
- **stay_agent** — sugere hospedagem
- **activities_agent** — sugere atividades turísticas
""")

# Formulário
with st.form("form_viagem"):
    col1, col2 = st.columns(2)
    with col1:
        destino = st.text_input("Destino", "Rio de Janeiro")
        data_ida = st.text_input("Data de ida", "2026-12-10")
    with col2:
        data_volta = st.text_input("Data de volta", "2026-12-15")
        orcamento = st.text_input("Orçamento", "R$ 5.000")

    enviado = st.form_submit_button("Planejar viagem")

if enviado:
    if not destino or not data_ida or not data_volta or not orcamento:
        st.warning("Preencha todos os campos.")
    else:
        with st.spinner("Os agentes estão trabalhando... isso pode levar 30-60 segundos."):
            try:
                resultado = asyncio.run(
                    planejar_viagem(destino, data_ida, data_volta, orcamento)
                )

                if resultado:
                    st.success("Itinerário gerado com sucesso!")
                    st.markdown("---")
                    st.markdown(resultado)
                    st.markdown("---")

                    # Botão de download
                    st.download_button(
                        label="Baixar itinerário (.md)",
                        data=resultado,
                        file_name=f"itinerario_{destino.replace(' ', '_')}.md",
                        mime="text/markdown",
                    )
                else:
                    st.error("Os agentes não retornaram resposta. Tente novamente.")
            except Exception as e:
                st.error(f"Erro ao executar os agentes: {e}")

st.markdown("---")
st.caption("Desenvolvido para o FastCamp de Agentes Inteligentes")