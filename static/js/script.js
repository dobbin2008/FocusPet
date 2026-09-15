
// ============================================
// MODO ESCURO / CLARO
// ============================================

const temaBtn = document.getElementById("temaBtn");

function atualizarIcone() {
    if (document.body.classList.contains("claro")) {
        temaBtn.textContent = "🌙";
    } else {
        temaBtn.textContent = "☀️";
    }
}

const temaSalvo = localStorage.getItem("tema");

if (temaSalvo === "light") {
    document.body.classList.add("claro");
} else {
    document.body.classList.remove("claro");
}

atualizarIcone();

temaBtn.addEventListener("click", () => {

    document.body.classList.toggle("claro");

    if (document.body.classList.contains("claro")) {
        localStorage.setItem("tema", "light");
    } else {
        localStorage.setItem("tema", "dark");
    }

    atualizarIcone();

});


// ============================================
// MODO FOCO - CRONÔMETRO
// ============================================

let sessoesAtivas = {}; // { sessaoId: { inicio, intervalo, vezesDistraido } }

const focoBtn = document.getElementById("focoBtn");
const encerrarFocoBtn = document.getElementById("encerrarFocoBtn");
const cronometroContainer = document.getElementById("cronometroContainer");
const cronometroTempo = document.getElementById("cronometroTempo");
const vezesDistaidoDisplay = document.getElementById("vezesDistraido");

if (focoBtn && encerrarFocoBtn) {
    focoBtn.addEventListener("click", iniciarModoFoco);
    encerrarFocoBtn.addEventListener("click", encerrarModoFoco);
}

