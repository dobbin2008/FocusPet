
// ============================================
// MODO ESCURO / CLARO
// ============================================

const temaBtn = document.getElementById("temaBtn");

function atualizarIcone() {
    if (!temaBtn) return;
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

if (temaBtn) {
    temaBtn.addEventListener("click", () => {
        document.body.classList.toggle("claro");
        localStorage.setItem("tema", document.body.classList.contains("claro") ? "light" : "dark");
        atualizarIcone();
    });
}


// ============================================
// MODO FOCO - CRONÔMETRO
// ============================================

let sessoesAtivas = {}; // { sessaoId: { inicio, intervalo, vezesDistraido } }
const confirmacoesExtensao = new Map();

window.addEventListener("message", (evento) => {
    if (evento.source !== window || evento.origin !== window.location.origin) return;
    if (evento.data?.tipo !== "BLOQUEIO_ATIVADO_RESULTADO") return;
    const resolver = confirmacoesExtensao.get(evento.data.requestId);
    if (!resolver) return;
    confirmacoesExtensao.delete(evento.data.requestId);
    resolver(evento.data);
});

const focoBtn = document.getElementById("focoBtn");
const encerrarFocoBtn = document.getElementById("encerrarFocoBtn");
const cronometroContainer = document.getElementById("cronometroContainer");
const cronometroTempo = document.getElementById("cronometroTempo");
const vezesDistaidoDisplay = document.getElementById("vezesDistraido");
const materiaFocoSelect = document.getElementById("materiaFoco");

if (focoBtn && encerrarFocoBtn) {
    focoBtn.addEventListener("click", iniciarModoFoco);
    encerrarFocoBtn.addEventListener("click", encerrarModoFoco);
    if (materiaFocoSelect) {
        focoBtn.disabled = true;
        carregarMateriasFoco().finally(recuperarSessaoFoco);
    } else {
        recuperarSessaoFoco();
    }
}

async function carregarMateriasFoco() {
    try {
        const response = await fetch("/api/materias");
        const data = await response.json();
        if (!response.ok) throw new Error(data.erro || "Não foi possível carregar as matérias.");
        for (const materia of data.materias) {
            const option = document.createElement("option");
            option.value = materia.id;
            option.textContent = materia.nome;
            materiaFocoSelect.appendChild(option);
        }
    } catch (erro) {
        mostrarMensagem("Não foi possível carregar as matérias; você ainda pode iniciar o foco sem selecionar uma.", "aviso");
    } finally {
        focoBtn.disabled = false;
    }
}

async function iniciarModoFoco() {
    focoBtn.disabled = true;
    try {
        const response = await fetch("/api/foco/iniciar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                materia_id: materiaFocoSelect?.value || null
            })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.erro || "Não foi possível iniciar o modo foco.");

        if (data.sucesso) {
            restaurarSessaoFoco({
                sessao_id: data.sessao_id,
                token_api: data.token_api,
                inicio: data.inicio,
                vezes_distraido: data.vezes_distraido,
                materia_id: data.materia_id
            });
            mostrarMensagem("✅ Modo foco ativado! Bloqueio de sites iniciado.", "sucesso");
        }
    } catch (erro) {
        mostrarMensagem("❌ " + erro.message, "erro");
    } finally {
        focoBtn.disabled = false;
    }
}

function restaurarSessaoFoco(sessao) {
    const sessoesId = String(sessao.sessao_id);
    const inicio = sessao.inicio.endsWith("Z") ? sessao.inicio : `${sessao.inicio}Z`;
    const inicioTimestamp = Date.parse(inicio);
    if (!Number.isFinite(inicioTimestamp)) {
        throw new Error("Não foi possível recuperar o horário da sessão de foco.");
    }
    sessoesAtivas[sessoesId] = {
        inicio: inicioTimestamp,
        intervalo: null,
        vezesDistraido: sessao.vezes_distraido || 0,
        sessoesId,
        tokenApi: sessao.token_api
    };
    if (materiaFocoSelect) {
        materiaFocoSelect.value = sessao.materia_id ? String(sessao.materia_id) : "";
        materiaFocoSelect.disabled = true;
    }
    focoBtn.style.display = "none";
    cronometroContainer.style.display = "block";
    vezesDistaidoDisplay.textContent = sessoesAtivas[sessoesId].vezesDistraido;
    atualizarCronometro(sessoesId);
    sessoesAtivas[sessoesId].intervalo = setInterval(() => {
        atualizarCronometro(sessoesId);
    }, 1000);
    enviarListaBloqueioParaExtensao(sessoesId);
}

