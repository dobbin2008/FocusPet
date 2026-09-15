from database import DatabaseGateway, get_database, registro


class CriarPetService:
    def __init__(self, database: DatabaseGateway = None):
        self.database = database

    def _db(self):
        return self.database or get_database()

    def execute(self, nome: str, nivel: int = 1):
        if not nome or not nome.strip():
            raise ValueError("Nome do pet é obrigatório")
        banco = self._db()
        cursor = banco.execute("INSERT INTO pets (nome, nivel) VALUES (?, ?)", (nome.strip(), nivel))
        banco.commit()
        return registro(banco.execute("SELECT * FROM pets WHERE id = ?", (cursor.lastrowid,)).fetchone())


class ListarPetsService:
    def __init__(self, database: DatabaseGateway = None):
        self.database = database

    def _db(self):
        return self.database or get_database()

    def execute(self):
        return [registro(linha) for linha in self._db().execute("SELECT * FROM pets ORDER BY id").fetchall()]


class DeletarPetService:
    def __init__(self, database: DatabaseGateway = None):
        self.database = database

    def _db(self):
        return self.database or get_database()

    def execute(self, pet_id: int) -> None:
        banco = self._db()
        banco.execute("DELETE FROM pets WHERE id = ?", (pet_id,))
        banco.commit()


class CriarTriboService:
    def __init__(self, database: DatabaseGateway = None):
        self.database = database

    def _db(self):
        return self.database or get_database()

    def execute(self, materia: str):
        if not materia or not materia.strip():
            raise ValueError("Matéria é obrigatória")
        banco = self._db()
        cursor = banco.execute("INSERT INTO tribos (materia) VALUES (?)", (materia.strip(),))
        banco.commit()
        return registro(banco.execute("SELECT * FROM tribos WHERE id = ?", (cursor.lastrowid,)).fetchone())


class ListarTribosService:
    def __init__(self, database: DatabaseGateway = None):
        self.database = database

    def _db(self):
        return self.database or get_database()

    def execute(self):
        return [registro(linha) for linha in self._db().execute("SELECT * FROM tribos ORDER BY id").fetchall()]


class DeletarTriboService:
    def __init__(self, database: DatabaseGateway = None):
        self.database = database

    def _db(self):
        return self.database or get_database()

    def execute(self, tribo_id: int) -> None:
        banco = self._db()
        banco.execute("DELETE FROM tribos WHERE id = ?", (tribo_id,))
        banco.commit()
