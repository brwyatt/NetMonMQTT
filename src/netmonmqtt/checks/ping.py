from typing import Tuple
from pythonping import ping


def check_ping(
    target: str,
    timeout: int = 2,
    count: int = 1,
    min_success_ratio: float = 1,
) -> Tuple[bool, float]:
    if min_success_ratio > 1:
        min_success_ratio = 1
    elif min_success_ratio < 0:
        min_success_ratio = 0

    try:
        result = ping(target, timeout=timeout, count=count)
    except Exception as e:
        return False, 0
    
    return result.stats_success_ratio >= min_success_ratio, result.rtt_avg * 1000  # seconds to ms