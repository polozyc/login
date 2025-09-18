#!/usr/bin/env python3
"""
Sistema de Login em Python (CLI) com SQLite + PBKDF2 (sem dependências externas).
- Registro de usuários (com verificação de duplicidade)
- Login com verificação segura (compare_digest)
- Lista de usuários cadastrados
"""

from pathlib import Path
import sqlite3
import os
import binascii
import getpass
import hashlib
import time
from datetime import datetime

DB_PATH = Path(os.getenv("LOGIN_DB_PATH", "users.db"))

ITERATIONS = 200_000  # PBKDF2 iterations
HASH_NAME = "sha256"
KEY_LEN = 32  # 256-bit key


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                pwd_salt TEXT NOT NULL,
                pwd_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def pbkdf2_hash(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        HASH_NAME,
        password.encode("utf-8"),
        salt,
        ITERATIONS,
        dklen=KEY_LEN,
    )


def create_user(username: str, password: str) -> bool:
    if not username or not password:
        print("Usuário e senha não podem ser vazios.")
        return False

    salt = os.urandom(16)
    pwd_hash = pbkdf2_hash(password, salt)

    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO users (username, pwd_salt, pwd_hash, created_at) VALUES (?, ?, ?, ?)",
                (
                    username.strip(),
                    binascii.hexlify(salt).decode("ascii"),
                    binascii.hexlify(pwd_hash).decode("ascii"),
                    datetime.utcnow().isoformat() + "Z",
                ),
            )
            conn.commit()
        print(f"✅ Usuário '{username}' criado com sucesso.")
        return True
    except sqlite3.IntegrityError:
        print("⚠️ Nome de usuário já existe. Escolha outro.")
        return False


def verify_login(username: str, password: str) -> bool:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT pwd_salt, pwd_hash FROM users WHERE username = ?", (username.strip(),)
        )
        row = cur.fetchone()
        if not row:
            print("Usuário ou senha inválidos.")
            return False

        salt_hex, hash_hex = row
        salt = binascii.unhexlify(salt_hex)
        expected_hash = binascii.unhexlify(hash_hex)

        provided_hash = pbkdf2_hash(password, salt)

        if hashlib.compare_digest(provided_hash, expected_hash):
            return True
        else:
            print("Usuário ou senha inválidos.")
            return False


def list_users():
    with get_conn() as conn:
        cur = conn.execute("SELECT id, username, created_at FROM users ORDER BY id")
        rows = cur.fetchall()
        if not rows:
            print("Nenhum usuário cadastrado.")
            return
        print("\n=== Usuários cadastrados ===")
        for rid, uname, created in rows:
            print(f"[{rid}] {uname} • criado em {created}")
        print("============================\n")


def clear_screen():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass


def pause():
    try:
        input("\nPressione Enter para continuar...")
    except EOFError:
        time.sleep(1)


def menu():
    while True:
        clear_screen()
        print("=== Sistema de Login (CLI) ===")
        print("1) Registrar novo usuário")
        print("2) Fazer login")
        print("3) Listar usuários")
        print("4) Sair")
        choice = input("Escolha uma opção: ").strip()

        if choice == "1":
            username = input("Novo usuário: ").strip()
            pwd1 = getpass.getpass("Senha: ")
            pwd2 = getpass.getpass("Confirme a senha: ")
            if pwd1 != pwd2:
                print("As senhas não coincidem.")
                pause()
                continue
            create_user(username, pwd1)
            pause()

        elif choice == "2":
            username = input("Usuário: ").strip()
            password = getpass.getpass("Senha: ")
            print("Verificando...")
            ok = verify_login(username, password)
            if ok:
                print(f"✅ Login bem-sucedido! Bem-vindo, {username}.")
            else:
                print("❌ Falha no login.")
            pause()

        elif choice == "3":
            list_users()
            pause()

        elif choice == "4":
            print("Até logo!")
            break
        else:
            print("Opção inválida.")
            pause()


if __name__ == "__main__":
    init_db()
    menu()
