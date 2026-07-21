import os
import traceback
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

    def get_system_info(self) -> dict:
        """
        Devuelve información del backend utilizada por la interfaz.
        """
        llm_name = "Desconocido"
        if hasattr(self.llm, "model"):
            llm_name = self.llm.model
        elif hasattr(self.llm, "model_name"):
            llm_name = self.llm.model_name
        embedding_name = "No cargado"
        if self.embeddings is not None:
            embedding_name = self.embeddings.model_name if hasattr(
                self.embeddings,
                "model_name",
            ) else "BAAI/bge-m3"
        return {
            "llm": llm_name,
            "embeddings": embedding_name,
            "vector_store": "FAISS",
        }

    def _initialize_embeddings(self) -> None:
        """
        Carga el modelo local de embeddings en la memoria RAM usando la CPU.
        """
        print("Cargando modelo local de embeddings en memoria...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-m3",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
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

    def _format_documents(self, documents) -> str:
        """
        Convierte los documentos recuperados por FAISS en un único bloque
        de contexto para el LLM.
        """
        formatted_docs = []

        for doc in documents:
            metadata = doc.metadata or {}
            header = []
            if metadata.get("Title"):
                header.append(metadata["Title"])
            if metadata.get("Chapter"):
                header.append(metadata["Chapter"])
            if metadata.get("Section"):
                header.append(metadata["Section"])
            if metadata.get("Article"):
                header.append(metadata["Article"])

            prefix = " | ".join(header)

            if prefix:
                formatted_docs.append(
                    f"{prefix}\n{doc.page_content}"
                )
            else:
                formatted_docs.append(doc.page_content)

        return "\n\n-----------------------------\n\n".join(formatted_docs)

    def setup_rag_chain(self) -> None:
        """
        Inicializa la infraestructura del agente.
        """
        print("Iniciando configuracion del agente RAG...")

        self._initialize_embeddings()
        self._load_vector_store()
        self._load_prompt_template()

        if not self.vector_store or not self.prompt or not self.llm:
            raise ValueError(
                "Los componentes del agente no se inicializaron correctamente."
            )

        print("Agente RAG configurado y listo para recibir consultas.")

    def answer_question(self, question: str) -> str:
        """
        Ejecuta una búsqueda RAG y devuelve la respuesta junto con
        las fuentes consultadas.
        """
        try:
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 10},
            )

            retrieved_docs = retriever.invoke(question)
            context = self._format_documents(retrieved_docs)
            prompt = self.prompt.format(
                context=context,
                question=question,
            )

            response = self.llm.invoke(prompt)
            if hasattr(response, "content"):
                answer = response.content
            else:
                answer = str(response)

            ###################################################################
            # Construcción de las fuentes
            ###################################################################

            sources = []

            for doc in retrieved_docs:
                metadata = doc.metadata or {}
                title = (
                    metadata.get("Title")
                    or metadata.get("source")
                )

                if title and title not in sources:
                    sources.append(title)

            if sources:
                answer += "\n\n---\n\n### 📚 Fuentes consultadas\n"
                for source in sources:
                    answer += f"\n- {source}"

            return answer

        except Exception as error:
            print(error)
            traceback.print_exc()
            return (
                "Lo sentimos, ocurrió un problema al procesar la consulta."
            )


# Bloque de verificacion tecnica y pruebas multi-modelo
if __name__ == "__main__":
    import sys
    import traceback
    from dotenv import load_dotenv
    
    load_dotenv()

    agent = LegalRAGAgent()
    try:
        agent.setup_rag_chain()
        
        test_query = "Artículo 15 Convocatoria y Quórum?"
        print(f"\n==========================================")
        print(f"CONSULTA DE PRUEBA: {test_query}")
        print(f"==========================================\n")
        
        # --- BLOQUE DE DEPURACIÓN LOCAL (NUESTRO PROPIO LANGSMITH) ---
        print("--- [FAISS RETRIEVAL INSPECTOR] ---")
        # Forzamos la extracción manual de los fragmentos que FAISS encuentra
        retriever = agent.vector_store.as_retriever(search_kwargs={"k": 10})
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
        print("\n===== ERROR =====")
        traceback.print_exc()
