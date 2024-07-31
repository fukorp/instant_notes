import os
import subprocess
import sys
import venv
import webbrowser
import time

def create_venv():
    venv_dir = 'venv'
    if not os.path.exists(venv_dir):
        print("Création de l'environnement virtuel...")
        venv.create(venv_dir, with_pip=True)
    return venv_dir

def get_venv_python_path(venv_dir):
    if sys.platform == "win32":
        return os.path.join(venv_dir, 'Scripts', 'python.exe')
    return os.path.join(venv_dir, 'bin', 'python')

def install_dependencies(venv_dir):
    print("Installation des dépendances...")
    python_path = get_venv_python_path(venv_dir)
    subprocess.check_call([python_path, '-m', 'pip', 'install', 'selenium', 'webdriver-manager', 'flask', 'pandas'])
    print("Installation terminée.")

def run_app():
    from flask import Flask, jsonify, render_template, send_from_directory
    import pandas as pd
    from collections import defaultdict
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.edge.service import Service
    from selenium.webdriver.edge.options import Options
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    from datetime import datetime
    import glob

    app = Flask(__name__)

    def download_results(username, password):

        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        options = Options()
        options.add_experimental_option("prefs", {
            "download.default_directory": script_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True
        })
        
        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        
        wait = WebDriverWait(driver, 10)
        
        try:
            driver.get("https://webaurion.centralelille.fr/")
            wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
            password_elem = driver.find_element(By.ID, "password")
            password_elem.send_keys(password)
            password_elem.send_keys(Keys.RETURN)
            
            wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'ui-menuitem-link') and contains(., 'Résultats')]"))).click()
            wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'ui-menuitem-link') and contains(., 'ITEEM')]"))).click()
            wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'ui-menuitem-link') and contains(., 'aux épreuves')]"))).click()
            
            wait.until(EC.element_to_be_clickable((By.ID, "form:exportButton"))).click()
            wait.until(EC.element_to_be_clickable((By.ID, "form:j_idt170"))).click()
            
            wait.until(lambda driver: any(file.endswith('.csv') for file in os.listdir(script_dir)))
            
            old_file = max(glob.glob(os.path.join(script_dir, '*.csv')), key=os.path.getctime)
            new_filename = f"resultats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            new_file = os.path.join(script_dir, new_filename)
            os.rename(old_file, new_file)
            
            csv_files = glob.glob(os.path.join(script_dir, 'resultats_*.csv'))
            csv_files.sort(key=os.path.getctime, reverse=True)
            for file in csv_files[1:]:
                os.remove(file)
            
            print(f"Téléchargement terminé. Fichier sauvegardé : {new_filename}")
            return new_file
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            return None
        finally:
            driver.quit()
        
            csv_files = glob.glob('resultats_*.csv')
            for file in csv_files[:-1]:  # Garder seulement le plus récent
                os.remove(file)
            return csv_files[-1] if csv_files else None

    def load_and_process_csv(file_path):
        df = pd.read_csv(file_path, sep=';')
        modules = defaultdict(list)
        
        for _, row in df.iterrows():
            module = row['Module']
            note = {
                'epreuve': row['Épreuve'],
                'note': float(row['Notes']) if pd.notna(row['Notes']) else None,
                'coefficient': float(row["Coefficient de l'Épreuve dans le Module"]) if pd.notna(row["Coefficient de l'Épreuve dans le Module"]) else 1,
                'details': {
                    'type': row['Type de contrôle'],
                    'detail': row['Détail sur le contrôle'],
                    'debut': row['Début'],
                    'fin': row['Fin'],
                    'appreciation': row['Appréciation']
                }
            }
            modules[module].append(note)
        
        for module, notes in modules.items():
            total_weighted_score = sum(n['note'] * n['coefficient'] for n in notes if n['note'] is not None)
            total_coefficient = sum(n['coefficient'] for n in notes if n['note'] is not None)
            moyenne = total_weighted_score / total_coefficient if total_coefficient > 0 else None
            modules[module] = {
                'notes': notes,
                'moyenne': moyenne
            }
        
        return modules

    @app.route('/')
    def index():
        return send_from_directory('.', 'index.html')

    @app.route('/api/results')
    def get_results():
        csv_files = glob.glob('resultats_*.csv')
        if not csv_files:
            return jsonify({"error": "Aucun fichier de résultats trouvé"}), 404
        
        latest_file = max(csv_files, key=os.path.getctime)
        results = load_and_process_csv(latest_file)
        return jsonify(results)

    username = input("Entrez votre nom d'utilisateur : ")
    password = input("Entrez votre mot de passe : ")
    
    csv_file = download_results(username, password)
    
    if csv_file:
        print("Lancement du serveur Flask...")
        webbrowser.open('http://127.0.0.1:5000')  # Ouvre le navigateur automatiquement
        app.run(debug=True)
    else:
        print("Échec du téléchargement des résultats. L'application ne peut pas être lancée.")

if __name__ == "__main__":
    venv_dir = create_venv()
    install_dependencies(venv_dir)
    
    # Exécuter l'application dans l'environnement virtuel
    python_path = get_venv_python_path(venv_dir)
    script_path = os.path.abspath(__file__)
    os.environ['PYTHONPATH'] = os.path.dirname(script_path)
    
    subprocess.call([python_path, "-c", 
                     "from votre_script_principal import run_app; run_app()"])