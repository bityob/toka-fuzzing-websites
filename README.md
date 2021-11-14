# toka-fuzzing-websites

1. Run the service with following commands:
```
cd <current_repository>
pip install -r requirments.txt
set PYTHONPATH=.
python app\command_line.py
```
```
C:\Code\toka-fuzzing-websites>python app\command_line.py --url https://www.example.com
[2b25a833-9035-491b-be8f-aa494b422ba3] Started run with arguments: stop_event=<asyncio.locks.Event object at 0x0000023C24A2AFE0 [unset]>, task_id=UUID('2b25a833-9035-491b-be8f-aa494b422ba3'), user_agent=None
[2b25a833-9035-491b-be8f-aa494b422ba3] Handling url... https://www.example.com
[2b25a833-9035-491b-be8f-aa494b422ba3] Response: 200,
User-Agent: Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36
[2b25a833-9035-491b-be8f-aa494b422ba3] Sleeping...
[2b25a833-9035-491b-be8f-aa494b422ba3] Cancelded... run
Aborted!
````

2. Run the server with following commands:
```
cd <current_repository>
pip install -r requirments.txt
set PYTHONPATH=.
uvicorn app.server:app --reload
```
