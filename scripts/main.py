# scripts/main.py

"""
Skoomtown Archive Hack Simulator – Entry Point
"""

from games.data_stream_decrypt import data_stream_decrypt

def main() -> None:
    """
    Main game loop.
    """
    print("Welcome to the Skoomtown Archives Hack Simulator.\n")
    if data_stream_decrypt():
        print("Financial data unlocked! Proceed to the next layer...")
    else:
        print("Access denied. Mission abort.")

if __name__ == "__main__":
    main()
