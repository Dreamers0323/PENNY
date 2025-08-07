# main.py
# this script initializes the database and sets up the environment for the application
from database.db import initialize_database

def main():
    initialize_database()
    print("Database initialized and ready!")

if __name__ == '__main__':
    main()
