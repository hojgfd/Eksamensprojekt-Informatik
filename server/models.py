from database import get_db

def create_user(username, password, address):
    db = get_db()
    db.execute(
        "INSERT INTO users (username, password, address) VALUES (?, ?, ?)",
        (username, password, address)
    )
    db.commit()
    db.close()

def get_user(username):
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    db.close()
    return user