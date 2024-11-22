import subprocess
import time
import curses
import threading

class ProcessInfo:
    def __init__(self, pid, name):
        self.pid = pid
        self.name = name
        self.in_data = 0  # Incoming data in bytes
        self.out_data = 0  # Outgoing data in bytes

    def update_bandwidth(self, new_in_data, new_out_data):
        self.in_data = new_in_data
        self.out_data = new_out_data

    def reset(self):
        self.in_data = 0
        self.out_data = 0

class ProcessMonitor:
    def __init__(self, interval=1, top_n=20):
        self.interval = interval
        self.top_n = top_n
        self.process_data = {}
        self.running = True

    def parse_nettop_output(self, output):
        lines = output.strip().split('\n')
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) < 4:
                continue  # Skip lines that don't have the expected format

            try:
                pid = int(parts[0])
                process_name = parts[1]
                in_data = float(parts[2])  # Bytes in
                out_data = float(parts[3])  # Bytes out

                self.process_data[pid] = ProcessInfo(pid, process_name)
                self.process_data[pid].update_bandwidth(in_data, out_data)
            except ValueError:
                continue  # Skip lines with parsing errors

    def fetch_network_data(self):
        # Run `nettop` command in batch mode for continuous updates
        self.proc = subprocess.Popen(
            ["nettop", "-P", "-L", "0", "-x", "-d", str(self.interval), "-J", "bytes_in,bytes_out"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        while self.running:
            output = ''
            try:
                output = self.proc.stdout.readline()
                if output == '':
                    break  # EOF
                self.parse_nettop_output(output)
            except Exception as e:
                print(f"Error reading nettop output: {e}")
                break

    def display_processes(self, stdscr):
        stdscr.nodelay(True)
        while self.running:
            stdscr.clear()
            max_y, max_x = stdscr.getmaxyx()

            header = f"{'PID':<10}{'Process':<25}{'In Data (MB)':<15}{'Out Data (MB)':<15}"
            try:
                stdscr.addstr(0, 0, header[:max_x])
                stdscr.addstr(1, 0, "-" * min(65, max_x))
            except curses.error:
                pass

            # Sort processes by incoming data and take the top N
            sorted_processes = sorted(
                self.process_data.values(),
                key=lambda x: x.in_data,
                reverse=True
            )[:self.top_n]

            total_in_data = 0
            total_out_data = 0
            row = 2

            for process_info in sorted_processes:
                if row >= max_y - 1:
                    break

                total_in_data += process_info.in_data
                total_out_data += process_info.out_data

                line = (
                    f"{process_info.pid:<10}"
                    f"{process_info.name[:25]:<25}"
                    f"{process_info.in_data / (1024 * 1024):<15.2f}"
                    f"{process_info.out_data / (1024 * 1024):<15.2f}"
                )[:max_x]

                try:
                    stdscr.addstr(row, 0, line)
                    row += 1
                except curses.error:
                    pass

            # Display the total accumulated data at the bottom
            total_line = (
                f"{'TOTAL':<35}"
                f"{total_in_data / (1024 * 1024):<15.2f}"
                f"{total_out_data / (1024 * 1024):<15.2f}"
            )[:max_x]

            try:
                stdscr.addstr(max_y - 1, 0, total_line)
            except curses.error:
                pass

            stdscr.refresh()
            time.sleep(self.interval)

            # Check for reset key press
            try:
                key = stdscr.getkey()
                if key == 'r':
                    self.reset_data()
            except:
                pass  # No key pressed

    def reset_data(self):
        for process_info in self.process_data.values():
            process_info.reset()

    def start_monitoring(self, stdscr):
        try:
            # Start the network data fetching in a separate thread
            fetch_thread = threading.Thread(target=self.fetch_network_data)
            fetch_thread.start()

            # Start displaying the data
            self.display_processes(stdscr)

        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            if self.proc:
                self.proc.terminate()
            fetch_thread.join()
            stdscr.addstr(0, 0, "Monitoring stopped.")
            stdscr.refresh()
            time.sleep(1)

if __name__ == "__main__":
    import sys

    # Optional argument for top_n, default is 20
    top_n = int(sys.argv[1]) if len(sys.argv) > 1 else 20

    monitor = ProcessMonitor(interval=2, top_n=top_n)
    curses.wrapper(monitor.start_monitoring)
