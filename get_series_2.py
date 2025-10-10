import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- Configurações ---
LOGIN_URL = "https://global.grupoconstruserv.eng.br/login"
FORM_URL = "https://global.grupoconstruserv.eng.br/telemetria/geral/downloads_form"
DOWNLOAD_URL = "https://global.grupoconstruserv.eng.br/telemetria/geral/downloads"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0"

# --- Login ---
def login(usuario, senha):
    sess = requests.Session()
    sess.headers.update({"User-Agent": UA})
    payload = {"usuario": usuario, "senha": senha, "remember": "true"}
    headers = {"Referer": "https://global.grupoconstruserv.eng.br/index"}
    resp = sess.post(LOGIN_URL, data=payload, headers=headers)
    if "Sair" in resp.text or "Logout" in resp.text or resp.url != LOGIN_URL:
        print("✅ Login bem-sucedido!")
        return sess
    else:
        print("❌ Falha no login.")
        with open("login_erro.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        return None

# --- Extrair campos do formulário ---
def extrair_campos(sess):
    resp = sess.get(FORM_URL)
    soup = BeautifulSoup(resp.text, "html.parser")
    form = soup.find("form", {"id": "form_varias"})
    payload = {}

    # inputs (hidden, text, radios)
    for inp in form.find_all("input"):
        name = inp.get("name")
        if not name:
            continue
        if inp.get("type") in ["radio", "checkbox"]:
            if inp.has_attr("checked"):
                payload[name] = inp.get("value")
        else:
            payload[name] = inp.get("value", "")

    # selects múltiplos
    for sel in form.find_all("select"):
        name = sel.get("name")
        if not name:
            continue
        options = sel.find_all("option")
        # seleciona todos os que já estão selected
        valores = [opt.get("value") for opt in options if opt.has_attr("selected")]
        # se nenhum, pega todos (para horários)
        if not valores and sel.has_attr("multiple"):
            valores = [opt.get("value") for opt in options]
        payload[name] = valores if sel.has_attr("multiple") else valores[0] if valores else ""

    return payload

# --- Baixar Excel ---
def baixar_excel(sess, data_ini, data_fim, usinas_ids=None):
    payload = extrair_campos(sess)

    # sobrescrever datas e estações
    payload["data_ini"] = data_ini
    payload["data_fim"] = data_fim
    if usinas_ids:
        payload["usinas[]"] = usinas_ids

    headers = {
        "User-Agent": UA,
        "Referer": FORM_URL,
        "Origin": "https://global.grupoconstruserv.eng.br",
    }

    resp = sess.post(DOWNLOAD_URL, data=payload, headers=headers, stream=True)

    if resp.status_code == 200 and "application/vnd.ms-excel" in resp.headers.get("Content-Type", ""):
        cd = resp.headers.get("Content-Disposition", "")
        if "filename=" in cd:
            filename = cd.split("filename=")[-1].strip('"')
        else:
            filename = f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xls"

        with open(filename, "wb") as f:
            for chunk in resp.iter_content(8192):
                if chunk:
                    f.write(chunk)
        print(f"✅ Arquivo baixado: {filename}")
    else:
        print("❌ Erro ao baixar. Status:", resp.status_code)
        with open("erro_download.html", "wb") as f:
            f.write(resp.content)

# --- Main ---
if __name__ == "__main__":
    usuario = input("Usuário: ")
    senha = input("Senha: ")
    sess = login(usuario, senha)
    if sess:
        data_ini = input("Data inicial (DD/MM/YYYY): ")
        data_fim = input("Data final (DD/MM/YYYY): ")
        # IDs das estações que deseja baixar
        usinas = ["1882"]
        baixar_excel(sess, data_ini, data_fim, usinas_ids=usinas)
