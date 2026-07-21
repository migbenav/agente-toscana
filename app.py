import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from src.agent import LegalRAGAgent

load_dotenv()

# ============================================================
# Preguntas sugeridas
# ============================================================
EXAMPLE_QUESTIONS = [
    "¿Cómo se convoca una junta de propietarios?",
    "¿Qué funciones tiene el presidente de la Junta de Propietarios?",
    "¿Cómo se aprueba el presupuesto anual?",
    "¿Qué mayoría se necesita para modificar el Reglamento Interno?",
    "¿Quién puede representar a un propietario en una asamblea?",
    "¿Qué obligaciones establece la Ley de Protección de Datos Personales para una Junta de Propietarios?",
]

# ============================================================
# Configuración inicial
# ============================================================

def setup_page_config() -> None:
    """Configura la página."""
    st.set_page_config(
        page_title="Asistente Virtual de Propiedad Horizontal",
        layout="centered",
        initial_sidebar_state="expanded",
    )

def load_css() -> None:
    """
    Carga los estilos personalizados.
    """
    css_file = Path("styles.css")
    if css_file.exists():
        with open(css_file, encoding="utf-8") as file:
            st.markdown(
                f"<style>{file.read()}</style>",
                unsafe_allow_html=True,
            )

def initialize_agent_safely() -> LegalRAGAgent:
    """
    Inicializa el agente.
    """
    agent = LegalRAGAgent()
    agent.setup_rag_chain()
    return agent

def initialize_session_state() -> None:
    """
    Variables persistentes de Streamlit.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_question" not in st.session_state:
        st.session_state.selected_question = None

# ============================================================
# Sidebar
# ============================================================

def render_documents() -> None:
    """
    Muestra la lista de documentos disponibles.
    """
    documents = sorted(Path("data").glob("*.md"))
    st.markdown(
        f"""
        <div class="sidebar-title">
            Base documental ({len(documents)})
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not documents:
        st.caption("No se encontraron documentos.")
        return
    with st.expander("Ver documentos", expanded=False):
        for document in documents:
            st.markdown(
                f"""
                <div class="document-item">
                {document.stem}
                </div>
                """,
                unsafe_allow_html=True,
            )

def render_system_info(agent: LegalRAGAgent) -> None:
    """
    Muestra información general del sistema.
    """
    document_count = len(list(Path("data").glob("*.md")))
    system = agent.get_system_info()
    st.markdown(
        """
        <div class="sidebar-title">
        Sistema
        </div>
        """,
        unsafe_allow_html=True,
    )
    if os.path.exists(agent.vector_store_path):
        status = "Sistema listo"
    else:
        status = "Base vectorial no disponible"
    st.markdown(
        f"""
        <div class="document-item">
        <strong>Estado</strong><br>
        {status}<br><br>
        <strong>Tecnología</strong><br>
        {system["llm"]}<br>
        {system["embeddings"]}<br>
        {system["vector_store"]}<br><br>
        <strong>Base documental</strong><br>
        {document_count} documento(s)
        </div>
        """,
        unsafe_allow_html=True,
    )

# Preguntas sugeridas
def render_example_questions_sidebar() -> None:
    """
    Muestra las consultas de ejemplo en el panel lateral.
    """
    with st.expander("Consultas de ejemplo", expanded=False):
        for index, question in enumerate(EXAMPLE_QUESTIONS):
            if st.button(
                question,
                key=f"sidebar_question_{index}",
                use_container_width=True,
            ):
                st.session_state.selected_question = question
                st.rerun()

def render_sidebar(agent: LegalRAGAgent) -> None:
    """
    Renderiza el panel lateral.
    """
    with st.sidebar:
        render_system_info(agent)
        st.divider()
        render_documents()
        st.divider()
        render_example_questions_sidebar()
        st.divider()
        if st.button(
            "Limpiar conversación",
            use_container_width=True,
        ):
            st.session_state.messages = []
            st.session_state.selected_question = None
            st.rerun()

# ============================================================
# Historial
# ============================================================

def render_chat_history() -> None:
    """Renderiza el historial de conversación."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ============================================================
# Procesamiento
# ============================================================

def process_question(agent: LegalRAGAgent, question: str) -> None:
    """Envía la consulta al agente y muestra la respuesta."""
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Analizando la normativa..."):
            response = agent.answer_question(question)
            st.markdown(response)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )

def handle_user_input(agent: LegalRAGAgent) -> None:
    """Gestiona la entrada del usuario."""
    question = st.session_state.selected_question
    if question:
        st.session_state.selected_question = None
        process_question(agent, question)
        return
    question = st.chat_input("Realice una consulta sobre propiedad horizontal...")
    if question:
        process_question(agent, question)

# ============================================================
# Principal
# ============================================================

def main() -> None:
    setup_page_config()
    load_css()
    st.markdown(
        "<h1>Asistente Virtual de Propiedad Horizontal</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="main-subtitle">
            Consultas sobre el Decreto Legislativo N.º 1568,
            la Ley N.º 27157, el Reglamento Interno y la
            normativa sobre Protección de Datos Personales.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    try:
        if "rag_agent" not in st.session_state:
            with st.spinner("Cargando base documental..."):
                st.session_state.rag_agent = initialize_agent_safely()
        agent = st.session_state.rag_agent
    except Exception as error:
        st.error("No fue posible inicializar el asistente.")
        st.exception(error)
        return
    initialize_session_state()
    render_sidebar(agent)
    render_chat_history()
    handle_user_input(agent)


if __name__ == "__main__":
    main()