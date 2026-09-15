// ============================================
// FOCUSPET BLOCKER - BACKGROUND.JS
// ============================================
// Este é o Service Worker da extensão Chrome
// Gerencia o bloqueio de sites durante sessões de Modo Foco

// Estado global do bloqueio
let estadoBloqueio = {
  ativo: false,
  urlsBloqueadas: [],
  sessoesId: null,
  inicioSessao: null
};

console.log("[FocusPet Blocker] Service Worker iniciado");

function abrirBlocoNotas() {
  chrome.tabs.query({}).then((tabs) => {
    const abaFocusPet = tabs.find((tab) => tab.url && tab.url.startsWith("http://localhost:5000"));
    const url = "http://localhost:5000/?abrir_notas=1";
    if (abaFocusPet) {
      chrome.tabs.update(abaFocusPet.id, { active: true, url });
      chrome.windows.update(abaFocusPet.windowId, { focused: true });
    } else {
      chrome.tabs.create({ url });
    }
  });
}

chrome.commands.onCommand.addListener((command) => {
  if (command === "abrir_bloco_notas") abrirBlocoNotas();
});

// ============================================
// LISTENERS DE MENSAGEM
// ============================================

// Receber mensagens do content script ou página
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log("[FocusPet Blocker] Mensagem recebida:", message.tipo);

  if (message.tipo === "ABRIR_BLOCO_NOTAS") {
    abrirBlocoNotas();
    return;
  }

  if (message.tipo === "ATUALIZAR_HOTKEY") {
    chrome.storage.local.set({ atalhoNotas: message.hotkey });
    chrome.tabs.query({}).then((tabs) => {
      tabs.forEach((tab) => {
        if (tab.id) chrome.tabs.sendMessage(tab.id, {
          tipo: "HOTKEY_ATUALIZADA",
          hotkey: message.hotkey
        }).catch(() => {});
      });
    });
    return;
  }
  
  if (message.tipo === "ATIVAR_BLOQUEIO") {
    // Ativar bloqueio de sites
    estadoBloqueio.ativo = true;
    estadoBloqueio.urlsBloqueadas = message.urls || [];
    estadoBloqueio.sessoesId = message.sessoesId;
    estadoBloqueio.inicioSessao = Date.now();
    
    console.log("[FocusPet Blocker] ✅ Bloqueio ATIVADO");
    console.log("[FocusPet Blocker] URLs bloqueadas:", estadoBloqueio.urlsBloqueadas);
    console.log("[FocusPet Blocker] Sessão ID:", estadoBloqueio.sessoesId);
    
    // Notificar popup
    chrome.runtime.sendMessage({
      tipo: "STATUS_ATUALIZADO",
      ativo: true
    }).catch(() => {
      // Popup pode não estar aberto
    });
    
    sendResponse({ sucesso: true, mensagem: "Bloqueio ativado" });
  } 
  else if (message.tipo === "DESATIVAR_BLOQUEIO") {
    // Desativar bloqueio
    estadoBloqueio.ativo = false;
    estadoBloqueio.urlsBloqueadas = [];
    estadoBloqueio.sessoesId = null;
    
    console.log("[FocusPet Blocker] ❌ Bloqueio DESATIVADO");
    
    // Notificar popup
    chrome.runtime.sendMessage({
      tipo: "STATUS_ATUALIZADO",
      ativo: false
    }).catch(() => {
      // Popup pode não estar aberto
    });
    
    sendResponse({ sucesso: true, mensagem: "Bloqueio desativado" });
  }
  else if (message.tipo === "GET_STATUS") {
    // Retornar status atual (usado pelo popup)
    sendResponse({
      ativo: estadoBloqueio.ativo,
      urls: estadoBloqueio.urlsBloqueadas,
      sessoesId: estadoBloqueio.sessoesId
    });
  }
});


// ============================================
// BLOQUEIO VIA webNavigation
// ============================================

