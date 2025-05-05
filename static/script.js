// Archivo script.js - Código completo actualizado

let allSalariesData = []; // Variable para almacenar todos los datos cargados

// Objeto para mapear siglas a su significado completo
const siglasSignificados = {
    "TONC": "Trabajador en Ocupación No Calificada",
    "TOSC": "Trabajador en Ocupación Semicalificada",
    "TOC": "Trabajador en Ocupación Calificada",
    "TOE": "Trabajador en Ocupación Especializada",
    "TES": "Trabajador de Especialización Superior",
    "TONCG": "Trabajador en Ocupación No Calificada (Genérico)",
    "TOSCG": "Trabajador en Ocupación Semicalificada (Genérico)",
    "TOCG": "Trabajador en Ocupación Calificada (Genérico)",
    "TMED": "Técnico Medio en Educación Diversificada",
    "TOEG": "Trabajador en Ocupación Especializada (Genérico)",
    "TEdS": "Técnico de Educación Superior",
    "DES": "Diplomado de Educación Superior",
    "Bach": "Bachiller Universitario", // Usamos 'Bach' como está en tu lista
    "Lic": "Licenciado Universitario"
    // Asegúrate de que las claves (las siglas) coincidan exactamente con los valores en tu CSV
};

// Función para obtener el significado de una sigla
function getSignificadoSigla(sigla) {
    // Buscar la sigla en nuestro objeto. Si no se encuentra, devolver la sigla original o 'N/A'.
    return siglasSignificados[sigla] || sigla || 'N/A';
}


// Función para cargar los datos desde la API del backend
async function loadSalaries() {
    const salariesListDiv = document.getElementById('salaries-list');
    salariesListDiv.innerHTML = '<p>Cargando datos...</p>'; // Mostrar mensaje de carga

    // Limpiar secciones de detalle y análisis al cargar (por si refresca con secciones abiertas)
    const detailsSection = document.getElementById('details-section');
    const jobDetailsDiv = document.getElementById('job-details');
    const analyzeButton = document.getElementById('analyze-button');
    const aiAnalysisResultDiv = document.getElementById('ai-analysis-result');

    detailsSection.style.display = 'none';
    jobDetailsDiv.innerHTML = '';
    analyzeButton.style.display = 'none';
    aiAnalysisResultDiv.style.display = 'none';
    aiAnalysisResultDiv.innerHTML = '';
    // Fin de limpieza inicial


    try {
        const response = await fetch('/salaries'); // Hacer petición a la API /salaries
        if (!response.ok) {
             if (response.status === 404) {
                 salariesListDiv.innerHTML = '<p>Archivo de datos de salarios no encontrado en el servidor.</p>';
                 console.error("Error: Archivo salarios_limpios_2025.csv no encontrado en el backend.");
             } else {
                throw new Error(`HTTP error! status: ${response.status}`);
             }
             allSalariesData = []; // Asegurar que esté vacío en caso de error
        } else {
            allSalariesData = await response.json(); // Guardar los datos en la variable global
            console.log("Datos cargados:", allSalariesData);

            if (allSalariesData.length === 0) {
                 salariesListDiv.innerHTML = '<p>No se encontraron datos de salarios.</p>';
            } else {
                displaySalaries(allSalariesData); // Mostrar todos los datos inicialmente
            }
        }

    } catch (error) {
        console.error("Error al cargar los salarios:", error);
        salariesListDiv.innerHTML = `<p>Error al cargar los datos: ${error.message}</p>`;
        allSalariesData = []; // Asegurar que esté vacío en caso de error
    }
}

// Función para mostrar una lista de salarios en el HTML
function displaySalaries(salariesToDisplay) {
    const salariesListDiv = document.getElementById('salaries-list');
    salariesListDiv.innerHTML = ''; // Limpiar lista actual

    if (salariesToDisplay.length === 0) {
        salariesListDiv.innerHTML = '<p>No hay resultados que coincidan con la búsqueda.</p>';
        return;
    }

    salariesToDisplay.forEach((salary, index) => { // Usamos index para un posible ID único si no hay otro
        const itemDiv = document.createElement('div');
        itemDiv.classList.add('salary-item');
        // Añadir un data attribute para identificar el puesto si es necesario
        itemDiv.dataset.index = index; // Usamos el índice como ID temporal

        // Obtener el significado completo de la sigla
        const significado = getSignificadoSigla(salary.Codigo);

        // Formato: Puesto (Código - Significado): Salario
        // Usamos toLocaleString para formatear el número del salario con separadores locales (¢ y .)
        itemDiv.innerHTML = `
            <strong>${salary.Puesto || 'N/A'}</strong> (${salary.Codigo || 'N/A'} - ${significado}): ¢${(salary.Salario || 0).toLocaleString('es-CR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
        `;
        itemDiv.addEventListener('click', () => showDetails(salary)); // Añadir evento click para mostrar detalles
        salariesListDiv.appendChild(itemDiv);
    });
}

