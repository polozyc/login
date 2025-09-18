import os
from pathlib import Path
import importlib
import shutil

TEST_DB = Path("tests/.tmp-db-unit.db")

def setup_module(module):
    # define DB de teste ANTES de importar o módulo
    os.environ["LOGIN_DB_PATH"] = str(TEST_DB)
    # garanta ambiente limpo
    if TEST_DB.exists():
        TEST_DB.unlink()

def teardown_module(module):
    # limpar DB de teste
    if TEST_DB.exists():
        TEST_DB.unlink()
    # limpar pasta exports, se criada no teste futuramente
    exp = Path("exports")
    if exp.exists():
        shutil.rmtree(exp)

def test_password_min_length():
    # importa depois de setar o env
    login_cli = importlib.import_module("login_cli")
    login_cli.init_db()

    # senha < 8 deve falhar
    ok = login_cli.create_user("alice", "1234567")  # 7 chars
    assert ok is False

def test_create_and_login_success():
    login_cli = importlib.import_module("login_cli")
    login_cli.init_db()

    # criar usuário com senha válida
    assert login_cli.create_user("bob", "senha_forte_123") is True

    # login deve funcionar
    assert login_cli.verify_login("bob", "senha_forte_123") is True

def test_duplicate_username():
    login_cli = importlib.import_module("login_cli")
    login_cli.init_db()

    assert login_cli.create_user("carol", "abcdefgh") is True
    # tentar recriar mesmo usuário deve falhar
    assert login_cli.create_user("carol", "abcdefgh") is False

def test_wrong_password():
    login_cli = importlib.import_module("login_cli")
    login_cli.init_db()

    assert login_cli.create_user("dave", "abcdefgh") is True
    # senha errada deve falhar
    assert login_cli.verify_login("dave", "xxxxx") is False
