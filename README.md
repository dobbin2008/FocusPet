# Study Buddy

Study Buddy é uma aplicação web em Flask para apoiar o estudo com um companion gamificado. O sistema combina planejamento de estudos, sessões de foco, blocos de notas e pets virtuais para incentivar a rotina de aprendizagem.

## Integrantes

- Gabriel Foini Dobbin
- Francisco Ferrão Silva de Lima Corrêa
- Davi Tavares Diamantino Montalvão
- Lucas Parreira Paiva
- Rafael Batista Silva Abreu
- Maria Cecília Guerin Duboc

## Stack

- Frontend: HTML, CSS e JavaScript
- Backend: Flask e Python, organizado por Controllers, Services, Models e Repositories
- Banco de dados: SQLite com SQLAlchemy ORM

## Funcionalidades Implementadas

1. **Bloqueio de sites:** bloqueio de sites cadastrados durante uma sessão de foco por meio da extensão do Chrome.
2. **Blacklist de sites indesejados:** cadastro, listagem e remoção de sites que o estudante deseja bloquear.
3. **Bloco de notas:** criação, edição, consulta e exclusão de anotações pessoais.
4. **Hotkey para o bloco de notas:** configuração de um atalho de teclado para abrir o bloco de notas, inclusive pela extensão do Chrome.
5. **Agenda para gerenciar tarefas:** visualização das atividades de estudo organizadas por data.
6. **Criação de tarefas programadas:** cadastro de tarefas com título, data programada e duração estimada.
7. **Ativação do modo foco:** início e encerramento de sessões de foco com cronômetro e registro de distrações.
8. **Sistema de ganho de XP:** atribuição de XP ao estudante e ao pet equipado após a conclusão de atividades e sessões de foco.
9. **Cadastro de usuário:** criação de contas com nome de exibição, email, senha e foto de perfil opcional.
10. **Login e autenticação de usuário:** acesso com sessão persistente, logout e proteção das áreas que exigem autenticação.
11. **Equipar pet:** Alternar entre pets disponíveis e equipa-los.
12. **Evoluir pets:** progredir por 10 níveis conforme os marcos de XP e visualizar as evoluções dos níveis 4 e 9.
13. **Verificação antirobô:** proteção do cadastro com Cloudflare Turnstile.
14. **Resumo semanal:** consolidação do tempo estudado, XP ganho e distrações.
15. **Múltiplas Notações:** Poder alternar entre notações salvas com nomes.
16. **Edição de perfil:** Maneira de editar nome de usuario e foto de perfil.
17. **Histórico de sessões de foco:** página para consultar sessões anteriores, com data, duração, distrações e XP recebido. Pode permitir filtrar por período e abrir os detalhes de uma sessão.
18. **Matérias de estudo:** cadastrar e editar matérias, acompanhar o tempo estudado na semana e associá-las opcionalmente às sessões de foco.
19. **Lembretes de tarefas:** configurar um horário opcional na agenda e receber uma notificação do navegador quando chegar a hora, com a agenda aberta.
20. **Metas de estudo:** configurar uma meta diária ou semanal, acompanhar o progresso de foco e receber bônus de XP ao alcançá-la.

## Estrutura do projeto

- app.py: factory da aplicação Flask e registro das rotas
- backend/controllers/: Controllers HTTP organizados por recurso
- backend/services/: casos de uso, cada um em sua própria classe com `execute()`
- backend/models/: entidades SQLAlchemy com operações CRUD básicas
- backend/repositories/: consultas e persistência especializada
- backend/database.py: inicialização e migração aditiva do banco
- frontend/pages/: páginas HTML estáticas, sem renderização de templates
- frontend/static/: CSS, JavaScript e imagens consumindo a API Flask
- extensao-chrome-exemplo/: integração da extensão Chrome
- tests/: testes de integração com banco temporário
- docs/diagrama_classes.md: diagrama Mermaid das Models e relacionamentos atuais

## Diagrama de classes

O diagrama de classes atualizado está em [docs/diagrama_classes.md](docs/diagrama_classes.md).

## Arquitetura dos casos de uso

Cada caso de uso possui uma classe Service própria com o método `execute()`. Os Controllers tratam HTTP e chamam Services; os Services validam e coordenam a ação; os Repositories encapsulam consultas especializadas e persistência. As Models herdam de `db.Model` e oferecem `salvar()`, `atualizar()`, `deletar()`, `listar_todos()` e `buscar_por_id()`.

As páginas são arquivos HTML estáticos, sem renderização Jinja. O navegador executa o JavaScript do frontend, que consome endpoints JSON da API Flask. Atualmente os arquivos estáticos e a API são servidos pela mesma aplicação/origem; a interface não depende de templates do servidor.

O bloco de notas permite manter várias notas nomeadas e alternar entre elas; anotações antigas são migradas automaticamente para uma primeira nota, preservando o atalho configurado. O perfil pode ser atualizado pela página **Perfil**, incluindo remoção ou troca da foto.

Na página **Matérias**, cada estudante pode cadastrar e renomear suas matérias. Antes de iniciar o modo foco, pode escolher uma matéria ou manter a opção sem matéria; as sessões associadas são somadas no indicador semanal. As horas de sessões ainda ativas também são atualizadas durante o estudo.

