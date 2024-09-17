container_name=db
venv_name=myvenv
activate=. $(venv_name)/bin/activate && export PYTHONPATH="src:$$PYTHONPATH"
working_dir=src
host=0.0.0.0
port=8000

enter_to_container:
	docker exec -it $(container_name) sh 


run: 
	$(activate) && uvicorn ${working_dir}.app:app --host $(host) --port $(port)