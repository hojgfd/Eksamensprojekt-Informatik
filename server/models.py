from database import get_db
from nominatim import distance_coord_to_string

lat_skole = 56.156277
long_skole = 10.187640



def create_user(username, password, address, plate):
    db = get_db()
    db.execute(
        "INSERT INTO users (username, password, address, plate) VALUES (?, ?, ?, ?)",
        (username, password, address, plate)
    )
    db.commit()
    db.close()
    print(f"Distance til skolen for {username}: {distance_coord_to_string(lat_skole, long_skole, address)}")


def get_user(username):
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    db.close()
    return user

def update_user(user_id, address, plate):
    db = get_db()
    db.execute(
        "UPDATE users SET address = ?, plate = ? WHERE id = ?",
        (address, plate, user_id)
    )
    db.commit()
    db.close()