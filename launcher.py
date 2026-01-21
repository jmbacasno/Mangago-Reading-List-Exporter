"""
Launcher script for Mangago Reading List Exporter.
"""

import sys
import os
import argparse

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="Mangago Reading List Exporter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py --cli           # Launch CLI interface
  python launcher.py --help          # Show this help message
  python launcher.py --version       # Show current version

For more information, visit: https://github.com/jmbacasno/Mangago-Reading-List-Exporter
        """
    )
    
    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--cli", 
        action="store_true", 
        help="Launch the CLI interface"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="Mangago Reading List Exporter 1.0.0"
    )
    
    args = parser.parse_args()
    args.cli = True
    
    if args.cli:
        print("⌨️  Launching CLI interface...\n")
        try:
            from cli.main import app
            app()
            return 0
        except ImportError as e:
            print(f"❌ Failed to launch CLI: {e}")
            print("📦 Make sure dependencies are installed: pip install -e .")
            return 1
        except Exception as e:
            print(f"❌ CLI launch error: {e}")
            return 1

if __name__ == "__main__":
    sys.exit(main())
