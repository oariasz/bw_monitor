import os
import pyshark

class TrafficCategorizer:
    def __init__(self, interface: str = 'en0'):
        """
        Initialize the traffic categorizer with the network interface to monitor.
        :param interface: Network interface to capture packets (e.g., 'en0', 'wlan0').
        """
        self.interface = interface
        self.categories = {
            "video": 0.0,
            "audio": 0.0,
            "apps": 0.0,
            "text": 0.0
        }

    def categorize_packet(self, packet):
        """
        Categorize a single packet based on its content or destination.
        :param packet: A pyshark packet object.
        """
        if 'IP' in packet:
            try:
                packet_content = str(packet)
                packet_size_mb = int(packet.length) / (1024 * 1024)

                if 'youtube' in packet_content or 'netflix' in packet_content:
                    self.categories['video'] += packet_size_mb
                elif 'spotify' in packet_content:
                    self.categories['audio'] += packet_size_mb
                elif 'slack' in packet_content or 'zoom' in packet_content:
                    self.categories['apps'] += packet_size_mb
                else:
                    self.categories['text'] += packet_size_mb
            except Exception as e:
                print(f"Error processing packet: {e}")

    def display_categorized_usage(self):
        """
        Display the categorized usage in the terminal.
        """
        os.system('clear')
        print(f"{'Category':<20}{'Usage (MB)':<20}")
        for category, usage in self.categories.items():
            print(f"{category.capitalize():<20}{usage:<20.2f}")

    def start_categorizing(self):
        """
        Start monitoring and categorizing network traffic.
        """
        print(f"Starting live capture on interface {self.interface}... Press Ctrl+C to stop.")
        capture = pyshark.LiveCapture(interface=self.interface)

        try:
            for packet in capture.sniff_continuously():
                self.categorize_packet(packet)
                self.display_categorized_usage()
        except KeyboardInterrupt:
            print("\nStopping capture.")
        finally:
            capture.close()
            self.final_summary()

    def final_summary(self):
        """
        Display a final summary of categorized usage.
        """
        print("\nFinal Summary of Categorized Usage:")
        for category, usage in self.categories.items():
            print(f"{category.capitalize():<20}{usage:<20.2f}")
