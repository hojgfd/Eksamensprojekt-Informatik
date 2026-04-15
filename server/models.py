from database import get_db
from nominatim import distance_coord_to_string

def create_user(username, password, address, distance, plate):
    db = get_db()
    db.execute(
        "INSERT INTO users (username, password, address, distance,  plate) VALUES (?, ?, ?, ?, ?)",
        (username, password, address, distance, plate)
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

def update_user(user_id, address, distance, plate):
    db = get_db()
    db.execute(
        "UPDATE users SET address = ?, distance = ?, plate = ? WHERE id = ?",
        (address, distance, plate, user_id)
    )
    db.commit()
    db.close()