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

class Restaurant(UserMixin):
    def __init__(self,username,password, name_surname , Restaurant_ID):
        self.id = username
        self.password = password
        self.name_surname = name_surname
        self.Restaurant_ID = Restaurant_ID
        self.is_admin = False
        self.active = True

    def get_username(self):
        return self.id
    
    @property
    def is_active(self):
        return self.active

def get_user(Username):

        sql = "SELECT * FROM Restaurant WHERE Owner_Username = %s"
        mycursor.execute(sql, (Username,))
        user = mycursor.fetchone()
        handled_user = Restaurant(user["Owner_Username"], user["Owner_Password"], user["Owner_Name"], user["Restaurant_ID"]) if user else None
        return handled_user