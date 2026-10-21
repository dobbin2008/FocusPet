const historicoFiltros = document.getElementById("historicoFiltros");
const filtroInicio = document.getElementById("filtroInicio");
const filtroFim = document.getElementById("filtroFim");
const historicoSessoes = document.getElementById("historicoSessoes");
const historicoMensagem = document.getElementById("historicoMensagem");
const historicoVazio = document.getElementById("historicoVazio");
const detalheDialog = document.getElementById("detalheSessaoDialog");

function formatarDataHora(valor) {
    if (!valor) return "—";
    return new Date(`${valor}Z`).toLocaleString("pt-BR", {
        dateStyle: "short",
        timeStyle: "short"
    });
}

function formatarDuracao(minutos) {
    const horas = Math.floor(minutos / 60);
    const resto = minutos % 60;
    return horas ? `${horas} h ${resto} min` : `${resto} min`;
}

async function carregarHistorico(evento) {
    evento?.preventDefault();
    historicoMensagem.textContent = "";
    historicoSessoes.replaceChildren();
    historicoVazio.hidden = true;

    const parametros = new URLSearchParams();
    if (filtroInicio.value) parametros.set("inicio", filtroInicio.value);
    if (filtroFim.value) parametros.set("fim", filtroFim.value);

    try {
        const resposta = await fetch(`/api/foco/historico?${parametros}`);
        const dados = await resposta.json();
        if (!resposta.ok) throw new Error(dados.erro || "Não foi possível carregar o histórico.");

        dados.sessoes.forEach((sessao) => {
            const linha = document.createElement("tr");
            const valores = [
                formatarDataHora(sessao.inicio),
                formatarDuracao(sessao.duracao_minutos),
                String(sessao.vezes_distraido),
                `${sessao.xp_ganho} XP`
            ];
            for (const valor of valores) {
                const celula = document.createElement("td");
                celula.textContent = valor;
                linha.appendChild(celula);
            }
            const celulaDetalhes = document.createElement("td");
            const botao = document.createElement("button");
            botao.type = "button";
            botao.className = "atalho-btn";
            botao.textContent = "Detalhes";
            botao.addEventListener("click", () => mostrarDetalhes(sessao.id));
            celulaDetalhes.appendChild(botao);
            linha.appendChild(celulaDetalhes);
            historicoSessoes.appendChild(linha);
        });
        historicoVazio.hidden = dados.sessoes.length !== 0;
    } catch (erro) {
        historicoMensagem.textContent = erro.message;
    }
}

async function mostrarDetalhes(sessaoId) {
    historicoMensagem.textContent = "";
    try {
        const resposta = await fetch(`/api/foco/historico/${sessaoId}`);
        const dados = await resposta.json();
        if (!resposta.ok) throw new Error(dados.erro || "Não foi possível carregar os detalhes.");

        const sessao = dados.sessao;
        document.getElementById("detalheSessaoTitulo").textContent =
            `Sessão de ${formatarDataHora(sessao.inicio)}`;
        const informacoes = [
            ["Início", formatarDataHora(sessao.inicio)],
            ["Fim", formatarDataHora(sessao.fim)],
            ["Duração", formatarDuracao(sessao.duracao_minutos)],
            ["Distrações", String(sessao.vezes_distraido)],
            ["XP recebido", `${sessao.xp_ganho} XP`],
            ["XP da sessão", `${sessao.xp_base} XP`],
            ["Bônus de meta", `${sessao.xp_bonus_meta} XP`],
            ["Matéria", sessao.materia || "Sem matéria associada"]
        ];
        const lista = document.getElementById("detalheSessaoDados");
        lista.replaceChildren();
        for (const [rotulo, valor] of informacoes) {
            const termo = document.createElement("dt");
            termo.textContent = rotulo;
            const descricao = document.createElement("dd");
            descricao.textContent = valor;
            lista.append(termo, descricao);
        }
        detalheDialog.showModal();
    } catch (erro) {
        historicoMensagem.textContent = erro.message;
    }
}

historicoFiltros.addEventListener("submit", carregarHistorico);
document.getElementById("limparFiltrosBtn").addEventListener("click", () => {
    historicoFiltros.reset();
    carregarHistorico();
});
document.getElementById("fecharDetalheBtn").addEventListener("click", () => {
    detalheDialog.close();
});

carregarHistorico();
