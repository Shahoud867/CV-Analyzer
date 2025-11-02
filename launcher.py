#!/usr/bin/env python3
"""
CV Analyzer Launcher
Choose between GUI and Command Line interfaces
"""

import sys
import os
from pathlib import Path

def main():
    """Main launcher function."""
    print("="*60)
    print("INTELLIGENT CV ANALYZER")
    print("String Matching Algorithms: Brute Force • Rabin-Karp • KMP")
    print("="*60)
    print()
    print("Choose interface:")
    print("1. 🖥️  GUI Application (Recommended)")
    print("2. 💻 Command Line Interface")
    print("3. ❌ Exit")
    print()
    
    while True:
        choice = input("Select option (1-3): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting GUI Application...")
            try:
                # Change to the intelligent_cv_analyzer directory
                os.chdir(Path(__file__).parent / "intelligent_cv_analyzer")
                
                # Import and run GUI
                from gui_app import main as gui_main
                gui_main()
                break
            except Exception as e:
                print(f"❌ Error starting GUI: {e}")
                print("💡 Try installing PyQt5: pip install PyQt5")
                break
                
        elif choice == "2":
            print("\n🚀 Starting Command Line Interface...")
            try:
                # Change to the intelligent_cv_analyzer directory
                os.chdir(Path(__file__).parent / "intelligent_cv_analyzer")
                
                # Import and run CLI
                from app import main as cli_main
                cli_main()
                break
            except Exception as e:
                print(f"❌ Error starting CLI: {e}")
                break
                
        elif choice == "3":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
