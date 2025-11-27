## to build the grader docker image

```bash
cd belfry-proto/grader
docker build -t belfry-grader:proto .
```


## for local testing of the grader
```bash
docker run --rm -v "$(pwd)/workspace:/workspace" belfry-grader:proto
cat workspace/result.json 
```


## to run the backend server locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn python-multipart aiofiles 
```

## to start the backend server

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 
```

## to run the frontend locally
```bash
pip install streamlit httpx 
```
