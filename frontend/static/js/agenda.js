const calendario = document.getElementById("calendario");
const mesAtual = document.getElementById("mesAtual");
const anoCalendario = document.getElementById("anoCalendario");
const dataAtividade = document.getElementById("dataAtividade");
const dataSelecionadaTexto = document.getElementById("dataSelecionadaTexto");
const atividadeForm = document.getElementById("atividadeForm");
const agendaMensagem = document.getElementById("agendaMensagem");
const atividadesDiaLista = document.getElementById("atividadesDiaLista");
const atividadeFormTitulo = document.getElementById("atividadeFormTitulo");
const salvarAtividadeBtn = document.getElementById("salvarAtividadeBtn");
const cancelarEdicaoBtn = document.getElementById("cancelarEdicaoBtn");
const lembreteAtividade = document.getElementById("lembreteAtividade");
const lembreteCampos = document.getElementById("lembreteCampos");
const dataHoraLembrete = document.getElementById("dataHoraLembrete");
const notificacaoStatus = document.getElementById("notificacaoStatus");
let dataVisualizada = new Date();
let atividades = [];
let atividadeEmEdicao = null;
let dataSelecionada = "";

function valorDataHoraLocal(data) {
    const fuso = data.getTimezoneOffset() * 60000;
    return new Date(data.getTime() - fuso).toISOString().slice(0, 16);
}

function atualizarStatusNotificacoes() {
    if (!("Notification" in window)) {
        notificacaoStatus.textContent = "Este navegador não oferece notificações na área de trabalho.";
    } else if (Notification.permission === "granted") {
        notificacaoStatus.textContent = "Notificações ativadas. Mantenha a agenda aberta para receber os lembretes.";
    } else if (Notification.permission === "denied") {
        notificacaoStatus.textContent = "Notificações bloqueadas pelo navegador. Altere a permissão do site nas configurações do navegador.";
    } else {
        notificacaoStatus.textContent = "Ao ativar um lembrete, o navegador solicitará permissão para mostrar notificações.";
    }
}

async function solicitarPermissaoNotificacoes() {
    if (!("Notification" in window)) {
        atualizarStatusNotificacoes();
        return;
    }
    if (Notification.permission === "default") {
        try {
            await Notification.requestPermission();
        } catch (erro) {
            console.warn("Não foi possível solicitar permissão para notificações:", erro);
        }
    }
    atualizarStatusNotificacoes();
}

lembreteAtividade.addEventListener("change", async () => {
    lembreteCampos.hidden = !lembreteAtividade.checked;
    dataHoraLembrete.disabled = !lembreteAtividade.checked;
    dataHoraLembrete.required = lembreteAtividade.checked;
    if (lembreteAtividade.checked) {
        dataHoraLembrete.min = valorDataHoraLocal(new Date());
        await solicitarPermissaoNotificacoes();
        dataHoraLembrete.focus();
    } else {
        dataHoraLembrete.value = "";
    }
});

function dataIso(ano, mes, dia) {
    return `${ano}-${String(mes + 1).padStart(2, "0")}-${String(dia).padStart(2, "0")}`;
}

function dataHojeIso() {
    const hoje = new Date();
    return dataIso(hoje.getFullYear(), hoje.getMonth(), hoje.getDate());
}

function atualizarEstadoBotaoSalvar() {
    salvarAtividadeBtn.disabled = Boolean(
        dataSelecionada &&
        dataSelecionada < dataHojeIso() &&
        atividadeEmEdicao === null
    );
}

function selecionarData(data) {
    dataSelecionada = data;
    dataAtividade.value = data;
    atualizarEstadoBotaoSalvar();
    const [ano, mes, dia] = data.split("-");
    dataSelecionadaTexto.textContent = `Atividades de ${dia}/${mes}/${ano}`;
    if (data < dataHojeIso() && atividadeEmEdicao === null) {
        agendaMensagem.textContent = "Não é possível criar atividades em dias que já passaram.";
    }
    document.querySelectorAll(".dia-calendario.selecionado").forEach((elemento) => elemento.classList.remove("selecionado"));
    const botao = document.querySelector(`[data-date="${data}"]`);
    if (botao) botao.classList.add("selecionado");
    renderizarAtividadesDoDia();
    document.getElementById("tituloAtividade").focus();
}

