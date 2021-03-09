import psycopg2
from random import randint


W = H = 1000


def get_apple_pos():
    lx = randint(10, W - 20)
    ly = randint(10, H - 20)

    while lx % 10 != 0:
        lx += 1
    while ly % 10 != 0:
        ly += 1

    return lx, ly


class DB:
    def __init__(self, color, x, y, body):
        """create new player"""
        self.conn = psycopg2.connect('postgres://qkhginftyhitkc:d6a75714496f449045ea09a0398a091d232b50897c43c5a56e1e6ddb253c6746@ec2-54-216-185-51.eu-west-1.compute.amazonaws.com:5432/d7u9eakjulip1f')  # connect to db
        self.cur = self.conn.cursor()
        self.color = color
        self.x = x
        self.y = y
        self.body = body

        self.create_table()

        self.cur.execute("INSERT INTO players(color, x, y, body) VALUES (%s, %s, %s, %s)", (color, x, y, body))
        self.conn.commit()

        self.cur.execute("SELECT id FROM players ORDER BY id DESC")
        self.id, = self.cur.fetchone()

    def create_table(self):
        """create a table if it not exists"""
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id serial NOT NULL PRIMARY KEY,
            color varchar(7) NOT NULL,
            x integer NOT NULL,
            y integer NOT NULL,
            body text NOT NULL
        )
        """)
        self.conn.commit()

    def update(self, x, y, body):
        """update player position"""
        self.x = x
        self.y = y
        self.body = body

        self.cur.execute("UPDATE players SET x = %s, y = %s, body = %s WHERE id = %s", (x, y, body, self.id))
        self.conn.commit()

    def delete(self):
        """delete player when he failing"""
        self.cur.execute("DELETE FROM players WHERE id = %s", (self.id,))
        self.conn.commit()

    def get_other_players(self):
        """return other players' positions"""
        self.cur.execute("SELECT * FROM players WHERE id != %s", (self.id,))
        return self.cur.fetchall()

    @staticmethod
    def parse_string(data: str):
        """parse serialized string"""
        arr = []
        if len(data) == 0:
            return []

        for i in data.split(';'):
            if not i:
                continue
            arr.append([])

            i = list(i)
            i.remove('(')
            i.remove(')')
            i = ''.join(i)

            for j in i.split(','):
                if j.isdigit():
                    j = int(j)
                arr[-1].append(j)

        return arr

    @staticmethod
    def parse_json(data: list):
        """parse dict to serialized string"""
        arr = ''

        if not data:
            return ''

        for i in data:
            arr += '('
            for idx, j in enumerate(i):
                arr += str(j)
                if idx != len(i) - 1:
                    arr += ','
            arr += ');'
        arr = list(arr)

        return ''.join(arr)

    @staticmethod
    def truncate_all():
        """truncate all table with restarting identity"""
        conn = psycopg2.connect('postgres://qkhginftyhitkc:d6a75714496f449045ea09a0398a091d232b50897c43c5a56e1e6ddb253c6746@ec2-54-216-185-51.eu-west-1.compute.amazonaws.com:5432/d7u9eakjulip1f')
        cur = conn.cursor()

        cur.execute("""
        TRUNCATE TABLE players, apples
        RESTART IDENTITY 
        """)
        conn.commit()


class Apple:
    def __init__(self, max_apples=5):
        """initialize new apple manager""" 
        self.conn = psycopg2.connect('postgres://qkhginftyhitkc:d6a75714496f449045ea09a0398a091d232b50897c43c5a56e1e6ddb253c6746@ec2-54-216-185-51.eu-west-1.compute.amazonaws.com:5432/d7u9eakjulip1f')  # connect to db
        self.cur = self.conn.cursor()
        self.max_apples = max_apples

        self.create_table()

    def create_table(self):
        """create a table if it not exists"""
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS apples (
            id serial NOT NULL PRIMARY KEY,
            x integer NOT NULL,
            y integer NOT NULL
        )
        """)
        self.conn.commit()

    def get_apples(self):
        """return apples and creates more if it less than max_apples"""
        self.cur.execute("SELECT x, y FROM apples")
        data = self.cur.fetchall()
        for _ in range(self.max_apples - len(data)):
            self.cur.execute("INSERT INTO apples(x, y) VALUES (%s, %s)", get_apple_pos())
            self.conn.commit()
        self.cur.execute("SELECT * FROM apples")
        return self.cur.fetchall()

    def remove_apple(self, id):
        self.cur.execute("DELETE FROM apples WHERE id = %s", (id,))
        self.conn.commit()
