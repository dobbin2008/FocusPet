from database import DatabaseGateway, get_database, registro


class CadastrarEstudanteService:
    def __init__(self, database: DatabaseGateway = None):
        self.database = database

    def _db(self):
        return self.database or get_database()

    def execute(self, email: str, senha: str):
        if not email or not senha:
            raise ValueError("Email e senha são obrigatórios")
        banco = self._db()
        if banco.execute("SELECT 1 FROM estudantes WHERE email = ?", (email,)).fetchone():
            raise ValueError("Este email já está cadastrado")
        cursor = banco.execute(
            "INSERT INTO estudantes (email, senha) VALUES (?, ?)", (email, senha)
        )
        banco.commit()
        return registro(banco.execute("SELECT * FROM estudantes WHERE id = ?", (cursor.lastrowid,)).fetchone())


class AutenticarEstudanteService:
    def __init__(self, database: DatabaseGateway = None):
        self.database = database

    def _db(self):
        return self.database or get_database()

    def execute(self, email: str, senha: str):
        return registro(self._db().execute(
            "SELECT * FROM estudantes WHERE email = ? AND senha = ?", (email, senha)
        ).fetchone())


class ListarEstudantesService:
    def __init__(self, database: DatabaseGateway = None):
        self.database = database

    def _db(self):
        return self.database or get_database()

    def execute(self):
        return [registro(linha) for linha in self._db().execute(
            "SELECT * FROM estudantes ORDER BY id"
        ).fetchall()]
