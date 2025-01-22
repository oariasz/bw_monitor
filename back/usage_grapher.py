import time
import threading
from typing import List
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import psutil

class BandwidthGrapher:
    def __init__(self, refresh_rate: int = 1):
        """
        Initialize the bandwidth grapher.
        :param refresh_rate: The interval in seconds for updating data.
        """
        self.refresh_rate = refresh_rate
        self.in_usage: List[float] = []  # List to store incoming bandwidth usage
        self.out_usage: List[float] = []  # List to store outgoing bandwidth usage
        self.time_points: List[float] = []  # List to store time points
        self.start_time = time.time()  # Start time to calculate elapsed time
        self.running = True  # Flag to control the graphing loop

    def get_bandwidth_usage(self):
        """
        Retrieve the current bandwidth usage in MB.
        """
        net_io = psutil.net_io_counters()
        incoming_mb = net_io.bytes_recv / (1024 * 1024)
        outgoing_mb = net_io.bytes_sent / (1024 * 1024)
        return incoming_mb, outgoing_mb

    def update_usage_data(self):
        """
        Continuously collect bandwidth usage data.
        """
        prev_in, prev_out = self.get_bandwidth_usage()
        while self.running:
            time.sleep(self.refresh_rate)
            current_in, current_out = self.get_bandwidth_usage()
            elapsed_time = time.time() - self.start_time

            # Calculate usage since last update
            in_diff = current_in - prev_in
            out_diff = current_out - prev_out

            self.in_usage.append(in_diff)
            self.out_usage.append(out_diff)
            self.time_points.append(elapsed_time)

            # Update previous values
            prev_in, prev_out = current_in, current_out

    def animate_graph(self, i):
        """
        Update the graph with the latest data.
        """
        plt.cla()  # Clear the current plot

        # Plot incoming and outgoing data
        plt.plot(self.time_points, self.in_usage, label="Incoming (MB)")
        plt.plot(self.time_points, self.out_usage, label="Outgoing (MB)")

        # Customize the graph
        plt.title("Real-Time Bandwidth Usage")
        plt.xlabel("Time (s)")
        plt.ylabel("Usage (MB)")
        plt.legend()
        plt.grid()

    def start_graphing(self):
        """
        Start the graphing process.
        """
        # Start a thread to update usage data
        data_thread = threading.Thread(target=self.update_usage_data, daemon=True)
        data_thread.start()

        # Set up real-time plotting
        fig = plt.figure()
        ani = animation.FuncAnimation(fig, self.animate_graph, interval=1000)  # Update every 1 second
        plt.show()

        # Stop the data thread when graphing is done
        self.running = False
        data_thread.join()

# Example standalone usage
if __name__ == "__main__":
    grapher = BandwidthGrapher(refresh_rate=1)
    grapher.start_graphing()


'''
TO INTEGRATE IT...

from traffic_categorizer import TrafficCategorizer
from usage_grapher import BandwidthGrapher

if __name__ == "__main__":
    print("Choose an option:")
    print("1. General Bandwidth Monitoring")
    print("2. Categorized Traffic Monitoring")
    print("3. Real-Time Graphing of Bandwidth Usage")
    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == '1':
        from bandwidth_monitor import BandwidthMonitor  # Your precious code untouched!
        monitor = BandwidthMonitor(threshold=100, refresh_rate=5)
        monitor.run()
    elif choice == '2':
        interface = input("Enter network interface to monitor (default 'en0'): ").strip() or 'en0'
        categorizer = TrafficCategorizer(interface=interface)
        categorizer.start_categorizing()
    elif choice == '3':
        refresh_rate = int(input("Enter refresh rate for graphing (seconds, default 1): ").strip() or 1)
        grapher = BandwidthGrapher(refresh_rate=refresh_rate)
        grapher.start_graphing()
    else:
        print("Invalid choice. Exiting.")

'''