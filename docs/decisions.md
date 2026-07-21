# Decisiones de Diseño

← [Volver al README](../README.md)

---

## Objetivo

Este documento resume las principales decisiones técnicas adoptadas durante el desarrollo del proyecto y las razones que motivaron cada elección.

---

## ¿Por qué una arquitectura RAG?

La normativa legal cambia con el tiempo y puede ampliarse con nuevos documentos.

Utilizar una arquitectura RAG permite actualizar la base documental sin necesidad de reentrenar un modelo de lenguaje.

Además, las respuestas se generan utilizando información recuperada de los documentos disponibles, reduciendo el riesgo de respuestas incorrectas.

---

## ¿Por qué Markdown?

En lugar de indexar directamente los PDF, los documentos se transforman previamente a Markdown.

Este formato permite:

- conservar la estructura jerárquica;
- facilitar correcciones manuales;
- simplificar el procesamiento posterior;
- separar la preparación documental del proceso de consulta.

---

## ¿Por qué FAISS?

FAISS ofrece una búsqueda semántica rápida y puede almacenarse localmente.

Esto permite evitar la reconstrucción del índice en cada ejecución y reduce considerablemente los tiempos de respuesta.

---

## ¿Por qué BAAI/bge-m3?

Se eligió por ser un modelo multilingüe con buen desempeño en tareas de recuperación semántica.

Su soporte para español y su facilidad de ejecución local lo convierten en una buena alternativa para este proyecto.

---

## ¿Por qué Google Gemini?

Gemini ofrece una buena relación entre calidad de respuesta, velocidad y facilidad de integración mediante LangChain.

La arquitectura del proyecto permite sustituir el modelo por otros LLM en futuras versiones.

---

## ¿Por qué LangChain?

LangChain simplifica la integración entre:

- modelos de lenguaje;
- embeddings;
- recuperadores;
- prompts;
- bases vectoriales.

Esto facilita el mantenimiento del proyecto y futuras ampliaciones.

---

## Diseño modular

El proyecto se dividió en componentes independientes para facilitar su mantenimiento.

- `app.py` implementa la interfaz.
- `agent.py` concentra la lógica del asistente.
- `data_cleaner.py` prepara los documentos.
- `prompts/` contiene las instrucciones del sistema.
- `vector_store/` almacena el índice vectorial.

Esta separación permite modificar un componente sin afectar el resto de la aplicación.

---

← [Volver al README](../README.md)