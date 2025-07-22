# main.py

from database.db import initialize_database

def main():
    initialize_database()
    print("Database initialized and ready!")

if __name__ == '__main__':
    main()
