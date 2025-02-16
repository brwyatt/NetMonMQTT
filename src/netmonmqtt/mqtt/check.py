from random import randint
from threading import Thread
from time import sleep
from typing import Any, Callable, Dict, List, Optional, Tuple

from netmonmqtt.mqtt.entity import Entity


class Check():
    def __init__(
        self,
        check: Callable[..., Tuple[Any]],
        check_args: List[Any],
        check_kwargs: Dict[str, Any],
        entities: Tuple[Entity],
        interval: int = 60,
        jitter: float = 0.5,
    ):
        self.check = check
        self.check_args = check_args
        self.check_kwargs = check_kwargs
        self.entities = entities
        self.interval = interval
        self.jitter = jitter
        self.do_run = False
        self.thread: Optional[Thread] = None

    def run_check(self):
        results = self.check(*self.check_args, **self.check_kwargs)

        index = 0
        for entity in self.entities:
            entity.publish_state(results[index])
            index += 1

    def loop(self):
        while self.do_run:
            self.run_check()
            sleep(self.interval + (float(randint(0, int(self.jitter * 1000))) / 1000))

    def start(self):
        print("Check Start")
        self.do_run = True
        self.thread = Thread(target=self.loop).start()

    def stop(self):
        print("Check Start")
        self.do_run = True
        self.thread = None
