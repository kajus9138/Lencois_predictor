import requests

LOGIN_URL = "https://global.grupoconstruserv.eng.br/login"

def login(usuario, senha):
    session = requests.Session()

    payload = {
        "usuario": usuario,
        "senha": senha,
        "remember": "true",  # pode omitir se não quiser "manter conectado"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://global.grupoconstruserv.eng.br/index",
    }

    resp = session.post(LOGIN_URL, data=payload, headers=headers)
    
    # Testar se login deu certo
    if "Sair" in resp.text or "Logout" in resp.text or resp.url != LOGIN_URL:
        print("✅ Login bem-sucedido!")
        return session
    else:
        print("❌ Falha no login.")
        with open("login_erro.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        return None

if __name__ == "__main__":
    usuario = input("Usuário: ")
    senha = input("Senha: ")
    sess = login(usuario, senha)
    if sess:
        # A partir daqui, pode acessar páginas internas logado
        r = sess.get("https://global.grupoconstruserv.eng.br/index")
        print(r.status_code)
        # print(r.text)  # se quiser ver o HTML da página logada
