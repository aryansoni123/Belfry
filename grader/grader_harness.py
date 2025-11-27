#!/usr/bin/env python3
import json,sys,subprocess,time,os

WORKDIR="/workspace"
CODE_FILE=os.path.join(WORKDIR,"solution.py")
TESTS_FILE=os.path.join(WORKDIR,"tests.json")
OUT_FILE=os.path.join(WORKDIR,"result.json")

def load_tests():
    with open(TESTS_FILE) as f:
        return json.load(f)

def run_case(inp,timeout_s=2):
    t0=time.time()
    try:
        p=subprocess.run(["python3", CODE_FILE], input=inp.encode(), capture_output=True, timeout=timeout_s)
        runtime=int((time.time()-t0)*1000)
        return {"stdout": p.stdout.decode(), "stderr": p.stderr.decode(), "exit": p.returncode, "runtime_ms": runtime}
    except subprocess.TimeoutExpired:
        return {"stdout":"", "stderr": "TIMEOUT", "exit": -1, "runtime_ms": timeout_s*1000}

def main():
    tests=load_tests()
    results=[]
    for tc in tests:
        r = run_case(tc.get("input",""), timeout_s=tc.get("timeout_s",2))
        expected = tc.get("expected","")
        # simple normalization
        passed = r["stdout"].strip() == expected.strip()
        results.append({
            "input": tc.get("input",""),
            "expected": expected,
            "stdout": r["stdout"],
            "stderr": r["stderr"],
            "exit": r["exit"],
            "runtime_ms": r["runtime_ms"],
            "passed": passed
        })
    total = sum(1 for r in results if r["passed"])
    out = {"results": results, "passed_count": total, "total_cases": len(results)}
    with open(OUT_FILE,"w") as f:
        json.dump(out,f)
    print(json.dumps(out))

if __name__=="__main__":
    main()
