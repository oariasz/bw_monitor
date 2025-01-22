import pyshark

# Capture packets from a live interface
capture = pyshark.LiveCapture(interface='eth0')

# Start capturing packets
capture.sniff(timeout=10)

# Print captured packets
for packet in capture:
    print(packet)