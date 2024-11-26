import time
import psutil
from scapy.all import sniff
from collections import defaultdict
import threading
from tabulate import tabulate

# Global dictionary to store bandwidth usage per process
process_bandwidth = defaultdict(lambda: {'sent': 0, 'received': 0})

def packet_callback(packet):
    if 'IP' in packet:
        src_ip = packet['IP'].src
        dst_ip = packet['IP'].dst
        packet_len = len(packet)

        matched = False
        for conn in psutil.net_connections(kind='inet'):
            try:
                if conn.laddr and conn.raddr:
                    if conn.laddr.ip == src_ip:
                        process_bandwidth[conn.pid]['sent'] += packet_len
                        matched = True
                    elif conn.raddr.ip == dst_ip:
                        process_bandwidth[conn.pid]['received'] += packet_len
                        matched = True
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
        
        if not matched:
            print(f"Unmatched packet: {src_ip} -> {dst_ip}, Length: {packet_len}")


def monitor_traffic(interface='eth0'):
    """
    Monitor packets on the given interface.
    """
    print(f"Starting packet capture on {interface}...")
    sniff(prn=packet_callback, iface=interface, store=False)


def monitor_top_processes(interval=5, top_n=5):
    """
    Monitor and display the top N processes by bandwidth usage every interval seconds.
    """
    print(f"Monitoring top {top_n} processes by bandwidth usage every {interval} seconds...")
    
    while True:
        time.sleep(interval)

        # Sort processes by bandwidth usage
        sorted_bandwidth = sorted(
            process_bandwidth.items(),
            key=lambda x: x[1]['sent'] + x[1]['received'],
            reverse=True
        )[:top_n]

        # Prepare data for table
        table_data = []
        for pid, usage in sorted_bandwidth:
            proc_name = None
            try:
                proc_name = psutil.Process(pid).name()
            except psutil.NoSuchProcess:
                proc_name = "Unknown"

            sent = usage['sent'] / (1024 * 1024)  # Convert to MB
            received = usage['received'] / (1024 * 1024)  # Convert to MB
            table_data.append([pid, proc_name, f"{sent:.2f} MB", f"{received:.2f} MB"])

        # Print table
        print("\n" + tabulate(table_data, headers=["PID", "Process Name", "Sent", "Received"], tablefmt="grid"))

def main():
    """
    Main function to run the combined packet monitoring and bandwidth display.
    """
    try:
        # Set interface for packet monitoring
        interface = 'en2'  # Replace with your interface (e.g., 'Wi-Fi', 'en0' for macOS)

        # Start packet sniffing in a separate thread
        sniff_thread = threading.Thread(target=monitor_traffic, args=(interface,))
        sniff_thread.daemon = True
        sniff_thread.start()

        # Start monitoring top processes
        interval = 5
        top_n = 5
        monitor_top_processes(interval=interval, top_n=top_n)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")


if __name__ == "__main__":
    main()