// Función para manejar la búsqueda (client-side por ahora)
function handleSearch() {
    // --- Limpiar secciones de detalle y análisis al iniciar una nueva búsqueda ---
    const detailsSection = document.getElementById('details-section');
    const jobDetailsDiv = document.getElementById('job-details');
    const analyzeButton = document.getElementById('analyze-button');
    const aiAnalysisResultDiv = document.getElementById('ai-analysis-result');

    detailsSection.style.display = 'none'; // Ocultar la sección completa de detalles
    jobDetailsDiv.innerHTML = ''; // Limpiar el contenido de los detalles
    analyzeButton.style.display = 'none'; // Ocultar el botón de análisis IA
    aiAnalysisResultDiv.style.display = 'none'; // Ocultar el área de resultados IA
    aiAnalysisResultDiv.innerHTML = ''; // Limpiar el contenido del análisis IA
    // --- Fin de limpieza ---


    const searchInput = document.getElementById('search-input');
    const searchTerm = searchInput.value.toLowerCase(); // Obtener el texto de búsqueda en minúsculas

    // Filtrar los datos cargados basados en el término de búsqueda
    const filteredSalaries = allSalariesData.filter(salary => {
        // Asegurarse de que las propiedades existen y convertir a minúsculas o string
        const puesto = (salary.Puesto || '').toLowerCase();
        const codigo = (salary.Codigo || '').toLowerCase();
        // Obtener el significado completo también para incluirlo en la búsqueda
        const significado = getSignificadoSigla(salary.Codigo).toLowerCase();

        // Convertir salario a string para poder buscar (manejar posibles NaN o null)
        const salario = (salary.Salario || '').toString().toLowerCase();


        // Buscar el término en cualquiera de las columnas relevantes (Puesto, Código, Significado, Salario)
        // También limpiamos el término de búsqueda si tiene '¢' o '.'/' de miles para compararlo mejor con la cadena del salario
        const searchTermCleaned = searchTerm.replace('¢', '').replace('.', '').replace(',', '.'); // Ajuste para búsqueda numérica/con formato


        return puesto.includes(searchTerm) ||
               codigo.includes(searchTerm) ||
               significado.includes(searchTerm) || // <--- Incluir búsqueda por significado
               salario.includes(searchTermCleaned);
    });

    displaySalaries(filteredSalaries); // Mostrar los resultados filtrados
}

// Función para mostrar detalles de un puesto seleccionado
function showDetails(salary) {
    const detailsSection = document.getElementById('details-section');
    const jobDetailsDiv = document.getElementById('job-details');
    const analyzeButton = document.getElementById('analyze-button');
    const aiAnalysisResultDiv = document.getElementById('ai-analysis-result'); // Get the AI result div

    // Mostrar la sección de detalles
    detailsSection.style.display = 'block';
    aiAnalysisResultDiv.style.display = 'none'; // Ocultar resultado IA previo
     aiAnalysisResultDiv.innerHTML = ''; // Limpiar contenido resultado IA previo


    // Obtener el significado completo de la sigla para los detalles
    const significado = getSignificadoSigla(salary.Codigo);

    // Llenar los detalles del puesto seleccionado, incluyendo el significado
     jobDetailsDiv.innerHTML = `
        <p><strong>Puesto:</strong> ${salary.Puesto || 'N/A'}</p>
        <p><strong>Código:</strong> ${salary.Codigo || 'N/A'}</p>
        <p><strong>Significado:</strong> ${significado}</p> {# Línea para el significado #}
        <p><strong>Salario:</strong> ¢${(salary.Salario || 0).toLocaleString('es-CR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
        `;

    // Configurar y mostrar el botón de análisis IA
    analyzeButton.style.display = 'block';
    // Guardar el puesto en un data attribute del botón para pasarlo a la función de análisis
    analyzeButton.dataset.jobTitle = salary.Puesto;


    // Opcional: Scroll suave hacia la sección de detalles
    detailsSection.scrollIntoView({ behavior: 'smooth' });
}

