import requests
import pandas as pd
import tabula
import os
import re # Importar módulo de expresiones regulares para limpiar salario

# URL del PDF oficial
pdf_url = "https://www.mtss.go.cr/temas-laborales/salarios/Documentos-Salarios/lista_salarios_2025.pdf"
pdf_filename = "lista_salarios_2025.pdf"

# Lista de códigos/categorías válidos que queremos extraer
# Asegúrate de que esta lista esté completa según el PDF
codigos_validos = [
    'TONC', 'TOSC', 'TOC', 'TOE', 'TES', 'TONCG', 'TOSCG', 'TOCG',
    'TMED', 'TOEG', 'TEdS', 'DES', 'Bach', 'Lic'
]

# --- Descargar el PDF (esta parte sigue igual) ---
print(f"Descargando el PDF de: {pdf_url}")
try:
    response = requests.get(pdf_url, stream=True)
    response.raise_for_status() # Lanza una excepción si la petición falla

    with open(pdf_filename, 'wb') as pdf_file:
        for chunk in response.iter_content(chunk_size=8192):
            pdf_file.write(chunk)

    print(f"PDF descargado exitosamente como: {pdf_filename}")

except requests.exceptions.RequestException as e:
    print(f"Error al descargar el PDF: {e}")
    # Si el archivo ya existe y no se pudo descargar de nuevo, podemos intentar continuar
    # asumiendo que el PDF existente es el correcto. Manejo básico:
    if not os.path.exists(pdf_filename):
         exit()
    else:
         print("Usando el archivo PDF existente.")


# --- Extraer tablas del PDF usando tabula-py ---
print(f"Intentando extraer tablas de: {pdf_filename}")

# Lista para almacenar los datos limpios extraídos
clean_records = []

try:
    # Usamos la configuración que "funcionó" para extraer las tablas anchas y desordenadas.
    # Si la extracción con área hubiera funcionado mejor, usaríamos esa configuración aquí.
    # Dado el output anterior, trabajaremos con el resultado de esta llamada:
    tables = tabula.read_pdf(
        pdf_filename,
        pages='all', # Extraer de todas las páginas
        multiple_tables=True, # Buscar múltiples tablas por página (aunque encontró solo 2 grandes)
        stream=True, # Usar modo stream
        # area=[...] # Si definiste áreas que mejoran la extracción, úsalas aquí en lugar de 'all' pages
        # lattice=True # Si stream=True no funciona, prueba con lattice=True
    )

    print(f"Se encontraron {len(tables)} DataFrames iniciales (posiblemente desordenados).")

    # --- Procesar y limpiar cada DataFrame extraído ---
    for i, table in enumerate(tables):
        print(f"Procesando DataFrame {i+1} con {table.shape[0]} filas y {table.shape[1]} columnas.")

        # Renombrar columnas para trabajar más fácil (aunque los nombres originales sean feos)
        table.columns = [f'col_{j}' for j in range(table.shape[1])]

        # Recorrer cada fila del DataFrame
        for index, row in table.iterrows():
            # Recorrer las columnas en bloques de 3 (Puesto, Código, Salario)
            for col_index in range(0, len(row), 3):
                # Asegurarse de que hay al menos 3 columnas más para un bloque Puesto/Código/Salario
                if col_index + 2 < len(row):
                    # Extraer los posibles Puesto, Código y Salario
                    posible_puesto = row[col_index]
                    posible_codigo = row[col_index + 1]
                    posible_salario = row[col_index + 2]

                    # Validar si el posible código está en nuestra lista de códigos válidos
                    # y si el puesto no está vacío
                    if pd.notna(posible_codigo) and str(posible_codigo).strip() in codigos_validos and pd.notna(posible_puesto):
                        # Si es válido, añadir a nuestra lista de registros limpios
                        clean_records.append({
                            'Puesto_Raw': posible_puesto, # Guardamos el raw para limpieza posterior
                            'Codigo': str(posible_codigo).strip(),
                            'Salario_Raw': posible_salario # Guardamos el raw para limpieza posterior
                        })
                    # else:
                        # print(f"Saltando bloque (índice {col_index}) por código/puesto no válido: Codigo='{posible_codigo}', Puesto='{posible_puesto}'")


    # --- Crear un nuevo DataFrame con los registros limpios ---
    raw_cleaned_df = pd.DataFrame(clean_records)

    if raw_cleaned_df.empty:
        print("\nNo se extrajeron registros válidos con los códigos especificados.")
    else:
        print(f"\nSe extrajeron {raw_cleaned_df.shape[0]} registros potenciales.")
        print("--- Primeros registros limpios (antes de limpieza final de columnas) ---")
        print(raw_cleaned_df.head())
        print(f"Columnas iniciales limpias: {raw_cleaned_df.columns.tolist()}")

        # --- Limpieza final de columnas Puesto y Salario ---

        # Limpiar la columna 'Puesto_Raw' (eliminar espacios extra, saltos de línea, etc.)
        raw_cleaned_df['Puesto'] = raw_cleaned_df['Puesto_Raw'].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True) # Eliminar espacios múltiples y saltos de línea
        raw_cleaned_df = raw_cleaned_df.drop(columns=['Puesto_Raw']) # Eliminar columna raw

        # Limpiar la columna 'Salario_Raw' (eliminar '¢', comas, espacios, convertir a número)
        def clean_salary(salario_str):
            if pd.isna(salario_str):
                return None
            salario_str = str(salario_str).strip()
            salario_str = salario_str.replace('¢', '').replace('.', '').replace(',', '.') # Reemplazar ',' por '.' si es el separador decimal
            # Usar regex para encontrar un número (int o float)
            match = re.search(r'[\d\.]+', salario_str)
            if match:
                 try:
                     return float(match.group(0))
                 except ValueError:
                     return None
            return None # Retornar None si no se encuentra un número válido

        raw_cleaned_df['Salario'] = raw_cleaned_df['Salario_Raw'].apply(clean_salary)
        raw_cleaned_df = raw_cleaned_df.drop(columns=['Salario_Raw']) # Eliminar columna raw

        # Reordenar columnas y eliminar filas con salario no válido si hubo error en conversión
        final_salarios_df = raw_cleaned_df[['Puesto', 'Codigo', 'Salario']].dropna(subset=['Salario']).reset_index(drop=True)


        print("\n--- DataFrame Final de Salarios Limpios ---")
        print(final_salarios_df.head(10))
        print(f"\nTotal de registros finales válidos: {final_salarios_df.shape[0]}")
        print(f"Columnas finales: {final_salarios_df.columns.tolist()}")

        # Guardar el DataFrame limpio a un archivo CSV
        final_salarios_df.to_csv("salarios_limpios_2025.csv", index=False)
        print("\nDatos limpios guardados en salarios_limpios_2025.csv")


except Exception as e:
    print(f"Error durante la extracción o procesamiento inicial: {e}")
    import traceback
    traceback.print_exc()
    print("\nVerifica la estructura del PDF o los parámetros de extracción/limpieza.")


# --- Limpieza del archivo PDF descargado (opcional) ---
# if os.path.exists(pdf_filename):
#    os.remove(pdf_filename)
#    print(f"\nArchivo {pdf_filename} eliminado.")