# Troubleshooting

← [Volver al README](../README.md)

---

## Objetivo

Este documento recopila los principales problemas encontrados durante el desarrollo del proyecto y la forma en que fueron resueltos.

---

## Streamlit Community Cloud

### Error

Aplicación sin iniciar correctamente.

### Solución

Verificar la versión de Python utilizada por Streamlit Cloud y las dependencias instaladas.

---

## Streamlit File Watcher

### Error

Problemas durante la ejecución local relacionados con la supervisión de archivos.

### Solución

Ejecutar la aplicación mediante:

```bash
streamlit run app.py --server.fileWatcherType none
```

---

## Base vectorial inexistente

### Error

No se encuentra el directorio `vector_store`.

### Solución

Regenerar el índice vectorial antes de iniciar la aplicación.

---

## Variables de entorno

### Error

No se encuentra `GOOGLE_API_KEY`.

### Solución

Crear un archivo `.env` en la raíz del proyecto y configurar la clave correspondiente.

---

## Respuestas repetitivas

### Problema

El modelo repetía la referencia al documento en múltiples ocasiones.

### Solución

Se modificó el procesamiento de las fuentes para consolidarlas al final de la respuesta.

---

## Actualización de documentos

Cuando se agregan nuevos documentos es necesario regenerar el índice vectorial para que puedan ser utilizados por el asistente.

---

← [Volver al README](../README.md)