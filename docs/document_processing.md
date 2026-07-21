# Procesamiento Documental y Pipeline RAG

← [Volver al README](../README.md)

---

## Objetivo

Este documento describe el proceso mediante el cual los documentos legales son transformados en una base de conocimiento consultable mediante lenguaje natural.

El procesamiento se divide en dos etapas independientes:

- **Preparación documental (offline):** se ejecuta únicamente cuando se incorporan o actualizan documentos.
- **Consulta (online):** se ejecuta cada vez que un usuario realiza una pregunta.

Esta separación permite mantener tiempos de respuesta bajos y facilita la incorporación de nueva normativa sin modificar el resto del sistema.

---

# Preparación documental (Offline)

La preparación documental se realiza una sola vez por cada documento antes de incorporarlo al sistema.

```
PDF
 │
 ▼
Extracción de texto
 │
 ▼
Limpieza y estructuración con IA
 │
 ▼
Markdown
 │
 ▼
División en fragmentos
 │
 ▼
Embeddings
 │
 ▼
Índice FAISS
```

---

## 1. Extracción del contenido

Los documentos originales se reciben normalmente en formato PDF.

Durante esta etapa se extrae el texto de cada página preservando el contenido original para su posterior procesamiento.

---

## 2. Limpieza y estructuración

El script `data_cleaner.py` utiliza un modelo LLM para transformar el texto extraído en un documento Markdown limpio y estructurado.

Entre las tareas realizadas se encuentran:

- eliminación de encabezados y pies de página;
- eliminación de índices y elementos repetitivos;
- organización de títulos, capítulos y artículos;
- conversión de tablas a formato Markdown;
- enriquecimiento contextual cuando una norma hace referencia a artículos anteriores.

El resultado es un documento mucho más adecuado para procesos de recuperación semántica.

---

## 3. Conversión a Markdown

Todos los documentos procesados se almacenan en la carpeta `data/` en formato Markdown.

Utilizar Markdown como formato intermedio aporta varias ventajas:

- conserva la estructura jerárquica de la normativa;
- facilita correcciones manuales cuando son necesarias;
- desacopla el procesamiento documental de la indexación;
- simplifica la incorporación de nuevos documentos.

---

## 4. División en fragmentos

Antes de generar los embeddings, los documentos se dividen en fragmentos utilizando una estrategia en dos etapas:

- `MarkdownHeaderTextSplitter`, que preserva la jerarquía legal;
- `RecursiveCharacterTextSplitter`, que divide únicamente los bloques demasiado extensos.

Cada fragmento conserva metadatos como el documento de origen, título, capítulo o artículo.

---

## 5. Generación de embeddings

Cada fragmento se transforma en un vector utilizando el modelo **BAAI/bge-m3**.

Estos vectores representan el significado semántico del texto y permiten encontrar información relacionada incluso cuando la consulta utiliza palabras diferentes a las presentes en los documentos.

---

## 6. Creación del índice vectorial

Los embeddings generados se almacenan en una base vectorial FAISS.

Este índice se guarda en la carpeta `vector_store/` y puede reutilizarse en todas las ejecuciones posteriores sin necesidad de recalcular los embeddings.

La indexación solo debe repetirse cuando:

- se agregan nuevos documentos;
- se modifica el procesamiento documental;
- se cambia el modelo de embeddings.

---

# Consulta del usuario (Online)

Una vez creada la base vectorial, cada consulta sigue el siguiente flujo.

```
Pregunta
 │
 ▼
Embedding de la consulta
 │
 ▼
Búsqueda en FAISS
 │
 ▼
Fragmentos relevantes
 │
 ▼
Construcción del prompt
 │
 ▼
Google Gemini
 │
 ▼
Respuesta
```

---

## 1. Recepción de la consulta

El usuario realiza una pregunta desde la interfaz desarrollada con Streamlit.

---

## 2. Recuperación del contexto

La consulta se transforma en un embedding y se compara contra el índice FAISS.

Se recuperan los fragmentos más relevantes para responder la pregunta.

---

## 3. Construcción del prompt

El agente reúne los fragmentos recuperados y construye un único contexto.

Posteriormente incorpora:

- las instrucciones del sistema (`legal_agent.md`);
- la consulta realizada por el usuario;
- el contexto recuperado.

Este prompt completo se envía al modelo de lenguaje.

---

## 4. Generación de la respuesta

Google Gemini genera una respuesta utilizando el contexto recuperado.

Finalmente, la aplicación muestra al usuario la respuesta junto con los documentos utilizados como fuente.

---

## Próximas mejoras

La arquitectura fue diseñada para facilitar futuras mejoras, entre ellas:

- incorporación de nuevos modelos LLM;
- comparación entre distintos modelos de embeddings;
- estrategias de reranking;
- búsqueda híbrida (semántica + léxica);
- ampliación de la base documental;
- incorporación de nuevos tipos de documentos.

---

← [Volver al README](../README.md)