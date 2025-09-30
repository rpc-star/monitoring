import time
import socket

def check_tcp(endpoint: str, timeout: float = 5.0):
    host, port = endpoint.split(":")
    port = int(port)
    t1 = time.monotonic_ns()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
        t2 = time.monotonic_ns()
        latency_ms = (t2-t1)/1e6
        return {
            "success": True,
            "latency_ms": latency_ms,
            "status_info": f"TCP connect {host}:{port} ok",
        }
    except Exception as e:
        t2 = time.monotonic_ns()
        latency_ms = (t2-t1)/1e6
        return {
            "success": False,
            "latency_ms": latency_ms,
            "status_info": str(e),
        }