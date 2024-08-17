import os
import subprocess
import sys
import venv

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



def check_and_install_dependencies():
    venv_dir = create_venv()
    install_dependencies(venv_dir)
    python_path = get_venv_python_path(venv_dir)
    os.environ['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))
    return python_path

if __name__ == "__main__":
    python_path = check_and_install_dependencies()
    subprocess.call([python_path, "-c",
                     "from main import run_app; run_app()"])
else:
    print("ESLLZAFAZFLKZA?PFN?")
    from flask import Flask, render_template, send_from_directory, jsonify
    import csv
    import codecs
    import os
    import glob
    import webbrowser
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.edge.service import Service
    from selenium.webdriver.edge.options import Options
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    from datetime import datetime
    

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
    driver.maximize_window()
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


def detect_delimiter(file_path):
    with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        first_line = file.readline()
        if ',' in first_line:
            return ','
        elif ';' in first_line:
            return ';'
        elif '\t' in first_line:
            return '\t'
    return None

def read_csv_data():
    grades = []
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'grades.csv')
        delimiter = detect_delimiter(file_path)
        if not delimiter:
            print("Impossible de détecter le séparateur du CSV.")
            return grades

        with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            csv_reader = csv.DictReader(file, delimiter=delimiter)
            for row in csv_reader:
                grades.append(row)

        print(f"Nombre de lignes lues : {len(grades)}")
        if grades:
            print("Exemple de première ligne :")
            print(grades[0])
        else:
            print("Aucune donnée n'a été lue du fichier CSV.")

    except FileNotFoundError:
        print("Le fichier grades.csv n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture du fichier : {e}")
    return grades

from flask import Flask, render_template, send_from_directory, jsonify

app = Flask(__name__)

@app.route('/')
def display_grades():
    grades_data = read_csv_data()
    return render_template('grades.html', grades=grades_data)

def run_app():
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
    python_path = check_and_install_dependencies()
    subprocess.call([python_path, "-c",
                     "from main import run_app; run_app()"])
