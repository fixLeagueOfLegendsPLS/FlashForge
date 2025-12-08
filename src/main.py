#!/usr/bin/env python3
"""
FlashForge - Local Flashcard Application
Entry point for the application.
"""

import sys
import os

# Add src to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Main entry point."""
    from src.app import run
    run()


if __name__ == "__main__":
    main()
