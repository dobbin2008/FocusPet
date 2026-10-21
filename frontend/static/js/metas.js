const metasForm = document.getElementById("metasForm");
const metasMensagem = document.getElementById("metasMensagem");
const salvarMetasBtn = document.getElementById("salvarMetasBtn");
const metaDiariaInput = document.getElementById("metaDiaria");
const metaSemanalInput = document.getElementById("metaSemanal");

function formatarTempo(minutos) {
    const horas = Math.floor(minutos / 60);
    const restantes = minutos % 60;
    if (horas && restantes) return `${horas} h ${restantes} min`;
    if (horas) return `${horas} h`;
    return `${restantes} min`;
}

function renderizarProgresso(tipo, dados) {
    const diario = tipo === "diaria";
    const texto = document.getElementById(diario ? "metaDiariaTexto" : "metaSemanalTexto");
    const barra = document.getElementById(diario ? "metaDiariaBarra" : "metaSemanalBarra");
    const status = document.getElementById(diario ? "metaDiariaStatus" : "metaSemanalStatus");
    const bonus = document.getElementById(diario ? "metaDiariaBonus" : "metaSemanalBonus");

    if (!dados.meta_minutos) {
        texto.textContent = "Meta desativada.";
        barra.value = 0;
        status.textContent = "Opcional";
        bonus.textContent = "Configure uma meta para acompanhar seu progresso.";
        return;
    }
    texto.textContent = `${formatarTempo(dados.minutos_estudados)} de ${formatarTempo(dados.meta_minutos)}`;
    barra.value = dados.percentual;
    status.textContent = dados.atingida ? "Meta alcançada!" : `${dados.percentual}%`;
    bonus.textContent = dados.bonus_concedido
        ? `Bônus de +${dados.bonus_xp} XP recebido neste período.`
        : dados.atingida
            ? `Bônus de +${dados.bonus_xp} XP será adicionado ao encerrar a sessão que atingiu a meta.`
            : `Bônus de até +${dados.bonus_xp} XP ao atingir a meta.`;
}

function exibirMetas(dados) {
    metaDiariaInput.value = dados.meta_diaria_minutos;
    metaSemanalInput.value = dados.meta_semanal_minutos;
    renderizarProgresso("diaria", dados.diaria);
    renderizarProgresso("semanal", dados.semanal);
}

async function carregarMetas() {
    const resposta = await fetch("/api/metas");
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro || "Não foi possível carregar suas metas.");
    exibirMetas(dados);
}

metasForm.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    salvarMetasBtn.disabled = true;
    metasMensagem.textContent = "";
    try {
        const resposta = await fetch("/api/metas", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                meta_diaria_minutos: Number(metaDiariaInput.value),
                meta_semanal_minutos: Number(metaSemanalInput.value)
            })
        });
        const dados = await resposta.json();
        if (!resposta.ok) throw new Error(dados.erro || "Não foi possível salvar as metas.");
        exibirMetas(dados);
        metasMensagem.textContent = "Metas salvas.";
    } catch (erro) {
        metasMensagem.textContent = erro.message;
    } finally {
        salvarMetasBtn.disabled = false;
    }
});

carregarMetas().catch((erro) => {
    metasMensagem.textContent = erro.message;
});
