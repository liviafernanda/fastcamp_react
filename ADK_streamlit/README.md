# Atividade 11

Foram criados dois códigos

- Códigos gerados com o conteúdo do card - planejador de viagens
- Códigos novos por mim com meus conhecimentos adquiridos - suporte


## Planejador de Viagens Multi-Agente (Google ADK)

Projeto da Atividade 11 do FastCamp de Agentes Inteligentes com o conteúdo do card.

## O que é

Um assistente de viagens que usa quatro agentes do Google ADK
para planejar uma viagem completa: voos, hospedagem e atividades.

## Arquitetura
Usuário → Streamlit UI → host_agent\
├── flight_agent\
├── stay_agent\
└── activities_agent


- `host_agent` coordena e delega
- `flight_agent`, `stay_agent`, `activities_agent` são especialistas

## Variação Própria: Suporte Técnico Multi-Agente

Para demonstrar que os conceitos foram internalizados, foi criado um
segundo sistema multi-agente aplicando o mesmo padrão do ADK
(`sub_agents` + `mode="single_turn"` + `Runner` + Streamlit) em um
domínio diferente: suporte técnico.

### Arquitetura

Usuário → Streamlit UI → support_orchestrator\
├── bug_agent\
├── feature_agent\
└── billing_agent

### O que mudou em relação ao sistema de viagens

- Domínio: viagens → suporte técnico
- Agentes: flight/stay/activities → bug/feature/billing
- Prompt: planejamento → diagnóstico e triagem

### O que permaneceu igual

- Uso de `Agent(name, model, mode, description, instruction)`
- Orquestração via `sub_agents` com `mode="single_turn"`
- Execução via `Runner` + `InMemorySessionService`
- Interface Streamlit com formulário e download do resultado

### Conclusão

A mesma estrutura arquitetural pode ser reaproveitada para diferentes
domínios, bastando redefinir os agentes especializados e as instruções.
Isso demonstra a modularidade do ADK.

## Como executar

### 1. Clone o repositório

```bash
git clone <link do repositório>
cd fastcamp_react/ADK_streamlit
```

### 2. Faça a configuração da sua chave api, rode o ambiente virtual e as dependências:

1. Criar um ambiente virtual (python -m venv .venv).

2. Instalar dependências (pip install -r requirements.txt).

3. Criar um arquivo .env e colocar sua GOOGLE_API_KEY.

4. Executar o app (streamlit run app.py ou streamlit run app_suporte.py).