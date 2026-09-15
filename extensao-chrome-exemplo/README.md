# Extensão Chrome FocusPet Blocker

## 📁 Estrutura de Arquivos

```
extensao-chrome-exemplo/
├── manifest.json          # Configuração da extensão
├── background.js          # Service Worker (lógica principal)
├── content.js            # Script injetado em todas as páginas
├── popup.html            # Interface do popup
├── popup.js              # Lógica do popup
├── bloqueado.html        # Página mostrada quando site é bloqueado
├── styles.css            # Estilos compartilhados (opcional)
└── icons/
    ├── icon-16.png       # Ícone 16x16
    ├── icon-48.png       # Ícone 48x48
    └── icon-128.png      # Ícone 128x128
```

## 📋 Descrição dos Arquivos

### 1. **manifest.json**
Arquivo de configuração da extensão. Define:
- Versão do Manifest (V3 - obrigatório em navegadores modernos)
- Permissões necessárias
- Scripts de background e content
- UI (popup, ícones)
- Host permissions para interceptar URLs

### 2. **background.js**
Service Worker que:
- Gerencia estado global do bloqueio
- Intercepta navegação via `chrome.webNavigation`
- Bloqueia URLs configuradas
- Comunica com content scripts
- Atualiza ícone da extensão
- Reporta distrações ao FocusPet

### 3. **content.js**
Script injetado em todas as páginas que:
- Atua como intermediário entre página e background
- Captura mensagens via `window.postMessage()`
- Envia para background via `chrome.runtime.sendMessage()`
- Injeta API segura na página
- Protege contra bypasses

### 4. **popup.html**
Interface visual do popup com:
- Status do bloqueio
- Lista de URLs bloqueadas
- Cronômetro
- Botões de controle
- Informações da sessão

### 5. **popup.js**
Lógica do popup que:
- Atualiza status em tempo real
- Gerencia cronômetro visual
- Permite desativar bloqueio manualmente
- Abre FocusPet em nova aba

### 6. **bloqueado.html**
Página mostrada quando site é bloqueado com:
- Design atrativo
- Informações de bloqueio
- Estatísticas da sessão
- Opções de continuar ou encerrar
- Auto-fechamento após 5 segundos

## 🚀 Como Instalar

### Para Desenvolvedores

1. **Clonar ou copiar** este diretório
2. **Abrir Chrome** e acessar `chrome://extensions/`
3. **Ativar "Modo do desenvolvedor"** (canto superior direito)
4. **Clicar "Carregar extensão não empacotada"**
5. **Selecionar a pasta** `extensao-chrome-exemplo/`
6. **Pronto!** A extensão aparecerá na barra de ferramentas

### Abrir o bloco de notas em qualquer aba

Com a extensão carregada, `CTRL + Y` abre o bloco de notas mesmo quando a aba atual não é o FocusPet. O atalho configurado no menu do bloco de notas também é sincronizado com as outras abas.

Depois de alterar os arquivos da extensão, acesse `chrome://extensions/` e clique em **Recarregar** na extensão para ativar a versão nova.

### Ícones Temporários

Se não tiver os ícones:
1. Usar imagens placeholder (qualquer PNG 16x16, 48x48, 128x128)
2. Ou comentar as linhas de ícones em `manifest.json`

## 🔌 Como Funciona

### Fluxo de Ativação

```
1. Usuário clica "ATIVAR MODO FOCO" no FocusPet
   ↓
2. JavaScript do FocusPet envia window.postMessage({tipo: "ATIVAR_BLOQUEIO", urls: [...]})
   ↓
3. content.js captura a mensagem
   ↓
4. content.js chama chrome.runtime.sendMessage() para background.js
   ↓
5. background.js ativa o bloqueio e começa interceptar navegação
   ↓
6. popup.js atualiza status visual
```

### Fluxo de Bloqueio

```
1. Usuário tenta acessar https://reddit.com
   ↓
2. chrome.webNavigation.onBeforeNavigate intercepta
   ↓
3. background.js verifica se está na lista
   ↓
4. Se sim, redireciona para bloqueado.html
   ↓
5. Chama reportarDistracaoAoFocusPet()
   ↓
6. FocusPet recebe window.postMessage({tipo: "DISTRACAO_DETECTADA"})
   ↓
7. Incrementa vezes_distraido e registra via API
```

## 🎨 Personalização

### Mudar Cores
Editar `popup.html` e `bloqueado.html`:
```css
/* De azul #1565ff para verde #4caf50 por exemplo */
background: #4caf50;
border-color: #4caf50;
```

### Mudar Mensagens
Editar strings em:
- `popup.html` - Interface do popup
- `bloqueado.html` - Página de bloqueio
- `background.js` - Logs do console

### Adicionar Novas Funcionalidades
1. Adicionar novo `tipo` em `manifest.json` se for nova permissão
2. Implementar listener em `background.js` ou `content.js`
3. Testar com `chrome://extensions/` > "Recarregar"

## 🐛 Troubleshooting

### Bloqueio não funciona
- [ ] Verificar se extensão está ativada
- [ ] Abrir DevTools e verificar erros em `chrome://extensions/`
- [ ] Verificar se URL está formatada corretamente (`https://exemplo.com`)
- [ ] Testar com tab nova (algumas abas antigas podem ter cache)

### Extensão não carrega
- [ ] Verificar `manifest.json` por erros JSON
- [ ] Verificar permissões necessárias
- [ ] Ver erros específicos em `chrome://extensions/`

### Distração não registra
- [ ] Verificar se FocusPet está na aba que tentou acessar
- [ ] Verificar console de FocusPet para erros
- [ ] Verificar se API retorna 200 OK

### Popup não atualiza
- [ ] Forçar recarregar extensão em `chrome://extensions/`
- [ ] Fechar e abrir popup novamente
- [ ] Verificar `chrome://extensions/` para erros

## 📚 Recursos Úteis

- [Chrome Extensions Documentation](https://developer.chrome.com/docs/extensions/)
- [Chrome Web Store Upload](https://chrome.google.com/webstore/category/extensions)
- [Manifest V3 Migration Guide](https://developer.chrome.com/docs/extensions/migrating/)

## 🔒 Segurança

- ✅ Content script isolado da página (contexto separado)
- ✅ Sem acesso a senhas/dados sensíveis
- ✅ Comunicação verificada por `event.source`
- ✅ Bloqueio por webNavigation (não por JavaScript)
- ✅ Service Worker sem acesso direto ao DOM

## 📝 Limitações

1. **Não funciona em abas incógnito** (por padrão)
2. **Não bloqueia extensões** (apenas navegação web)
3. **Não intercepta requisições XHR** (apenas navegação)
4. **Pode ter lag** se lista tiver muitos sites (>1000)
5. **Recarregar página** após desinstalar extensão

## ✨ Melhorias Futuras

- [ ] Interface de gerenciamento em novo tab
- [ ] Histórico de bloqueios
- [ ] Estatísticas detalhadas
- [ ] Sincronização com servidor
- [ ] Notificações do navegador
- [ ] Atalhos de teclado
- [ ] Temas customizáveis
- [ ] Suporte a regex patterns

## 📞 Suporte

Para problemas com a extensão:
1. Verificar arquivos JSON para erros de sintaxe
2. Abrir DevTools em `chrome://extensions/`
3. Verificar logs do Service Worker
4. Testar em perfil novo do Chrome
5. Limpar cache de extensão

---

**Versão**: 1.0.0  
**Status**: ✅ Funcional  
**Última Atualização**: 2026-08-16
