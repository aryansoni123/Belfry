## to build the grader docker image

```bash
cd belfry-proto/grader
docker build -t belfry-grader:1.0 .
```


## to create a virtual env
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r req.txt
```

## to start the backend server

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 
```

## to run the frontend locally
```bash
cd ui
streamlit run app.py
```

# Optional

## for local testing of the grader
```bash
docker run --rm -v "$(pwd)/workspace:/workspace" belfry-grader:proto
cat workspace/result.json 
```


