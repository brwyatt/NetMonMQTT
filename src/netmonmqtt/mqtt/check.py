from random import randint
from threading import Event, Thread
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
        self.stop_thread = Event()
        self.thread: Optional[Thread] = None

    def run_check(self):
        results = self.check(*self.check_args, **self.check_kwargs)

        index = 0
        for entity in self.entities:
            entity.publish_state(results[index])
            index += 1

    def loop(self):
        threadname = self.thread.name if self.thread is not None else "UNKNOWN"
        print(f"Loop Started: {threadname}")
        while not self.stop_thread.is_set():
            self.run_check()
            jitter_ms = int(self.jitter * 1000)
            self.stop_thread.wait(self.interval + (float(randint((-1 * jitter_ms), jitter_ms)) / 1000))
        print(f"Loop Ended: {threadname}")

    def start(self):
        print("Check Start")
        if self.thread is not None and self.thread.is_alive():
            print("Thread already running!")
            return
        self.stop_thread.clear()
        self.thread = Thread(target=self.loop)
        self.thread.start()

    def stop(self):
        print("Check Stop")
        self.stop_thread.set()
        self.thread = None
