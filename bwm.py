import os
import time
import psutil
import argparse
import sys
import platform
import curses
import platform

class BandwidthMonitor:
    def __init__(self, threshold=100.0, refresh_rate=5, incremental_threshold=0.1, stdscr=None):
        """
        Initialize Bandwidth Monitor with configurable parameters
        """
        self.total_threshold = threshold
        self.incremental_threshold = incremental_threshold
        self.refresh_rate = refresh_rate

        # Resettable bandwidth tracking variables
        self.in_usage = 0.0  # Initialize incremental incoming usage
        self.out_usage = 0.0  # Initialize incremental outgoing usage
        self.total_in = 0.0
        self.total_out = 0.0
        self.accumulated = 0.0
        self.threshold_reached_count = 0

        # Lifetime bandwidth tracking variables
        self.lifetime_total_in = 0.0
        self.lifetime_total_out = 0.0
        self.lifetime_accumulated = 0.0

        # Control flags
        self.running = True

        # Curses window
        self.stdscr = stdscr
        self.start_time = time.time()
        
    def beep(self):
        if platform.system() == "Darwin":
            print("Playing beep using 'osascript'...")
            os.system('osascript -e "beep 1"')
        else:
            print("This method is specific to macOS.")

    def get_avg_usage_minute(self):
        """
        Calculate the average usage per minute.
        Returns:
            float: Average usage per minute, or None if no elapsed minutes.
        """
        elapsed_time = time.time() - self.start_time
        elapsed_minutes = elapsed_time / 60  # Convert seconds to minutes
        if elapsed_minutes == 0:
            return None
        return self.accumulated / elapsed_minutes

    def get_avg_usage_hour(self):
        """
        Calculate the average usage per hour.
        Returns:
            float: Average usage per hour, or None if no elapsed hours.
        """
        elapsed_time = time.time() - self.start_time
        elapsed_hours = elapsed_time / 3600  # Convert seconds to hours
        if elapsed_hours == 0:
            return None
        return self.accumulated / elapsed_hours

<<<<<<< HEAD
=======
    def beep(self):
        """Use 'afplay' to play a system sound."""
        if platform.system() == "Darwin":
            print("Playing beep using 'afplay'...")
            os.system('afplay /System/Library/Sounds/Ping.aiff')
        else:
            print('beep: Only works on Mac OS')
        
