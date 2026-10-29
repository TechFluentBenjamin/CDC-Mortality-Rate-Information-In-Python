# main.py
#added sys, and changed "break" to sys.exit(0) to ensure the program exits cleanly when the user chooses to exit.

import program_dashboard as p1
import program_anomaly as p2
import program_bubbles as p3
import sys


def show_menu():
    print("\n" + "=" * 30)
    print(" CDC MORTALITY DATA TOOLKIT ")
    print("=" * 30)
    print("1. Run Rate-of-Change Dashboard")
    print("2. Run Anomaly Detector")
    print("3. Run Animated Bubble Chart")
    print("4. Exit")
    print("=" * 30)


def main():
    while True:
        show_menu()
        choice = input("Please select an option (1-4): ")

        if choice == "1":
            print("\nLaunching Dashboard...")
            p1.run_dashboard()

        elif choice == "2":
            print("\nLaunching Anomaly Detector...")
            p2.run_anomaly()

        elif choice == "3":
            print("\nLaunching Bubble Chart...")
            p3.run_bubbles()

        elif choice == "4":
            print("Exiting program. Goodbye!")
            sys.exit(0)

        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
