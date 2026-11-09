import logging
from .create_table import create_tables

def main():
    logging.basicConfig(level=logging.INFO)
    create_tables()

if __name__ == "__main__":
    main()
