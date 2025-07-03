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
        return redirect('/invaliduser')

@app.route('/bemvindo')
def bemvindo():
    return render_template('bemvindo.html')

@app.route('/invaliduser')
def invalid_user():
    return render_template('invaliduser.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        # Aqui futuramente vamos salvar no banco
        return '<h3>Cadastro recebido!</h3><a href="/">Fazer login</a>'
    return render_template('register.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