function renderizarCalendario() {
    const ano = dataVisualizada.getFullYear();
    const mes = dataVisualizada.getMonth();
    mesAtual.textContent = dataVisualizada.toLocaleDateString("pt-BR", { month: "long" }).replace(/^./, (letra) => letra.toUpperCase());
    anoCalendario.value = ano;
    calendario.innerHTML = "";
    const primeiroDia = new Date(ano, mes, 1).getDay();
    const totalDias = new Date(ano, mes + 1, 0).getDate();
    for (let vazio = 0; vazio < primeiroDia; vazio += 1) calendario.appendChild(document.createElement("span"));
    for (let dia = 1; dia <= totalDias; dia += 1) {
        const data = dataIso(ano, mes, dia);
        const atividadesDoDia = atividades.filter((atividade) => atividade.data === data);
        const pendentes = atividadesDoDia.filter((atividade) => !atividade.concluido).length;
        const botao = document.createElement("button");
        botao.type = "button";
        botao.className = `dia-calendario${pendentes ? " tem-atividade" : ""}${atividadesDoDia.length && !pendentes ? " atividade-concluida" : ""}`;
        botao.dataset.date = data;
        const numero = document.createElement("strong");
        numero.textContent = dia;
        const resumo = document.createElement("small");
        resumo.textContent = pendentes
            ? `${pendentes} pendente(s)`
            : atividadesDoDia.length
                ? "Concluída"
                : "Adicionar";
        botao.append(numero, resumo);
        botao.addEventListener("click", () => selecionarData(data));
        calendario.appendChild(botao);
    }
    if (dataSelecionada) {
        const selecionado = document.querySelector(`[data-date="${dataSelecionada}"]`);
        if (selecionado) selecionado.classList.add("selecionado");
    }
}

function criarBotaoAcao(rotulo, acao, desabilitado = false) {
    const botao = document.createElement("button");
    botao.type = "button";
    botao.className = "atividade-acao-btn";
    botao.textContent = rotulo;
    botao.disabled = desabilitado;
    botao.addEventListener("click", acao);
    return botao;
}

function renderizarAtividadesDoDia() {
    if (!dataSelecionada) {
        atividadesDiaLista.replaceChildren();
        const vazio = document.createElement("p");
        vazio.className = "agenda-empty";
        vazio.textContent = "Selecione um dia no calendário para ver as atividades.";
        atividadesDiaLista.appendChild(vazio);
        return;
    }
    const atividadesDoDia = atividades
        .filter((atividade) => atividade.data === dataSelecionada)
        .sort((a, b) => a.id - b.id);
    if (!atividadesDoDia.length) {
        const vazio = document.createElement("p");
        vazio.className = "agenda-empty";
        vazio.textContent = "Nenhuma atividade neste dia.";
        atividadesDiaLista.replaceChildren(vazio);
        return;
    }

    const cards = atividadesDoDia.map((atividade) => {
        const card = document.createElement("article");
        card.className = `agenda-atividade-card${atividade.concluido ? " concluida" : ""}`;
        const info = document.createElement("div");
        info.className = "agenda-atividade-info";
        const titulo = document.createElement("strong");
        titulo.textContent = atividade.titulo;
        const detalhes = document.createElement("small");
        detalhes.textContent = atividade.concluido
            ? `Concluída · ${atividade.duracao_minutos} min · ${atividade.xp} XP`
            : `${atividade.duracao_minutos} min${atividade.lembrete_em ? " · Lembrete configurado" : ""}`;
        info.append(titulo, detalhes);
        card.appendChild(info);
        const acoes = document.createElement("div");
        acoes.className = "agenda-atividade-acoes";
        if (!atividade.concluido) {
            acoes.append(
                criarBotaoAcao("Concluir", () => concluirAtividade(atividade.id)),
                criarBotaoAcao("Editar", () => iniciarEdicao(atividade))
            );
        }
        acoes.appendChild(criarBotaoAcao("Excluir", () => excluirAtividade(atividade.id)));
        card.appendChild(acoes);
        return card;
    });
    atividadesDiaLista.replaceChildren(...cards);
}

