import os
import psutil
import time
import threading
import sys
from typing import Tuple

class BandwidthMonitor:
    def __init__(self, threshold: int = 100, refresh_rate: int = 5):
        """
        Initialize the bandwidth monitor with default or user-specified thresholds and refresh rates.
        """
        self.threshold = threshold  # Total threshold in MB
        self.refresh_rate = refresh_rate  # Refresh rate in seconds
        self.total_in = 0.0  # Total incoming data in MB
        self.total_out = 0.0  # Total outgoing data in MB
        self.alert_count = 0  # Number of times the threshold was reached
        self.running = True  # Flag to keep the monitoring loop running
        self.lock = threading.Lock()  # For thread-safe updates

    def get_bandwidth_usage(self) -> Tuple[float, float]:
        """
        Retrieve the current bandwidth usage.
        """
        net_io = psutil.net_io_counters()
        incoming_mb = net_io.bytes_recv / (1024 * 1024)
        outgoing_mb = net_io.bytes_sent / (1024 * 1024)
        return incoming_mb, outgoing_mb

    def display_usage(self):
        """
        Clear the screen and display the current bandwidth usage statistics.
        """
        os.system('clear')
        accumulated = self.total_in + self.total_out
        print(f"{'Bandwidth Monitor':^50}")
        print(f"{'Incoming (MB)':<20}{'Outgoing (MB)':<20}{'Total (MB)':<20}")
        print(f"{self.total_in:<20.2f}{self.total_out:<20.2f}{accumulated:<20.2f} ({accumulated/1024:.2f} GB)")

        if accumulated >= self.threshold:
            self.alert_count += 1
            print(f"\nCAUTION: High consumption! Threshold {self.threshold} MB has been reached.")
            sys.stdout.write('\a')  # Play beep

    def reset(self):
        """
        Reset the accumulated bandwidth usage and alert count.
        """
        with self.lock:
            self.total_in = 0.0
            self.total_out = 0.0
        print("\nAccumulated usage reset to 0 MB.")

    def set_refresh_rate(self, new_rate: int):
        """
        Update the refresh rate for monitoring.
        """
        with self.lock:
            self.refresh_rate = new_rate
        print(f"\nRefresh rate updated to {new_rate} seconds.")

    def set_threshold(self, new_threshold: int):
        """
        Update the total threshold for alerts.
        """
        with self.lock:
            self.threshold = new_threshold
        print(f"\nThreshold updated to {new_threshold} MB.")

    def monitor_bandwidth(self):
        """
        Continuously monitor and update bandwidth usage.
        """
        while self.running:
            with self.lock:
                incoming, outgoing = self.get_bandwidth_usage()
                self.total_in += incoming
                self.total_out += outgoing
                self.display_usage()
            time.sleep(self.refresh_rate)

    def handle_commands(self):
        """
        Handle user commands for resetting, quitting, updating settings, and displaying help.
        """
        while self.running:
            command = input("\nEnter a command (H for help): ").strip().lower()
            if command == 'q':
                self.running = False
                self.final_summary()
            elif command == 'r':
                self.reset()
            elif command == 'u':
                try:
                    new_rate = int(input("Enter new refresh rate (seconds): ").strip())
                    self.set_refresh_rate(new_rate)
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
            elif command == 't':
                try:
                    new_threshold = int(input("Enter new total threshold (MB): ").strip())
                    self.set_threshold(new_threshold)
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
            elif command == 'h':
                self.show_help()
            else:
                print("Unknown command. Press H for help.")

    def show_help(self):
        """
        Display the help menu with available commands.
        """
        print("\nAvailable Commands:")
        print("H or h: Show this help menu.")
        print("R or r: Reset accumulated usage.")
        print("Q or q: Quit the app.")
        print("U or u: Update refresh rate.")
        print("T or t: Update total threshold.")

    def final_summary(self):
        """
        Display a final summary before quitting the app.
        """
        print("\nFinal Summary:")
        print(f"Total bandwidth used: {self.total_in + self.total_out:.2f} MB")
        print(f"Threshold reached: {self.alert_count} times")
        print("Goodbye!")

    def run(self):
        """
        Start the monitoring and command-handling threads.
        """
        monitor_thread = threading.Thread(target=self.monitor_bandwidth, daemon=True)
        monitor_thread.start()

        self.handle_commands()
        monitor_thread.join()

# Entry point
if __name__ == "__main__":
    monitor = BandwidthMonitor(threshold=100, refresh_rate=5)
    monitor.run()