// Interceptar tentativas de navegação
chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
  if (!estadoBloqueio.ativo) return;
  if (details.frameId !== 0) return; // Apenas frame principal
  
  try {
    const urlAtual = new URL(details.url);
    const dominioAtual = urlAtual.hostname;
    
    console.log("[FocusPet Blocker] Verificando URL:", dominioAtual);
    
    // Verificar se a URL está na lista bloqueada
    const estaBloqueada = estadoBloqueio.urlsBloqueadas.some(urlBloqueada => {
      try {
        const urlObj = new URL(urlBloqueada);
        // Comparar apenas domínio
        return dominioAtual === urlObj.hostname || 
               dominioAtual.endsWith("." + urlObj.hostname);
      } catch (e) {
        // Se for um padrão simples (ex: "reddit.com")
        return dominioAtual.includes(urlBloqueada) || 
               urlBloqueada.includes(dominioAtual);
      }
    });
    
    if (estaBloqueada) {
      console.log("[FocusPet Blocker] 🚫 Bloqueando:", dominioAtual);
      
      if (estadoBloqueio.sessoesId) {
        try {
          const response = await fetch(`http://localhost:5000/api/foco/registrar-distracao/${estadoBloqueio.sessoesId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
          });
          const data = await response.json();
          console.log("[FocusPet Blocker] Distracao registrada:", data);
        } catch (erro) {
          console.warn("[FocusPet Blocker] Falha ao registrar distração no FocusPet:", erro);
        }
      }
      
      // Criar URL de bloqueio
      const bloqueioUrl = chrome.runtime.getURL("bloqueado.html") + 
        "?url=" + encodeURIComponent(details.url) +
        "&sessoesId=" + estadoBloqueio.sessoesId;
      
      // Bloquear navegação
      chrome.tabs.update(details.tabId, { url: bloqueioUrl });
    }
  } catch (erro) {
    console.error("[FocusPet Blocker] Erro ao verificar bloqueio:", erro);
  }
});


// ============================================
// REPORTE DE DISTRAÇÃO
// ============================================

async function reportarDistracaoAoFocusPet(tabId) {
  try {
    // Executar script no tab para reportar
    await chrome.scripting.executeScript({
      target: { tabId: tabId },
      function: () => {
        // Enviar mensagem para página do FocusPet
        window.postMessage({
          tipo: "DISTRACAO_DETECTADA",
          sessoesId: sessionStorage.getItem("focuspet_sessoesId"),
          timestamp: Date.now()
        }, "*");
      }
    });
    
    console.log("[FocusPet Blocker] ⚠️ Distração reportada");
  } catch (erro) {
    // Tab pode ter sido fechado ou estar inacessível
    console.log("[FocusPet Blocker] Não foi possível reportar distração:", erro.message);
  }
}


// ============================================
// GERENCIAMENTO DE ABAS
// ============================================

// Quando uma aba é atualizada, verificar se precisa recarregar bloqueio
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "loading" && estadoBloqueio.ativo) {
    // Injetar content script se necessário
    chrome.scripting.executeScript({
      target: { tabId: tabId },
      function: () => {
        console.log("[FocusPet] Content script injetado");
      }
    }).catch(() => {
      // Pode falhar em abas do sistema
    });
  }
});

// Quando uma aba é fechada
chrome.tabs.onRemoved.addListener((tabId) => {
  console.log("[FocusPet Blocker] Aba fechada:", tabId);
});


// ============================================
// ATUALIZAÇÃO DE CONTEXTO
// ============================================

// Atualizar ícone quando estado muda
function atualizarIcone() {
  if (estadoBloqueio.ativo) {
    chrome.action.setIcon({ path: "icons/icon-128.png" });
    chrome.action.setBadgeText({ text: "ON" });
    chrome.action.setBadgeBackgroundColor({ color: "#f44336" });
  } else {
    chrome.action.setIcon({ path: "icons/icon-128.png" });
    chrome.action.setBadgeText({ text: "" });
  }
}

// Inicializar ícone
atualizarIcone();


// ============================================
// EVENT LISTENERS
// ============================================

// Listener para quando o popup é aberto/fechado
chrome.runtime.onConnect.addListener((port) => {
  console.log("[FocusPet Blocker] Popup conectado:", port.name);
  
  if (port.name === "popup") {
    // Enviar status ao popup
    port.postMessage({
      tipo: "STATUS",
      ativo: estadoBloqueio.ativo,
      urls: estadoBloqueio.urlsBloqueadas,
      sessoesId: estadoBloqueio.sessoesId
    });
    
    port.onMessage.addListener((msg) => {
      if (msg.tipo === "DESATIVAR") {
        estadoBloqueio.ativo = false;
        atualizarIcone();
        port.postMessage({ tipo: "CONFIRMADO" });
      }
    });
  }
});


// ============================================
// TIMEOUTS E LIMPEZA
// ============================================

// Limpar estado se sessão expirar (opcional)
setInterval(() => {
  if (estadoBloqueio.ativo && estadoBloqueio.inicioSessao) {
    const duracao = Date.now() - estadoBloqueio.inicioSessao;
    // Se duraron mais de 8 horas, desativar automaticamente
    if (duracao > 8 * 60 * 60 * 1000) {
      console.log("[FocusPet Blocker] ⏰ Sessão expirada, desativando bloqueio");
      estadoBloqueio.ativo = false;
      atualizarIcone();
    }
  }
}, 60000); // Verificar a cada minuto


console.log("[FocusPet Blocker] Service Worker pronto para bloqueio");