async function iniciarModoFoco() {
    try {
        const response = await fetch("/api/foco/iniciar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

        const data = await response.json();

        if (data.sucesso) {
            const sessoesId = data.sessao_id;

            // Guardar info da sessão
            sessoesAtivas[sessoesId] = {
                inicio: Date.now(),
                intervalo: null,
                vezesDistraido: 0,
                sessoesId: sessoesId
            };

            // Atualizar UI
            focoBtn.style.display = "none";
            cronometroContainer.style.display = "block";

            // Iniciar cronômetro
            atualizarCronometro(sessoesId);
            sessoesAtivas[sessoesId].intervalo = setInterval(() => {
                atualizarCronometro(sessoesId);
            }, 1000);

            // Enviar lista de bloqueio para extensão Chrome
            enviarListaBloqueioParaExtensao(sessoesId);

            mostrarMensagem("✅ Modo foco ativado! Bloqueio de sites iniciado.", "sucesso");

        } else {
            mostrarMensagem("❌ Erro ao ativar modo foco: " + data.erro, "erro");
        }
    } catch (erro) {
        mostrarMensagem("❌ Erro de conexão: " + erro, "erro");
    }
}

function atualizarCronometro(sessoesId) {
    const tempoDecorrido = Date.now() - sessoesAtivas[sessoesId].inicio;
    const horas = Math.floor(tempoDecorrido / 3600000);
    const minutos = Math.floor((tempoDecorrido % 3600000) / 60000);
    const segundos = Math.floor((tempoDecorrido % 60000) / 1000);

    cronometroTempo.textContent = 
        String(horas).padStart(2, '0') + ':' +
        String(minutos).padStart(2, '0') + ':' +
        String(segundos).padStart(2, '0');
}

async function encerrarModoFoco() {
    // Pegar a sessão ativa (deve haver apenas uma)
    const sessoesId = Object.keys(sessoesAtivas)[0];
    
    if (!sessoesId) {
        mostrarMensagem("❌ Nenhuma sessão de foco ativa", "erro");
        return;
    }

    try {
        const response = await fetch(`/api/foco/encerrar/${sessoesId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

        const data = await response.json();

        if (data.sucesso) {
            // Parar cronômetro
            clearInterval(sessoesAtivas[sessoesId].intervalo);
            delete sessoesAtivas[sessoesId];

            // Atualizar UI
            focoBtn.style.display = "block";
            cronometroContainer.style.display = "none";
            cronometroTempo.textContent = "00:00:00";
            vezesDistaidoDisplay.textContent = "0";

            // Notificar extensão para desbloquear
            desbloquearSitesNaExtensao();

            mostrarMensagem(
                `✅ ${data.mensagem}\n📊 Tempo: ${data.tempo_minutos}min | Distrações: ${data.vezes_distraido} | XP: +${data.xp_ganho}`,
                "sucesso"
            );
        } else {
            mostrarMensagem("❌ Erro ao encerrar: " + data.erro, "erro");
        }
    } catch (erro) {
        mostrarMensagem("❌ Erro de conexão: " + erro, "erro");
    }
}


// ============================================
// LISTA BLOQUEADA
// ============================================

const adicionarSiteBtn = document.getElementById("adicionarSiteBtn");
const novoSiteInput = document.getElementById("novoSite");
const descricaoSiteInput = document.getElementById("descricaoSite");
const listaSitesContainer = document.getElementById("listaSitesContainer");
const mensagemBlacklist = document.getElementById("mensagemBlacklist");

if (adicionarSiteBtn && novoSiteInput && descricaoSiteInput && listaSitesContainer) {
    adicionarSiteBtn.addEventListener("click", adicionarSite);
    novoSiteInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") adicionarSite();
    });
}

async function adicionarSite() {
    const url = novoSiteInput.value.trim();
    const descricao = descricaoSiteInput.value.trim();

    if (!url) {
        mostrarMensagemBlacklist("⚠️ Digite uma URL válida", "aviso");
        return;
    }

    // Validar URL
    if (!ehUrlValida(url)) {
        mostrarMensagemBlacklist("⚠️ URL inválida. Use: https://exemplo.com", "aviso");
        return;
    }

    try {
        const response = await fetch("/api/blacklist/adicionar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                url: url,
                descricao: descricao || null
            })
        });

        const data = await response.json();

        if (data.sucesso) {
            // Limpar inputs
            novoSiteInput.value = "";
            descricaoSiteInput.value = "";

            // Adicionar à lista visual
            adicionarSiteALista(data.id, data.url, data.descricao);

            // Atualizar extensão se modo foco estiver ativo
            if (Object.keys(sessoesAtivas).length > 0) {
                enviarListaBloqueioParaExtensao(Object.keys(sessoesAtivas)[0]);
            }

            mostrarMensagemBlacklist("✅ " + data.mensagem, "sucesso");
        } else {
            mostrarMensagemBlacklist("❌ " + data.erro, "erro");
        }
    } catch (erro) {
        mostrarMensagemBlacklist("❌ Erro de conexão: " + erro, "erro");
    }
}

function adicionarSiteALista(id, url, descricao) {
    const siteElement = document.createElement("div");
    siteElement.className = "site-item";
    siteElement.id = `site-${id}`;
    siteElement.innerHTML = `
        <div class="site-info">
            <strong>${url}</strong>
            ${descricao ? `<p>${descricao}</p>` : ''}
        </div>
        <button class="btn-remover" onclick="removerSite(${id})">🗑️</button>
    `;
    listaSitesContainer.appendChild(siteElement);
}

async function removerSite(siteId) {
    try {
        const response = await fetch(`/api/blacklist/remover/${siteId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

        const data = await response.json();

        if (data.sucesso) {
            // Remover do DOM
            const elemento = document.getElementById(`site-${siteId}`);
            if (elemento) {
                elemento.remove();
            }

            // Atualizar extensão se modo foco estiver ativo
            if (Object.keys(sessoesAtivas).length > 0) {
                enviarListaBloqueioParaExtensao(Object.keys(sessoesAtivas)[0]);
            }

            mostrarMensagemBlacklist("✅ " + data.mensagem, "sucesso");
        } else {
            mostrarMensagemBlacklist("❌ " + data.erro, "erro");
        }
    } catch (erro) {
        mostrarMensagemBlacklist("❌ Erro de conexão: " + erro, "erro");
    }
}

function ehUrlValida(url) {
    try {
        new URL(url);
        return true;
    } catch (e) {
        return false;
    }
}

// Carregar lista bloqueada ao iniciar
async function carregarListaBloqueada() {
    try {
        const response = await fetch("/api/blacklist/listar");
        const data = await response.json();

        if (data.sucesso) {
            listaSitesContainer.innerHTML = "";
            data.sites.forEach(site => {
                adicionarSiteALista(site.id, site.url, site.descricao);
            });
        }
    } catch (erro) {
        console.error("Erro ao carregar lista bloqueada:", erro);
    }
}

carregarListaBloqueada();


// ============================================
// INTEGRAÇÃO COM EXTENSÃO CHROME
// ============================================

async function enviarListaBloqueioParaExtensao(sessoesId) {
    // Envia a lista de URLs bloqueadas para a extensão Chrome via API.
    // A extensão deve estar ouvindo este evento e fazer o bloqueio.
    try {
        const response = await fetch("/api/blacklist/urls");
        const data = await response.json();

        if (data.sucesso) {
            // Enviar para extensão Chrome via postMessage
            const payload = {
                tipo: "ATIVAR_BLOQUEIO",
                urls: data.urls_bloqueadas,
                sessoesId: sessoesId,
                timestamp: Date.now()
            };

            // Se a extensão estiver injetada, ela receberá esta mensagem
            window.postMessage(payload, "*");

            // Também fazer uma requisição AJAX para o endpoint da extensão (se houver)
            // A extensão pode ter seu próprio servidor local
            try {
                await fetch("http://localhost:3000/api/bloqueio/ativar", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        urls: data.urls_bloqueadas,
                        sessoesId: sessoesId
                    })
                });
            } catch (e) {
                console.log("Extensão Chrome não está respondendo (isto é normal se ainda não foi instalada)");
            }
        }
    } catch (erro) {
        console.error("Erro ao enviar bloqueio para extensão:", erro);
    }
}

