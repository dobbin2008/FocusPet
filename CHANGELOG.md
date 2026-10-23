# Histórico de versões

## 1.1.2 — 2026-10-23

### Agenda
- Impedida a criação de atividades em datas passadas, tanto pela interface quanto pela API. A edição de atividades existentes continua permitida.

## 1.1.1

### Perfil
- Adicionada a possibilidade de alterar o email e a senha pela página de perfil, com confirmação da senha atual.
- Protegida a conta reservada do desenvolvedor contra transferência ou apropriação por outra conta.

### Bloco de notas e extensão
- Corrigido o atalho do bloco de notas para abrir o Study Buddy sem recarregar a página atual.
- Reduzido o tamanho do bloco de notas para caber melhor na tela.
- Removido o popup aberto pelo ícone da extensão.
- Removidos da página de bloqueio os indicadores de tempo estudado e distrações.

## 1.1

### Agenda e metas
- Adicionadas opções para listar, concluir, editar e remover atividades da agenda.
- Atividades concluídas podem ser removidas da agenda preservando o histórico e o XP.
- Adicionados lembretes de atividades com notificações do navegador.
- Metas diárias passaram a aceitar minutos ou horas; metas semanais, horas ou dias distintos com sessão de foco concluída.

### Acesso e interface
- Adicionado o botão para mostrar ou ocultar a senha no cadastro e no login.
- Atualizada a organização e a documentação da arquitetura, incluindo o diagrama de classes e a lista de funcionalidades.

### Pets
- Adicionados 12 novos pets ao catálogo. Entre eles Charmander, Mewtwo, Suicune, Slakoth, Squirtle, Aron, Wailmer, Genesect, Grubbin, Hoopa, Nymble e Dreepy.

## 1.0

### Versão inicial
- Criada a aplicação Study Buddy com frontend em HTML, CSS e JavaScript, API Flask e persistência SQLite com SQLAlchemy.
- Implementados cadastro, login e áreas protegidas por autenticação.
- Adicionados sessões de foco com cronômetro, registro de distrações e ganho de XP.
- Criados pets virtuais com níveis, evolução e opção para equipar o pet.
- Adicionadas agenda de estudos, matérias, metas, histórico e resumo semanal.
- Implementados bloco de notas com atalho de teclado e extensão Chrome para bloqueio de sites durante o foco.