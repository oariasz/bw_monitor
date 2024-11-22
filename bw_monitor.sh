#!/bin/zsh

# Interval in seconds (you can adjust this value)
INTERVAL=2

# Function to display the bandwidth usage
display_bandwidth() {
  clear
  echo "PID       Process                   In Data (MB)   Out Data (MB)"
  echo "-------------------------------------------------------------------"
  
  # Use nettop in batch mode to get the data
  sudo nettop -P -L 1 -x -d $INTERVAL -J bytes_in,bytes_out -k state | \
  awk -F',' '
    NR>1 {
      pid=$1
      proc=$2
      in_bytes=$3
      out_bytes=$4
      in_mb[pid]+=(in_bytes/1048576)
      out_mb[pid]+=(out_bytes/1048576)
      proc_name[pid]=proc
    }
    END {
      for (pid in in_mb) {
        printf "%-9s %-25s %-15.2f %-15.2f\n", pid, proc_name[pid], in_mb[pid], out_mb[pid]
      }
    }
  ' | sort -k3 -nr
}

# Initialize associative arrays
typeset -A in_mb
typeset -A out_mb
typeset -A proc_name

# Main loop
while true; do
  display_bandwidth
  echo -e "\nPress 'r' to reset data, 'q' to quit."
  read -t $INTERVAL -k1 key
  if [[ $key == "r" ]]; then
    # Reset accumulated data
    unset in_mb
    unset out_mb
    unset proc_name
    typeset -A in_mb
    typeset -A out_mb
    typeset -A proc_name
  elif [[ $key == "q" ]]; then
    break
  fi
done
