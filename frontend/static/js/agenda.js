const calendario = document.getElementById("calendario");
const mesAtual = document.getElementById("mesAtual");
const anoCalendario = document.getElementById("anoCalendario");
const dataAtividade = document.getElementById("dataAtividade");
const dataSelecionadaTexto = document.getElementById("dataSelecionadaTexto");
const atividadeForm = document.getElementById("atividadeForm");
const agendaMensagem = document.getElementById("agendaMensagem");
const lembreteAtividade = document.getElementById("lembreteAtividade");
const lembreteCampos = document.getElementById("lembreteCampos");
const dataHoraLembrete = document.getElementById("dataHoraLembrete");
const notificacaoStatus = document.getElementById("notificacaoStatus");
let dataVisualizada = new Date();
let atividades = [];

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

function selecionarData(data) {
    dataAtividade.value = data;
    const [ano, mes, dia] = data.split("-");
    dataSelecionadaTexto.textContent = `Atividade para ${dia}/${mes}/${ano}`;
    document.querySelectorAll(".dia-calendario.selecionado").forEach((elemento) => elemento.classList.remove("selecionado"));
    const botao = document.querySelector(`[data-date="${data}"]`);
    if (botao) botao.classList.add("selecionado");
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
        const botao = document.createElement("button");
        botao.type = "button";
        botao.className = `dia-calendario${atividadesDoDia.length ? " tem-atividade" : ""}`;
        botao.dataset.date = data;
        botao.innerHTML = `<strong>${dia}</strong><small>${atividadesDoDia.length ? `${atividadesDoDia.length} atividade(s)` : "Adicionar"}</small>`;
        botao.addEventListener("click", () => selecionarData(data));
        calendario.appendChild(botao);
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
atividadeForm.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    if (!dataAtividade.value) {
        agendaMensagem.textContent = "Escolha um dia no calendário.";
        return;
    }
    const enviarBtn = atividadeForm.querySelector('[type="submit"]');
    enviarBtn.disabled = true;
    agendaMensagem.textContent = "";
    try {
        const resposta = await fetch("/api/agenda", {
            method: "POST",
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
        atividades.push(dados.atividade);
        atividadeForm.reset();
        document.getElementById("duracaoAtividade").value = 30;
        lembreteCampos.hidden = true;
        dataHoraLembrete.disabled = true;
        dataHoraLembrete.required = false;
        atualizarStatusNotificacoes();
        agendaMensagem.textContent = dados.atividade.lembrete_em
            ? "Atividade e lembrete adicionados. Mantenha esta página aberta para receber a notificação."
            : "Atividade adicionada à agenda.";
        renderizarCalendario();
        selecionarData(dados.atividade.data);
    } catch (_erro) {
        agendaMensagem.textContent = "Falha de conexão. Verifique sua internet e tente novamente.";
    } finally {
        enviarBtn.disabled = false;
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