function desbloquearSitesNaExtensao() {
    // Notifica a extensão para desbloquear os sites.
    const payload = {
        tipo: "DESATIVAR_BLOQUEIO",
        timestamp: Date.now()
    };

    window.postMessage(payload, "*");

    // Também fazer uma requisição para o servidor da extensão
    try {
        fetch("http://localhost:3000/api/bloqueio/desativar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });
    } catch (e) {
        console.log("Extensão Chrome não está respondendo");
    }
}

// Listener para quando a extensão reportar uma tentativa de acesso a site bloqueado
window.addEventListener("message", async (event) => {
    if (event.source !== window) return;

    if (event.data.tipo === "DISTRACAO_DETECTADA") {
        const sessoesId = event.data.sessoesId;

        if (sessoesId && sessoesAtivas[sessoesId]) {
            try {
                const response = await fetch(`/api/foco/registrar-distracao/${sessoesId}`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    }
                });

                const data = await response.json();

                if (data.sucesso) {
                    sessoesAtivas[sessoesId].vezesDistraido = data.vezes_distraido;
                    vezesDistaidoDisplay.textContent = data.vezes_distraido;
                    
                    vezesDistaidoDisplay.style.animation = "pulse 0.5s";
                    setTimeout(() => {
                        vezesDistaidoDisplay.style.animation = "";
                    }, 500);
                }
            } catch (erro) {
                console.error("Erro ao registrar distração:", erro);
            }
        }
    }
});


// ============================================
// FUNÇÕES AUXILIARES
// ============================================

function mostrarMensagem(mensagem, tipo) {
    const container = document.createElement("div");
    container.className = `alerta alerta-${tipo}`;
    container.textContent = mensagem;
    document.body.appendChild(container);

    setTimeout(() => {
        container.remove();
    }, 4000);
}

function mostrarMensagemBlacklist(mensagem, tipo) {
    mensagemBlacklist.textContent = mensagem;
    mensagemBlacklist.className = `mensagem-blacklist mensagem-${tipo}`;
    mensagemBlacklist.style.display = "block";

    setTimeout(() => {
        mensagemBlacklist.style.display = "none";
    }, 3000);
}


// ============================================
// LOGIN MODAL
// ============================================

const openLogin = document.getElementById("loginBtn");
const closeLogin = document.getElementById("fecharBtn");
const modal = document.getElementById("loginModal");

if (openLogin && modal) {
    function abrirLogin() {
        modal.classList.add("active");
    }

    function fecharLogin() {
        modal.classList.remove("active");
    }

    openLogin.addEventListener("click", abrirLogin);

    if (closeLogin) {
        closeLogin.addEventListener("click", fecharLogin);
    }

    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            fecharLogin();
        }
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            fecharLogin();
        }
    });
}

// ============================================
// BLOCO DE NOTAS E ATAalho CONFIGURAVEL
// ============================================

const notasModal = document.getElementById("notasModal");
const abrirNotasBtn = document.getElementById("abrirNotasBtn");
const fecharNotasBtn = document.getElementById("fecharNotasBtn");
const salvarNotasBtn = document.getElementById("salvarNotasBtn");
const conteudoNotas = document.getElementById("conteudoNotas");
const statusNotas = document.getElementById("statusNotas");
const atalhoNotasResumo = document.getElementById("atalhoNotasResumo");
const configurarAtalhoBtn = document.getElementById("configurarAtalhoBtn");
const configuracaoAtalho = document.getElementById("configuracaoAtalho");
const capturaAtalho = document.getElementById("capturaAtalho");
const salvarAtalhoBtn = document.getElementById("salvarAtalhoBtn");
let atalhoNotas = "CTRL+Y";
let salvamentoNotas;

function formatarAtalho(atalho) {
    return atalho.replace(/\+/g, " + ");
}

function obterCombinacao(evento) {
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

function abrirBlocoNotas() {
    if (!notasModal) return;
    notasModal.classList.add("ativo");
    notasModal.setAttribute("aria-hidden", "false");
    conteudoNotas.focus();
}

async function salvarNotas() {
    if (!conteudoNotas) return;
    statusNotas.textContent = "Salvando...";
    try {
        const response = await fetch("/api/notas", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ conteudo: conteudoNotas.value })
        });
        if (!response.ok) throw new Error("Não foi possível salvar");
        statusNotas.textContent = "Salvo automaticamente";
    } catch (erro) {
        statusNotas.textContent = "Não foi possível salvar";
    }
}

