from datetime import datetime, timezone
from typing import List, Optional, Tuple, Union
from dns.resolver import resolve_at


def check_dns(
    host: str,
    server: str,
    query_type="A",
    timeout=2,
    answer: Optional[Union[str, List[str]]] = None
) -> Tuple[bool, float]:
    if answer is str:
        answer = [answer]

    start = datetime.now(timezone.utc)
    try:
        result = resolve_at(server, host, query_type, lifetime=timeout)
        end = datetime.now(timezone.utc)
        time = (end-start).microseconds/1000000
    except Exception as e:
        end = datetime.now(timezone.utc)
        time = (end-start).microseconds/1000000
        return False, time
    
    if answer is not None:
        records = [x.to_text() for x in result]
        if query_type.lower() == "txt":
            # strip quotes
            records = [x[1:-1] for x in records]

        return sorted(records) == sorted(answer), time
    else:
        if len(result) > 0:
            return True, time
    
    return False, time