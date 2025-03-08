from typing import List, Optional, Tuple, Union

from scapy.all import ICMP, IP, RandShort, sr1


def check_route(
    target: str,
    hop_count: int,
    timeout: int = 2,
    expected: Optional[Union[str, List[str]]] = None
) -> Tuple[bool, bool, Optional[str]]:
    # Result (tuple):
    #   * Success (bool): True if we got a time exceeded from an expected IP or Echo reply from the targer
    #   * Direct (bool): True if the response was an Echo reply from the target
    #   * source (str): the origin IP address of the response

    if expected is None:
        expected = []
    if isinstance(expected, str):
        expected = [expected]

    try:
        result = sr1(IP(dst=target, ttl=hop_count) / ICMP(type=8, seq=RandShort()), verbose=0, timeout=timeout)
    except Exception as e:
        print(f"Traceroute Check: Exception: {e}")
        return False, False, None

    if result is None:
        return False, False, None

    if ICMP in result and result[ICMP].type == 11:
        return result.src in expected, False, result.src

    if ICMP in result and result[ICMP].type == 0:
        return result.src == target, result.src == target, result.src

    # If we get here, something is very wrong.
    print(f"Traceroute Check: Unexpected response: {result.summary()}")
    return False, False, None
