// ============================================
// FOCUSPET BLOCKER - CONTENT.JS
// ============================================
// Script injetado em todas as páginas
// Funciona como intermediário entre página e background.js

console.log("[FocusPet] Content script carregado");

let atalhoNotas = "CTRL+Y";

function obterCombinacaoNotas(evento) {
  const partes = [];
  if (evento.ctrlKey) partes.push("CTRL");
  if (evento.altKey) partes.push("ALT");
  if (evento.shiftKey) partes.push("SHIFT");
  if (evento.metaKey) partes.push("META");
  const tecla = evento.key.toUpperCase();
  if (!partes.length || ["CONTROL", "ALT", "SHIFT", "META"].includes(tecla)) return "";
  partes.push(tecla === " " ? "SPACE" : tecla);
  return partes.join("+");
}

// A página web não recebe atalhos de outras abas; a extensão recebe este evento.
if (!window.location.hostname.includes("localhost") || window.location.port !== "5000") {
  chrome.storage.local.get(["atalhoNotas"], (dados) => {
    atalhoNotas = dados.atalhoNotas || "CTRL+Y";
  });

  chrome.storage.onChanged.addListener((mudancas, area) => {
    if (area === "local" && mudancas.atalhoNotas) {
      atalhoNotas = mudancas.atalhoNotas.newValue || "CTRL+Y";
    }
  });

  document.addEventListener("keydown", (evento) => {
    if (obterCombinacaoNotas(evento) !== atalhoNotas) return;
    evento.preventDefault();
    chrome.runtime.sendMessage({ tipo: "ABRIR_BLOCO_NOTAS" });
  }, true);
}

// ============================================
// LISTENER PARA MENSAGENS DA PÁGINA
// ============================================

window.addEventListener("message", (event) => {
  // Apenas processar mensagens da mesma origem
  if (event.source !== window) return;
  
  const data = event.data;
  
  if (!data.tipo) return;
  
  console.log("[FocusPet] Mensagem capturada:", data.tipo);
  
  // Repassar para background.js
  if (data.tipo === "ATIVAR_BLOQUEIO") {
    chrome.runtime.sendMessage({
      tipo: "ATIVAR_BLOQUEIO",
      urls: data.urls,
      sessoesId: data.sessoesId,
      timestamp: data.timestamp
    }, (response) => {
      console.log("[FocusPet] Resposta do bloqueio:", response);
    });
  }
  else if (data.tipo === "DESATIVAR_BLOQUEIO") {
    chrome.runtime.sendMessage({
      tipo: "DESATIVAR_BLOQUEIO",
      timestamp: data.timestamp
    }, (response) => {
      console.log("[FocusPet] Bloqueio desativado");
    });
  }
  else if (data.tipo === "ATUALIZAR_HOTKEY") {
    chrome.runtime.sendMessage({
      tipo: "ATUALIZAR_HOTKEY",
      hotkey: data.hotkey
    });
  }
});


// ============================================
// LISTENER PARA MENSAGENS DO BACKGROUND
// ============================================

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("[FocusPet] Mensagem do background:", request.tipo);

  if (request.tipo === "HOTKEY_ATUALIZADA") {
    atalhoNotas = request.hotkey;
    sendResponse({ sucesso: true });
  }
  
  if (request.tipo === "REPORTAR_DISTRACAO") {
    // Reportar distração para página do FocusPet
    window.postMessage({
      tipo: "DISTRACAO_DETECTADA",
      sessoesId: request.sessoesId
    }, "*");
    
    sendResponse({ sucesso: true });
  }
  else if (request.tipo === "GET_STATUS") {
    // Retornar status da página
    sendResponse({
      url: window.location.href,
      titulo: document.title
    });
  }
});


// ============================================
// INJETAR SESSION STORAGE
// ============================================

// Guardar ID da sessão para usar em scripts injetados
function atualizarSessoesId(sessoesId) {
  sessionStorage.setItem("focuspet_sessoesId", sessoesId);
  localStorage.setItem("focuspet_ultima_sessao", Date.now());
}

// Listener para atualizar sessoesId
window.addEventListener("message", (event) => {
  if (event.data.tipo === "ATIVAR_BLOQUEIO") {
    atualizarSessoesId(event.data.sessoesId);
  }
});


// ============================================
// COMUNICAÇÃO BIDIRECIONAL
// ============================================

// Classe para gerenciar comunicação
class FocusPetBridge {
  constructor() {
    this.listeners = {};
  }
  
  on(evento, callback) {
    if (!this.listeners[evento]) {
      this.listeners[evento] = [];
    }
    this.listeners[evento].push(callback);
  }
  
  emit(evento, dados) {
    if (this.listeners[evento]) {
      this.listeners[evento].forEach(callback => callback(dados));
    }
  }
  
  enviarParaBackground(tipo, dados) {
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        { tipo, ...dados },
        (response) => {
          if (chrome.runtime.lastError) {
            reject(chrome.runtime.lastError);
          } else {
            resolve(response);
          }
        }
      );
    });
  }
  
  enviarParaPagina(tipo, dados) {
    window.postMessage({ tipo, ...dados }, "*");
  }
}

// Instância global
window.focusPetBridge = new FocusPetBridge();

console.log("[FocusPet] Bridge criada - window.focusPetBridge disponível");


// ============================================
// DEBUG
// ============================================

// Adicionar informações ao console se DevTools estiver aberto
if (window.chrome && chrome.runtime) {
  window.__focusPetDebug = {
    ativo: false,
    urlsBloqueadas: [],
    sessoesId: null,
    logMensagem: (msg) => {
      console.log("[FocusPet Debug]", msg);
    }
  };
}

console.log("[FocusPet] Content script totalmente carregado e funcional");
