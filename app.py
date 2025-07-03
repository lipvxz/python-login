from flask import Flask, request, render_template, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'lipin_super_secreto'  # Esta linha vem logo DEPOIS de app = Flask(__name__)


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['usuario']
    senha = request.form['senha']

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute("SELECT senha FROM usuarios WHERE usuario = ?", (usuario,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado and check_password_hash(resultado[0], senha):
        session['usuario'] = usuario  # Salva o nome do usuário na sessão
        return redirect('/bemvindo')
    else:
        return redirect('/invaliduser')



@app.route('/bemvindo')
def bemvindo():
    if 'usuario' in session:
        return render_template('bemvindo.html', usuario=session['usuario'])
    else:
        return redirect('/')


@app.route('/invaliduser')
def invalid_user():
    return render_template('invaliduser.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        senha_hash = generate_password_hash(senha)

        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha_hash))
            conn.commit()
            return '<h3>✅ Cadastro realizado com sucesso!</h3><a href="/">Fazer login</a>'
        except sqlite3.IntegrityError:
            return '<h3>❌ Usuário já existe!</h3><a href="/register">Tentar outro</a>'
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


