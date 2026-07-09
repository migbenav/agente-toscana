import os
from typing import Any
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings


class LegalRAGAgent:
    """
    Orquesta el pipeline RAG usando LCEL para consultar la legislacion
    de Propiedad Horizontal en Peru.
    """

    def __init__(
        self,
        llm: Any = None,
        vector_store_path: str = "vector_store",
        prompt_template_path: str = "prompts/legal_agent.md",
    ):
        """
        Inicializa las rutas del sistema, componentes base e inyecta el LLM.
        """
        self.vector_store_path = vector_store_path
        self.prompt_template_path = prompt_template_path
        self.embeddings = None
        self.vector_store = None
        self.prompt = None
        self.rag_chain = None

        # Si no se provee un LLM, se asigna Gemini por defecto para mantener consistencia
        self.llm = llm if llm else ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.0,
            max_retries=2,
        )

    def _initialize_embeddings(self) -> None:
        """
        Carga el modelo local de embeddings en la memoria RAM usando la CPU.
        """
        print("Cargando modelo local de embeddings en memoria...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={"device": "cpu"},
        )

    def _load_vector_store(self) -> None:
        """
        Levanta el indice binario de FAISS persistido previamente en el disco.
        """
        if not os.path.exists(self.vector_store_path):
            raise FileNotFoundError(
                f"No se encontro el indice FAISS en el directorio: {self.vector_store_path}. "
                "Por favor, ejecute el pipeline de indexacion primero."
            )

        print("Cargando base de datos vectorial FAISS desde el disco...")
        self.vector_store = FAISS.load_local(
            folder_path=self.vector_store_path,
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True,
        )

    def _load_prompt_template(self) -> None:
        """
        Lee el archivo de texto plano del prompt y lo transforma a la estructura de LangChain.
        """
        if not os.path.exists(self.prompt_template_path):
            raise FileNotFoundError(
                f"No se encontro el archivo de plantilla: {self.prompt_template_path}"
            )

        print("Cargando plantilla de instrucciones juridicas...")
        with open(self.prompt_template_path, "r", encoding="utf-8") as file:
            template_content = file.read()

        self.prompt = PromptTemplate.from_template(template_content)

    def setup_rag_chain(self) -> None:
        """
        Inicializa de forma secuencial la infraestructura y ensambla la cadena LCEL.
        """
        print("Iniciando configuracion del agente RAG...")
        self._initialize_embeddings()
        self._load_vector_store()
        self._load_prompt_template()

        # Validacion estricta para asegurar que los componentes no sean None (elimina alertas del editor)
        if not self.vector_store or not self.prompt or not self.llm:
            raise ValueError("Los componentes del agente no se inicializaron correctamente.")
        
        # Configura el recuperador para extraer los 3 fragmentos mas similares
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4})

        # Construccion de la cadena lineal usando operadores Pipe de LCEL
        self.rag_chain = (
            {
                "context": retriever,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        print("Agente RAG configurado y listo para recibir consultas.")

    def answer_question(self, question: str) -> str:
        """
        Invoca la cadena para resolver la duda del usuario y gestiona fallos de ejecucion.
        """
        if not self.rag_chain:
            raise RuntimeError(
                "La cadena RAG no ha sido configurada. Llame a setup_rag_chain() antes de realizar consultas."
            )

        try:
            # Ejecucion sincrona del pipeline de datos
            response = self.rag_chain.invoke(question)
            return response
        except Exception as error:
            error_message = f"Error critico durante el procesamiento de la consulta: {str(error)}"
            print(error_message)
            return (
                "Lo sentimos, ocurrio un problema al conectar con el motor de Inteligencia Artificial. "
                "Por favor, intente de nuevo en unos momentos."
            )


# Bloque de verificacion tecnica y pruebas multi-modelo
if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    
    load_dotenv()

    agent = LegalRAGAgent()
    try:
        agent.setup_rag_chain()
        
        test_query = "¿Cuanto es la mora si no pago el recibo de mantenimiento?"
        print(f"\n==========================================")
        print(f"CONSULTA DE PRUEBA: {test_query}")
        print(f"==========================================\n")
        
        # --- BLOQUE DE DEPURACIÓN LOCAL (NUESTRO PROPIO LANGSMITH) ---
        print("--- [FAISS RETRIEVAL INSPECTOR] ---")
        # Forzamos la extracción manual de los fragmentos que FAISS encuentra
        retriever = agent.vector_store.as_retriever(search_kwargs={"k": 4})
        retrieved_docs = retriever.invoke(test_query)
        
        for index, doc in enumerate(retrieved_docs, 1):
            print(f"\n[Fragmento #{index}]")
            # Imprime los metadatos jerárquicos legal-peruanos guardados por tu splitter
            print(f"METADATOS: {doc.metadata}")
            print(f"CONTENIDO (Primeros 300 caracteres):")
            print(f"{doc.page_content[:300]}...\n")
            print("-" * 40)
        # -------------------------------------------------------------

        # Procedemos con la ejecución normal hacia el LLM
        print("\nEnviando contexto unificado a Google Gemini...")
        answer = agent.answer_question(test_query)
        print(f"\n================ RESPUESTA DEL LLM ================\n{answer}")
        
    except Exception as e:
        print(f"La inicializacion fallo: {e}")
