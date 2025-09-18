def create_user(username: str, password: str) -> bool:
    if not username or not password:
        print("Usuário e senha não podem ser vazios.")
        return False

    # NOVO: política mínima de senha
    if len(password) < 8:
        print("A senha deve ter pelo menos 8 caracteres.")
        return False