// Función para llamar al backend y obtener el análisis IA de un puesto
async function analyzePositionWithAI(jobTitle) {
    const aiAnalysisResultDiv = document.getElementById('ai-analysis-result');
    const analyzeButton = document.getElementById('analyze-button');

    // Mostrar área de resultados y estado de carga
    aiAnalysisResultDiv.style.display = 'block';
    aiAnalysisResultDiv.innerHTML = '<p>Solicitando análisis a la IA...</p>';
    analyzeButton.disabled = true; // Deshabilitar botón mientras analiza

    try {
        const response = await fetch('/analyze_position', {
            method: 'POST', // Usamos POST para enviar el título del puesto en el body
            headers: {
                'Content-Type': 'application/json', // Indicamos que enviamos JSON
            },
            body: JSON.stringify({ job_title: jobTitle }) // Enviamos el título del puesto como JSON
        });

        // Verificar si la petición fue exitosa
        if (!response.ok) {
            // Intentar leer el JSON de error del backend si está disponible
            const errorBody = await response.text(); // Leer como texto primero
            let errorDetail = errorBody;
             try {
                 const errorJson = JSON.parse(errorBody);
                 errorDetail = errorJson.error || errorBody;
             } catch (e) {
                 // No es JSON, usar el texto plano
             }
            throw new Error(`Error del servidor: ${response.status} - ${errorDetail}`);
        }

        // Parsear la respuesta JSON del backend
        const result = await response.json();
        console.log("Resultado análisis IA:", result);

        // Mostrar el resultado del análisis IA
        if (result.success) {
             // Esperamos la clave 'analysis_text' con la respuesta completa de la IA
             const analysisText = result.analysis_text || 'No se recibió texto de análisis.';

             // --- Usar marked.js para convertir el texto Markdown a HTML ---
             const analysisHTML = marked.parse(analysisText);

             aiAnalysisResultDiv.innerHTML = `
                 <h3>Análisis IA para "${result.job_title || 'Puesto'}"</h3>
                 <div class="ai-analysis-content">${analysisHTML}</div> {# Usar el HTML generado por marked.js #}
             `;
             // --- Fin de uso de marked.js ---

        } else {
            // Si la respuesta del backend indica un error pero success es false
            aiAnalysisResultDiv.innerHTML = `<p style="color: red;">Error en el análisis IA: ${result.error || 'Error desconocido en la respuesta del servidor.'}</p>`;
        }

    } catch (error) {
        // Capturar errores de red o errores lanzados por la verificación response.ok
        console.error("Error al obtener análisis IA:", error);
        aiAnalysisResultDiv.innerHTML = `<p style="color: red;">Error al conectar o procesar la respuesta de la IA: ${error.message}</p>`;
    } finally {
        // Este bloque se ejecuta siempre, tanto si hay éxito como si hay error
        analyzeButton.disabled = false; // Re-habilitar el botón
    }
}


// --- Event Listeners ---
// Esperar a que el DOM esté completamente cargado antes de ejecutar el script
document.addEventListener('DOMContentLoaded', () => {
    // Cargar los datos de salarios al cargar la página
    loadSalaries();

    // Configurar el evento 'input' para la barra de búsqueda
    const searchInput = document.getElementById('search-input');
    // 'input' es mejor que 'change' para filtrar en tiempo real al escribir
    searchInput.addEventListener('input', handleSearch);

    // Configurar el evento 'click' para el botón de análisis IA
    const analyzeButton = document.getElementById('analyze-button');
    analyzeButton.addEventListener('click', (event) => {
        // Obtener el título del puesto que guardamos en el data attribute del botón
        const jobTitle = event.target.dataset.jobTitle;
        if (jobTitle) {
            // Llamar a la función que maneja el análisis IA
            analyzePositionWithAI(jobTitle);
        } else {
            // Si por alguna razón no hay título guardado, mostrar un mensaje
             const aiAnalysisResultDiv = document.getElementById('ai-analysis-result');
             aiAnalysisResultDiv.innerHTML = '<p style="color: orange;">No se pudo determinar el puesto a analizar.</p>';
             aiAnalysisResultDiv.style.display = 'block';
        }
    });
});