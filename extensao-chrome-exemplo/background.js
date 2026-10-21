// ============================================
// STUDY BUDDY BLOCKER - BACKGROUND.JS
// ============================================
// Este é o Service Worker da extensão Chrome
// Gerencia o bloqueio de sites durante sessões de Modo Foco

// Estado global do bloqueio
let estadoBloqueio = {
  ativo: false,
  urlsBloqueadas: [],
  sessoesId: null,
  tokenApi: null,
  inicioSessao: null
};
let carregamentoEstado;

function carregarEstadoBloqueio() {
  if (!carregamentoEstado) {
    carregamentoEstado = chrome.storage.session.get("estadoBloqueio").then((dados) => {
      const salvo = dados.estadoBloqueio;
      if (salvo && typeof salvo === "object") {
        estadoBloqueio = {
          ativo: Boolean(salvo.ativo),
          urlsBloqueadas: Array.isArray(salvo.urlsBloqueadas) ? salvo.urlsBloqueadas : [],
          sessoesId: salvo.sessoesId || null,
          tokenApi: salvo.tokenApi || null,
          inicioSessao: salvo.inicioSessao || null
        };
      }
      return estadoBloqueio;
    }).catch((erro) => {
      carregamentoEstado = null;
      console.error("[Study Buddy Blocker] Não foi possível restaurar o estado do bloqueio:", erro);
      throw erro;
    });
  }
  return carregamentoEstado;
}

async function persistirEstadoBloqueio() {
  await chrome.storage.session.set({ estadoBloqueio });
}

console.log("[Study Buddy Blocker] Service Worker iniciado");

function abrirBlocoNotas() {
  chrome.tabs.query({}).then((tabs) => {
    const abaFocusPet = tabs.find((tab) => tab.url && tab.url.startsWith("http://127.0.0.1:5000"));
    const url = "http://127.0.0.1:5000/?abrir_notas=1";
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
  console.log("[Study Buddy Blocker] Mensagem recebida:", message.tipo);

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
    carregarEstadoBloqueio().then(async () => {
      estadoBloqueio.ativo = true;
      estadoBloqueio.urlsBloqueadas = Array.isArray(message.urls) ? message.urls : [];
      estadoBloqueio.sessoesId = message.sessoesId;
      estadoBloqueio.tokenApi = message.tokenApi;
      estadoBloqueio.inicioSessao = Date.now();
      await persistirEstadoBloqueio();
      chrome.runtime.sendMessage({ tipo: "STATUS_ATUALIZADO", ativo: true }).catch(() => {});
      sendResponse({
        sucesso: true,
        mensagem: "Bloqueio ativado",
        requestId: message.requestId
      });
    }).catch(() => {
      sendResponse({
        sucesso: false,
        mensagem: "Não foi possível ativar o bloqueio.",
        requestId: message.requestId
      });
    });
    return true;
  } 
  else if (message.tipo === "DESATIVAR_BLOQUEIO") {
    carregarEstadoBloqueio().then(async () => {
      estadoBloqueio.ativo = false;
      estadoBloqueio.urlsBloqueadas = [];
      estadoBloqueio.sessoesId = null;
      estadoBloqueio.tokenApi = null;
      estadoBloqueio.inicioSessao = null;
      await persistirEstadoBloqueio();
      chrome.runtime.sendMessage({ tipo: "STATUS_ATUALIZADO", ativo: false }).catch(() => {});
      sendResponse({ sucesso: true, mensagem: "Bloqueio desativado" });
    }).catch(() => {
      sendResponse({ sucesso: false, mensagem: "Não foi possível desativar o bloqueio." });
    });
    return true;
  }
  else if (message.tipo === "GET_STATUS") {
    carregarEstadoBloqueio().then(() => {
      sendResponse({
        ativo: estadoBloqueio.ativo,
        urls: estadoBloqueio.urlsBloqueadas,
        sessoesId: estadoBloqueio.sessoesId
      });
    }).catch(() => {
      sendResponse({ ativo: false, urls: [], sessoesId: null });
    });
    return true;
  }
});


// ============================================
// BLOQUEIO VIA webNavigation
// ============================================

// Interceptar tentativas de navegação
chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
  try {
    await carregarEstadoBloqueio();
  } catch (_erro) {
    return;
  }
  if (!estadoBloqueio.ativo) return;
  if (details.frameId !== 0) return; // Apenas frame principal
  
  try {
    const urlAtual = new URL(details.url);
    const dominioAtual = urlAtual.hostname;
    
    console.log("[Study Buddy Blocker] Verificando URL:", dominioAtual);
    
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
      console.log("[Study Buddy Blocker] 🚫 Bloqueando:", dominioAtual);
      
      if (estadoBloqueio.sessoesId) {
        try {
          const response = await fetch(`http://127.0.0.1:5000/api/foco/registrar-distracao/${estadoBloqueio.sessoesId}`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${estadoBloqueio.tokenApi}` }
          });
          const data = await response.json();
          console.log("[Study Buddy Blocker] Distracao registrada:", data);
        } catch (erro) {
          console.warn("[Study Buddy Blocker] Falha ao registrar distração no Study Buddy:", erro);
        }
      }
      
      // Criar URL de bloqueio
      const bloqueioUrl = chrome.runtime.getURL("bloqueado.html") + 
        "?url=" + encodeURIComponent(details.url) +
        "&sessoesId=" + estadoBloqueio.sessoesId +
        "&token=" + encodeURIComponent(estadoBloqueio.tokenApi || "");
      
      // Bloquear navegação
      chrome.tabs.update(details.tabId, { url: bloqueioUrl });
    }
  } catch (erro) {
    console.error("[Study Buddy Blocker] Erro ao verificar bloqueio:", erro);
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
        // Enviar mensagem para página do Study Buddy
        window.postMessage({
          tipo: "DISTRACAO_DETECTADA",
          sessoesId: sessionStorage.getItem("focuspet_sessoesId"),
          timestamp: Date.now()
        }, "*");
      }
    });
    
    console.log("[Study Buddy Blocker] ⚠️ Distração reportada");
  } catch (erro) {
    // Tab pode ter sido fechado ou estar inacessível
    console.log("[Study Buddy Blocker] Não foi possível reportar distração:", erro.message);
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
        console.log("[Study Buddy] Content script injetado");
      }
    }).catch(() => {
      // Pode falhar em abas do sistema
    });
  }
});

// Quando uma aba é fechada
chrome.tabs.onRemoved.addListener((tabId) => {
  console.log("[Study Buddy Blocker] Aba fechada:", tabId);
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
  console.log("[Study Buddy Blocker] Popup conectado:", port.name);
  
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
      console.log("[Study Buddy Blocker] ⏰ Sessão expirada, desativando bloqueio");
      estadoBloqueio.ativo = false;
      atualizarIcone();
    }
  }
}, 60000); // Verificar a cada minuto


console.log("[Study Buddy Blocker] Service Worker pronto para bloqueio");
