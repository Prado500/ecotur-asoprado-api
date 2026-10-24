import os

# 1. Configuración de carpetas y archivos a ignorar (¡Muy importante para no saturar el TXT!)
IGNORE_DIRS = {
    '.git', '__pycache__', 'venv', 'env', '.venv', 
    'build', '.dart_tool', 'ios', 'android', 'web', 'windows', 'macos', 'linux',
    'node_modules', '.azure-pipelines', 'alembic', '.idea', '.dart_tool',
}

IGNORE_EXTS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', 
    '.pyc', '.ttf', '.lock', '.exe', '.dll', '.so', '.pdf', '.zip', '.idea', '.metadata', '.flutter-plugins-dependencies', 'analysis_options.yaml'
    'ecotur_app.iml'
}

def generate_context(root_dir, output_filename):
    if not os.path.exists(root_dir):
        print(f" Error: La ruta '{root_dir}' no existe.")
        return

    print(f" Generando contexto para: {root_dir}")
    
    with open(output_filename, 'w', encoding='utf-8') as out:
        out.write(f"ESTRUCTURA DEL PROYECTO: {os.path.basename(root_dir)}\n")
        out.write("="*60 + "\n\n")

        # 2. Generar el árbol de directorios
        for root, dirs, files in os.walk(root_dir):
            # Filtrar carpetas ignoradas in-place
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            level = root.replace(root_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            out.write(f"{indent} {os.path.basename(root)}/\n")
            
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                if not any(f.endswith(ext) for ext in IGNORE_EXTS):
                    out.write(f"{subindent} {f}\n")

        out.write("\n\n" + "="*60 + "\n")
        out.write("CÓDIGO FUENTE\n")
        out.write("="*60 + "\n\n")

        # 3. Leer e imprimir el contenido de cada archivo
        files_processed = 0
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for f in files:
                if any(f.endswith(ext) for ext in IGNORE_EXTS):
                    continue
                
                file_path = os.path.join(root, f)
                relative_path = os.path.relpath(file_path, root_dir)
                
                # Formato de título de ruta
                out.write(f"--- {relative_path} ---\n")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        out.write(infile.read())
                except Exception as e:
                    out.write(f"// [Error leyendo este archivo: {e}]\n")
                
                out.write("\n\n")
                files_processed += 1

    print(f" ¡Completado! Se empaquetaron {files_processed} archivos en '{output_filename}'.")

# ==========================================
# EJECUCIÓN (Cambia estas rutas por las tuyas)
# ==========================================
if __name__ == "__main__":
    # Ruta de tu Backend (Usa \\ o / dependiendo de Windows)
    BACKEND_PATH = r"C:\projects\ecotur-asoprado\.opencode"
    generate_context(BACKEND_PATH, "arbol_flujo_agéntico.txt")

 


