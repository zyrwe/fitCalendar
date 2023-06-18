import sqlite3

def create_database():
    connection = sqlite3.connect('fitness.db')
    conn = connection.cursor()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS exercise (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description  TEXT
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS exersise_in_workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cwiczenie_id INTEGER,
            plan_id INTEGER ,
            FOREIGN KEY (cwiczenie_id) REFERENCES cwiczenia (id),
            FOREIGN KEY (plan_id) REFERENCES plany_treningowe (id)
        )
    ''')

