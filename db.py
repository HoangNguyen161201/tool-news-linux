import sqlite3

def connect_db(name = 'mydatabase.db'):
    conn = sqlite3.connect(name)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS links 
                    (id INTEGER PRIMARY KEY, url TEXT)''')
    

    conn.commit()
    conn.close()


# -------------- links news
def get_all_links(name = 'mydatabase.db'):
    conn = sqlite3.connect(name)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM links")
    
    result = cursor.fetchall()

    conn.close()

    return result



def check_link_exists(url, name = 'mydatabase.db'):
    conn = sqlite3.connect(name)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM links WHERE url=?", (url,))
    
    result = cursor.fetchone()

    conn.close()

    if result:
        return True
    else:
        return False
    

def insert_link(url, name = 'mydatabase.db'):
    conn = sqlite3.connect(name)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO links (url) VALUES (?)", (url,))
    conn.commit()
    conn.close()

def delete_link(url, name = 'mydatabase.db'):
    conn = sqlite3.connect(name)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM links WHERE url=?", (url,))
    conn.commit()
    conn.close()