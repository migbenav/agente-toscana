# Asistente Virtual de Propiedad Horizontal - RAG 🇵🇪

Este proyecto es un agente inteligente diseñado para responder consultas complejas sobre la Ley de Propiedad Horizontal en Perú, reglamentos internos y manuales de convivencia, entre otros, para edificios residenciales, utilizando arquitectura **RAG (Retrieval-Augmented Generation)**.

🚀 **Despliegue en vivo:** *(Enlace de Streamlit próximamente)*

---

## 📚 Estructura de la Documentación

Para mantener un registro ordenado y limpio del proceso de desarrollo, la bitácora técnica se dividirá en la carpeta `docs/` bajo los siguientes ejes:

* **Diseño y Arquitectura:** Explicación del flujo de datos, estrategias de enrutamiento y selección de herramientas.
* **Matriz de Experimentos:** Registro de pruebas con diferentes tamaños de *chunking*, técnicas de tokenización y rendimiento de LLMs.
* **Bitácora de Soluciones (Troubleshooting):** Errores encontrados y cómo se resolvieron.

---

## 🛠️ Tecnologías y Arquitectura

El backend del sistema está diseñado bajo principios de desacoplamiento y alta cohesión, permitiendo el intercambio de componentes mediante inyección de dependencias.

* **Lenguaje:** Python 3.14+
* **Orquestación RAG:** LangChain (Core, Text Splitters y Community)
* **Procesamiento de Texto:** `MarkdownHeaderTextSplitter` (preservación de jerarquía legal peruana) combinado con `RecursiveCharacterTextSplitter`.
* **Modelos de Embeddings:** `HuggingFaceEmbeddings` utilizando el modelo multilingüe local `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (optimizado para CPU y libre de restricciones de API Rate Limits).
* **Base de Datos Vectorial:** FAISS (Indexación y persistencia local en disco).
* **Generación de Respuestas (LLM):** Google Gemini (vía `langchain-google-genai`).
* **Interfaz de Usuario:** Streamlit (Despliegue futuro en Streamlit Community Cloud).