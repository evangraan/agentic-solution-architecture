Ensure python 3.13.*

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn bedrock_runtime_shim:app --host 0.0.0.0 --port 9001

```
