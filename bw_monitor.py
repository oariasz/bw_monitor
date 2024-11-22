import pyshark
import time
import threading
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)

# Time interval for updating data (in seconds)
INTERVAL = 2

# Dictionary to store cumulative data transferred per IP and port
traffic_data = defaultdict(lambda: {"in": 0, "out": 0})

def capture_packets(interface="en0"):
    """
    Capture packets on a specified network interface and update the traffic data.
    """
    capture = pyshark.LiveCapture(interface=interface)

    try:
        for packet in capture.sniff_continuously():
            process_packet(packet)
    except KeyboardInterrupt:
        logging.info("Stopping packet capture.")
    finally:
        capture.close()

def process_packet(packet):
    """
    Process each captured packet to aggregate in/out data by IP and port.
    """
    try:
        if "ip" in packet:
            src_ip = packet.ip.src
            dst_ip = packet.ip.dst
            size = int(packet.length)

            # Assuming the local IP as incoming, and remote as outgoing for simplicity
            if src_ip.startswith(("192.", "10.", "172.")):
                traffic_data[(src_ip, packet[packet.transport_layer].srcport)]["out"] += size
            else:
                traffic_data[(dst_ip, packet[packet.transport_layer].dstport)]["in"] += size

    except AttributeError:
        logging.debug("Packet without IP layer ignored.")

def display_traffic():
    """
    Display cumulative traffic data for each IP and port.
    """
    print(f"\n{'IP':<15}{'Port':<7}{'In Data (MB)':<15}{'Out Data (MB)'}")
    print("-" * 50)
    for (ip, port), data in traffic_data.items():
        print(f"{ip:<15}{port:<7}{data['in'] / (1024 * 1024):<15.2f}{data['out'] / (1024 * 1024):.2f}")

    print("\nPress 'r' to reset data, 'q' to quit.")

def reset_traffic_data():
    """
    Reset the accumulated traffic data.
    """
    global traffic_data
    traffic_data = defaultdict(lambda: {"in": 0, "out": 0})

if __name__ == "__main__":
    # Start packet capture in a separate thread
    capture_thread = threading.Thread(target=capture_packets)
    capture_thread.start()

    # Main loop for displaying data and handling user input
    try:
        while True:
            time.sleep(INTERVAL)
            display_traffic()
            # Handle user input for resetting or quitting
            key = input("\nPress 'r' to reset data, 'q' to quit: ").strip().lower()
            if key == "r":
                reset_traffic_data()
            elif key == "q":
                break

    except KeyboardInterrupt:
        logging.info("Exiting...")
    finally:
        capture_thread.join()
        logging.info("Capture thread has been joined. Exiting...")