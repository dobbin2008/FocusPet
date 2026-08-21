const calendario = document.getElementById("calendario");
const mesAtual = document.getElementById("mesAtual");
const anoCalendario = document.getElementById("anoCalendario");
const dataAtividade = document.getElementById("dataAtividade");
const dataSelecionadaTexto = document.getElementById("dataSelecionadaTexto");
const atividadeForm = document.getElementById("atividadeForm");
const agendaMensagem = document.getElementById("agendaMensagem");
let dataVisualizada = new Date();
let atividades = [];

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

async function carregarAtividades() {
    const resposta = await fetch("/api/agenda");
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro || "Não foi possível carregar a agenda");
    atividades = dados.atividades;
    renderizarCalendario();
}

document.getElementById("mesAnteriorBtn").addEventListener("click", () => {
    dataVisualizada.setMonth(dataVisualizada.getMonth() - 1);
    renderizarCalendario();
});
document.getElementById("proximoMesBtn").addEventListener("click", () => {
    dataVisualizada.setMonth(dataVisualizada.getMonth() + 1);
    renderizarCalendario();
});
anoCalendario.addEventListener("change", () => {
    dataVisualizada.setFullYear(Number(anoCalendario.value));
    renderizarCalendario();
});
atividadeForm.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    if (!dataAtividade.value) {
        agendaMensagem.textContent = "Escolha um dia no calendário.";
        return;
    }
    const resposta = await fetch("/api/agenda", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            data: dataAtividade.value,
            titulo: document.getElementById("tituloAtividade").value,
            duracao_minutos: document.getElementById("duracaoAtividade").value
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
    agendaMensagem.textContent = "Atividade adicionada à agenda.";
    renderizarCalendario();
    selecionarData(dados.atividade.data);
});

carregarAtividades().catch((erro) => { agendaMensagem.textContent = erro.message; });