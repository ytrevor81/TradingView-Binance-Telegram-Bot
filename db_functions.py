import sqlite3
''' Table name: user_info
    Columns:
    1. chat_id: text
    2. strategy_token: text
    3. buy_price: integer
    4. sell_price: integer
    5. cancelled: text (True/False)'''


class Database(object):
    def __init__(self):
        self.conn = sqlite3.connect('db.sqlite')
        self.c = self.conn.cursor()

    def chat_id_check(self):
        with self.conn:
            chat_id = self.c.execute("SELECT chat_id FROM user_info")
        self.conn.close()
        return chat_id

    def save_chat_id(self, chat_id):
        with self.conn:
            self.c.execute("UPDATE user_info SET chat_id=?", (chat_id,))
        self.conn.close()
