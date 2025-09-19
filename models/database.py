import sqlite3
import os

def createdatabase():
    if os.path.exists("data/parking.db"):
        print('path already exists')
        return
    conn=sqlite3.connect("data/parking.db")
    c=conn.cursor()

    c.execute("""CREATE TABLE USERS(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              Full_name TEXT NOT NULL,
              Email_id TEXT UNIQUE NOT NULL,
              Password TEXT NOT NULL,
              Address TEXT NOT NULL,
              Pincode INTEGER NOT NULL,
              role TEXT CHECK(role IN ('admin','user'))NOT NULL DEFAULT 'user' )
    """)

    c.execute("""CREATE TABLE Parking_lot(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              prime_location_name TEXT NOT NULL,
              Price INTEGER NOT NULL,
              Address TEXT NOT NULL,
              Pincode INTEGER NOT NULL,
              maximum_number_of_spots INTEGER NOT NULL)
              """)
    
    c.execute("""CREATE TABLE Parking_spot(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              lot_id INTEGER NOT NULL,
              status TEXT CHECK(status in ('A','O')) DEFAULT 'A',
              FOREIGN KEY (lot_id) REFERENCES Parking_lot(id))
              """)
    
    c.execute("""CREATE TABLE Reserve_parking_spot(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              spot_id INTEGER NOT NULL,
              user_id INTEGER NOT NULL,
              Parking_timestamp TEXT NOT NULL,
              Leaving_timestamp TEXT,
              Parking_cost INTEGER,
              vehicle_number TEXT,
              FOREIGN KEY (spot_id) REFERENCES Parking_spot(id),
              FOREIGN KEY (user_id) REFERENCES USERS(id)
              )
              """)
    
    c.execute("""INSERT INTO USERS (Full_name,Email_id,Password,Address,Pincode,role) VALUES ('ADMIN','ADMIN@gmail.com','ADMIN123','ADMINS HOME',000000,'admin' )""")

    conn.commit()
    conn.close()
    print('everything is good')
    


if __name__=='__main__':
    createdatabase()