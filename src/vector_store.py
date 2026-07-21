import os
from pathlib import Path
from typing import List, Optional, Type
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
#from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

class KnowledgeBaseBuilder:
    """
    Clase responsable de la ingesta de documentos Markdown y de la construccion
    del Vector Store mediante inyeccion de dependencias.
    """
    
    def __init__(
        self, 
        embedding_model: Embeddings, 
        vector_store_class: Type[VectorStore], 
        data_dir: str = "data", 
        vector_store_dir: str = "vector_store"
    ):
        self.embedding_model = embedding_model
        self.vector_store_class = vector_store_class
        self.data_dir = Path(data_dir)
        self.vector_store_dir = Path(vector_store_dir)
        
        # Configuracion de la jerarquia de encabezados Markdown para la primera division
        self.headers_to_split_on = [
            ("#", "Title"),
            ("##", "Chapter"),
            ("###", "Section"),
            ("####", "Article"),
        ]
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=False
        )
        
        # Configuracion del splitter secundario para controlar el tamaño maximo de los fragmentos
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=120
        )

    def load_and_split_markdown(self) -> List[Document]:
        """
        Lee los archivos del directorio de datos y los fragmenta aplicando
        la estrategia de doble division estructural y por caracteres.
        """
        all_processed_chunks = []
        
        if not self.data_dir.exists():
            raise FileNotFoundError(f"El directorio de datos '{self.data_dir}' no existe.")
            
        markdown_files = list(self.data_dir.glob("*.md"))
        if not markdown_files:
            print(f"No se encontraron archivos .md en el directorio '{self.data_dir}'")
            return []

        for file_path in markdown_files:
            print(f"Procesando documento: {file_path.name}")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Division inicial basada en la estructura de encabezados Markdown
                markdown_chunks = self.markdown_splitter.split_text(content)
                
                # Inyeccion del nombre del archivo origen en los metadatos de cada fragmento
                for chunk in markdown_chunks:
                    chunk.metadata["source"] = file_path.name
                
                # Sub-division por caracteres para limitar la longitud del texto enviado al modelo
                final_chunks = self.text_splitter.split_documents(markdown_chunks)
                all_processed_chunks.extend(final_chunks)
                
            except Exception as e:
                print(f"Error al procesar el archivo {file_path.name}: {str(e)}")
                
        print(f"Segmentacion finalizada. Total de fragmentos generados: {len(all_processed_chunks)}")
        return all_processed_chunks

    def build_vector_store(self) -> Optional[VectorStore]:
        """
        Orquesta el procesamiento de documentos, la generacion de embeddings
        y la persistencia del almacenamiento vectorial de forma local.
        """
        try:
            documents = self.load_and_split_markdown()
            if not documents:
                print("Operacion cancelada: No hay documentos validos para indexar.")
                return None

            print("Generando embeddings e indexando en la base de datos vectorial...")
            vector_store = self.vector_store_class.from_documents(documents, self.embedding_model)
            
            # Creacion del directorio de destino si no existe y persistencia en disco
            self.vector_store_dir.mkdir(parents=True, exist_ok=True)
            
            # Verificacion de soporte para guardado local (ej. FAISS o Chroma)
            if hasattr(vector_store, "save_local"):
                vector_store.save_local(str(self.vector_store_dir))
                print(f"Base de datos vectorial guardada con exito en: '{self.vector_store_dir}/'")
            else:
                print("El Vector Store seleccionado no requiere o no soporta almacenamiento local directo.")
            
            return vector_store
            
        except Exception as e:
            print(f"Error critico en la construccion del Vector Store: {str(e)}")
            return None

    def load_local_vector_store(self) -> Optional[VectorStore]:
        """
        Carga una instancia del almacenamiento vectorial previamente guardada en el disco.
        """
        try:
            if hasattr(self.vector_store_class, "load_local"):
                return self.vector_store_class.load_local(
                    str(self.vector_store_dir), 
                    self.embedding_model, 
                    allow_dangerous_deserialization=True
                )
            print("El Vector Store seleccionado no soporta el metodo de carga local estandar.")
            return None
        except Exception as e:
            print(f"Error al cargar el Vector Store local: {str(e)}")
            return None


if __name__ == "__main__":
    print("--- Inicializando Pipeline de Ingesta Vectorial RAG ---")
    
    # Inicializacion de los componentes especificos (Google GenAI y FAISS)
    default_embeddings = HuggingFaceEmbeddings(
        #model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        model_name="BAAI/bge-m3",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    
    # Construccion de la base de conocimiento inyectando las herramientas seleccionadas
    builder = KnowledgeBaseBuilder(
        embedding_model=default_embeddings, 
        vector_store_class=FAISS
    )
    builder.build_vector_store()