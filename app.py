import sqlite3
from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

# VULNÉRABILITÉ 1 (SECRET SCANNING) : Clé API codée en dur
# Les outils comme Gitleaks ou TruffleHog devraient détecter ceci.
STRIPE_API_KEY = "sk_live_51Mz9...CeCestUnFauxSecretPourLeTP..."


# Configuration de la base de données (pour la démo)
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    c.execute("INSERT INTO users VALUES ('admin', 'admin123')")
    conn.commit()
    conn.close()


@app.route('/')
def home():
    return "Bienvenue sur l'app vulnérable pour le TP Devoteam!"


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # VULNÉRABILITÉ 2 (SAST) : Injection SQL
    # Concaténation directe de chaîne. Les outils comme Snyk Code ou Bandit vont signaler ceci.
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        # Exécution non sécurisée
        c.execute(query)
        user = c.fetchone()
    except Exception as e:
        return str(e)
    finally:
        conn.close()

    if user:
        return "Connecté avec succès (Admin mode)!"
    else:
        return "Échec de connexion."


@app.route('/hello')
def hello():
    name = request.args.get('name', 'Guest')

    # VULNÉRABILITÉ 3 (SAST) : Cross-Site Scripting (XSS)
    # Rendu direct d'une entrée utilisateur sans échappement adéquat via render_template_string
    template = f'''
    <h1>Bonjour {name}!</h1>
    <p>Ceci est une page de test.</p>
    '''
    return render_template_string(template)


if __name__ == '__main__':
    init_db()
    # VULNÉRABILITÉ 4 (SAST) : Mode debug activé en production
    app.run(debug=True, host='127.0.0.1')