function fecharBlocoNotas() {
    salvarNotas();
    notasModal.classList.remove("ativo");
    notasModal.setAttribute("aria-hidden", "true");
}

async function carregarNotas() {
    if (!notasModal) return;
    try {
        const response = await fetch("/api/notas");
        const data = await response.json();
        if (data.sucesso) {
            conteudoNotas.value = data.conteudo;
            atalhoNotas = data.hotkey || "CTRL+Y";
            atalhoNotasResumo.textContent = formatarAtalho(atalhoNotas);
            if (new URLSearchParams(window.location.search).get("abrir_notas") === "1") {
                abrirBlocoNotas();
            }
        }
    } catch (erro) {
        statusNotas.textContent = "Notas indisponíveis";
    }
}

if (notasModal) {
    carregarNotas();
    abrirNotasBtn.addEventListener("click", abrirBlocoNotas);
    fecharNotasBtn.addEventListener("click", fecharBlocoNotas);
    salvarNotasBtn.addEventListener("click", salvarNotas);
    notasModal.addEventListener("click", (evento) => {
        if (evento.target === notasModal) fecharBlocoNotas();
    });
    conteudoNotas.addEventListener("input", () => {
        clearTimeout(salvamentoNotas);
        salvamentoNotas = setTimeout(salvarNotas, 700);
    });
    configurarAtalhoBtn.addEventListener("click", () => {
        abrirBlocoNotas();
        configuracaoAtalho.hidden = false;
        capturaAtalho.value = "";
        capturaAtalho.focus();
    });
    capturaAtalho.addEventListener("keydown", (evento) => {
        evento.preventDefault();
        const combinacao = obterCombinacao(evento);
        if (combinacao) capturaAtalho.value = combinacao;
    });
    salvarAtalhoBtn.addEventListener("click", async () => {
        if (!capturaAtalho.value) return;
        const response = await fetch("/api/notas", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ hotkey: capturaAtalho.value })
        });
        if (response.ok) {
            atalhoNotas = capturaAtalho.value;
            atalhoNotasResumo.textContent = formatarAtalho(atalhoNotas);
            window.postMessage({ tipo: "ATUALIZAR_HOTKEY", hotkey: atalhoNotas }, "*");
            configuracaoAtalho.hidden = true;
            mostrarMensagem("Atalho atualizado.", "sucesso");
        }
    });
    document.addEventListener("keydown", (evento) => {
        if (obterCombinacao(evento) === atalhoNotas) {
            evento.preventDefault();
            if (notasModal.classList.contains("ativo")) fecharBlocoNotas();
            else abrirBlocoNotas();
        }
        if (evento.key === "Escape" && notasModal.classList.contains("ativo")) fecharBlocoNotas();
    });
}

// ============================================
// ATIVIDADES PROXIMAS
// ============================================

const atividadesLista = document.getElementById("atividadesLista");

function renderizarAtividadesPrincipais(atividades) {
    if (!atividadesLista) return;
    const pendentes = atividades.filter((atividade) => !atividade.concluido);
    if (!pendentes.length) {
        atividadesLista.innerHTML = "<p>Nenhuma atividade pendente.</p>";
        return;
    }
    atividadesLista.innerHTML = pendentes.slice(0, 8).map((atividade) => `
        <button type="button" class="atividade-item" data-estudo-id="${atividade.id}">
            <span><strong>${atividade.titulo}</strong><small>${atividade.data} · ${atividade.duracao_minutos} min</small></span>
            <span class="atividade-xp">+${atividade.xp} XP</span>
        </button>
    `).join("");
    atividadesLista.querySelectorAll(".atividade-item").forEach((botao) => {
        botao.addEventListener("click", async () => {
            botao.disabled = true;
            const resposta = await fetch(`/api/agenda/${botao.dataset.estudoId}/concluir`, { method: "POST" });
            const dados = await resposta.json();
            if (resposta.ok) {
                mostrarMensagem(`Atividade concluída! +${dados.xp_ganho} XP`, "sucesso");
                carregarAtividadesPrincipais();
            } else {
                botao.disabled = false;
                mostrarMensagem(dados.erro || "Não foi possível concluir.", "erro");
            }
        });
    });
}

async function carregarAtividadesPrincipais() {
    if (!atividadesLista) return;
    try {
        const resposta = await fetch("/api/agenda");
        const dados = await resposta.json();
        if (!resposta.ok) throw new Error(dados.erro);
        renderizarAtividadesPrincipais(dados.atividades);
    } catch (erro) {
        atividadesLista.innerHTML = "<p>Não foi possível carregar as atividades.</p>";
    }
}

carregarAtividadesPrincipais();
