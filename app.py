from flask import Flask, request, render_template, redirect
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['usuario']
    senha = request.form['senha']
    if usuario == 'admin' and senha == '1234':
        return redirect('/bemvindo')
    else:
        return '<h3>Usuário ou senha inválidos!</h3><a href="/">Tentar novamente</a>'

@app.route('/bemvindo')
def bemvindo():
    return render_template('bemvindo.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