async function recuperarSessaoFoco() {
    try {
        const response = await fetch("/api/foco/ativa");
        const contentType = response.headers.get("content-type") || "";
        if (!contentType.includes("application/json")) {
            if (response.status === 404) {
                throw new Error("A rota nova ainda não foi carregada. Reinicie o servidor Flask.");
            }
            throw new Error(`A API respondeu de forma inesperada (HTTP ${response.status}).`);
        }
        const data = await response.json();
        if (!response.ok) throw new Error(data.erro || "Não foi possível consultar a sessão de foco.");
        if (data.sessao) restaurarSessaoFoco(data.sessao);
    } catch (erro) {
        mostrarMensagem("❌ " + erro.message, "erro");
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
            focoBtn.disabled = false;
            cronometroContainer.style.display = "none";
            cronometroTempo.textContent = "00:00:00";
            vezesDistaidoDisplay.textContent = "0";
            if (materiaFocoSelect) {
                materiaFocoSelect.disabled = false;
                materiaFocoSelect.value = "";
            }

            // Notificar extensão para desbloquear
            desbloquearSitesNaExtensao();

            mostrarMensagem(
                `✅ ${data.mensagem}\n📊 Tempo: ${data.tempo_minutos}min | Distrações: ${data.vezes_distraido} | XP: +${data.xp_ganho}${data.xp_bonus_meta ? ` (inclui +${data.xp_bonus_meta} XP de bônus da meta)` : ""}`,
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

            mostrarMensagemBlacklist("✅ Site adicionado à lista bloqueada.", "sucesso");
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
    const siteInfo = document.createElement("div");
    siteInfo.className = "site-info";
    const siteUrl = document.createElement("strong");
    siteUrl.textContent = url;
    siteInfo.appendChild(siteUrl);
    if (descricao) {
        const descricaoTexto = document.createElement("p");
        descricaoTexto.textContent = descricao;
        siteInfo.appendChild(descricaoTexto);
    }
    const removerBtn = document.createElement("button");
    removerBtn.type = "button";
    removerBtn.className = "btn-remover";
    removerBtn.textContent = "Remover";
    removerBtn.setAttribute("aria-label", "Remover site");
    removerBtn.addEventListener("click", () => removerSite(id));
    siteElement.append(siteInfo, removerBtn);
    listaSitesContainer.appendChild(siteElement);
}

async function removerSite(siteId) {
    try {
        const response = await fetch(`/api/blacklist/remover/${siteId}`, {
            method: "DELETE",
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

            mostrarMensagemBlacklist("✅ Site removido da lista bloqueada.", "sucesso");
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
    if (!listaSitesContainer) return;
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
    try {
        const response = await fetch("/api/blacklist/urls");
        const data = await response.json();

        if (data.sucesso) {
            const requestId = crypto.randomUUID();
            const payload = {
                tipo: "ATIVAR_BLOQUEIO",
                urls: data.urls_bloqueadas,
                sessoesId: sessoesId,
                tokenApi: sessoesAtivas[sessoesId]?.tokenApi,
                requestId
            };
            const confirmacao = new Promise((resolver) => {
                const timeout = setTimeout(() => {
                    confirmacoesExtensao.delete(requestId);
                    resolver({ sucesso: false, mensagem: "A extensão Chrome não respondeu." });
                }, 2000);
                confirmacoesExtensao.set(requestId, (resultado) => {
                    clearTimeout(timeout);
                    resolver(resultado);
                });
            });
            window.postMessage(payload, window.location.origin);
            const resultado = await confirmacao;
            if (!resultado.sucesso) {
                mostrarMensagem(
                    "A extensão de bloqueio não respondeu. Abra chrome://extensions, confira se Study Buddy Blocker está ativada e clique em Recarregar.",
                    "aviso"
                );
            }
        }
    } catch (erro) {
        mostrarMensagem("Não foi possível carregar a lista para o bloqueador: " + erro.message, "erro");
    }
}

function desbloquearSitesNaExtensao() {
    // Notifica a extensão para desbloquear os sites.
    const payload = {
        tipo: "DESATIVAR_BLOQUEIO",
        timestamp: Date.now()
    };

    window.postMessage(payload, window.location.origin);
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
const tituloNota = document.getElementById("tituloNota");
const conteudoNotas = document.getElementById("conteudoNotas");
const statusNotas = document.getElementById("statusNotas");
const notasLista = document.getElementById("notasLista");
const novaNotaForm = document.getElementById("novaNotaForm");
const novaNotaTitulo = document.getElementById("novaNotaTitulo");
const excluirNotaBtn = document.getElementById("excluirNotaBtn");
const atalhoNotasResumo = document.getElementById("atalhoNotasResumo");
const configurarAtalhoBtn = document.getElementById("configurarAtalhoBtn");
const configuracaoAtalho = document.getElementById("configuracaoAtalho");
const capturaAtalho = document.getElementById("capturaAtalho");
const salvarAtalhoBtn = document.getElementById("salvarAtalhoBtn");
let atalhoNotas = "CTRL+Y";
let notaAtualId = null;
let notaAlterada = false;
let notasSalvamentoPendente;
let salvamentoNotaEmAndamento;

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
    tituloNota.focus();
}

function salvarNotas() {
    if (!notaAtualId || !notaAlterada) return Promise.resolve(true);
    if (salvamentoNotaEmAndamento) return salvamentoNotaEmAndamento;
    const notaId = notaAtualId;
    const tituloEnviado = tituloNota.value;
    const conteudoEnviado = conteudoNotas.value;
    salvarNotasBtn.disabled = true;
    statusNotas.textContent = "Salvando...";
    salvamentoNotaEmAndamento = (async () => {
      try {
        const response = await fetch(`/api/notas/${notaId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ titulo: tituloEnviado, conteudo: conteudoEnviado })
        });
        const resultado = await response.json();
        if (!response.ok) throw new Error(resultado.erro || "Não foi possível salvar a nota.");
        if (notaAtualId === notaId) {
            notaAlterada = tituloNota.value !== tituloEnviado || conteudoNotas.value !== conteudoEnviado;
            statusNotas.textContent = notaAlterada ? "Salvando alterações..." : "Nota salva.";
            await carregarListaNotas(notaId, false);
        }
        return true;
      } catch (erro) {
        statusNotas.textContent = erro.message;
        return false;
      }
    })();
    return salvamentoNotaEmAndamento.then((salvou) => {
      salvamentoNotaEmAndamento = null;
      salvarNotasBtn.disabled = !notaAtualId || !notaAlterada;
      if (notaAlterada) {
        clearTimeout(notasSalvamentoPendente);
        notasSalvamentoPendente = setTimeout(salvarNotas, 900);
      }
      return salvou && !notaAlterada;
    }, (erro) => {
      salvamentoNotaEmAndamento = null;
      salvarNotasBtn.disabled = !notaAtualId || !notaAlterada;
      throw erro;
    });
}

async function fecharBlocoNotas() {
    const salvou = await salvarNotas();
    if (!salvou) return;
    notasModal.classList.remove("ativo");
    notasModal.setAttribute("aria-hidden", "true");
}

function marcarNotaAlterada() {
    if (!notaAtualId) return;
    notaAlterada = true;
    statusNotas.textContent = "Alterações não salvas.";
    salvarNotasBtn.disabled = false;
    clearTimeout(notasSalvamentoPendente);
    notasSalvamentoPendente = setTimeout(salvarNotas, 900);
}

function selecionarNotaNaLista(notaId) {
    notasLista.querySelectorAll("[data-nota-id]").forEach((botao) => {
        botao.classList.toggle("nota-selecionada", Number(botao.dataset.notaId) === notaId);
    });
}

async function abrirNota(notaId, salvarAntes = true) {
    if (salvarAntes && !(await salvarNotas())) return;
    try {
        const response = await fetch(`/api/notas/${notaId}`);
        const resultado = await response.json();
        if (!response.ok) throw new Error(resultado.erro || "Não foi possível abrir a nota.");
        notaAtualId = resultado.nota.id;
        tituloNota.value = resultado.nota.titulo;
        conteudoNotas.value = resultado.nota.conteudo;
        notaAlterada = false;
        tituloNota.disabled = false;
        conteudoNotas.disabled = false;
        salvarNotasBtn.disabled = false;
        excluirNotaBtn.disabled = false;
        statusNotas.textContent = "Nota salva.";
        selecionarNotaNaLista(notaAtualId);
    } catch (erro) {
        statusNotas.textContent = erro.message;
    }
}

async function carregarListaNotas(notaSelecionada = null, abrirSelecionada = true) {
    const response = await fetch("/api/notas");
    const resultado = await response.json();
    if (!response.ok) throw new Error(resultado.erro || "Não foi possível carregar as notas.");
    atalhoNotas = resultado.hotkey || "CTRL+Y";
    atalhoNotasResumo.textContent = formatarAtalho(atalhoNotas);
    notasLista.replaceChildren();
    if (!resultado.notas.length) {
        const vazio = document.createElement("p");
        vazio.className = "notas-vazio";
        vazio.textContent = "Crie uma nota para começar.";
        notasLista.appendChild(vazio);
        notaAtualId = null;
        tituloNota.value = "";
        conteudoNotas.value = "";
        tituloNota.disabled = true;
        conteudoNotas.disabled = true;
        salvarNotasBtn.disabled = true;
        excluirNotaBtn.disabled = true;
        notaAlterada = false;
        return;
    }
    resultado.notas.forEach((nota) => {
        const botao = document.createElement("button");
        botao.type = "button";
        botao.className = "nota-lista-item";
        botao.dataset.notaId = nota.id;
        botao.textContent = nota.titulo;
        botao.addEventListener("click", () => abrirNota(nota.id));
        notasLista.appendChild(botao);
    });
    const idParaAbrir = notaSelecionada ?? notaAtualId ?? resultado.notas[0].id;
    if (abrirSelecionada && resultado.notas.some((nota) => nota.id === idParaAbrir)) {
        await abrirNota(idParaAbrir);
    } else {
        selecionarNotaNaLista(notaAtualId);
    }
}

if (notasModal) {
    carregarListaNotas().catch((erro) => { statusNotas.textContent = erro.message; });
    abrirNotasBtn.addEventListener("click", async () => {
        try {
            await carregarListaNotas();
            abrirBlocoNotas();
        } catch (erro) {
            statusNotas.textContent = erro.message;
        }
    });
    fecharNotasBtn.addEventListener("click", fecharBlocoNotas);
    salvarNotasBtn.addEventListener("click", salvarNotas);
    notasModal.addEventListener("click", (evento) => {
        if (evento.target === notasModal) fecharBlocoNotas();
    });
    tituloNota.addEventListener("input", marcarNotaAlterada);
    conteudoNotas.addEventListener("input", marcarNotaAlterada);
    novaNotaForm.addEventListener("submit", async (evento) => {
        evento.preventDefault();
        if (!(await salvarNotas())) return;
        const botao = novaNotaForm.querySelector('[type="submit"]');
        botao.disabled = true;
        try {
            const response = await fetch("/api/notas", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ titulo: novaNotaTitulo.value })
            });
            const resultado = await response.json();
            if (!response.ok) throw new Error(resultado.erro || "Não foi possível criar a nota.");
            novaNotaForm.reset();
            notaAtualId = resultado.nota.id;
            await carregarListaNotas(resultado.nota.id);
            tituloNota.focus();
        } catch (erro) {
            statusNotas.textContent = erro.message;
        } finally {
            botao.disabled = false;
        }
    });
    excluirNotaBtn.addEventListener("click", async () => {
        if (!notaAtualId || !window.confirm(`Excluir a nota "${tituloNota.value}"?`)) return;
        if (!(await salvarNotas())) return;
        const notaExcluidaId = notaAtualId;
        try {
            const response = await fetch(`/api/notas/${notaExcluidaId}`, { method: "DELETE" });
            const resultado = await response.json();
            if (!response.ok) throw new Error(resultado.erro || "Não foi possível excluir a nota.");
            notaAtualId = null;
            notaAlterada = false;
            await carregarListaNotas();
            statusNotas.textContent = "Nota excluída.";
        } catch (erro) {
            statusNotas.textContent = erro.message;
        }
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
        const response = await fetch("/api/notas/atalho", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ hotkey: capturaAtalho.value })
        });
        if (response.ok) {
            const resultado = await response.json();
            atalhoNotas = resultado.hotkey;
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
            else abrirNotasBtn?.click();
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
        const vazio = document.createElement("p");
        vazio.textContent = "Nenhuma atividade pendente.";
        atividadesLista.replaceChildren(vazio);
        return;
    }
    const botoes = pendentes.slice(0, 8).map((atividade) => {
        const botao = document.createElement("button");
        botao.type = "button";
        botao.className = "atividade-item";
        botao.dataset.estudoId = atividade.id;
        const informacoes = document.createElement("span");
        const titulo = document.createElement("strong");
        titulo.textContent = atividade.titulo;
        const detalhes = document.createElement("small");
        detalhes.textContent = `${atividade.data} · ${atividade.duracao_minutos} min`;
        informacoes.append(titulo, detalhes);
        const xp = document.createElement("span");
        xp.className = "atividade-xp";
        xp.textContent = `+${atividade.xp} XP`;
        botao.append(informacoes, xp);
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
        return botao;
    });
    atividadesLista.replaceChildren(...botoes);
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
