def validar_senha(senha):
    senha = str(senha or "")
    requisitos = (
        len(senha) >= 12,
        any(caractere.isupper() for caractere in senha),
        any(caractere.islower() for caractere in senha),
        any(caractere.isdigit() for caractere in senha),
        any(not caractere.isalnum() and not caractere.isspace() for caractere in senha),
    )
    if not all(requisitos):
        raise ValueError(
            "A senha precisa ter ao menos 12 caracteres, uma maiúscula, "
            "uma minúscula, um número e um símbolo especial."
        )
