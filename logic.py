import sqlite3
from config import DB_NAME


class DB_Manager:
    def __init__(self, database):
        self.database = database

    def create_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()

            cur.execute('''CREATE TABLE IF NOT EXISTS blocked_links (
                            id INTEGER PRIMARY KEY, 
                            links TEXT)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY, 
                            chat_id INTEGER, 
                            warning_count INTEGER DEFAULT 0)''')
            conn.commit()

    # Добавление ссылки в черный список
    def add_link(self, chat_id, link):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()

            cur.execute(f'SELECT links FROM blocked_links WHERE id = {chat_id}')
            result = cur.fetchone()
            # Проверяем, существует ли запись
            if result:
                links = eval(result[0])

                links.append(link)
                links = str(links)
                

                cur.execute("""UPDATE blocked_links
                            SET links = ?
                            WHERE id = ?""", (links, chat_id))
                conn.commit()
            else:
                cur.execute("""INSERT INTO blocked_links (id, links)
                                VALUES (?, ?)""", (chat_id, f'["{link}"]'))
                conn.commit()


    # Удаление ссылки из черного списка
    def del_link(self, chat_id, link):#Ответы: False -> такой ссылки нет в чёрном списке, True -> ссылка удалена
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()

            cur.execute(f'SELECT links FROM blocked_links WHERE id = {chat_id}')
            result = cur.fetchone()
            try:
                if result:
                    links = eval(result[0])
                    links.remove(link)
                    links = str(links)
                    

                    cur.execute("""UPDATE blocked_links
                                SET links = ?
                                WHERE id = ?""", (links, chat_id))
                    conn.commit()
                else:
                    return False
                return True
            except ValueError:
                return False

    # Получение количества варнов пользователя
    def get_warning_count(self, user_id, chat_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(f"""SELECT warning_count
                        FROM users 
                        WHERE id = {user_id} AND chat_id = {chat_id}""") 
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                cur.execute("""INSERT INTO users (id, chat_id, warning_count)
                VALUES (?, ?, ?)""", (user_id, chat_id, 0))
                conn.commit()
                return 0

    # Получение списка запрещённых ссылок в определённой группе 
    def get_blocked_links(self, chat_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(f"""SELECT links
                        FROM blocked_links 
                        WHERE id = {chat_id}""")
            result = eval(cur.fetchall()[0][0])
            return result

    # Добавление варна пользователю
    def add_warning(self, user_id, chat_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            warning_count = self.get_warning_count(user_id, chat_id) + 1
            cur.execute(f"""UPDATE users
                            SET warning_count = {warning_count}
                            WHERE id = {user_id} AND chat_id = {chat_id}""")
            conn.commit()
            return warning_count

    # Проверяет, если указанная ссылка есть в бд
    def check_link_in_db(self, chat_id, check_link):
            conn = sqlite3.connect(self.database)
            with conn:
                cur = conn.cursor()
                cur.execute(f"""SELECT links
                            FROM blocked_links
                            WHERE id = {chat_id}""")
                links = eval(cur.fetchall()[0][0])

                for link in links:
                    if link in check_link:
                        return True
                return False

if __name__ == '__main__':
    db = DB_Manager(DB_NAME)
    db.create_table()
    # db.add_link(2, "https://google.com4")
    # db.add_link(2, "https://google.com5")
    # db.add_link(2, "https://google.com6")
    # db.del_link(1, "https://google.com2")
    # db.add_warning(1, 2)
    links = db.get_blocked_links(2)
    print(links)
