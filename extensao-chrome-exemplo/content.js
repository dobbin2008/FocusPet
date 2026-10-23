// ============================================
// STUDY BUDDY BLOCKER - CONTENT.JS
// ============================================
// Script injetado em todas as páginas
// Funciona como intermediário entre página e background.js

console.log("[Study Buddy] Content script carregado");

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

const estaNoStudyBuddy = ["localhost", "127.0.0.1"].includes(window.location.hostname)
  && window.location.port === "5000";

if (!estaNoStudyBuddy) {
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
    evento.stopPropagation();
    chrome.runtime.sendMessage({ tipo: "ABRIR_BLOCO_NOTAS" });
  }, true);
}

// ============================================
// LISTENER PARA MENSAGENS DA PÁGINA
// ============================================

window.addEventListener("message", (event) => {
  if (
    event.source !== window ||
    !["http://localhost:5000", "http://127.0.0.1:5000"].includes(event.origin)
  ) return;
  
  const data = event.data;
  
  if (!data.tipo) return;
  
  console.log("[Study Buddy] Mensagem capturada:", data.tipo);
  
  // Repassar para background.js
  if (data.tipo === "ATIVAR_BLOQUEIO") {
    chrome.runtime.sendMessage({
      tipo: "ATIVAR_BLOQUEIO",
      urls: data.urls,
      sessoesId: data.sessoesId,
      tokenApi: data.tokenApi,
      requestId: data.requestId
    }, (response) => {
      const erro = chrome.runtime.lastError;
      if (data.requestId) {
        window.postMessage({
          tipo: "BLOQUEIO_ATIVADO_RESULTADO",
          requestId: data.requestId,
          sucesso: !erro && Boolean(response?.sucesso),
          mensagem: erro?.message || response?.mensagem
        }, event.origin);
      }
    });
  }
  else if (data.tipo === "DESATIVAR_BLOQUEIO") {
    chrome.runtime.sendMessage({
      tipo: "DESATIVAR_BLOQUEIO",
      requestId: data.requestId
    }, (response) => {
      const erro = chrome.runtime.lastError;
      if (data.requestId && (!response?.sucesso || erro)) {
        window.postMessage({
          tipo: "BLOQUEIO_DESATIVADO_RESULTADO",
          requestId: data.requestId,
          sucesso: false,
          mensagem: erro?.message || response?.mensagem
        }, event.origin);
      }
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
  console.log("[Study Buddy] Mensagem do background:", request.tipo);

  if (request.tipo === "ABRIR_BLOCO_NOTAS") {
    window.postMessage({ tipo: "ABRIR_BLOCO_NOTAS" }, window.location.origin);
    sendResponse({ sucesso: true });
    return;
  }

  if (request.tipo === "HOTKEY_ATUALIZADA") {
    atalhoNotas = request.hotkey;
    sendResponse({ sucesso: true });
  }
  
  if (request.tipo === "REPORTAR_DISTRACAO") {
    // Reportar distração para página do Study Buddy
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
  if (
    event.source === window &&
    ["http://localhost:5000", "http://127.0.0.1:5000"].includes(event.origin) &&
    event.data.tipo === "ATIVAR_BLOQUEIO"
  ) {
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

console.log("[Study Buddy] Bridge criada - window.focusPetBridge disponível");


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
      console.log("[Study Buddy Debug]", msg);
    }
  };
}

console.log("[Study Buddy] Content script totalmente carregado e funcional");
