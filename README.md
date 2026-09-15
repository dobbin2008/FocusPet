# FocusPet

FocusPet é uma aplicação web em Flask para apoiar o estudo com um companion gamificado. O sistema combina planejamento de estudos, sessões de foco, blocos de notas, pets virtualizados e gerenciamento de tribos para incentivar a rotina de aprendizagem.

## Integrantes

- Gabriel Foini Dobbin
- Francisco Ferrão Silva de Lima Corrêa
- Davi Tavares Diamantino Montalvão
- Lucas Parreira Paiva
- Rafael Batista Silva Abreu
- Maria Cecília Guerin Duboc

## Stack

- Frontend: HTML, CSS e JavaScript
- Backend: Flask e Python
- Banco de dados: SQL direto com SQLite (`sqlite3`)

## Funcionalidades Implementadas

1. **Bloqueio de sites:** bloqueio de sites cadastrados durante uma sessão de foco por meio da extensão do Chrome.
2. **Blacklist de sites indesejados:** cadastro, listagem e remoção de sites que o estudante deseja bloquear.
3. **Bloco de notas:** criação, edição, consulta e exclusão de anotações pessoais.
4. **Hotkey para o bloco de notas:** configuração de um atalho de teclado para abrir o bloco de notas, inclusive pela extensão do Chrome.
5. **Agenda para gerenciar tarefas:** visualização das atividades de estudo organizadas por data.
6. **Criação de tarefas programadas:** cadastro de tarefas com título, data programada e duração estimada.
7. **Ativação do modo foco:** início e encerramento de sessões de foco com cronômetro e registro de distrações.
8. **Sistema de ganho de XP:** atribuição de XP ao estudante e ao pet após a conclusão de atividades e sessões de foco.
9. **Cadastro de usuário:** criação de contas de estudantes com email e senha.
10. **Login e autenticação de usuário:** acesso com sessão persistente, logout e proteção das áreas que exigem autenticação.

## Estrutura do projeto

- app.py: criação da aplicação Flask, configuração de sessão e inicialização do banco
- controllers/: controladores das rotas principais da aplicação
- database.py: conexão, schema, índices e view SQL do banco SQLite
- services/: casos de uso, cada um em sua própria classe com `execute()`
- templates/: páginas HTML estáticas da interface
- static/: arquivos estáticos como CSS, JS e imagens

## Arquitetura dos casos de uso

Cada caso de uso possui uma classe Service própria com o método `execute()`. Os controllers recebem os Services por injeção de dependência, e os Services recebem um `DatabaseGateway`, cuja implementação padrão usa SQLite. Isso mantém as responsabilidades separadas e permite substituir Services ou o banco em testes sem alterar as rotas.

## Como iniciar o projeto

### 1. Entre na pasta do projeto

```bash
cd c:\Users\rafae\OneDrive\Área de Trabalho\focuspet
```

### 2. Crie e ative um ambiente virtual (opcional, mas recomendado)

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install flask
```

### 4. Execute a aplicação

```bash
python app.py
```

### 5. Acesse no navegador

```text
http://localhost:5000
```

## Como instalar a extensão do Chrome

1. Abra o Google Chrome e acesse `chrome://extensions/`.
2. Ative o **Modo do desenvolvedor**, no canto superior direito.
3. Clique em **Carregar expandida**.
4. Selecione a pasta `extensao-chrome-exemplo/` dentro do repositório.
5. Confirme que a extensão **FocusPet Blocker** foi adicionada e está ativada.
6. Mantenha o FocusPet em execução com `python app.py` antes de iniciar uma sessão de foco.

Depois de alterar os arquivos da extensão, volte para `chrome://extensions/` e clique em **Recarregar** no cartão da extensão.