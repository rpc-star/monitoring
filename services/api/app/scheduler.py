from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
import httpx
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

TARGETS = [
    {"url": "https://sqlitebrowser.org/", "expected_code": 200},
    {"url": "https://rpc-star.com", "expected_code": 200}
]

async def probe_targets(target):
    """async check targets"""
    url = target["url"]
    expected_code = target.get("expected_code", 200)
    start_time = datetime.now(timezone.utc)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
        
        latency_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        if resp.status_code == expected_code:
            logger.info(f"{url} responded {resp.status_code} ({latency_ms:.1f} ms)")
        else:
            logger.warning(f"! {url} responded {resp.status_code} ({latency_ms:.1f} ms)")

    except Exception as e:
        latency_ms = (datetime.now(timezone.utc)- start_time).total_seconds() * 1000
        logger.error(f"!!! {url} failed after {latency_ms:.1f} ms: {e}")


async def run_periodic_probes():
    """check all targets"""
    logger.info("Running shceduler probes...")
    for target in TARGETS:
        await probe_targets(target)

def create_scheduler():
    """create and return APScheduler"""
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        run_periodic_probes,
        trigger=IntervalTrigger(minutes=5),
        id="probe_targets",
        name="Probe monitoring targets",
        replace_existing=True,
    ) 
    return scheduler