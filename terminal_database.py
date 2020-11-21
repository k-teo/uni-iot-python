import sqlite3
import os


def create_database():
    if os.path.exists("workers.db"):
        os.remove("workers.db")
        print("An old database removed.")
    connection = sqlite3.connect("workers.db")
    cursor = connection.cursor()
    cursor.execute(""" CREATE TABLE working_hours (
            worker text,
            terminal_id text,
            day text,
            time text
        )""")
    connection.commit()
    connection.close()
    print("The new database created.")


if __name__ == "__main__":
    create_database()







