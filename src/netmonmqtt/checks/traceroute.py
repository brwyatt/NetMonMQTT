from typing import List, Optional, Tuple, Union

from scapy.all import ICMP, IP, RandShort, sr1


def check_route(
    target: str,
    hop_count: int,
    timeout: int = 2,
    expected: Optional[Union[str, List[str]]] = None
) -> Tuple[bool, str]:
    if expected is None:
        expected = target
    if isinstance(expected, str):
        expected = [expected]

    try:
        result = sr1(IP(dst=target, ttl=hop_count) / ICMP(type=8, seq=RandShort()), verbose=0, timeout=timeout)
    except Exception as e:
        return False, None

    if result is None:
        return False, None

    return result.src in expected, result.src
