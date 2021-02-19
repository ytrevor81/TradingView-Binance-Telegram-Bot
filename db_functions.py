import sqlite3
''' Table name: user_info
    Columns:
    1. chat_id: text
    2. strategy_token: text
    3. buy_price: integer
    4. sell_price: integer
    5. cancelled: text (True/False)
    6. user: text'''


class Database(object):
    def __init__(self):
        self.conn = sqlite3.connect('db.sqlite')
        self.c = self.conn.cursor()

    def chat_id_check(self):
        ''' Only one chat can be initialized at a time by the owner of the bot '''
        with self.conn:
            chat_id_tuple = self.c.execute("SELECT chat_id FROM user_info")
        for id in chat_id_tuple:
            chat_id = id[0]
        return chat_id

    def user_check(self):
        ''' This is for security reasons. Only one specified user can use this bot '''
        with self.conn:
            user_tuple = self.c.execute("SELECT user FROM user_info")
        for user in user_tuple:
            username = user[0]
        return username

    def save_chat_id(self, chat_id):
        with self.conn:
            self.c.execute("UPDATE user_info SET chat_id=?", (chat_id,))

    def save_username(self, username):
        ''' Called only once in the Bot's history '''
        with self.conn:
            self.c.execute("UPDATE user_info SET user=?", (username,))
