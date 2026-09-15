// ============================================
// FOCUSPET BLOCKER - POPUP.JS
// ============================================

const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");
const statusContainer = document.getElementById("status");
const bloqueioInfo = document.getElementById("bloqueioInfo");
const urlasBloqueadasList = document.getElementById("urlasBloqueadasList");
const desativarBtn = document.getElementById("desativarBtn");
const abrirBtn = document.getElementById("abrirBtn");
const cronometro = document.getElementById("cronometro");
const sessaoInfo = document.getElementById("sessaoInfo");
const cronometroInfo = document.getElementById("cronometroInfo");

let cronometroInterval = null;
let tempoInicio = null;

console.log("[Popup] Script carregado");

// ============================================
// ATUALIZAR STATUS INICIAL
// ============================================

function atualizarStatus() {
  chrome.runtime.sendMessage({ tipo: "GET_STATUS" }, (response) => {
    console.log("[Popup] Status recebido:", response);
    
    if (response && response.ativo) {
      statusText.textContent = "Status: BLOQUEIO ATIVO 🔴";
      statusDot.classList.remove("inativo");
      statusDot.classList.add("ativo");
      statusContainer.classList.remove("inativo");
      statusContainer.classList.add("ativo");
      
      bloqueioInfo.style.display = "block";
      desativarBtn.style.display = "block";
      cronometroInfo.style.display = "block";
      
      // Listar URLs bloqueadas
      urlasBloqueadasList.innerHTML = "";
      if (response.urls && response.urls.length > 0) {
        response.urls.forEach(url => {
          const li = document.createElement("li");
          li.textContent = url;
          urlasBloqueadasList.appendChild(li);
        });
      } else {
        const li = document.createElement("li");
        li.textContent = "Nenhum site bloqueado";
        urlasBloqueadasList.appendChild(li);
      }
      
      // Mostrar ID da sessão
      if (response.sessoesId) {
        sessaoInfo.innerHTML = `<br><span class="sessao-id">Sessão #${response.sessoesId}</span>`;
        tempoInicio = Date.now();
        iniciarCronometro();
      }
    } else {
      statusText.textContent = "Status: INATIVO ⚪";
      statusDot.classList.remove("ativo");
      statusDot.classList.add("inativo");
      statusContainer.classList.remove("ativo");
      statusContainer.classList.add("inativo");
      
      bloqueioInfo.style.display = "none";
      desativarBtn.style.display = "none";
      
      if (cronometroInterval) {
        clearInterval(cronometroInterval);
        cronometroInterval = null;
      }
    }
  });
}

// Atualizar status quando popup abre
atualizarStatus();

// Atualizar a cada 2 segundos
setInterval(atualizarStatus, 2000);


// ============================================
// CRONÔMETRO
// ============================================

function iniciarCronometro() {
  if (cronometroInterval) {
    clearInterval(cronometroInterval);
  }
  
  cronometroInterval = setInterval(() => {
    if (tempoInicio) {
      const tempoDecorrido = Date.now() - tempoInicio;
      const horas = Math.floor(tempoDecorrido / 3600000);
      const minutos = Math.floor((tempoDecorrido % 3600000) / 60000);
      const segundos = Math.floor((tempoDecorrido % 60000) / 1000);
      
      cronometro.textContent = 
        String(horas).padStart(2, '0') + ':' +
        String(minutos).padStart(2, '0') + ':' +
        String(segundos).padStart(2, '0');
    }
  }, 1000);
}


// ============================================
// BOTÕES
// ============================================

// Desativar bloqueio
desativarBtn.addEventListener("click", () => {
  console.log("[Popup] Desativando bloqueio");
  
  chrome.runtime.sendMessage({ tipo: "DESATIVAR_BLOQUEIO" }, (response) => {
    console.log("[Popup] Bloqueio desativado:", response);
    
    statusText.textContent = "Status: INATIVO ⚪";
    statusDot.classList.remove("ativo");
    statusDot.classList.add("inativo");
    statusContainer.classList.remove("ativo");
    statusContainer.classList.add("inativo");
    
    bloqueioInfo.style.display = "none";
    desativarBtn.style.display = "none";
    
    if (cronometroInterval) {
      clearInterval(cronometroInterval);
    }
  });
});

// Abrir FocusPet
abrirBtn.addEventListener("click", () => {
  console.log("[Popup] Abrindo FocusPet");
  
  // Abrir aba com FocusPet (ajuste a URL conforme necessário)
  chrome.tabs.create({
    url: "http://localhost:5000/" // Ou a URL do seu FocusPet
  });
});


// ============================================
// LISTENER PARA ATUALIZAÇÕES
// ============================================

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("[Popup] Mensagem recebida:", request.tipo);
  
  if (request.tipo === "STATUS_ATUALIZADO") {
    console.log("[Popup] Atualizando status...");
    atualizarStatus();
  }
});


// ============================================
// FECHAR INTERVALO AO FECHAR POPUP
// ============================================

window.addEventListener("unload", () => {
  if (cronometroInterval) {
    clearInterval(cronometroInterval);
  }
  console.log("[Popup] Popup fechado");
});


console.log("[Popup] Script totalmente carregado e pronto");
