
import sqlite3

con = sqlite3.connect("hackaton-lnm.db")

cursor = con.cursor()

cursor.execute("""CREATE TABLE users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    password_hash TEXT,
                    token TEXT,
                    time_token TEXT,
                    ip TEXT,
                    fio TEXT,
                    links TEXT,
                    email TEXT,
                    resume TEXT
                    telegram TEXT,
                    date_create TEXT,
                    )
                """)

# commit model telegram, ip

cursor.execute("""CREATE TABLE projects
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_admin INTEGER,
                title TEXT,
                body TEXT,
                vacancies TEXT,
                image TEXT
                )
                """)

cursor.close()
con.close()
