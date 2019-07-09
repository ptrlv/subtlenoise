"""
Sends random values between 0.0 and 1.0 to the /ping address,
waiting for 1 second between each value.
"""
import argparse
import random
import time

from pythonosc import osc_message_builder
from pythonosc import udp_client


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="127.0.0.1",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=4559,
      help="The port the OSC server is listening on")
  args = parser.parse_args()

  client = udp_client.UDPClient(args.ip, args.port)

n = 0
while True:
  n += 1
  msg = osc_message_builder.OscMessageBuilder(address = "/ping")
  msg.add_arg(n)
  client.send(msg.build())
  time.sleep(1)
  print(n)