As atividades da agenda podem ter lembretes opcionais. Com a permissão de notificações concedida, o navegador apresenta uma notificação do sistema quando o horário chega. Para o lembrete ser verificado, mantenha o navegador aberto na página da agenda; com a página fechada, o Study Buddy não executa um serviço em segundo plano para dispará-lo.

A página **Histórico** lista apenas sessões de foco encerradas e permite filtrá-las por datas. Os detalhes são consultados sob demanda e respeitam a propriedade das sessões por usuário.

Na página **Metas**, cada estudante escolhe uma meta diária ou semanal de tempo em sessões de foco. Ao atingir a meta em uma sessão encerrada, o bônus é concedido uma vez no período correspondente ao estudante e ao pet equipado: 1 hora de meta concede 10 XP, os valores entre 1 e 4 horas aumentam proporcionalmente e metas de 4 horas ou mais concedem no máximo 20 XP. O tempo da meta inclui sessões encerradas; o bônus é registrado no histórico e no total de XP da sessão.

As senhas exigem pelo menos 12 caracteres, uma letra maiúscula, uma minúscula, um número e um símbolo especial. O backend valida esses requisitos e armazena hashes com o mecanismo do Werkzeug, nunca a senha em texto puro. Atividades concluídas e sessões de foco concedem XP ao estudante e ao pet equipado. O total exibido no perfil é calculado somando o XP acumulado de todos os pets pertencentes ao estudante; o XP individual continua associado a cada pet e determina sua evolução. O resumo semanal considera atividades concluídas e sessões de foco encerradas. Fotos de perfil aceitam PNG, JPEG ou WebP até 5 MB. O backend valida o conteúdo, converte para WebP, limita a dimensão a 512 pixels e armazena o arquivo em `instance/profile_photos/`, fora da pasta pública. A imagem é entregue por uma rota autenticada; contas sem foto continuam usando iniciais.

### Regras de XP

- **Sessão de foco:** 25 XP por hora, proporcional ao tempo, até 100 XP por sessão (atingidos em 4 horas). Cada distração desconta 20 XP; o resultado mínimo é 0.
- **Bônus de meta:** a meta de 60 minutos concede 10 XP; metas menores são proporcionais e as metas entre 60 e 240 minutos crescem proporcionalmente até 20 XP. Metas acima de 240 minutos permanecem limitadas a 20 XP. Cada meta é premiada uma vez por período diário ou semanal.
- **Atividade concluída:** 12,5 XP por hora, proporcional ao tempo, até 50 XP por atividade (atingidos em 4 horas). Durações acima de 4 horas continuam limitadas a 50 XP; uma atividade de duração zero concede 0 XP.
- **Níveis do pet:** são marcos de XP acumulado: nível 2 em 100 XP, nível 3 em 200 XP, até nível 10 em 900 XP. XP adicional não eleva o pet acima do nível 10.
- O resumo semanal apresenta o XP realmente concedido. Registros antigos de atividades concluídas preservam o valor calculado pela regra anterior durante a migração do banco.

### Acesso de desenvolvedor

Para ativar as ferramentas de desenvolvimento, defina `DEVELOPER_EMAIL` no `.env` com o email de uma conta já cadastrada. Entre com esse email e a senha normal da conta; o login levará à área `/desenvolvedor`. Somente essa sessão pode usar os endpoints protegidos de XP de teste e simulação de estudo. Sem `DEVELOPER_EMAIL`, as ferramentas não ficam disponíveis. A simulação registra uma atividade concluída, aplica a mesma regra de XP de uma atividade real e entra no resumo semanal.

## Como iniciar o projeto

### 1. Entre na pasta do projeto

```powershell
Set-Location "C:\caminho\para\a\pasta\Study Buddy"
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instale dependências e configure o ambiente

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env.example` é o modelo sem segredos, versionado para orientar a configuração. `.env` é a cópia local que a aplicação carrega em execução, deve conter os valores reais e é ignorada pelo Git; não publique nem compartilhe esse arquivo. Edite `.env` e defina `SECRET_KEY` com um valor aleatório longo. Para habilitar o cadastro, configure `TURNSTILE_SITE_KEY` e `TURNSTILE_SECRET_KEY` com as chaves do site no Cloudflare Turnstile. A chave secreta fica somente no backend; a API de configuração publica apenas a chave do site. Sem as duas chaves, o cadastro falha fechado com uma mensagem de configuração.

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
5. Confirme que a extensão **Study Buddy Blocker** foi adicionada e está ativada.
6. Mantenha o Study Buddy em execução com `python app.py` antes de iniciar uma sessão de foco.

Depois de alterar os arquivos da extensão, volte para `chrome://extensions/` e clique em **Recarregar** no cartão da extensão.

Na primeira inicialização sobre o banco legado, a aplicação cria/adiciona as estruturas necessárias e converte senhas antigas em hashes sem apagar as contas. Faça uma cópia de segurança do banco antes de atualizar uma instalação existente.

## Testes

```bash
python -m pytest -q
```

Os testes usam bancos temporários e não limpam o banco local da aplicação.
