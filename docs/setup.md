# Instalación y Configuración

← [Volver al README](../README.md)

---

## Requisitos

Antes de ejecutar el proyecto es necesario contar con:

- Python 3.12 (recomendado)
- Git
- Una clave de Google AI Studio (`GOOGLE_API_KEY`)

> **Nota:** Aunque el proyecto puede ejecutarse con versiones más recientes de Python, se recomienda utilizar Python 3.12 para evitar problemas de compatibilidad con algunas dependencias.

---

## Clonar el repositorio

```bash
git clone https://github.com/migbenav/agente-toscana.git
cd REPOSITORIO
```

---

## Crear un entorno virtual

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Configurar las variables de entorno

Crear un archivo `.env` en la raíz del proyecto.

```text
GOOGLE_API_KEY=TU_API_KEY
```

---

## Preparar los documentos

Los documentos utilizados por el sistema deben encontrarse en formato Markdown dentro de la carpeta:

```text
data/
```

Si los documentos originales están en PDF, primero deben procesarse utilizando:

```bash
python src/data_cleaner.py
```

Este proceso limpia y estructura automáticamente los documentos antes de su indexación.

---

## Generar el índice vectorial

Una vez preparados los documentos, ejecutar el proceso de indexación para crear la carpeta `vector_store`.

> Este paso solo es necesario cuando se agregan nuevos documentos o cambia el modelo de embeddings.

---

## Ejecutar la aplicación

Durante el desarrollo se recomienda ejecutar Streamlit utilizando:

```bash
streamlit run app.py --server.fileWatcherType none
```

Esta configuración evita problemas relacionados con el sistema de monitoreo de archivos en algunos entornos.

---

## Despliegue en Streamlit Community Cloud

Para publicar la aplicación:

1. Subir el proyecto a GitHub.
2. Crear una nueva aplicación en Streamlit Community Cloud.
3. Configurar el repositorio y la rama correspondiente.
4. Agregar la variable `GOOGLE_API_KEY` en la sección **Secrets**.
5. Desplegar la aplicación.

---

## Actualizar la base documental

Cuando se incorporen nuevos documentos, el flujo recomendado es:

1. Convertir los documentos a Markdown (si es necesario).
2. Regenerar el índice vectorial.
3. Reiniciar la aplicación.

No es necesario modificar el código del agente para incorporar nueva normativa.

---

← [Volver al README](../README.md)