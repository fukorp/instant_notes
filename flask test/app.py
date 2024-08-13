from flask import Flask, render_template
import csv
import codecs

import os
print("Répertoire de travail actuel :", os.getcwd())
app = Flask(__name__)
print("Fichiers dans le répertoire :")
for file in os.listdir(os.path.dirname(__file__)):
    print(file)

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

@app.route('/')
def display_grades():
    grades_data = read_csv_data()
    return render_template('grades.html', grades=grades_data)

if __name__ == '__main__':
    app.run(debug=True)