run:
	python login_cli.py

clean:
	rm -f users.db auth.log
	rm -rf __pycache__/
