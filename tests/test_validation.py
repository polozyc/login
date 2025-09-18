import os
import sys
import shutil
from pathlib import Path
import importlib

# 1) Garante que a raiz do repositório está no sys.path para importar login_cli.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

TEST_DB = Path("tests/.tmp-db-unit.db")

def setup_module(module):
    # 2) Define DB de teste ANTES de importar o módulo
    os.environ["LOGIN_DB_PATH"] = str(TEST_DB)
    if TEST_DB.exists():
        TEST_DB.unlink()

def teardown_module(module):
    if TEST_DB.exists():
        TEST_DB.unlink()
    exp = Path("exports")
    if exp.exists():
        shutil.rmtree(exp)

def test_password_min_length():
    login_cli = importlib.import_module("login_cli")
    login_cli.init_db()
    # senha com menos de 8 chars deve falhar
    ok = login_cli.create_user("alice", "1234567")  # 7 caracteres
    assert ok is False

def test_create_and_login_success():
    login_cli = importlib.import_module("login_cli")
    login_cli.init_db()
    # criar e logar com sucesso
    assert login_cli.create_user("bob", "senha_forte_123") is True
    assert login_cli.verify_login("bob", "senha_forte_123") is True

def test_duplicate_username():
    login_cli = importlib.import_module("login_cli")
    login_cli.init_db()
    assert login_cli.create_user("carol", "abcdefgh") is True
    # repetir o mesmo usuário deve falhar
    assert login_cli.create_user("carol", "abcdefgh") is False

def test_wrong_password():
    login_cli = importlib.import_module("login_cli")
    login_cli.init_db()
    assert login_cli.create_user("dave", "abcdefgh") is True
    # senha incorreta deve falhar
    assert login_cli.verify_login("dave", "xxxxx") is False
