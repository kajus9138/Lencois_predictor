# Sistema de Forecast Hidrológico — Rio Lençóis

Aplicação para **previsão de cotas do rio Lençóis** baseada em dados telemétricos e modelos ARIMA.
O sistema integra dados reais e previsões em uma **interface web interativa**, atualizando automaticamente as séries conforme novos dados são inseridos.

---

## Descrição Geral

O sistema:
- Carrega do banco de dados as cotas observadas e previsões anteriores.
- Treina (ou atualiza) o modelo ARIMA com as últimas medições.
- Gera previsões para a próxima semana.
- Exibe na interface dois gráficos principais:
  - **Gráfico comparativo:** previsões x cotas observadas da última semana.
  - **Gráfico de previsões futuras:** próximos 7 dias.
- Atualiza automaticamente os gráficos e o banco de dados quando novos dados são inseridos pelo operador.
- Emite alertas quando o nível medido ultrapassa 2 metros em qualquer estação.

---

## Estrutura do Projeto

```
Lencois_predictor/
├── main.py                  # Ponto de entrada da aplicação Streamlit
├── config.ini               # Configurações (arquivo de novo dado, estações)
├── requirements.txt         # Dependências Python
├── runtime.txt              # Versão do Python recomendada
├── dados/
│   ├── rio.db               # Banco de dados SQLite
│   ├── insert_historical_data.py
│   └── modelos/
│       ├── arima_mon.pkl    # Modelo ARIMA montante
│       ├── arima_jus.pkl    # Modelo ARIMA jusante
│       └── backup_modelos/  # Cópias de segurança dos modelos iniciais
├── input/
│   └── novo_dado.xlsx       # Arquivo de novos dados (substitua este arquivo)
├── src/
│   ├── update.py            # ETL e atualização do modelo ARIMA
│   ├── forecast.py          # Geração e inserção de previsões
│   ├── view_last_week.py    # Visualização comparativa da última semana
│   ├── view_next_week.py    # Visualização das previsões futuras
│   └── layout.py            # Componentes de interface
└── figuras/                 # Imagens exportadas dos gráficos
```

---

## Pré-requisitos

- **Python 3.11** (versão recomendada, conforme `runtime.txt`)
- `pip` e `venv` disponíveis no sistema

---

## Setup e Inicialização

### 1. Clonar o repositório

```bash
git clone https://github.com/kajus9138/Lencois_predictor.git
cd Lencois_predictor
```

### 2. Criar o ambiente virtual

```bash
python3.11 -m venv .venv
```

> Caso `python3.11` não esteja no PATH, use o caminho completo do interpretador, por exemplo:
> `python3 -m venv .venv`

### 3. Ativar o ambiente virtual

**Linux / macOS:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

O prompt do terminal deve exibir `(.venv)` ao lado, indicando que o ambiente está ativo.

### 4. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5. Popular o banco de dados com os dados históricos

Na primeira execução, o banco de dados `dados/rio.db` precisa ser preenchido com o histórico inicial:

```bash
cd dados
python insert_historical_data.py
cd ..
```

### 6. Configurar o arquivo de entrada

Edite `config.ini` para indicar o nome do arquivo de novos dados dentro da pasta `input/`:

```ini
[new_data]
arquivo = novo_dado.xlsx
```

Substitua o arquivo `input/novo_dado.xlsx` pelo arquivo de telemetria da semana atual antes de iniciar a aplicação.

### 7. Executar a aplicação

```bash
streamlit run main.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`.

---

## Uso da Interface

- **Upload de arquivo:** use o campo de upload na interface para enviar um arquivo `.xlsx` com os dados da semana. O sistema processa automaticamente, atualiza o banco de dados, retreina o modelo ARIMA e exibe os gráficos atualizados.
- **Resetar para estado inicial:** na barra lateral, marque a confirmação e clique em "Resetar para estado inicial" para apagar todos os dados e recarregar o histórico original.
- **Gráficos:** são exibidos automaticamente após o processamento — comparativo da última semana e previsões para os próximos 7 dias.
- **Alertas:** um aviso é exibido automaticamente se o nível em qualquer estação ultrapassar 200 cm (2 metros).

---

## Configuração (`config.ini`)

| Seção       | Chave    | Descrição                                          |
|-------------|----------|----------------------------------------------------|
| `estacoes`  | `estacoes` | IDs das estações monitoradas (ex: `[1,2]`)       |
| `mode`      | `update`   | Modo de atualização do modelo (`True`/`False`)   |
| `new_data`  | `arquivo`  | Nome do arquivo de novos dados na pasta `input/` |

---

## Fluxograma

<img width="849" height="1459" alt="image" src="https://github.com/user-attachments/assets/c0330a68-d985-443d-a7cc-365744c9f4cf" />

---

## Lógica do Sistema (Pseudocódigo)

```text
INICIO

1. Inicializar sistema
    - Conectar ao banco rio.db
    - Carregar modelo ARIMA salvo (se existir)
    - Obter timestamp atual

2. Carregar dados da ultima semana:
    - Buscar dados observados da tabela de cotas
    - Buscar previsoes correspondentes
    - Plotar grafico comparativo (observados + previsoes)
      -> funcao plot_comparativo()
    - Plotar grafico de previsoes futuras
      -> funcao plot_previsoes()

3. Loop continuo (aguardando novos dados):

    Aguardar evento de novo dado inserido pelo operador

    Quando novos dados forem detectados:
        timestamp_ultimo ← ultimo registro no banco
        timestamp_novo ← primeiro registro dos novos dados

        SE (timestamp_novo > timestamp_ultimo):
            - Tratar valores ausentes (NaN)
            - Tratar outliers
            - Atualizar tabela de dados observados no banco

            - Atualizar modelo ARIMA com novos dados (append)
            - Gerar novas previsoes para 7 dias
            - Atualizar tabela de previsoes no banco

            - Atualizar graficos:
                -> atualizar grafico comparativo (observados + previsoes)
                -> atualizar grafico de previsoes (somente previsoes futuras)

        SENAO:
            - Exibir aviso: "Dados fora de ordem. Aguardando sequencia correta."

    Retornar ao estado de espera por novos dados

FIM
```

---

## Dependências Principais

| Pacote        | Uso                                      |
|---------------|------------------------------------------|
| `streamlit`   | Interface web interativa                 |
| `pandas`      | Manipulação de dados tabulares           |
| `numpy`       | Operações numéricas                      |
| `statsmodels` | Modelo ARIMA                             |
| `matplotlib`  | Geração de gráficos                      |
| `scikit-learn`| Pré-processamento e métricas             |
| `openpyxl`    | Leitura de arquivos `.xlsx`              |
| `seaborn`     | Estilização de gráficos                  |
