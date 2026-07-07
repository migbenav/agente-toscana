import os
import time
from pathlib import Path
from pypdf import PdfReader
from dotenv import load_dotenv  
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# === CONFIGURACIÓN DE ENTORNO Y RUTAS DEL PROYECTO ===
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ENV_PATH = BASE_DIR / ".env"

# Cargar las variables de entorno desde la raíz del proyecto
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    print("No se encontró el archivo .env en la raíz del proyecto.")

# Validar la presencia de las credenciales necesarias
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY no está configurada en el archivo .env")

# === INICIALIZACIÓN DEL MODELO DE INTELIGENCIA ARTIFICIAL ===
# Usamos gemini-3.5-flash por su balance óptimo entre velocidad, costo y ventana de contexto
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.1)

# === EXTRACCIÓN DE TEXTO DESDE PDF ===
def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Lee un archivo PDF página por página e inyecta marcas de separación 
    para mantener la consistencia del documento crudo.
    """
    print(f"Leyendo PDF crudo: {pdf_path.name}...")
    reader = PdfReader(pdf_path)
    full_text = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            full_text.append(f"--- [PÁGINA ORIGINAL {i+1}] ---\n{text}")
    return "\n".join(full_text)

# === PIPELINE DE LIMPIEZA Y ESTRUCTURACIÓN SEMÁNTICA (IA) ===
def clean_and_structure_document(raw_text: str, doc_type: str) -> str:
    """
    Envía el texto crudo a Gemini aplicando ingeniería de prompts para 
    remover ruido y forzar una estructura jerárquica en formato Markdown.
    """
    print(f"Gemini está procesando y limpiando el documento ({doc_type})...")
    
    system_prompt = (
        "You are an expert legal data engineer specializing in RAG (Retrieval-Augmented Generation) architectures.\n"
        "Your task is to take raw, messy text extracted from a Peruvian residential property document and convert it into clean, semantic Markdown.\n\n"
        "STRICT RULES:\n"
        "1. REMOVE NOISE: Delete page numbers, headers/footers, watermarks, advertisements, and tables of contents.\n"
        "2. DOCUMENT HIERARCHY: Format the document strictly using Markdown headers:\n"
        "   - # for Document Title\n"
        "   - ## for Titles / Sections (e.g., TÍTULO I)\n"
        "   - ### for Chapters (e.g., CAPÍTULO II)\n"
        "   - #### for Articles or Specific Rules (e.g., Artículo 15.- [Name])\n"
        "3. RAG ENRICHMENT: If an article mentions vague terms like 'the previous article', contextually enrich the text in brackets.\n"
        "4. TABLES & SANCTIONS: Convert any list of fines or sanctions into a clean Markdown Table (| Code | Infraction | Sanction |).\n"
        "5. LANGUAGE: The output MUST be entirely in SPANISH.\n"
        "6. Return ONLY the markdown content."
    )
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Here is the raw text from the document ({doc_type}):\n\n{text}")
    ])
    
    chain = prompt_template | llm
    response = chain.invoke({"doc_type": doc_type, "text": raw_text})
    
    # Manejo defensivo del formato de respuesta según la versión del SDK de LangChain
    if hasattr(response, "text") and response.text:
        return response.text
    elif isinstance(response.content, str):
        return response.content
    elif isinstance(response.content, list):
        text_parts = []
        for block in response.content:
            if isinstance(block, str):
                text_parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                text_parts.append(block["text"])
        return "".join(text_parts)
    
    return str(response.content)

# === ORQUESTADOR DEL PROCESAMIENTO DE ARCHIVOS ===
def process_file(filename: str, doc_type: str, output_name: str):
    """
    Valida las rutas de entrada/salida y coordina la lectura, el parsing 
    con el LLM y la escritura del archivo Markdown final en disco.
    """
    input_path = DATA_DIR / filename
    output_path = DATA_DIR / output_name
    
    if not input_path.exists():
        print(f"Error: No se encontró el archivo '{filename}' en la carpeta data/")
        return
        
    # Selección dinámica del extractor según el tipo de archivo
    if input_path.suffix.lower() == ".pdf":
        raw_text = extract_text_from_pdf(input_path)
    else:
        with open(input_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
            
    clean_markdown = clean_and_structure_document(raw_text, doc_type)
    
    # Persistencia del resultado estructurado
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(clean_markdown)
        
    print(f"Archivo guardado en: {output_path.name}\n" + "-"*50)

# === PUNTO DE ENTRADA DEL SCRIPT ===
if __name__ == "__main__":
    print("Iniciando Pipeline Automatizado de Limpieza de Datos para RAG...\n")
    
    # Ejecución del pipeline para la Ley de Propiedad Horizontal del Perú
    process_file(
        filename="Guía para el tratamiento de datos personales en edificios.pdf", 
        doc_type="Guía sobre el tratamiento de datos personales en edificios", 
        output_name="guia_tratamiento_datos_personales_edificios.md"
    )