const materiaForm = document.getElementById("materiaForm");
const nomeMateriaInput = document.getElementById("nomeMateria");
const materiasLista = document.getElementById("materiasLista");
const materiasMensagem = document.getElementById("materiasMensagem");

materiaForm.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const botao = materiaForm.querySelector('button[type="submit"]');
    botao.disabled = true;
    try {
        const resposta = await fetch("/api/materias", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome: nomeMateriaInput.value })
        });
        const dados = await resposta.json();
        if (!resposta.ok) throw new Error(dados.erro || "Não foi possível cadastrar a matéria.");
        nomeMateriaInput.value = "";
        materiasMensagem.textContent = "Matéria cadastrada.";
        await carregarMaterias();
    } catch (erro) {
        materiasMensagem.textContent = erro.message;
    } finally {
        botao.disabled = false;
    }
});

async function carregarMaterias() {
    const resposta = await fetch("/api/materias");
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro || "Não foi possível carregar as matérias.");

    materiasLista.replaceChildren();
    if (dados.materias.length === 0) {
        const vazio = document.createElement("p");
        vazio.className = "materias-vazio";
        vazio.textContent = "Você ainda não cadastrou matérias.";
        materiasLista.appendChild(vazio);
        return;
    }
    dados.materias.forEach((materia) => materiasLista.appendChild(criarCartaoMateria(materia)));
}

function criarCartaoMateria(materia) {
    const cartao = document.createElement("article");
    cartao.className = "materia-card";

    const detalhes = document.createElement("div");
    detalhes.className = "materia-card-detalhes";
    const nome = document.createElement("h3");
    nome.textContent = materia.nome;
    const horas = document.createElement("p");
    const formatador = new Intl.NumberFormat("pt-BR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    horas.textContent = `${formatador.format(materia.horas_estudadas_semana)} h nesta semana`;
    detalhes.append(nome, horas);

    const editar = document.createElement("button");
    editar.type = "button";
    editar.className = "atalho-btn";
    editar.textContent = "Editar";
    editar.addEventListener("click", () => iniciarEdicaoMateria(cartao, materia));
    cartao.append(detalhes, editar);
    return cartao;
}

function iniciarEdicaoMateria(cartao, materia) {
    const formulario = document.createElement("form");
    formulario.className = "materia-edicao";

    const entrada = document.createElement("input");
    entrada.type = "text";
    entrada.value = materia.nome;
    entrada.maxLength = 80;
    entrada.required = true;
    entrada.setAttribute("aria-label", "Nome da matéria");

    const salvar = document.createElement("button");
    salvar.type = "submit";
    salvar.className = "notas-btn";
    salvar.textContent = "Salvar";

    const cancelar = document.createElement("button");
    cancelar.type = "button";
    cancelar.className = "atalho-btn";
    cancelar.textContent = "Cancelar";
    cancelar.addEventListener("click", () => carregarMaterias().catch(mostrarErro));

    formulario.append(entrada, salvar, cancelar);
    formulario.addEventListener("submit", async (evento) => {
        evento.preventDefault();
        salvar.disabled = true;
        try {
            const resposta = await fetch(`/api/materias/${materia.id}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nome: entrada.value })
            });
            const dados = await resposta.json();
            if (!resposta.ok) throw new Error(dados.erro || "Não foi possível editar a matéria.");
            materiasMensagem.textContent = "Matéria atualizada.";
            await carregarMaterias();
        } catch (erro) {
            materiasMensagem.textContent = erro.message;
            salvar.disabled = false;
        }
    });
    cartao.replaceChildren(formulario);
    entrada.focus();
}

function mostrarErro(erro) {
    materiasMensagem.textContent = erro.message;
}

carregarMaterias().catch(mostrarErro);