function iniciarEdicao(atividade) {
    atividadeEmEdicao = atividade.id;
    selecionarData(atividade.data);
    document.getElementById("tituloAtividade").value = atividade.titulo;
    document.getElementById("duracaoAtividade").value = atividade.duracao_minutos;
    lembreteAtividade.checked = Boolean(atividade.lembrete_em);
    lembreteCampos.hidden = !lembreteAtividade.checked;
    dataHoraLembrete.disabled = !lembreteAtividade.checked;
    dataHoraLembrete.required = lembreteAtividade.checked;
    dataHoraLembrete.value = atividade.lembrete_em
        ? valorDataHoraLocal(new Date(atividade.lembrete_em))
        : "";
    atividadeFormTitulo.textContent = "Editar atividade";
    salvarAtividadeBtn.textContent = "Salvar alterações";
    cancelarEdicaoBtn.hidden = false;
    document.getElementById("tituloAtividade").focus();
}

function limparEdicao() {
    atividadeEmEdicao = null;
    atividadeForm.reset();
    dataAtividade.value = dataSelecionada;
    atualizarEstadoBotaoSalvar();
    document.getElementById("duracaoAtividade").value = 30;
    lembreteCampos.hidden = true;
    dataHoraLembrete.disabled = true;
    dataHoraLembrete.required = false;
    atividadeFormTitulo.textContent = "Nova atividade";
    salvarAtividadeBtn.textContent = "Adicionar atividade";
    cancelarEdicaoBtn.hidden = true;
}

async function concluirAtividade(id) {
    try {
        const resposta = await fetch(`/api/agenda/${id}/concluir`, { method: "POST" });
        const dados = await resposta.json();
        if (!resposta.ok) throw new Error(dados.erro || "Não foi possível concluir a atividade.");
        await carregarAtividades();
        agendaMensagem.textContent = `Atividade concluída! +${dados.xp_ganho} XP.`;
    } catch (erro) {
        agendaMensagem.textContent = erro.message;
    }
}

async function excluirAtividade(id) {
    const atividade = atividades.find((item) => item.id === id);
    const confirmacao = atividade?.concluido
        ? "Remover esta atividade da agenda? O registro de conclusão e o XP serão preservados."
        : "Deseja excluir esta atividade pendente?";
    if (!window.confirm(confirmacao)) return;
    try {
        const resposta = await fetch(`/api/agenda/${id}`, { method: "DELETE" });
        const dados = await resposta.json();
        if (!resposta.ok) throw new Error(dados.erro || "Não foi possível excluir a atividade.");
        if (atividadeEmEdicao === id) limparEdicao();
        await carregarAtividades();
        agendaMensagem.textContent = "Atividade excluída.";
    } catch (erro) {
        agendaMensagem.textContent = erro.message;
    }
}

function navegarMes(deslocamento) {
    dataVisualizada.setDate(1);
    dataVisualizada.setMonth(dataVisualizada.getMonth() + deslocamento);
    renderizarCalendario();
}

async function carregarAtividades() {
    const resposta = await fetch("/api/agenda");
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro || "Não foi possível carregar a agenda");
    atividades = dados.atividades;
    renderizarCalendario();
    renderizarAtividadesDoDia();
}

