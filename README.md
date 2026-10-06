# Monitoramento

Sistema de monitoramento de disponibilidade de sites utilizando **Selenium, Firefox, PostgreSQL e Streamlit**, com suporte a monitoramento de endereços `.onion` através da rede Tor.

O projeto foi desenvolvido com foco em **monitoramento automatizado, armazenamento histórico das verificações e visualização dos resultados em um dashboard web**.
---
#### Inspirado em: https://www.ransomlook.io/urls e para continuação dos meus estudos sobre darkweb com automatização da busca por novas fontes. 
---

## Objetivo

O Monitoramento tem como objetivo acompanhar a disponibilidade de diferentes alvos web e registrar os resultados das verificações em um banco de dados PostgreSQL.

O sistema diferencia:

- 🌐 Sites convencionais
- 🧅 Endereços `.onion`

Cada verificação pode registrar informações como:

- URL monitorada
- Status
- URL final
- Título da página
- Mensagem de erro
- Tempo de resposta
- Data e hora da verificação

---

## Estrutura do projeto

```text
.
├── app.py
├── executar_monitoramento.sh
├── importar_links.py
├── links_exemplo.txt
├── monitor_comum.py
├── monitor_onion.py
├── monitor_sites.py
├── requirements.txt
└── .gitignore
```

### `app.py`

Aplicação Streamlit responsável pelo dashboard de monitoramento.
Depois de pronto o proprio steamlit vai exibir um link para voce visualizar o dashboard. 

### `monitor_comum.py`

Contém as funções compartilhadas por ambos codigos tanto surface quanto os onion, incluindo conexão com PostgreSQL, criação do navegador Selenium e registro das verificações.

### `monitor_sites.py`

Realiza o monitoramento dos sites convencionais pelo firefox.

### `monitor_onion.py`

Realiza o monitoramento dos endereços `.onion` utilizando Tor.

### `executar_monitoramento.sh`

Script para executar o monitoramento com uma fonte mista, ou seja, com links "normais" e '.onion'.

### `importar_links.py`

Importa os alvos definidos no arquivo `links.txt` para a tabela de alvos do PostgreSQL.

### `links_exemplo.txt`

Arquivo contendo exemplos seguros de URLs para demonstrar o formato utilizado pelo projeto.
As fontes devem estar neste arquivo, cuidado com o cabeçalho já que o postgree faz uma verificação neste arquivo, para saber quantas fontes são novas, quantas verificações foram feitas. 

---

## Requisitos

Para executar o projeto localmente, são necessários:

- Linux
- Python 3.12 ou compatível
- Firefox
- Geckodriver
- PostgreSQL
- Tor, caso seja utilizado o monitoramento `.onion`

---

## Instalação

Clone o repositório:

```bash
git clone git@github.com:M41R40/monitoramento.git
cd monitoramento
```

Crie um ambiente virtual:

```bash
python3 -m venv venv
```

Ative o ambiente virtual:

```bash
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## Configuração do banco de dados

As credenciais do PostgreSQL **não devem ser armazenadas diretamente no código ou publicadas no GitHub**.

Crie um arquivo `.env` na raiz do projeto:

```env
DB_HOST=localhost
DB_NAME=monitoramento
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
```

O arquivo `.env` deve permanecer fora do repositório.

---

## Banco de dados

O projeto utiliza PostgreSQL para armazenar:

- Alvos monitorados
- Tipo do alvo
- Histórico das verificações
- Status
- Tempo de resposta
- Data e hora das verificações

A estrutura principal utiliza as tabelas:

```text
alvos
verificacoes
```

---

## Executando o monitoramento

Com o ambiente virtual ativado:

```bash
./executar_monitoramento.sh
```

Ou, individualmente:

### Sites convencionais

```bash
python monitor_sites.py
```
### Instalação do Tor

O monitoramento de endereços .onion utiliza o Tor como proxy SOCKS5 local.

No Ubuntu/Debian, instale o Tor com:

```bash
 sudo apt update
 ```

```bash
 sudo apt install tor
 ```

Após a instalação, inicie o serviço:

```bash
 sudo systemctl start tor@default
 ```

Para verificar se o Tor está em execução:

```bash
 sudo systemctl status tor@default
 ```

O serviço deve aparecer como:

Active: active (running)

O projeto utiliza a porta SOCKS5:

127.0.0.1:9050

Para verificar se a porta está disponível:

```bash
 ss -lntp | grep 9050
 ```

Se quiser iniciar o Tor automaticamente

```bash
 sudo systemctl enable tor@default
 ```

Ou, para habilitar e iniciar imediatamente:

```bash
 sudo systemctl enable --now tor@default
 ```

Depois disso, não é necessário iniciar manualmente o Tor a cada execução.

Execução do monitoramento

O projeto separa o monitoramento em dois grupos:

Sites comuns → Firefox utilizando a conexão normal.

Endereços .onion → Firefox utilizando o Tor através de 127.0.0.1:9050.

Para executar o monitoramento completo:

```bash
 ./executar_monitoramento.sh
 ```

o monitor_onion.py não inicia o Tor. O serviço tor@default deve estar em execução antes do monitoramento de endereços .onion. Recomenda-se utilizar sudo systemctl enable --now tor@default para iniciar o Tor automaticamente com o sistema.

### Endereços `.onion`

```bash
python monitor_onion.py
```

---

## Executando o dashboard

Ative o ambiente virtual:

```bash
source venv/bin/activate
```

Execute:

```bash
streamlit run app.py
```

O Streamlit disponibilizará o dashboard localmente.

---

## Fluxo do sistema

O fluxo básico é:

```text
links.txt -- Adicione suas fontes aqui, conforme o cabeçalho
    │
    ▼
importar_links.py -- execute este arquivo, configure o banco antes, ele manda para o postgree 
    │
    ▼
PostgreSQL  -- depois ele separa oque é onion e oque é surface para exibir no streamlit, e tambem ordena para qual codigo vai cada tipo de link. 
    │
    ├── Sites convencionais
    │       │
    │       ▼
    │   Selenium + Firefox
    │
    └── Sites .onion
            │
            ▼
        Tor + Selenium
            │
            ▼
       verificacoes
            │
            ▼
         Streamlit
```

---
