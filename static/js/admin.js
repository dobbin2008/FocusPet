const estudantesLista = document.getElementById("estudantesLista");
const petsLista = document.getElementById("petsLista");
const tribosLista = document.getElementById("tribosLista");

function preencherLista(elemento, itens, vazio, renderizar) {
    if (!elemento) return;
    elemento.innerHTML = itens.length ? itens.map(renderizar).join("") : `<li>${vazio}</li>`;
}

function escaparHTML(valor) {
    return String(valor).replace(/[&<>'"]/g, (caractere) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "'": "&#39;",
        '"': "&quot;"
    })[caractere]);
}

function formularioExclusao(url) {
    return `<form method="post" action="${url}" style="display:inline;">
        <button type="submit" class="danger-btn">Excluir</button>
    </form>`;
}

async function carregarDadosAdmin() {
    const resposta = await fetch("/admin/api/dados");
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro || "Não foi possível carregar os dados.");

    preencherLista(estudantesLista, dados.estudantes, "Nenhum estudante cadastrado.", (estudante) =>
        `<li>${escaparHTML(estudante.email)} — ID ${estudante.id}</li>`
    );
    preencherLista(petsLista, dados.pets, "Nenhum pet cadastrado.", (pet) =>
        `<li>${escaparHTML(pet.nome)} — nível ${pet.nivel} ${formularioExclusao(`/admin/pets/${pet.id}/delete`)}</li>`
    );
    preencherLista(tribosLista, dados.tribos, "Nenhuma tribo cadastrada.", (tribo) =>
        `<li>${escaparHTML(tribo.materia)} ${formularioExclusao(`/admin/tribos/${tribo.id}/delete`)}</li>`
    );
}

carregarDadosAdmin().catch((erro) => {
    [estudantesLista, petsLista, tribosLista].forEach((lista) => {
        if (lista) lista.innerHTML = `<li>${erro.message}</li>`;
    });
});
