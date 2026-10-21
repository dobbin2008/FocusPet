# Diagrama de classes do domínio

O diagrama representa as Models atuais e seus relacionamentos por chave estrangeira. `BlocoNotas` e `Estudante.meta_diaria_minutos` permanecem apenas para compatibilidade e migração de dados antigos.

```mermaid
classDiagram
    class CrudModel {
        +id: int
        +salvar()
        +atualizar()
        +deletar()
        +listar_todos()
        +buscar_por_id()
    }

    class Estudante {
        +email: str
        +senha: hash
        +nome_exibicao: str
        +foto_perfil: str
        +xp_total: int
        +tema_de_cores: str
        +meta_diaria_minutos: int
        +assinatura: bool
        +tribo_id: int
        +pet_equipado_id: int
    }

    class Pet {
        +nome: str
        +nivel: int
        +linha_evolutiva: str
        +descricao: str
        +imagem: str
        +imagem_nivel_1: str
        +imagem_nivel_2: str
        +imagem_nivel_3: str
        +xp_atual: int
        +eh_padrao: bool
        +estudante_id: int
        +tribo_id: int
    }

    class Tribo {
        +materia: str
    }

    class Agenda {
        +data_atual: datetime
        +estudante_id: int
    }

    class Estudo {
        +titulo: str
        +inicio: datetime
        +fim: datetime
        +duracao_minutos: int
        +concluido: bool
        +xp_ganho: int
        +lembrete_em: datetime
        +lembrete_notificado: bool
        +agenda_id: int
    }

    class SessaoFoco {
        +inicio: datetime
        +fim: datetime
        +modo_ativo: bool
        +vezes_distraido: int
        +tempo_total_minutos: int
        +xp_ganho: int
        +xp_bonus_meta: int
        +token_api: str
        +estudante_id: int
        +materia_id: int
    }

    class Materia {
        +nome: str
        +estudante_id: int
    }

    class ListaBloqueada {
        +url: str
        +descricao: str
        +estudante_id: int
    }

    class BlocoNotas {
        +conteudo: text
        +hotkey: str
        +notas_migradas: bool
        +estudante_id: int
    }

    class Nota {
        +titulo: str
        +conteudo: text
        +estudante_id: int
    }

    class MetaEstudo {
        +meta_diaria_minutos: int
        +meta_semanal_minutos: int
        +estudante_id: int
    }

    class BonusMeta {
        +tipo: str
        +periodo_inicio: date
        +xp_ganho: int
        +estudante_id: int
    }

    class ResumoSemanal {
        +data_inicio: datetime
        +data_fim: datetime
        +horas_estudadas: float
        +vezes_distraido: int
        +progresso_pet: float
        +estudante_id: int
    }

    CrudModel <|-- Estudante
    CrudModel <|-- Pet
    CrudModel <|-- Tribo
    CrudModel <|-- Agenda
    CrudModel <|-- Estudo
    CrudModel <|-- SessaoFoco
    CrudModel <|-- Materia
    CrudModel <|-- ListaBloqueada
    CrudModel <|-- BlocoNotas
    CrudModel <|-- Nota
    CrudModel <|-- MetaEstudo
    CrudModel <|-- BonusMeta
    CrudModel <|-- ResumoSemanal

    Estudante "0..*" --> "0..1" Tribo : participa
    Pet "0..*" --> "0..1" Tribo : pertence
    Estudante "0..1" --> "0..*" Pet : possui
    Estudante "0..1" --> "0..1" Pet : equipa
    Estudante "1" --> "0..1" Agenda : organiza
    Agenda "1" --> "0..*" Estudo : agenda
    Estudante "1" --> "0..*" SessaoFoco : registra
    Materia "0..1" --> "0..*" SessaoFoco : classifica
    Estudante "1" --> "0..*" Materia : cadastra
    Estudante "1" --> "0..*" ListaBloqueada : configura
    Estudante "1" --> "0..1" BlocoNotas : preferencias legadas
    Estudante "1" --> "0..*" Nota : escreve
    Estudante "1" --> "0..1" MetaEstudo : configura
    Estudante "1" --> "0..*" BonusMeta : recebe
    Estudante "1" --> "0..*" ResumoSemanal : consulta
```

`Estudante` herda de `CrudModel` e de `db.Model`, assim como as demais Models de domínio. `MetaEstudo` tem uma configuração por estudante; `BonusMeta` impede premiações duplicadas para o mesmo tipo e período. A matéria de uma sessão é opcional.
