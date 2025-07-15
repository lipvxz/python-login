import sqlite3

conn = sqlite3.connect('usuarios.db')
cursor = conn.cursor()

cursor.execute("SELECT id, usuario FROM usuarios")
usuarios = cursor.fetchall()

if usuarios:
    print("👥 Usuários cadastrados:")
    for id, nome in usuarios:
        print(f"ID: {id} | Usuário: {nome}")
else:
    print("⚠️ Nenhum usuário cadastrado ainda.")

conn.close()
input("\nPressione Enter para fechar...")