>>>>>>> 8f691e814d38943389a31263c4924c20328943fc
    def get_bandwidth_usage(self):
        """
        Retrieve current network bandwidth usage in MB
        """
        net_io = psutil.net_io_counters()
        return (net_io.bytes_recv / (1024 * 1024),
                net_io.bytes_sent / (1024 * 1024))

    def run(self):
        """
        Main loop for monitoring bandwidth and handling input.
        """
        self.stdscr.nodelay(True)  # Set getch() to be non-blocking
        previous_in, previous_out = self.get_bandwidth_usage()
        last_refresh_time = time.time()

        while self.running:
            # Check for keyboard input
            key = self.stdscr.getch()
            if key != -1:
                key_char = chr(key).lower()
                if key_char == 'q':
                    self.quit()
                elif key_char == 'r':
                    self.reset()
                elif key_char == 'h':
                    self.show_help()
                elif key_char == 'u':
                    self.set_refresh_rate()
                elif key_char == 't':
                    self.set_total_threshold()
                elif key_char == 'i':
                    self.set_incremental_threshold()

            # Check if it's time to refresh the metrics
            current_time = time.time()
            if current_time - last_refresh_time >= self.refresh_rate:
                # Get current bandwidth usage
                current_in, current_out = self.get_bandwidth_usage()

                # Calculate interval bandwidth usage
                in_usage = current_in - previous_in
                out_usage = current_out - previous_out
                total_interval_usage = in_usage + out_usage

                # Store incremental usage for display
                self.in_usage = in_usage
                self.out_usage = out_usage

                # Check incremental threshold if set
                if (self.incremental_threshold is not None and
                    total_interval_usage > self.incremental_threshold):
                    self.alert_incremental_threshold(total_interval_usage)

                # Update cumulative metrics
                self.total_in += in_usage
                self.total_out += out_usage
                self.accumulated += total_interval_usage

                # Update lifetime cumulative metrics
                self.lifetime_total_in += in_usage
                self.lifetime_total_out += out_usage
                self.lifetime_accumulated += total_interval_usage

                # Check total threshold
                if self.accumulated >= self.total_threshold:
                    self.threshold_reached_count += 1
                    self.alert_total_threshold()

                # Display usage
                self.display_usage()

                # Update previous usage and last refresh time
                previous_in, previous_out = current_in, current_out
                last_refresh_time = current_time

            # Small sleep to prevent CPU overuse
            time.sleep(0.1)

    def display_usage(self):
        """
        Display current bandwidth usage statistics
        Clear screen and show formatted metrics using curses
        """
        # Get the screen size (rows and columns)
        max_rows, max_cols = self.stdscr.getmaxyx()
        
        # Clear the screen
        self.stdscr.clear()
        
        # Display header
        line = 0
        self.stdscr.addstr(line, 0, "Bandwidth Monitor")
        self.stdscr.addstr(line + 1, 0, "=" * 20)

        # Display parameters
        line += 3
        self.stdscr.addstr(line, 0, f"Refresh Rate: {self.refresh_rate}s | Incremental Threshold: {self.incremental_threshold or 'N/A'} MB | Total Threshold: {self.total_threshold} MB")

        # Display incremental and accumulated usage
        line += 2
        self.stdscr.addstr(line, 0, f"Incremental In:        {self.in_usage:.2f} MB")
        self.stdscr.addstr(line + 1, 0, f"Incremental Out:       {self.out_usage:.2f} MB")
        line += 3
        self.stdscr.addstr(line, 0, f"Accumulated In:        {self.total_in:.2f} MB ({self.total_in / 1024:.2f} GB)")
        self.stdscr.addstr(line + 1, 0, f"Accumulated Out:       {self.total_out:.2f} MB ({self.total_out / 1024:.2f} GB)")
        self.stdscr.addstr(line + 2, 0, f"Total Accumulated:     {self.accumulated:.2f} MB ({self.accumulated / 1024:.2f} GB)")
        
        # Display lifetime usage if there is enough space
        line += 6
        if line + 3 < max_rows:
            self.stdscr.addstr(line, 0, "Lifetime Usage (since start):")
            self.stdscr.addstr(line + 1, 0, f"Lifetime In:          {self.lifetime_total_in:.2f} MB ({self.lifetime_total_in / 1024:.2f} GB)")
            self.stdscr.addstr(line + 2, 0, f"Lifetime Out:         {self.lifetime_total_out:.2f} MB ({self.lifetime_total_out / 1024:.2f} GB)")
            self.stdscr.addstr(line + 3, 0, f"Lifetime Total:       {self.lifetime_accumulated:.2f} MB ({self.lifetime_accumulated / 1024:.2f} GB)")
            line += 4
        
        # Display threshold and instructions if there is enough space
        if line + 2 < max_rows:
            self.stdscr.addstr(line, 0, f"Threshold Reached: {self.threshold_reached_count}")
            self.stdscr.addstr(line + 2, 0, "Press 'H' for Help")

        # Refresh the screen
        self.stdscr.refresh()

    def alert_total_threshold(self):
        self.stdscr.addstr(9, 0, f"CAUTION: High consumption! Threshold {self.total_threshold} MB reached.")
        self.stdscr.refresh()
<<<<<<< HEAD
        self.beep()
=======
        # Beep sound
        self.beep()   # My own beep
