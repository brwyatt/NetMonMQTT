from typing import Any, Callable, Dict, List, Tuple

from netmonmqtt.mqtt.entity import Entity


class Check():
    def __init__(
        self,
        check: Callable[..., Tuple[Any]],
        check_args: List[Any],
        check_kwargs: Dict[str, Any],
        entities: Tuple[Entity],
        interval: int = 60,
    ):
        self.check = check
        self.check_args = check_args
        self.check_kwargs = check_kwargs
        self.entities = entities
        self.interval = interval

    def run_check(self):
        results = self.check(*self.check_args, **self.check_kwargs)

        index = 0
        for entity in self.entities:
            entity.publish_state(results[index])
            index += 1
