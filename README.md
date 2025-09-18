# Python Login CLI

Sistema de login em Python (modo console) usando **SQLite** e **PBKDF2-HMAC-SHA256**, sem dependências externas.

## Recursos
- Registro de usuário com _salt_ único e hash PBKDF2 (200k iterações).
- Login com comparação em tempo constante (`compare_digest`).
- Listagem de usuários.

## Executar
```bash
python login_cli.py
