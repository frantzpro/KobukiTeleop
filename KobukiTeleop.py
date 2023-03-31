#!/usr/bin/env python
import signal
import sys
import time
from time import sleep

from AbstractVirtualCapability import AbstractVirtualCapability, VirtualCapabilityServer, formatPrint


class KobukiTeleop(AbstractVirtualCapability):
    def __init__(self, server):
        super().__init__(server)
        self.functionality = {"pressedJoyA": None, "pressedJoyB": None, "pressedJoyX": None, "pressedJoyY": None}

    def loop(self):
        command = {"type": "response", "capability": "pressedButton", "parameters": {}, "src": f"KobukiTeleop-{time.time()}"}
        if self.functionality["pressedJoyA"]():
            command["parameters"]["XBOX360Button"] = "A"
        elif self.functionality["pressedJoyB"]():
            command["parameters"]["XBOX360Button"] = "B"
        elif self.functionality["pressedJoyX"]():
            command["parameters"]["XBOX360Button"] = "X"
        elif self.functionality["pressedJoyY"]():
            command["parameters"]["XBOX360Button"] = "Y"
        if command["parameters"]["XBOX360Button"] is not None:
            self.send_message(command)


if __name__ == '__main__':
    # Needed for properly closing when process is being stopped with SIGTERM signal
    def handler(signum, frame):
        print("[Main] Received SIGTERM signal")
        listener.kill()
        quit(1)


    try:
        port = None
        if len(sys.argv[1:]) > 0:
            port = int(sys.argv[1])
        server = VirtualCapabilityServer(port)
        listener = KobukiTeleop(server)
        listener.start()
        signal.signal(signal.SIGTERM, handler)
        listener.join()
    # Needed for properly closing, when program is being stopped wit a Keyboard Interrupt
    except KeyboardInterrupt:
        print("[Main] Received KeyboardInterrupt")
        server.kill()
        listener.kill()
