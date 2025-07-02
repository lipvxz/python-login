from flask import Flask, request, render_template, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['usuario']
    senha = request.form['senha']
    if usuario == 'admin' and senha == '1234':
        return render_template('bemvindo.html')
    else:
        return '<h3>Usuário ou senha inválidos!</h3><a href="/">Tentar novamente</a>'

if __name__ == '__main__':
    app.run(debug=True)
