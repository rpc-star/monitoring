import time
import httpx
import logging
from fastapi import FastAPI, Response, Request, Depends
from prometheus_client import Counter, Gauge, generate_latest
from scheduler import create_scheduler
from contextlib import asynccontextmanager

from db import Base, engine, get_session
from sqlalchemy.ext.asyncio import AsyncSession
from models import Result

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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("SQLite table created")


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
async def probe(
    url: str = "https://sqlitebrowser.org/", 
    expected_code: int = 200,
    session: AsyncSession = Depends(get_session)
    ):
    """HTTP GET probe"""
    start = time.time()
    try:
        resp = httpx.get(url, timeout=5.0)
        latency_ms = (time.time() - start) * 1000

        PROBE_LATENCY.set(latency_ms)

        success = resp.status_code == expected_code

        if success:
            PROBE_SUCCESS.inc()
        
        else:
            PROBE_FAILURE.inc()

        db_record = Result(
            url=url,
            status_code=resp.status_code,
            latency_ms=latency_ms,
            success=success,
            error=None
        )
    except Exception as e:
        PROBE_FAILURE.inc()
        db_record = Result(
            url=url,
            status_code=0,
            latency_ms=None,
            success=False,
            error=str(e)
        )
        return {"success": False, "error": str(e)}

    session.add(db_record)
    await session.commit()

    return {
        "success": db_record.success,
        "latency_ms": db_record.latency_ms,
        "status_code": db_record.status_code
    }

