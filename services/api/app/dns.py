import time
import dns.resolver

def check_dns(name: str, timeout: float = 5.0):
    resolver = dns.resolver.Resolver()
    t1 = time.monotonic_ns()
    try:
        answers = resolver.resolve(name, "A", lifetime=timeout)
        t2 = time.monotonic_ns()
        latency_ms = (t2-t1)/1e6
        addrs = [rdata.address for rdata in answers]
        return {
            "success": True,
            "latency_ms": latency_ms,
            "status_info": f"A {addrs}",
        }
    except Exception as e:
        t2 = time.monotonic_ns()
        latency_ms = (t2-t1)/1e6
        return {
            "success": False,
            "latency_ms": latency_ms,
            "status_info": str(e),
        }