>>>>>>> 8f691e814d38943389a31263c4924c20328943fc

    def alert_incremental_threshold(self, current_usage):
        self.stdscr.addstr(10, 0, f"WARNING: Interval usage {current_usage:.2f} MB exceeds {self.incremental_threshold} MB limit.")
        self.stdscr.refresh()
        self.beep()

    def reset(self):
        previous_total = self.accumulated
        previous_threshold_count = self.threshold_reached_count

        # Reset only the resettable metrics
        self.total_in = 0.0
        self.total_out = 0.0
        self.accumulated = 0.0
        self.threshold_reached_count = 0

        self.stdscr.addstr(12, 0, "Bandwidth Usage Reset:")
        self.stdscr.addstr(13, 0, f"Previous Total Usage: {previous_total:.2f} MB")
        self.stdscr.addstr(14, 0, f"Previous Threshold Reaches: {previous_threshold_count}")
        self.stdscr.refresh()
        time.sleep(2)

    def quit(self):
        self.running = False
        elapsed_time = time.time() - self.start_time
        elapsed_hours, rem = divmod(int(elapsed_time), 3600)
        elapsed_minutes, elapsed_seconds = divmod(rem, 60)
        elapsed_formatted = f"{elapsed_hours:02}:{elapsed_minutes:02}:{elapsed_seconds:02}"

        avg_per_minute = self.get_avg_usage_minute()
        avg_per_hour = self.get_avg_usage_hour()

        curses.endwin()
        os.system("clear")

        print("\nFinal Bandwidth Summary")
        print("=" * 25)
        print(f"Total In:                 {self.total_in:.2f} MB ({self.total_in / 1024:.2f} GB)")
        print(f"Total Out:                {self.total_out:.2f} MB ({self.total_out / 1024:.2f} GB)")
        print(f"Total Accumulated:        {self.accumulated:.2f} MB ({self.accumulated / 1024:.2f} GB)")
        print(f"Lifetime Total In:        {self.lifetime_total_in:.2f} MB ({self.lifetime_total_in / 1024:.2f} GB)")
        print(f"Lifetime Total Out:       {self.lifetime_total_out:.2f} MB ({self.lifetime_total_out / 1024:.2f} GB)")
        print(f"Lifetime Total:           {self.lifetime_accumulated:.2f} MB ({self.lifetime_accumulated / 1024:.2f} GB)")
        print(f"Elapsed Time:             {elapsed_formatted}")
        if avg_per_minute:
            print(f"Average Usage per Minute: {avg_per_minute:.2f} MB")
        else:
            print("Average Usage per Minute: N/A")
        if avg_per_hour:
            print(f"Average Usage per Hour:   {avg_per_hour:.2f} MB")
        else:
            print("Average Usage per Hour: N/A")
        print(f"Threshold Reached: {self.threshold_reached_count}")
        print("\nGoodbye!")

        sys.exit(0)

    def set_refresh_rate(self):
        curses.echo()
        self.stdscr.addstr(10, 0, "Enter new refresh rate (in seconds): ")
        self.stdscr.clrtoeol()
        self.stdscr.refresh()
        input_str = self.stdscr.getstr(10, 36).decode('utf-8')
        curses.noecho()
        try:
            new_rate = float(input_str)
            self.refresh_rate = new_rate
            self.stdscr.addstr(11, 0, f"Refresh rate updated to {new_rate} seconds.")
        except ValueError:
            self.stdscr.addstr(11, 0, "Invalid input. Refresh rate unchanged.")
        self.stdscr.clrtoeol()
        self.stdscr.refresh()
        time.sleep(2)

    def set_total_threshold(self):
        curses.echo()
        self.stdscr.addstr(10, 0, "Enter new total threshold (in MB): ")
        self.stdscr.clrtoeol()
        self.stdscr.refresh()
        input_str = self.stdscr.getstr(10, 34).decode('utf-8')
        curses.noecho()
        try:
            new_threshold = float(input_str)
            self.total_threshold = new_threshold
            self.stdscr.addstr(11, 0, f"Total threshold updated to {new_threshold} MB.")
        except ValueError:
            self.stdscr.addstr(11, 0, "Invalid input. Threshold unchanged.")
        self.stdscr.clrtoeol()
        self.stdscr.refresh()
        time.sleep(2)

    def set_incremental_threshold(self):
        curses.echo()
        self.stdscr.addstr(10, 0, "Enter new incremental threshold (in MB): ")
        self.stdscr.clrtoeol()
        self.stdscr.refresh()
        input_str = self.stdscr.getstr(10, 42).decode('utf-8')
        curses.noecho()
        try:
            new_threshold = float(input_str)
            self.incremental_threshold = new_threshold
            self.stdscr.addstr(11, 0, f"Incremental threshold updated to {new_threshold} MB.")
        except ValueError:
            self.stdscr.addstr(11, 0, "Invalid input. Incremental threshold unchanged.")
        self.stdscr.clrtoeol()
        self.stdscr.refresh()
        time.sleep(2)

    def show_help(self):
        self.stdscr.addstr(13, 0, "Bandwidth Monitor - Help Menu:")
        self.stdscr.addstr(14, 0, "-" * 30)
        self.stdscr.addstr(15, 0, "R/r  : Reset bandwidth usage")
        self.stdscr.addstr(16, 0, "Q/q  : Quit application")
        self.stdscr.addstr(17, 0, "U/u  : Set new refresh rate")
        self.stdscr.addstr(18, 0, "T/t  : Set new total threshold")
        self.stdscr.addstr(19, 0, "I/i  : Set new incremental threshold")
        self.stdscr.addstr(20, 0, "H/h  : Show this help menu")
        self.stdscr.refresh()
        time.sleep(5)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Bandwidth Monitoring Tool')
    parser.add_argument('-t', '--threshold', type=float, default=100.0,
                        help='Total bandwidth threshold in MB')
    parser.add_argument('-r', '--refresh', type=int, default=5,
                        help='Refresh rate in seconds')
    parser.add_argument('-i', '--incremental', type=float,
                        help='Per-interval bandwidth threshold')
    return parser.parse_args()

def main():
    args = parse_arguments()

    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    try:
        monitor = BandwidthMonitor(
            threshold=args.threshold,
            refresh_rate=args.refresh,
            incremental_threshold=10.0,
            stdscr=stdscr
        )
        monitor.run()
    except KeyboardInterrupt:
        print("\nInterrupted! Exiting...")
        monitor.quit()
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

if __name__ == "__main__":
    main()
