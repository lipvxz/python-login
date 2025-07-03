from flask import Flask, request, render_template, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os

app = Flask(__name__)
app.secret_key = 'lipin_super_secreto'  # Esta linha vem logo DEPOIS de app = Flask(__name__)

# Conexão com PostgreSQL (substitua a senha quando estiver disponível)
conn = psycopg2.connect(
    host="dpg-d1jf4cbe5dus73fs606g-a.oregon-postgres.render.com",
    port="5432",
    database="login_flask_db",
    user="login_flask_db_user",
    password="DB_PASSWORD"
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL
)
""")
conn.commit()


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = generate_password_hash(request.form['senha'])

        try:
            cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, senha))
            conn.commit()
            return redirect('/')
        except psycopg2.Error as e:
            conn.rollback()
            return f"Erro ao cadastrar: {e.pgerror}"

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        cursor.execute("SELECT id, nome, email, senha, is_admin FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()

        if usuario and check_password_hash(usuario[3], senha):
            session['usuario_id'] = usuario[0]
            session['usuario_nome'] = usuario[1]
            session['is_admin'] = usuario[4]
            return redirect('/bemvindo')  # ou qualquer rota protegida que você tenha
        else:
            return render_template('invaliduser.html')


    return render_template('login.html')


@app.route('/bemvindo')
def bemvindo():
    if 'usuario_id' in session:
        return render_template(
            'bemvindo.html',
            usuario=session['usuario_nome'],
            is_admin=session.get('is_admin', False)
        )
    else:
        return redirect('/')



@app.route('/invaliduser')
def invalid_user():
    return render_template('invaliduser.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    session.pop('usuario_nome', None)
    return redirect('/')

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect('/')
    
    cursor.execute("SELECT nome, email FROM usuarios")
    usuarios = cursor.fetchall()
    return render_template('admin.html', usuarios=usuarios)

cursor.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE")
conn.commit()

cursor.execute("UPDATE usuarios SET is_admin = TRUE WHERE email = 'filipematos1821@email.com'")
conn.commit()

# Criação da tabela (se ainda não existir)
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL
)
""")
conn.commit()

# Adiciona a coluna is_admin se ainda não existir
cursor.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE")
conn.commit()

@app.route('/debug_admin')
def debug_admin():
    cursor.execute("SELECT nome, email, is_admin FROM usuarios")
    usuarios = cursor.fetchall()
    html = "<h2>🔍 Debug de Admins</h2><ul>"
    for nome, email, is_admin in usuarios:
        html += f"<li>{nome} — {email} — is_admin: {is_admin}</li>"
    html += "</ul>"
    return html

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


