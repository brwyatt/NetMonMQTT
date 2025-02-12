
import sys
from typing import List, Optional

from netmonmqtt.config import Config
from netmonmqtt.mqtt import connect


def main(args: Optional[List[str]] = None):
    if args is None:
        args = sys.argv[1:]

    conf = Config()

    client = connect(conf["host"], conf["port"], conf["username"], conf["password"], secure=True, async_connect=True)

    client.loop_forever()


if __name__ == "__main__":
    main()
