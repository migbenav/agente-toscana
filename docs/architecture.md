# Arquitectura del Sistema

← [Volver al README](../README.md)

---

## Objetivo

La aplicación implementa una arquitectura **Retrieval-Augmented Generation (RAG)** para responder consultas sobre normativa peruana de propiedad horizontal.

En lugar de depender únicamente del conocimiento del modelo de lenguaje, el sistema recupera primero la información más relevante desde una base documental propia y utiliza ese contexto para generar respuestas fundamentadas.

Esta estrategia permite reducir alucinaciones, mantener las respuestas alineadas con la normativa cargada y facilitar la incorporación de nuevos documentos sin necesidad de reentrenar el modelo.

---

## Arquitectura General

```
                    Documentos PDF
                           │
                           ▼
                  data_cleaner.py
                           │
                           ▼
              Documentos Markdown (.md)
                           │
                           ▼
               Pipeline de indexación
                           │
                           ▼
          Embeddings (BAAI / bge-m3)
                           │
                           ▼
               Base vectorial FAISS
                           │
────────────────────────────────────────────────────
                           │
                    Consulta del usuario
                           │
                           ▼
                      app.py (UI)
                           │
                           ▼
                  LegalRAGAgent
                           │
                           ▼
               Recuperación de contexto
                           │
                           ▼
                Prompt + Google Gemini
                           │
                           ▼
                     Respuesta final
```

---

## Componentes principales

### app.py

Punto de entrada de la aplicación.

Sus responsabilidades son:

- Construir la interfaz con Streamlit.
- Mostrar el historial de conversación.
- Gestionar las consultas del usuario.
- Mostrar información del sistema y documentos cargados.
- Enviar las preguntas al agente RAG.

---

### agent.py

Implementa la lógica principal del asistente.

Entre sus funciones se encuentran:

- Inicializar el modelo de embeddings.
- Cargar el índice FAISS.
- Recuperar los fragmentos más relevantes.
- Construir el contexto enviado al LLM.
- Generar la respuesta final.
- Mostrar las fuentes documentales utilizadas.

---

### data_cleaner.py

Procesa los documentos antes de ser incorporados a la base documental.

Su función es transformar documentos PDF en archivos Markdown estructurados mediante un proceso asistido por un modelo LLM.

Este procesamiento se realiza una única vez antes de la indexación.

El detalle del proceso puede consultarse en [rag_pipeline.md](rag_pipeline.md).

---

### data/

Contiene los documentos fuente utilizados por el sistema.

Actualmente se almacenan en formato Markdown para preservar la estructura jerárquica de la normativa y facilitar su posterior división e indexación.

---

### vector_store/

Almacena el índice vectorial generado con FAISS.

Este índice permite realizar búsquedas semánticas eficientes sin necesidad de recalcular los embeddings en cada ejecución.

---

### prompts/

Contiene las plantillas utilizadas para construir las instrucciones enviadas al modelo de lenguaje.

Separar los prompts del código facilita su mantenimiento y experimentación.

---

## Flujo de una consulta

Cada consulta sigue el siguiente proceso:

1. El usuario realiza una pregunta desde la interfaz.
2. El agente convierte la consulta en un vector mediante el modelo de embeddings.
3. FAISS recupera los fragmentos más similares.
4. Los fragmentos recuperados se incorporan al prompt.
5. El modelo Gemini genera una respuesta utilizando únicamente el contexto proporcionado.
6. La respuesta se devuelve junto con la referencia de los documentos consultados.

---

## Principios de diseño

Durante el desarrollo se priorizaron los siguientes criterios:

- Separación entre interfaz, lógica del agente y procesamiento documental.
- Componentes desacoplados para facilitar futuras sustituciones de modelos.
- Uso de archivos Markdown como formato documental intermedio.
- Persistencia local del índice vectorial para reducir tiempos de carga.
- Arquitectura preparada para incorporar nuevos documentos y modelos LLM con cambios mínimos.

---

Para conocer con mayor detalle el procesamiento documental y la construcción del índice vectorial, consulte el documento [Pipeline RAG](rag_pipeline.md).

---

← [Volver al README](../README.md)