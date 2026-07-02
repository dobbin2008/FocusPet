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
- Banco de dados: SQLAlchemy com SQLite

## Funcionalidades implementadas

### Autenticação e acesso
- Cadastro de estudante
- Login e logout
- Proteção de rotas com sessão autenticada

### Painel principal
- Página inicial com redirecionamento para dashboard quando o usuário está autenticado
- Dashboard principal da aplicação

### Administração
- Cadastro e visualização de estudantes
- Criação, listagem e exclusão de pets
- Criação, listagem e exclusão de tribos

### Modelos do sistema
- Estudante: usuário da aplicação, com XP, metas, pet equipado e relações com agenda, notas, sessões e resumos
- Pet: pet virtual com evolução por XP e níveis
- Tribo: agrupamento de estudantes com relação a pets e ranking
- BlocoDeNotas: notas rápidas do estudante
- SessaoFoco: controle de sessões de foco, sites bloqueados, distrações e cálculo de XP
- Agenda: organização de estudos por agenda do estudante
- Estudo: atividades de estudo com duração, conclusão e cálculo de XP
- ResumoSemanal: estatísticas semanais de produtividade e progresso do pet

## Estrutura do projeto

- app.py: criação da aplicação Flask e inicialização do banco
- controllers/: controladores das rotas principais da aplicação
- models/: modelos SQLAlchemy do domínio
- services/: lógica de negócio para autenticação e administração
- templates/: páginas HTML da interface
- static/: arquivos estáticos como CSS, JS e imagens

## Como iniciar o projeto

### 1. Entre na pasta do projeto

```bash
cd c:\Users\rafae\OneDrive\Área de Trabalho\focuspet
```

### 2. Crie e ative um ambiente virtual (opcional, mas recomendado)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install flask flask-sqlalchemy
```

### 4. Execute a aplicação

```bash
python app.py
```

### 5. Acesse no navegador

```text
http://localhost:5000
```

## Observações

- Ao iniciar a aplicação, o banco de dados SQLite é criado automaticamente no arquivo focuspet.db.
- A aplicação recria as tabelas no início da execução, então dados locais podem ser reinicializados a cada execução.
