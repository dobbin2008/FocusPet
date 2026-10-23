const summaryPeriod = document.getElementById("summaryPeriod");
const summaryMessage = document.getElementById("summaryMessage");
const summaryMetrics = document.getElementById("summaryMetrics");

function formatarDataResumo(valor) {
    return new Date(`${valor}T12:00:00`).toLocaleDateString("pt-BR");
}

async function carregarResumoSemanal() {
    try {
        const resposta = await fetch("/api/resumo-semanal");
        const dados = await resposta.json();
        if (!resposta.ok) throw new Error(dados.erro || "Não foi possível carregar o resumo.");

        const ultimoDia = new Date(`${dados.fim}T12:00:00`);
        ultimoDia.setDate(ultimoDia.getDate() - 1);
        summaryPeriod.textContent =
            `${formatarDataResumo(dados.inicio)} a ${ultimoDia.toLocaleDateString("pt-BR")}`;
        document.getElementById("summaryHours").textContent =
            `${Number(dados.horas_estudadas).toFixed(1)} h`;
        document.getElementById("summaryXp").textContent = `${dados.xp_ganho} XP`;
        document.getElementById("summaryDistractions").textContent = dados.vezes_distraido;
        document.getElementById("summaryPetXp").textContent = `${dados.progresso_pet} XP`;
        summaryMetrics.hidden = false;
    } catch (erro) {
        summaryPeriod.textContent = "";
        summaryMessage.textContent = erro.message;
    }
}

carregarResumoSemanal();
