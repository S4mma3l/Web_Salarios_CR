# Aplicación Web de Salarios Mínimos Oficiales Costa Rica 2025 con Análisis IA

Este proyecto es una aplicación web que permite consultar los salarios mínimos oficiales de Costa Rica para el año 2025, extraídos de un documento PDF oficial. La aplicación ofrece funcionalidades de búsqueda, visualización detallada de puestos e integración con Inteligencia Artificial (Gemini) para proporcionar análisis y sugerencias sobre los puestos laborales.

## Características

* **Extracción de Datos:** Procesa y extrae la tabla de salarios mínimos desde el PDF oficial del Ministerio de Trabajo y Seguridad Social (MTSS) de Costa Rica para 2025.
* **Procesamiento de Datos:** Utiliza `pandas` para limpiar y estructurar los datos extraídos del PDF.
* **Interfaz Web Moderna:** Frontend construido con HTML, CSS (diseño moderno y responsivo) y JavaScript para una experiencia de usuario interactiva.
* **Visualización de Lista:** Muestra un listado de todos los puestos y sus salarios asociados.
* **Búsqueda:** Permite filtrar la lista de puestos por nombre, código de categoría salarial o el significado completo del código.
* **Detalle del Puesto:** Al seleccionar un puesto, muestra su información detallada, incluyendo el significado completo de la sigla.
* **Análisis con IA (Gemini):** Integra la API de Gemini para, al seleccionar un puesto, generar un análisis que incluye sugerencias de conocimientos/habilidades requeridas y una opinión simulada desde la perspectiva de un reclutador profesional.
* **Gestión Segura de API Key:** Utiliza `python-dotenv` para cargar la clave de API de Gemini de forma segura desde un archivo `.env`.

## Tecnologías Utilizadas

* **Backend:** Python
    * Flask (Framework Web)
    * requests (Descarga de archivos)
    * pandas (Procesamiento de datos)
    * tabula-py (Extracción de tablas de PDF - Requiere Java)
    * python-dotenv (Carga de variables de entorno)
    * google-generativeai (Interacción con la API de Gemini)
* **Frontend:**
    * HTML
    * CSS
    * JavaScript
    * marked.js (Renderizado de Markdown en el frontend)

## Requisitos

* Python 3.6+
* Java Runtime Environment (JRE) o Java Development Kit (JDK) instalado.
* Una Clave de API de Gemini (puedes obtenerla en [Google AI Studio](https://makersuite.google.com/)).

## Configuración e Instalación

Sigue estos pasos para poner en marcha el proyecto:

1.  **Clonar el Repositorio** (Si está en un repositorio Git)
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DE_LA_CARPETA>
    ```
    O navega a la carpeta donde tienes los archivos del proyecto.

2.  **Crear y Activar un Entorno Virtual**
    ```bash
    python -m venv .venv
    ```
    * En Windows:
        ```bash
        .\.venv\Scripts\activate
        ```
    * En macOS/Linux:
        ```bash
        source ./.venv/bin/activate
        ```

3.  **Instalar Dependencias de Python**
    Primero, genera el archivo `requirements.txt` con las librerías que ya instalaste:
    ```bash
    pip freeze > requirements.txt
    ```
    Luego, instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar la Clave de API de Gemini**
    Crea un archivo llamado `.env` en la **raíz del proyecto** (al mismo nivel que `app.py`). Agrega la siguiente línea, reemplazando `TU_CLAVE_AQUI` con tu clave API real de Gemini:
    ```env
    GOOGLE_API_KEY=TU_CLAVE_AQUI
    ```
    **Importante:** No compartas este archivo `.env` si usas control de versiones (como Git). Es buena práctica añadir `.env` a tu archivo `.gitignore`.

5.  **Extraer los Datos del PDF**
    Ejecuta el script de extracción para generar el archivo `salarios_limpios_2025.csv`. Asegúrate de que el script (`extract_salaries.py`) esté configurado con la URL correcta del PDF y que Java esté instalado.
    ```bash
    python extract_salaries.py
    ```
    Verifica que el archivo `salarios_limpios_2025.csv` se haya creado correctamente en la raíz del proyecto.

6.  **Ejecutar la Aplicación Flask**
    Asegúrate de que tu entorno virtual aún esté activado. Ejecuta el archivo principal de la aplicación:
    ```bash
    python app.py
    ```

7.  **Acceder a la Aplicación**
    Abre tu navegador web y visita la dirección:
    ```
    [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
    ```
    (o la dirección que indique Flask en la terminal).

## Estructura del Proyecto

salario_cr_app/
├── .venv/                  # Entorno virtual
├── .env                    # Variables de entorno (ej: GOOGLE_API_KEY)
├── app.py                  # Aplicación principal Flask (Backend)
├── extract_salaries.py     # Script para extraer datos del PDF
├── requirements.txt        # Dependencias de Python
├── salarios_limpios_2025.csv # Datos extraídos y limpios
├── static/                 # Archivos estáticos (CSS, JS)
│   ├── style.css
│   └── script.js
└── templates/              # Archivos HTML
└── index.html

## Próximas Mejoras Potenciales

* Implementación de gráficos interactivos para visualizar tendencias o comparativas de salarios.
* Configuración de la tarea de actualización horaria (en el servidor) para re-ejecutar `extract_salaries.py` y verificar si hay un nuevo PDF o cambios (considerando que el PDF oficial se actualiza raramente de forma horaria).
* Mejorar la lógica de búsqueda (ej: búsqueda por rango salarial específico).
* Manejo más robusto de errores de extracción de PDF y errores de API.
* Contenedorización (Docker) para facilitar el despliegue.

---
*Este proyecto fue desarrollado como parte de un ejercicio de programación utilizando Python, JavaScript, CSS, HTML y la API de Gemini.*