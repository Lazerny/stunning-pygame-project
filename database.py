import sqlite3


class DatabaseManager:
    def __init__(self, db_name='Spaceship.sqlite'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        try:
            if params:
                result = self.cursor.execute(query, params).fetchall()
            else:
                result = self.cursor.execute(query)
            self.conn.commit()
            return result

        except Exception as e:
            print(e)

    def fetch_data(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()
