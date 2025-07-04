from app import app

# Render executa esse arquivo, então o app precisa rodar aqui
if __name__ != "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
