import os, uuid, json, threading, subprocess, shutil, time
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

ROOT = os.path.abspath(os.path.dirname(__file__))
JOBS_DIR = os.path.join(ROOT, "jobs")
GRADER_IMAGE = "belfry-grader:proto"

os.makedirs(JOBS_DIR, exist_ok=True)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def run_grader(job_id):
    job_path = os.path.join(JOBS_DIR, job_id)
    workspace = job_path  # mount workspace directly
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{workspace}:/workspace:ro",   # read-only so grader can't modify host; grader writes result.json in container not host
        GRADER_IMAGE
    ]
    # We mount read-only; to get result.json back we will copy via docker cp; simpler: mount rw and allow output
    # For prototype, use rw:
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{workspace}:/workspace",
        "--memory=200m", "--cpus=0.5",
        GRADER_IMAGE
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate(timeout=30)
    # read result.json created in workspace
    result_file = os.path.join(workspace, "result.json")
    if os.path.exists(result_file):
        with open(result_file) as f:
            data = json.load(f)
    else:
        data = {"error": "no result.json", "stdout": out, "stderr": err}
    # save summary
    with open(os.path.join(workspace, "summary.json"), "w") as f:
        json.dump(data, f)
    return

@app.post("/submit")
async def submit(code_file: UploadFile = File(...), assignment: str = "default"):
    # Create job
    job_id = str(uuid.uuid4())[:8]
    job_path = os.path.join(JOBS_DIR, job_id)
    os.makedirs(job_path, exist_ok=True)
    # Save code
    code_path = os.path.join(job_path, "solution.py")
    with open(code_path, "wb") as f:
        f.write(await code_file.read())
    # copy assignment tests — for prototype, use file per assignment
    tests_src = os.path.join(ROOT, "assignments", f"{assignment}_tests.json")
    if not os.path.exists(tests_src):
        return JSONResponse(status_code=400, content={"error":"assignment tests not found"})
    shutil.copy(tests_src, os.path.join(job_path, "tests.json"))
    # mark status
    with open(os.path.join(job_path, "status.txt"), "w") as f:
        f.write("queued")
    # start background thread
    def worker():
        with open(os.path.join(job_path, "status.txt"), "w") as f:
            f.write("running")
        try:
            run_grader(job_id)
            with open(os.path.join(job_path, "status.txt"), "w") as f:
                f.write("done")
        except Exception as e:
            with open(os.path.join(job_path, "status.txt"), "w") as f:
                f.write("error")
            with open(os.path.join(job_path, "error.txt"), "w") as f:
                f.write(str(e))
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return {"job_id": job_id}

@app.get("/status/{job_id}")
def status(job_id: str):
    job_path = os.path.join(JOBS_DIR, job_id)
    if not os.path.exists(job_path):
        return JSONResponse(status_code=404, content={"error":"job not found"})
    status_file = os.path.join(job_path, "status.txt")
    s = "unknown"
    if os.path.exists(status_file):
        s = open(status_file).read()
    summary = None
    summ_file = os.path.join(job_path, "summary.json")
    if os.path.exists(summ_file):
        summary = json.load(open(summ_file))
    return {"job_id": job_id, "status": s, "summary": summary}
