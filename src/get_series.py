import requests
from bs4 import BeautifulSoup

LOGIN_URL = "https://global.grupoconstruserv.eng.br/login"

def baixar_dados(sess):
    print("Iniciando download...")
    
    # 1. ACESSAR A PÁGINA DO FORMULÁRIO E EXTRAIR CAMPOS OCULTOS
    url_form = "https://global.grupoconstruserv.eng.br/telemetria/geral/downloads_form"
    print(f"1. Acessando o formulário em: {url_form}")
    
    # É vital fazer um GET para a página que contém o formulário antes de tentar o POST.
    form_resp = sess.get(url_form)
    
    if not form_resp.ok:
        print(f"❌ Falha ao carregar a página do formulário: {form_resp.status_code}")
        return

    # Usar BeautifulSoup para analisar o HTML do formulário
    soup = BeautifulSoup(form_resp.text, 'html.parser')
    
    # Tenta encontrar o campo oculto (CSRF token) dentro do formulário id="form_varias"
    # O nome do campo oculto pode variar, mas geralmente é "csrf_token_name" ou similar.
    # Vamos buscar todos os inputs hidden no formulário.
    form_data = {}
    form_varias = soup.find('form', {'id': 'form_varias'})
    
    if form_varias:
        # Extrai todos os campos ocultos, incluindo o token CSRF, se existir.
        hidden_inputs = form_varias.find_all('input', {'type': 'hidden'})
        for tag in hidden_inputs:
            # Garante que o input tem name e value
            if tag.get('name') and tag.get('value'):
                 form_data[tag.get('name')] = tag.get('value')
                 print(f"   => Encontrado campo oculto: {tag.get('name')}: {tag.get('value')[:20]}...")
    else:
        print("⚠️ Atenção: Não foi encontrado o formulário #form_varias. Tentando mesmo assim.")
        
    
    # URL de POST continua a mesma
    url_export = "https://global.grupoconstruserv.eng.br/telemetria/geral/downloads"

    # Seus parâmetros de download
    payload_download = {
        "usinas[]": ["1882", "1600"],
        "data_ini": "01/09/2025",
        "data_fim": "30/09/2025",
        "hora_ini": "00:00",
        "horarios[]": [str(i) for i in range(24)],
        "formato": "xls",
        "campos[]": [
            "preciptacao", "nivel", "vazao", "cotareal",
            "vazao_afluente", "vazao_defluente",
        ],
        "soma": "H",
        "subtotal": "N",
        "totalGeral": "S"
    }
    
    # COMBINAR: Adiciona campos ocultos ao payload de download
    payload_final = {**form_data, **payload_download} # Combina os dois dicionários

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": url_form, # O referer deve ser a página onde o formulário foi pego
    }

    print("2. Enviando POST de download com dados combinados e Referer do formulário.")
    resp = sess.post(url_export, data=payload_final, headers=headers)
    
    # ----------------------------------------------------
    # PASSO 3: Verificação de Sucesso (Download)
    # ----------------------------------------------------
    if resp.ok and "Content-Disposition" in resp.headers:
        # Lógica de salvar arquivo (mantida do código anterior)
        try:
            filename = resp.headers["Content-Disposition"].split("filename=")[-1].strip('"')
            if not filename.lower().endswith('.xls'):
                 filename += '.xls'
        except:
            filename = "dados_baixados.xls"

        with open(filename, "wb") as f:
            f.write(resp.content)
        print(f"✅ Arquivo baixado com sucesso: {filename}")
        
    else:
        print("❌ Erro ao baixar o arquivo. Resposta final não contém o arquivo.")
        print(f"Status Code: {resp.status_code}")
        
        # Se for um redirecionamento, a resposta será HTML (text/html) e não terá Content-Disposition.
        if 'Refresh' in resp.headers:
            print("❌ O servidor ainda está enviando um 'Refresh'. O token CSRF não resolveu ou o formulário exige JS.")
            
        with open("erro_download_csrf.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        print("Salvo HTML em 'erro_download_csrf.html' para debug final.")

def login(usuario, senha):
    session = requests.Session()
    # A primeira requisição para a página de login pode ser necessária
    # para obter um token de segurança (CSRF token), mas tentaremos sem primeiro.
    # Se falhar, precisaremos adicionar a captura do token.
    
    payload = {
        "usuario": usuario,
        "senha": senha,
        "remember": "true",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": LOGIN_URL, # Usando a própria URL de login como referer
    }

    resp = session.post(LOGIN_URL, data=payload, headers=headers)
    
    # Testar se login deu certo (procurando por algo que só aparece logado ou verificando redirecionamento)
    if "Sair" in resp.text or "Logout" in resp.text or resp.url != LOGIN_URL:
        print("✅ Login bem-sucedido!")
        return session
    else:
        print("❌ Falha no login.")
        with open("login_erro.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        print("Salvo HTML da página de resposta em 'login_erro.html' para debug.")
        return None

if __name__ == "__main__":
    usuario = input("Usuário: ")
    senha = input("Senha: ")
    sess = login(usuario, senha)
    if sess:
        # Uma requisição GET para uma página interna antes de baixar é uma boa prática
        # para garantir que a sessão está ativa e obter cookies adicionais (se houver).
        # r = sess.get("https://global.grupoconstruserv.eng.br/index") 
        # print(f"Status da página inicial logada: {r.status_code}")
        
        baixar_dados(sess)