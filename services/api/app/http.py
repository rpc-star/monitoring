import time
import httpx

def check_http(endpoint: str, expected_code: int = 200, timeout: float = 5.0):
    t1 = time.monotonic_ns()
    try:
        resp = httpx.get(endpoint, timeout=timeout)
        t2 = time.monotonic_ns()
        latency_ms = (t2-t1)/1e6
        success = resp.status_code == expected_code
        return {
            "success": success,
            "latency_ms": latency_ms,
            "status_info": f"HTTP {resp.status_code}",
        }
    except Exception as e:
        t2 = time.monotonic_ns()
        latency_ms = (t2-t1)/1e6
        return {
            "success": False,
            "latency_ms": latency_ms,
            "status_info": str(e),
        }