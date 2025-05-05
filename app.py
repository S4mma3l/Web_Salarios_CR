from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
import google.generativeai as genai
import re
from dotenv import load_dotenv # <--- Importar load_dotenv

# --- Cargar variables del archivo .env ---
load_dotenv() # <--- Llamar a la función para cargar las variables

app = Flask(__name__)

# --- Configuración de la API de Gemini ---
# Ahora os.getenv() leerá del archivo .env si la variable no está ya en el entorno del sistema
API_KEY = os.getenv('GOOGLE_API_KEY')

if not API_KEY:
    print("Error: La variable GOOGLE_API_KEY no se cargó desde el archivo .env ni está configurada en el entorno del sistema.")
    print("Asegúrate de tener un archivo .env en la raíz del proyecto con GOOGLE_API_KEY=TU_CLAVE.")
    # La aplicación puede seguir corriendo pero la función de análisis IA no funcionará.
else:
    genai.configure(api_key=API_KEY)
    print("API de Gemini configurada.")
    # Opcional: Prueba de conexión si la necesitas descomentar
    # try:
    #     model = genai.GenerativeModel('gemini-1.5-flash-latest')
    #     response = model.generate_content("Hello, world!")
    #     print("Conexión con Gemini exitosa.")
    # except Exception as e:
    #     print(f"Error al conectar con Gemini: {e}")
    #     API_KEY = None


# --- Cargar los datos del CSV ---
# La ruta al archivo CSV
csv_filepath = 'salarios_limpios_2025.csv'
salarios_df = pd.DataFrame() # Inicializamos un DataFrame vacío

# Función para cargar los datos (se ejecutará al iniciar la app)
def load_salaries_data():
    global salarios_df # Usamos la variable global
    if os.path.exists(csv_filepath):
        try:
            salarios_df = pd.read_csv(csv_filepath)
            print(f"Datos cargados desde {csv_filepath}. {salarios_df.shape[0]} registros.")
        except Exception as e:
            print(f"Error al cargar el archivo CSV {csv_filepath}: {e}")
            salarios_df = pd.DataFrame() # Asegurarse de que sea un DataFrame vacío en caso de error
    else:
        print(f"Archivo CSV no encontrado: {csv_filepath}. Ejecuta extract_salaries.py primero.")
        salarios_df = pd.DataFrame() # Asegurarse de que sea un DataFrame vacío

# Cargar los datos al iniciar la aplicación
load_salaries_data()


# --- Rutas de la Aplicación Flask ---

@app.route('/')
def index():
    """Sirve la página HTML principal."""
    return render_template('index.html')

@app.route('/salaries', methods=['GET'])
def get_salaries():
    """API que devuelve todos los datos de salarios o resultados de búsqueda."""
    # Aquí podrías añadir lógica para filtrar si la búsqueda se hiciera en el backend
    if not salarios_df.empty:
        return jsonify(salarios_df.to_dict(orient='records'))
    else:
        return jsonify([]), 404

@app.route('/analyze_position', methods=['POST'])
def analyze_position():
    """API que llama a Gemini para analizar un puesto."""
    if not API_KEY:
        return jsonify({"error": "La API de Gemini no está configurada en el servidor."}), 500

    data = request.get_json()
    job_title = data.get('job_title', '').strip()

    if not job_title:
        return jsonify({"error": "No se proporcionó un título de puesto para analizar."}), 400

    print(f"Solicitando análisis IA para el puesto: '{job_title}'")

    try:
        # --- Construir el Prompt para Gemini ---
        # Mantenemos el prompt igual, pidiendo las secciones, para guiar a Gemini a darnos el formato.
        prompt = f"""
        Analiza el puesto de trabajo "{job_title}" dentro del contexto del mercado laboral en Costa Rica.

        Proporciona la siguiente información:
        1.  **Conocimientos y Habilidades Sugeridas:** Lista los conocimientos técnicos y las habilidades blandas comunes o recomendadas para este puesto o roles similares. Sugiere posibles áreas de estudio, cursos o certificaciones relevantes.
        2.  **Opinión desde la Perspectiva de un Reclutador Profesional:** Imagina que eres un reclutador profesional especializado en el mercado de Costa Rica. Da una breve opinión sobre la relevancia del puesto, el nivel de demanda (si es posible inferirlo), y qué aspectos buscarías en un candidato para este rol, basándote en tu conocimiento general del mercado laboral y el puesto especificado.

        Formatea tu respuesta claramente, separando las dos secciones con los títulos exactos indicados (usando negritas y numeración). Sé conciso y profesional.
        """

        # --- Llamar a la API de Gemini ---
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)

        # Verificar si la respuesta contiene texto
        if not response.text:
             # Intentar con response.parts[0].text si response.text está vacío
             ai_analysis_text = ""
             if response.parts:
                 for part in response.parts:
                     if hasattr(part, 'text'):
                         ai_analysis_text += part.text + "\n" # Concatenar partes de texto

             if not ai_analysis_text.strip(): # Si sigue vacío después de intentar partes
                  return jsonify({"error": "La IA no pudo generar una respuesta de texto para este puesto.", "detail": str(response)}), 500


        # --- Procesar la respuesta de la IA (SIMPLIFICADO) ---
        # Ahora simplemente enviamos el texto completo recibido de la IA.
        ai_analysis_text = response.text if response.text else ai_analysis_text # Usar response.text si está disponible, sino lo de parts

        # Devolver la respuesta de la IA al frontend en formato JSON
        return jsonify({
            "success": True,
            "job_title": job_title,
            "analysis_text": ai_analysis_text # Enviamos el texto completo bajo una sola clave
        })

    except Exception as e:
        print(f"Error al llamar a la API de Gemini: {e}")
        import traceback
        traceback.print_exc()
        # Devolver un mensaje de error al frontend
        return jsonify({"error": "Error al obtener el análisis de la IA.", "detail": str(e)}), 500


# --- Punto de inicio para ejecutar la aplicación ---
if __name__ == '__main__':
    app.run(debug=True)