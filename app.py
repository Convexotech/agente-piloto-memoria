import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv


load_dotenv()

# Configuração inicial da página Streamlit
st.set_page_config(
    page_title="Sistema de Comunicação de MKT",
    page_icon="👌",
    layout="centered"
)

# Inicialização do cliente Groq utilizando variável de ambiente
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.error("⚠️ A variável de ambiente GROQ_API_KEY não foi configurada no servidor Render.")
    st.stop()

client = Groq(api_key=api_key)

# Prompt de Sistema (System Message) com todas as diretrizes solicitadas
SYSTEM_PROMPT = """
Você é um especilista em marketing digital e automção de ferramentas de comunicação.

OBJETIVO:
Responder às dúvidas do usuário com precisão técnica e clareza didática. Você deve manter total coerência contextual a partir do resumo de memória de longo prazo e das últimas mensagens do histórico, recuperando dados fornecidos anteriormente e adaptando-se instantaneamente caso o usuário mude de assunto.

ESTILO:
Profissional, focado, articulado e didático. Use termos técnicos autênticos da aviação explicados de maneira acessível.

TOM:
Calmo, confiante, acolhedor e focado na segurança da comunicação empresarial descolada e moderna.

PÚBLICO-ALVO:
Time de marketing, clientes de escola e parceiros.

FORMATO DE RESPOSTA:
- Respostas diretas e organizadas em parágrafos curtos.
- Se o usuário mudar bruscamente de tópico, reconheça e adapte a conversa naturally sem travar (ex: "Entendido, alterando nossa rota para falar sobre...").
- Nunca invente fatos e mantenha rigorosa consistência factual com o histórico recente.
"""

# Interface Visual
st.title("😎🥳 Especialista em marketing ... ")
st.caption("Como posso auxiliar no seu voo hoje?")

# Inicialização do Histórico de Conversa na Sessão do Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibição das mensagens anteriores do chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Captura de nova entrada do usuário
if prompt := st.chat_input("Digite sua dúvida para o Comandante..."):
    # Adiciona e exibe a mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Preparação das mensagens enviadas para a API (incluindo o system prompt)
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]

    # Geração da resposta via Groq
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Chamada com streaming para melhor UX
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=api_messages,
                temperature=0.6,
                max_tokens=1024,
                stream=True
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Erro no sistema de comunicação: {str(e)}")