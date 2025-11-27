import streamlit as st, httpx, time

API = "http://localhost:8000"

st.title("Belfry Prototype — Student")

assignment = st.selectbox("Assignment", ["default"])
uploaded = st.file_uploader("Upload solution.py", type=["py"])
if st.button("Submit") and uploaded:
    files = {"code_file": (uploaded.name, uploaded.getvalue())}
    with st.spinner("Uploading..."):
        r = httpx.post(f"{API}/submit", files=files, data={"assignment": assignment})
    if r.status_code==200:
        job = r.json()["job_id"]
        st.success(f"Submitted. Job id: {job}")
        status_area = st.empty()
        while True:
            s = httpx.get(f"{API}/status/{job}").json()
            status_area.write(s["status"])
            if s["status"] in ["done","error"]:
                st.json(s.get("summary", {}))
                break
            time.sleep(1)
    else:
        st.error(r.text)
