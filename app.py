from flask import Flask, request, render_template, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os
from dotenv import load_dotenv
from flask_mail import Mail, Message
from reset_token import generate_token, confirm_token
import bcrypt

# Carrega variáveis do .env
load_dotenv()

# Inicializa o app Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# Configurações de e-mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")
mail = Mail(app)


# Função utilitária para obter conexão e cursor do banco
def get_db():
    conn = psycopg2.connect(
        host="dpg-d1jf4cbe5dus73fs606g-a.oregon-postgres.render.com",
        port="5432",
        database="login_flask_db",
        user="login_flask_db_user",
        password=os.environ.get("DB_PASSWORD")
    )
    return conn, conn.cursor()

# Criação da tabela e coluna admin (executa só se conseguir conectar)
try:
    conn, cursor = get_db()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )
    """)
    cursor.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE")
    cursor.execute("UPDATE usuarios SET is_admin = TRUE WHERE email = 'filipematos1821@gmail.com'")
    conn.commit()
    cursor.close()
    conn.close()
except Exception as e:
    print(f"[AVISO] Não foi possível conectar ao banco para criar tabela: {e}")

# Rotas
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
            conn, cursor = get_db()
            cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, senha))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/')
        except psycopg2.Error as e:
            return f"Erro ao cadastrar: {e.pgerror}"

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        try:
            conn, cursor = get_db()
            cursor.execute("SELECT id, nome, email, senha, is_admin FROM usuarios WHERE email = %s", (email,))
            usuario = cursor.fetchone()
            cursor.close()
            conn.close()
        except Exception as e:
            return f"Erro ao conectar ao banco: {e}"

        if usuario and check_password_hash(usuario[3], senha):
            session['usuario_id'] = usuario[0]
            session['usuario_nome'] = usuario[1]
            session['is_admin'] = usuario[4]
            return redirect('/bemvindo')
        else:
            return render_template('invaliduser.html')

    return render_template('login.html')

@app.route('/bemvindo')
def bemvindo():
    if 'usuario_id' in session:
        return render_template('bemvindo.html', usuario=session['usuario_nome'], is_admin=session.get('is_admin', False))
    return redirect('/')

@app.route('/invaliduser')
def invalid_user():
    return render_template('invaliduser.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect('/')
    try:
        conn, cursor = get_db()
        cursor.execute("SELECT nome, email FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        return f"Erro ao conectar ao banco: {e}"
    return render_template('admin.html', usuarios=usuarios)

@app.route('/debug_admin')
def debug_admin():
    try:
        conn, cursor = get_db()
        cursor.execute("SELECT nome, email, is_admin FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        return f"Erro ao conectar ao banco: {e}"
    html = "<h2>🔍 Debug de Admins</h2><ul>"
    for nome, email, is_admin in usuarios:
        html += f"<li>{nome} — {email} — is_admin: {is_admin}</li>"
    html += "</ul>"
    return html

@app.route('/promover_admin')
def promover_admin():
    if 'usuario_id' not in session:
        return redirect('/')
    try:
        conn, cursor = get_db()
        cursor.execute("UPDATE usuarios SET is_admin = TRUE WHERE id = %s", (session['usuario_id'],))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        return f"Erro ao conectar ao banco: {e}"
    return "✅ Você agora é admin! Faça logout e login novamente."

@app.route('/forcar_admin')
def forcar_admin():
    try:
        conn, cursor = get_db()
        cursor.execute("UPDATE usuarios SET is_admin = TRUE WHERE email = 'filipematos1821@gmail.com'")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        return f"Erro ao conectar ao banco: {e}"
    return "✅ Conta promovida a admin com sucesso!"

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        token = generate_token(email)
        link = url_for('reset_password', token=token, _external=True)
        msg = Message("Redefina sua senha", recipients=[email])
        msg.body = f"Clique no link para redefinir sua senha: {link}"
        mail.send(msg)
        return "E-mail enviado com sucesso!"
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = confirm_token(token)
    if not email:
        return "Token inválido ou expirado."
    if request.method == 'POST':
        nova_senha = request.form['senha']
        hash_senha = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())
        try:
            conn, cursor = get_db()
            cursor.execute("UPDATE usuarios SET senha = %s WHERE email = %s", (hash_senha, email))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            return f"Erro ao conectar ao banco: {e}"
        return "Senha atualizada com sucesso!"
    return render_template('reset_password.html')

from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config.get('SECURITY_PASSWORD_SALT', 'email-reset'))

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config.get('SECURITY_PASSWORD_SALT', 'email-reset'),
            max_age=expiration
        )
    except Exception:
        return False
    return email
# Inicia o servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
