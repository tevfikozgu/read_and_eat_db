import mysql.connector

mydb = mysql.connector.connect(

  host="hwr4wkxs079mtb19.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
  user="rfabp6xkkpmc6lkv",
  password="jaaefkttt1a0lo10",
  database = "vhvllv9pn37u5nr1",
  ssl_disabled=True,

)


INIT_STATEMENTS = ['''
        CREATE TABLE IF NOT EXISTS User(
        User_ID INTEGER AUTO_INCREMENT,
        Username VARCHAR(40) NOT NULL UNIQUE,
        Name_Surname VARCHAR(40) NOT NULL,
        Password VARCHAR(50) NOT NULL,
        PRIMARY KEY (User_ID))''',
        
        '''
        CREATE TABLE IF NOT EXISTS Restaurant(
        Restaurant_ID INTEGER AUTO_INCREMENT,
        Address VARCHAR(255) NOT NULL,
        Name VARCHAR(30) NOT NULL,
        City VARCHAR(20) NOT NULL,
        District VARCHAR(30) NOT NULL,
        Owner_Username VARCHAR(30) NOT NULL UNIQUE,
        Owner_Password VARCHAR(40) NOT NULL,
        Owner_Name VARCHAR(30) NOT NULL,
        PRIMARY KEY (Restaurant_ID))''',


        '''
        CREATE TABLE IF NOT EXISTS Food(
        Food_ID INTEGER AUTO_INCREMENT,
        Food_Name VARCHAR (255) NOT NULL,
        Restaurant_ID INTEGER NOT NULL,
        Price INTEGER NOT NULL,
        PRIMARY KEY (Food_ID),
        FOREIGN KEY (Restaurant_ID) REFERENCES Restaurant(Restaurant_ID) 
            ON DELETE CASCADE ON UPDATE CASCADE,
        CHECK (Price > 0))''',

        '''
        CREATE TABLE IF NOT EXISTS Comments(
        Comment_ID INTEGER AUTO_INCREMENT,
        Restaurant_ID INTEGER,
        Food_ID INTEGER,
        Sender_ID INTEGER NOT NULL,
        Comment VARCHAR (255) NOT NULL,
        Comment_Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (Comment_ID),
        FOREIGN KEY (Restaurant_ID) REFERENCES Restaurant(Restaurant_ID)
            ON DELETE CASCADE ON UPDATE CASCADE, 
        FOREIGN KEY (Sender_ID) REFERENCES User(User_ID)
            ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (Food_ID) REFERENCES Food(Food_ID)
            ON DELETE CASCADE ON UPDATE CASCADE)''',


            '''
        CREATE TABLE IF NOT EXISTS Votes(
        Vote_ID INTEGER AUTO_INCREMENT,
        Restaurant_ID INTEGER,
        Food_ID INTEGER,
        Sender_ID INTEGER NOT NULL,
        Vote INTEGER NOT NULL,
        PRIMARY KEY (Vote_ID),
        FOREIGN KEY (Restaurant_ID) REFERENCES Restaurant(Restaurant_ID)
            ON DELETE CASCADE ON UPDATE CASCADE, 
        FOREIGN KEY (Sender_ID) REFERENCES User(User_ID)
            ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (Food_ID) REFERENCES Food(Food_ID)
            ON DELETE CASCADE ON UPDATE CASCADE)''',

            '''
        CREATE TABLE IF NOT EXISTS Demands(
        Demand_ID INTEGER AUTO_INCREMENT,
        Demand VARCHAR (255) NOT NULL,
        Restaurant_ID INTEGER NOT NULL,
        Sender_ID INTEGER NOT NULL,
        Demand_Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (Demand_ID),
        FOREIGN KEY (Restaurant_ID) REFERENCES Restaurant(Restaurant_ID) 
            ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (Sender_ID) REFERENCES User(User_ID) 
            ON DELETE CASCADE ON UPDATE CASCADE)
        '''

        ]

def initialize():
    cursor=mydb.cursor()
    for statement in INIT_STATEMENTS:
        cursor.execute(statement)
        mydb.commit()
    cursor.close()
    return mydb

if __name__=="__main__":
    initialize()