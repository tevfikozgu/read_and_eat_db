from flask import current_app
from flask_login import UserMixin
import mysql.connector

mydb = mysql.connector.connect(

  host="hwr4wkxs079mtb19.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
  user="rfabp6xkkpmc6lkv",
  password="jaaefkttt1a0lo10",
  database = "vhvllv9pn37u5nr1",
  ssl_disabled=True,

)

mycursor = mydb.cursor(dictionary=True)

class User(UserMixin):
    def __init__(self,username,password, name_surname , User_ID, userType):
        self.id = username
        self.password = password
        self.name_surname = name_surname
        self.User_ID = User_ID
        self.userType = userType
        self.is_admin = False
        self.active = True

    def get_username(self):
        return self.id
    
    @property
    def is_active(self):
        return self.active

def get_user(Username):
    if Username in current_app.config["ADMIN_USERS"]:
        user = User("admin",current_app.config["PASSWORD"].get(Username), "ADMIN", -1,-1)
        user.is_admin = True
        return user
    else:
        sql = "SELECT * FROM User WHERE Username = %s"
        mycursor.execute(sql, (Username,))
        user = mycursor.fetchone()
        handled_user = User(user["Username"], user["Password"], user["Name_Surname"], user["User_ID"],0) if user else None
        return handled_user

