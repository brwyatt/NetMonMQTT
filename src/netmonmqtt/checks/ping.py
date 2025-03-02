from typing import Tuple
from pythonping import ping


def check_ping(
    target: str,
    timeout: int = 2,
    count: int = 1,
    min_success_ratio: float = 1,
) -> Tuple[bool, float, float]:
    if min_success_ratio > 1:
        min_success_ratio = 1
    elif min_success_ratio < 0:
        min_success_ratio = 0

    try:
        result = ping(target, timeout=timeout, count=count)
    except Exception as e:
        return False, None, 0

    success_average_time = (
        None
        if result.stats_packets_returned == 0
        else
        # Remove timeouts from average
        (result.rtt_avg_ms-(float(timeout*1000*result.stats_packets_lost)/count))*(float(count)/result.stats_packets_returned)
    )

    return result.stats_success_ratio >= min_success_ratio, success_average_time, result.stats_success_ratio * 100
