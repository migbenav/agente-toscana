import os
from dotenv import load_dotenv

# Carga de variables de entorno de manera prioritaria antes de instanciar componentes
load_dotenv()

import streamlit as st
from src.agent import LegalRAGAgent

def setup_page_config() -> None:
    """
    Configura los parametros principales de la interfaz del navegador en Streamlit.
    """
    st.set_page_config(
        page_title="Asistente Virtual de Propiedad Horizontal",
        layout="centered",
        initial_sidebar_state="expanded"
    )

def initialize_agent_safely() -> LegalRAGAgent:
    """
    Instancia el agente de forma directa para capturar errores explicitos en la UI.
    """
    agent_instance = LegalRAGAgent()
    agent_instance.setup_rag_chain()
    return agent_instance

def initialize_session_state() -> None:
    """
    Garantiza que las variables para almacenar el historial existan en la sesion actual.
    """
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

def render_sidebar(agent: LegalRAGAgent) -> None:
    """
    Renderiza los elementos laterales, indicadores de estado y controles operativos.
    """
    with st.sidebar:
        st.title("Panel de Control")
        st.markdown("---")
        
        vector_store_exists = os.path.exists(agent.vector_store_path)
        if vector_store_exists:
            st.success("Base de datos local activa")
        else:
            st.error("Base de datos local no detectada")
            
        st.markdown("---")
        if st.button("Limpiar historial de chat", use_container_width=True):
            st.session_state["messages"] = []
            print("Historial de conversacion reiniciado por el usuario.")
            st.rerun()

def render_chat_history() -> None:
    """
    Itera y despliega todos los mensajes cronologicos guardados en el estado de la sesion.
    """
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_user_input(agent: LegalRAGAgent) -> None:
    """
    Captura consultas de entrada, ejecuta el pipeline RAG y procesa el renderizado de la UI.
    """
    if user_query := st.chat_input("Escriba su consulta legal o de convivencia aqui..."):
        st.session_state["messages"].append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Analizando base legal de propiedad horizontal..."):
                print(f"Procesando consulta desde la UI: {user_query}")
                response_text = agent.answer_question(user_query)
                st.markdown(response_text)
                
        st.session_state["messages"].append({"role": "assistant", "content": response_text})

def main() -> None:
    """
    Funcion principal de orquestacion para la aplicacion de interfaz de usuario en Streamlit.
    """
    setup_page_config()
    
    st.title("Asistente de Propiedad Horizontal")
    st.caption("Consultas sobre la Ley 27157, reglamentos internos y manuales de convivencia en el Peru")
    st.markdown("---")
    
    try:
        if "rag_agent" not in st.session_state:
            with st.spinner("Cargando embeddings y base de datos vectorial local... (Esto puede tardar un momento)"):
                st.session_state["rag_agent"] = initialize_agent_safely()
        
        agent = st.session_state["rag_agent"]
        
    except Exception as general_error:
        st.error("Se detecto un fallo critico al inicializar el backend de IA:")
        st.exception(general_error)
        return

    initialize_session_state()
    render_sidebar(agent)
    render_chat_history()
    handle_user_input(agent)

if __name__ == "__main__":
    main()