document.getElementById("mesAnteriorBtn").addEventListener("click", () => {
    navegarMes(-1);
});
document.getElementById("proximoMesBtn").addEventListener("click", () => {
    navegarMes(1);
});
anoCalendario.addEventListener("change", () => {
    const ano = Number(anoCalendario.value);
    if (!Number.isInteger(ano) || ano < 2000 || ano > 2100) {
        agendaMensagem.textContent = "Informe um ano entre 2000 e 2100.";
        anoCalendario.value = dataVisualizada.getFullYear();
        return;
    }
    dataVisualizada.setFullYear(ano);
    renderizarCalendario();
});
cancelarEdicaoBtn.addEventListener("click", limparEdicao);
atividadeForm.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const estaEditando = atividadeEmEdicao !== null;
    if (!dataAtividade.value) {
        agendaMensagem.textContent = "Escolha um dia no calendário.";
        return;
    }
    if (!estaEditando && dataAtividade.value < dataHojeIso()) {
        agendaMensagem.textContent = "Não é possível criar atividades em dias que já passaram.";
        return;
    }
    const enviarBtn = atividadeForm.querySelector('[type="submit"]');
    enviarBtn.disabled = true;
    agendaMensagem.textContent = "";
    try {
        const url = estaEditando
            ? `/api/agenda/${atividadeEmEdicao}`
            : "/api/agenda";
        const resposta = await fetch(url, {
            method: estaEditando ? "PATCH" : "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                data: dataAtividade.value,
                titulo: document.getElementById("tituloAtividade").value,
                duracao_minutos: document.getElementById("duracaoAtividade").value,
                lembrete_em: lembreteAtividade.checked
                    ? new Date(dataHoraLembrete.value).toISOString()
                    : null
            })
        });
        const dados = await resposta.json();
        if (!resposta.ok) {
            agendaMensagem.textContent = dados.erro || "Não foi possível adicionar.";
            return;
        }
        if (estaEditando) {
            atividades = atividades.map((atividade) =>
                atividade.id === dados.atividade.id ? dados.atividade : atividade
            );
        } else {
            atividades.push(dados.atividade);
        }
        limparEdicao();
        atualizarStatusNotificacoes();
        agendaMensagem.textContent = estaEditando
            ? "Atividade atualizada."
            : dados.atividade.lembrete_em
                ? "Atividade e lembrete adicionados. Mantenha esta página aberta para receber a notificação."
                : "Atividade adicionada à agenda.";
        renderizarCalendario();
        renderizarAtividadesDoDia();
        selecionarData(dados.atividade.data);
    } catch (_erro) {
        agendaMensagem.textContent = "Falha de conexão. Verifique sua internet e tente novamente.";
    } finally {
        atualizarEstadoBotaoSalvar();
    }
});

async function verificarLembretes() {
    if (!("Notification" in window) || Notification.permission !== "granted") return;
    const resposta = await fetch("/api/agenda/lembretes-vencidos");
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro || "Não foi possível consultar os lembretes.");

    for (const lembrete of dados.lembretes) {
        try {
            const notificacao = new Notification("Study Buddy — lembrete de estudo", {
                body: lembrete.titulo,
                tag: `study-buddy-lembrete-${lembrete.id}`
            });
            notificacao.addEventListener("click", () => {
                window.focus();
                notificacao.close();
            });
            const confirmacao = await fetch(
                `/api/agenda/${lembrete.id}/lembrete-enviado`,
                { method: "POST" }
            );
            if (!confirmacao.ok) {
                throw new Error("Não foi possível confirmar o envio do lembrete.");
            }
        } catch (erro) {
            console.error(`Falha ao exibir o lembrete da atividade ${lembrete.id}:`, erro);
        }
    }
}

atualizarStatusNotificacoes();
renderizarCalendario();
renderizarAtividadesDoDia();
carregarAtividades().catch((erro) => { agendaMensagem.textContent = erro.message; });
verificarLembretes().catch((erro) => console.error("Falha ao consultar lembretes:", erro));
setInterval(() => {
    verificarLembretes().catch((erro) => console.error("Falha ao consultar lembretes:", erro));
}, 15000);
document.addEventListener("visibilitychange", () => {
    if (!document.hidden) {
        verificarLembretes().catch((erro) => console.error("Falha ao consultar lembretes:", erro));
    }
});