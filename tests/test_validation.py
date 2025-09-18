import os
import sys
import shutil
from pathlib import Path
import importlib.util

# Caminho absoluto do arquivo login_cli.py na raiz do repo
ROOT = Path(__file__).resolve().parents[1]
LOGIN_FILE = ROOT / "login_cli.py"

def load_login_module():
    spec = importlib.util.spec_from_file_location("login_cli", LOGIN_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module

TEST_DB = ROOT / "tests" / ".tmp-db-unit.db"

def setup_module(module):
    # Usar DB de teste ANTES de carregar o módulo
    os.environ["LOGIN_DB_PATH"] = str(TEST_DB)
    if TEST_DB.exists():
        TEST_DB.unlink()

def teardown_module(module):
    if TEST_DB.exists():
        TEST_DB.unlink()
    exp = ROOT / "exports"
    if exp.exists():
        shutil.rmtree(exp)

def test_password_min_length():
    login_cli = load_login_module()
    login_cli.init_db()
    assert login_cli.create_user("alice", "1234567") is False  # 7 chars

def test_create_and_login_success():
    login_cli = load_login_module()
    login_cli.init_db()
    assert login_cli.create_user("bob", "senha_forte_123") is True
    assert login_cli.verify_login("bob", "senha_forte_123") is True

def test_duplicate_username():
    login_cli = load_login_module()
    login_cli.init_db()
    assert login_cli.create_user("carol", "abcdefgh") is True
    assert login_cli.create_user("carol", "abcdefgh") is False  # repetido

def test_wrong_password():
    login_cli = load_login_module()
    login_cli.init_db()
    assert login_cli.create_user("dave", "abcdefgh") is True
    assert login_cli.verify_login("dave", "xxxxx") is False
