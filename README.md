# toka-fuzzing-websites

1. Run the service with following commands:
```
cd <current_repository>
pip install -r requirments.txt
set PYTHONPATH=.
python app\command_line.py 
```

2. Run the server with following commands:
```
cd <current_repository>
pip install -r requirments.txt
set PYTHONPATH=.
uvicorn app.server:app --reload
```