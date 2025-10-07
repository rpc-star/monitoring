import time
import httpx
import logging
from fastapi import FastAPI, Response, Request
from prometheus_client import Counter, Gauge, generate_latest
from services.api.app.scheduler import create_scheduler
from contextlib import asynccontextmanager



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



PROBE_SUCCESS = Counter(
    "probe_success_total",
    "Total number of successful probes"
)

PROBE_FAILURE = Counter(
    "probe_failure_total",
    "Total number of failed probes"
)

PROBE_LATENCY = Gauge(
    "probe_latency_ms",
    "Latency of last probe in milliseconds"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = create_scheduler()
    scheduler.start()
    logger.info("APScheduler started")
    app.state.scheduler = scheduler
    yield
    scheduler.shutdown()
    logger.info("APScheduler stopped")


app = FastAPI(lifespan=lifespan)



@app.get("/healthz")
def healthz():
    return {"status":"ok"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain; version=0.0.4")

@app.get("/probe")
def probe(url: str = "https://localhost", expected_code: int = 200):
    """HTTP GET probe"""
    start = time.time()
    try:
        resp = httpx.get(url, timeout=5.0)
        latency_ms = (time.time() - start) * 1000

        PROBE_LATENCY.set(latency_ms)

        if resp.status_code == expected_code:
            PROBE_SUCCESS.inc()
            return {"success": True, "latency_ms": latency_ms, "status_code": resp.status_code}
        else:
            PROBE_FAILURE.inc()
            return {"success": False, "latency_ms": latency_ms, "status_code": resp.status_code}

    except Exception as e:
        PROBE_FAILURE.inc()
        return {"success": False, "error": str(e)}