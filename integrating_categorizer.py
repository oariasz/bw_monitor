
from traffic_categorizer import TrafficCategorizer

if __name__ == "__main__":
    print("Choose an option:")
    print("1. General Bandwidth Monitoring")
    print("2. Categorized Traffic Monitoring")
    choice = input("Enter your choice (1/2): ").strip()

    if choice == '1':
        from bandwidth_monitor import BandwidthMonitor  # Your precious code untouched!
        monitor = BandwidthMonitor(threshold=100, refresh_rate=5)
        monitor.run()
    elif choice == '2':
        interface = input("Enter network interface to monitor (default 'en0'): ").strip() or 'en0'
        categorizer = TrafficCategorizer(interface=interface)
        categorizer.start_categorizing()
    else:
        print("Invalid choice. Exiting.")
