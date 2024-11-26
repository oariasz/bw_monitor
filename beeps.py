import os
import platform
from time import sleep

def beep_way_1():
    """Use the 'say' command to generate a beep-like sound."""
    if platform.system() == "Darwin":
        print("Playing beep using the 'say' command...")
        os.system('say "beep"')
    else:
        print("This method is specific to macOS.")

def beep_way_2():
    """Use 'afplay' to play a system sound."""
    if platform.system() == "Darwin":
        print("Playing beep using 'afplay'...")
        os.system('afplay /System/Library/Sounds/Ping.aiff')
    else:
        print("This method is specific to macOS.")

def beep_way_3():
    """Use the 'osascript' command to play a system alert sound."""
    if platform.system() == "Darwin":
        print("Playing beep using 'osascript'...")
        os.system('osascript -e "beep 1"')
    else:
        print("This method is specific to macOS.")

def main():
    print("Select a way to play a beep:")
    print("1. Use 'say' command (macOS only)")
    print("2. Use 'afplay' to play a system sound (macOS only)")
    print("3. Use 'osascript' to play a system alert (macOS only)")
    choice = input("Enter the way number (1, 2, or 3): ")

    if choice == "1":
        beep_way_1()
    elif choice == "2":
        beep_way_2()
    elif choice == "3":
        beep_way_3()
    else:
        print("Invalid choice! Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
