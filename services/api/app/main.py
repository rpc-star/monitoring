from fastapi import FastAPI, Response

app = FastAPI()


@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    content = """# HELP my_app_requests_total Total number of requests
# TYPE my_app_requests_total counter
my_app_requests_total 42

# HELP my_app_up Is the app up
# TYPE my-App_up gauge
my_app_up 1
"""
    return Response(content=content, media_type="text/plain; version=0.0.4")