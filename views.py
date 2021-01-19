from datetime import datetime
from flask import render_template, current_app,abort, request, redirect, url_for, flash, session
import mysql.connector
import hashlib
from functools import wraps
import math


mydb = mysql.connector.connect(

  host="hwr4wkxs079mtb19.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
  user="rfabp6xkkpmc6lkv",
  password="jaaefkttt1a0lo10",
  database = "vhvllv9pn37u5nr1",
  ssl_disabled=True,

)

mycursor = mydb.cursor(dictionary=True)

def get_score_name(avg):
    if avg == 0:
        return "Not Voted Yet"
    elif avg == 1:
        return "Very Bad"
    elif avg == 2:
        return "Bad"
    elif avg == 3:
        return "Can be Improved"
    elif avg == 4:
        return "Good"
    elif avg == 5:
        return "Excellent"
    else:
        return ""

def login_required_owner(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if 'user_type' in session:
            if session['user_type'] == 'owner':
                return f(*args,**kwargs)
            else:  
                return redirect(url_for("home_page"))
        else:  
            return redirect(url_for("login_page"))
    return decorated_function

def login_required_admin(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if 'user_type' in session:
            if session['user_type'] == 'admin':
                return f(*args,**kwargs)
            else:  
                return redirect(url_for("home_page"))
        else:  
            return redirect(url_for("login_page"))
    return decorated_function

def login_required_user(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if 'user_type' in session:
            if session['user_type'] == 'user':
                return f(*args,**kwargs)
            else:
                return redirect(url_for("home_page"))
        else:
            return redirect(url_for("login_page"))
    return decorated_function

def md5(string):
    return hashlib.md5(string.encode()).hexdigest()

def home_page():
    return render_template("home.html")

@login_required_owner
def edit_foods_page():
    if request.method == "POST":
        if 'delete_food' in request.form:
            try:
                delete_query = "DELETE FROM Food WHERE Food_ID = %s AND Restaurant_ID = %s"
                mycursor.execute(delete_query,(request.form['delete_food'],session['user_id'],))
                mydb.commit()
            except:
                mycursor.rollback()
        else:
            return redirect(url_for('update_food',food_key = request.form['update_food']))
    try:
        restaurant_foods_fetch = """ 
                                    SELECT SUM(Vote),COUNT(Sender_ID), Food.Food_ID,Price,Food.Food_Name FROM Food 
                                    LEFT JOIN Votes ON Food.Food_ID = Votes.Food_ID WHERE Food.Restaurant_ID = %s 
                                    GROUP BY Food.Food_ID
                                """
        mycursor.execute(restaurant_foods_fetch,(session['user_id'],))
        restaurant_foods = mycursor.fetchall()
        return render_template("edit_foods.html", restaurant_foods=restaurant_foods)
    except:
        mycursor.rollback()
        return render_template("edit_foods.html")
    
@login_required_user
def restaurants_page():
    try:
        restaurantFetch = '''SELECT * FROM Restaurant
                            ORDER BY Restaurant_ID ASC
                        '''
        mycursor.execute(restaurantFetch,)
        restaurants = mycursor.fetchall()
        return render_template("restaurants.html", restaurants=restaurants)
    except:
        mydb.rollback()
        return render_template("restaurants.html")
    
@login_required_user
def restaurant_detail_page(restaurant_key):
    vote_info = hasVoteRestaurant(restaurant_key)
    if request.method == 'POST':
        if "send_comment" in request.form:
            if request.form["send_comment"] == "send_comment_clicked":
                if request.form["comment"] !=  '' and request.form["comment"].strip() != '':
                    try:
                        sql = "INSERT INTO Comments SET Restaurant_ID = %s, Comment = %s, Sender_ID = %s"
                        mycursor.execute(sql, (restaurant_key, request.form["comment"], session['user_id']))
                        mydb.commit()
                    except:
                        mycursor.rollback()
        elif "edit_comment" in request.form:
            return redirect(url_for('edit_restaurant_comment',comment_key = request.form['edit_comment'], restaurant_key_comment = restaurant_key))
        elif "delete_vote" in request.form:
            sql = "DELETE FROM Votes WHERE Sender_ID = %s AND Restaurant_ID = %s"
            mycursor.execute(sql, (session['user_id'],restaurant_key,))
            mydb.commit()     
        if "send_demand" in request.form:
            if request.form["send_demand"] == "send_demand_clicked":
                try:
                    sql = "INSERT INTO Demands SET Restaurant_ID = %s, Demand = %s, Sender_ID = %s"
                    mycursor.execute(sql, (restaurant_key, request.form["demand"], session['user_id']))
                    mydb.commit()
                except:
                    mycursor.rollback()   
        else:
            if "optionsRadios" in request.form:
                vote = int(request.form["optionsRadios"])
                try:
                    if vote_info:
                        update_score_query = """
                            UPDATE Votes
                            SET Vote=%s 
                            WHERE Restaurant_ID=%s AND Sender_ID = %s
                        """
                        mycursor.execute(update_score_query, (vote,restaurant_key, session['user_id']))
                        mydb.commit()
                    else:
                        add_score_query = """
                            INSERT INTO Votes
                            SET Vote=%s, Restaurant_ID=%s, Sender_ID = %s 
                        """
                        mycursor.execute(add_score_query, (vote, restaurant_key,session['user_id']))
                        mydb.commit()
                except:
                    mydb.rollback()
    
    try:
        vote_info = hasVoteRestaurant(restaurant_key)
        restaurant_menu_fetch = "SELECT Food.Food_ID, Food_Name, Price, Name FROM Restaurant " \
            "INNER JOIN Food ON Food.Restaurant_ID = Restaurant.Restaurant_ID " \
            "WHERE Restaurant.Restaurant_ID = %s"

        mycursor.execute(restaurant_menu_fetch, (int(restaurant_key),))
        resturant_menu = mycursor.fetchall()

        restaurant_detail_fetch = '''SELECT * FROM Restaurant
                                    WHERE Restaurant_ID = %s
                                    '''
                                    
        mycursor.execute(restaurant_detail_fetch, (int(restaurant_key),))
        restaurant_details = mycursor.fetchone()

        total_votes_and_count = "SELECT Count(Sender_ID),SUM(Vote) FROM Votes WHERE Restaurant_ID = %s GROUP BY Restaurant_ID"
        mycursor.execute(total_votes_and_count, (int(restaurant_key),))
        restaurant_votes = mycursor.fetchone()
        score_name = ""
        vote_avg = 0
        vote_count = 0

        if restaurant_votes:
            vote_count = restaurant_votes['Count(Sender_ID)']
            vote_avg = int(restaurant_votes['SUM(Vote)']) / int(restaurant_votes['Count(Sender_ID)'])
            score_name = get_score_name(math.ceil(vote_avg))
            vote_avg = '{:.2f}'.format(vote_avg)
        else:
            vote_avg = 0
            score_name = get_score_name(0)

        restaurant_comments_fetch = "SELECT Comments.Sender_ID, Comment_ID, Name_Surname, Comments.Comment, Comment_Time FROM User \
                                    INNER JOIN Comments ON Comments.Sender_ID = User_ID \
                                    Where User_ID IN ( \
                                        SELECT Sender_ID FROM Restaurant \
                                                INNER JOIN Comments ON Comments.Restaurant_ID = Restaurant.Restaurant_ID \
                                                WHERE Restaurant.Restaurant_ID = %s \
                                    ) AND Food_ID IS NULL AND Comments.Restaurant_ID = %s"  

        mycursor.execute(restaurant_comments_fetch, (int(restaurant_key),int(restaurant_key)))
        resturant_comments = mycursor.fetchall()
        return render_template("restaurant_details.html",restaurant_menu = resturant_menu, restaurant_details = restaurant_details, resturant_comments=resturant_comments,vote_info=vote_info, vote_avg = vote_avg, score_name=score_name,vote_count=vote_count)

    except:
        mydb.rollback()
        return render_template("restaurant_details.html")

@login_required_owner
def restaurant_detail_owner():
    if request.method == 'POST':
        return redirect(url_for('update_restaurant_info'))
    try:
        restaurant_detail_fetch = '''SELECT * FROM Restaurant
                                    WHERE Restaurant_ID = %s
                                    '''
                                    
        mycursor.execute(restaurant_detail_fetch, (session['user_id'],))
        restaurant_details = mycursor.fetchone()

        total_votes_and_count = "SELECT Count(Sender_ID),SUM(Vote) FROM Votes WHERE Restaurant_ID = %s GROUP BY Restaurant_ID"
        mycursor.execute(total_votes_and_count, (session['user_id'],))
        restaurant_votes = mycursor.fetchone()
        score_name = ""
        vote_avg = 0
        vote_count = 0

        if restaurant_votes:
            vote_count = restaurant_votes['Count(Sender_ID)']
            vote_avg = int(restaurant_votes['SUM(Vote)']) / int(restaurant_votes['Count(Sender_ID)'])
            score_name = get_score_name(math.ceil(vote_avg))
            vote_avg = '{:.2f}'.format(vote_avg)
        else:
            vote_avg = 0
            score_name = get_score_name(0)

        restaurant_comments_fetch = "SELECT Comments.Sender_ID, Comment_ID, Name_Surname, Comments.Comment, Comment_Time FROM User \
                                    INNER JOIN Comments ON Comments.Sender_ID = User_ID \
                                    Where User_ID IN ( \
                                        SELECT Sender_ID FROM Restaurant \
                                                INNER JOIN Comments ON Comments.Restaurant_ID = Restaurant.Restaurant_ID \
                                                WHERE Restaurant.Restaurant_ID = %s \
                                    ) AND Food_ID IS NULL AND Comments.Restaurant_ID = %s"  


        mycursor.execute(restaurant_comments_fetch, (session['user_id'],session['user_id'],))
        resturant_comments = mycursor.fetchall()

        demands_query = """SELECT Demand, Demand_Time, Name_Surname FROM Demands INNER JOIN User ON User.User_ID = Demands.Sender_ID WHERE Restaurant_ID = %s """
        mycursor.execute(demands_query, (session['user_id'],))
        demands = mycursor.fetchall()

        return render_template("restaurant_details_owner.html", restaurant_details = restaurant_details, resturant_comments=resturant_comments, vote_avg = vote_avg, score_name=score_name,vote_count=vote_count, demands=demands)

    except:
        mydb.rollback()
        return render_template("restaurant_details_owner.html")


@login_required_user
def food_detail_page(restaurant_key,food_key):
    vote_info = hasVoteFood(food_key)
    if request.method == 'POST':
        if "send_comment" in request.form:
            if request.form["send_comment"] == "send_comment_clicked":
                if request.form["comment"] !=  '' and request.form["comment"].strip() != '':
                    try:
                        sql = "INSERT INTO Comments SET Food_ID = %s, Comment = %s, Sender_ID = %s"
                        mycursor.execute(sql, (food_key, request.form["comment"], session['user_id']))
                        mydb.commit()
                    except:
                        mydb.rollback()
        elif "edit_comment" in request.form:
            return redirect(url_for('edit_food_comment',comment_key = request.form['edit_comment'], food_key_comment = food_key, restaurant_key_comment = restaurant_key))
        elif "delete_vote" in request.form:
            sql = "DELETE FROM Votes WHERE Sender_ID = %s AND Food_ID = %s"
            mycursor.execute(sql, (session['user_id'],food_key,))
            mydb.commit()
        else:
            if "optionsRadios" in request.form:
                vote = int(request.form["optionsRadios"])
                try:
                    if vote_info:
                        update_score_query = """
                            UPDATE Votes
                            SET Vote=%s 
                            WHERE Food_ID=%s AND Sender_ID = %s
                        """
                        mycursor.execute(update_score_query, (vote, food_key,session['user_id'],))
                        mydb.commit()
                    else:
                        add_score_query = """
                            INSERT INTO Votes
                            SET Vote=%s, Food_ID=%s, Sender_ID = %s 
                        """
                        mycursor.execute(add_score_query, (vote, food_key,session['user_id']))
                        mydb.commit()
                except:
                    mydb.rollback()
    try:
        vote_info = hasVoteFood(food_key)
        food_detail_fetch = "SELECT Name, Food_Name, Price FROM Food " \
            "INNER JOIN Restaurant ON Food.Restaurant_ID = Restaurant.Restaurant_ID " \
            "WHERE Restaurant.Restaurant_ID = %s AND Food_ID = %s"

        mycursor.execute(food_detail_fetch, (int(restaurant_key),int(food_key),))
        food_details = mycursor.fetchone()
        
        total_votes_and_count = "SELECT Count(Sender_ID),SUM(Vote) FROM Votes WHERE Food_ID = %s GROUP BY Food_ID"
        mycursor.execute(total_votes_and_count, (int(food_key),))
        food_votes = mycursor.fetchone()
        score_name = ""
        vote_avg = 0
        vote_count = 0

        if food_votes:
            vote_count = food_votes['Count(Sender_ID)']
            vote_avg = int(food_votes['SUM(Vote)']) / int(food_votes['Count(Sender_ID)'])
            score_name = get_score_name(math.ceil(vote_avg))
            vote_avg = '{:.2f}'.format(vote_avg)
        else:
            vote_avg = 0
            score_name = get_score_name(0)

        food_comments_fetch = "SELECT Comment_ID, Comments.Sender_ID,Name_Surname, Comments.Comment, Comment_Time FROM User \
                                    INNER JOIN Comments ON Comments.Sender_ID = User_ID \
                                    Where User_ID IN ( \
                                        SELECT Sender_ID FROM Food \
                                                INNER JOIN Comments ON Comments.Food_ID = Food.Food_ID \
                                                WHERE Food.Food_ID = %s \
                                    ) AND Restaurant_ID IS NULL AND Comments.Food_ID = %s"  
        mycursor.execute(food_comments_fetch, (int(food_key),int(food_key)))
        food_comments = mycursor.fetchall()
        return render_template("food_details.html",food_details = food_details, food_comments = food_comments, score_name=score_name,vote_avg=vote_avg,vote_info=vote_info, vote_count=vote_count)

    except:
        mydb.rollback()
        return render_template("food_details.html")

def about_page():
    if request.method == 'POST':
        if request.form["submit_button"] == "edit":
            return redirect(url_for('update_profile'))
        elif request.form["submit_button"] == "change_password":
            return redirect(url_for('edit_password'))
    else:
        return render_template("about.html")

@login_required_owner
def add_food_page():
    error = ''
    if request.method == 'POST':
        if request.form['Food_Name'] == '':
            error = 'Please Write Food Name!'
        elif request.form['Price'] == '':
            error = 'Please Write Price!'
        elif (has_this_food(request.form['Food_Name'], session['user_id'])):
            error = 'There is a Food with this name in your restaurant'
        else:
            try:
                sql = "INSERT INTO Food SET Food_Name = %s, Restaurant_ID = %s, Price = %s"
                mycursor.execute(sql, (request.form['Food_Name'], session['user_id'], request.form['Price']))
                mydb.commit()
                if mycursor.rowcount:
                    return redirect(url_for('edit_foods_page'))
                else:
                    error = 'There is a technical problem!'
            except:
                mydb.rollback()
                error = 'There is a technical problem!'

    return render_template("add_food.html", error=error)

@login_required_admin
def delete_restaurant_page():
    if request.method == "GET":
        try:
            restaurantFetch = '''SELECT * FROM Restaurant
                            ORDER BY Restaurant_ID ASC
                            '''
            mycursor.execute(restaurantFetch,)
            restaurants = mycursor.fetchall()
            return render_template("delete_restaurants.html", restaurants=restaurants)
        except:
            return render_template("delete_restaurants.html")
    else:
        form_restaurant_keys = request.form.getlist("restaurant_keys")
        for restaurant_ID in form_restaurant_keys:
            delete_from_restaurants(restaurant_ID)
        mydb.commit()
        return redirect(url_for("delete_restaurant_page"))

@login_required_admin
def delete_users():
    if request.method == "GET":
        try:
            userFetch = '''SELECT * FROM User
                            ORDER BY User_ID ASC
                            '''
            mycursor.execute(userFetch,)
            users = mycursor.fetchall()
            return render_template("delete_users.html", users=users)
        except:
            return render_template("delete_users.html")
    else:
        form_user_keys = request.form.getlist("user_keys")
        for user_ID in form_user_keys:
            delete_from_users(user_ID)
        mydb.commit()

        return redirect(url_for("delete_users"))

def login_page():
    if 'user_id' in session:
        return redirect(url_for('home_page'))
    error = ''
    if request.method == 'POST':
        if request.form['username'] == '':
            error = 'Type Username!'
        elif request.form['password'] == '':
            error = 'Type Password!'
        else:
            if request.form["login_type"] == "User":
                try:
                    sql = "SELECT * FROM User WHERE Username = %s AND Password = %s"
                    mycursor.execute(sql, (request.form['username'], md5(request.form['password']),))
                    user = mycursor.fetchone()
                    if user:
                        session['user_id'] = user['User_ID']
                        session['username'] = user['Username']
                        session["user_type"] = "user"
                        session['password'] = user['Password']
                        session['name_surname'] = user['Name_Surname']
                        return redirect(url_for('home_page'))
                    else:
                        error = 'There is no users with these informations.'
                except:
                    error = 'There is a problem.'

            elif request.form["login_type"] == "Owner":
                try:
                    sql = "SELECT * FROM Restaurant WHERE Owner_Username = %s AND Owner_Password=%s"
                    mycursor.execute(sql, (request.form['username'], md5(request.form['password']),))
                    user = mycursor.fetchone()
                    if user:
                        session['user_id'] = user['Restaurant_ID']
                        session["user_type"] = "owner"
                        return redirect(url_for('home_page'))
                    else:
                        error = 'There is no Restaurant account with these informations.'
                except:
                    error = 'There is a problem.'

            elif request.form["login_type"] == "Admin":
                try:
                    if request.form['username'] in current_app.config["ADMIN_USERS"] and current_app.config["PASSWORD"]['admin'] == md5(request.form['password']) :
                        session['user_id'] = 'ADMIN'
                        session["user_type"] = "admin"
                        return redirect(url_for('home_page'))
                    else:
                        error = 'There is no admin with these informations.'
                except:
                    mydb.rollback()
                    error = 'There is a problem.'
    return render_template('login.html', error=error)

@login_required_admin
def delete_from_restaurants(restaurant_ID):
    try:
        delete_interrupt = "DELETE FROM Restaurant WHERE Restaurant_ID = %s"
        mycursor.execute(delete_interrupt,(restaurant_ID,))
        mydb.commit()
    except:
        mydb.rollback()

@login_required_admin
def delete_from_users(user_ID):
    try:
        delete_interrupt = "DELETE FROM User WHERE User_ID = %s"
        mycursor.execute(delete_interrupt,(user_ID,))
        mydb.commit()
    except:
        mydb.rollback()

def register_page():
    error = ''
    if request.method == 'POST':
        if request.form['Name_Surname'] == '':
            error = 'Type name and Surname'
        elif request.form['Username'] == '':
            error = 'Type Usename'
        elif request.form['password'] == '' or request.form['re_password'] == '':
            error = 'Type password'
        elif request.form['password'] != request.form['re_password']:
            error = 'Passwords do not match'
        elif hasUser(request.form['Username']):
            error = 'There is a user with this username'
        elif ' ' in (request.form['Username']):
            error = 'There cannot be space in your username'
        elif ' ' in request.form['password']:
            error = 'There cannot be space in your password'
        elif len(request.form['Username']) < 6:
            error = 'Type username longer than 5 char'
        elif len(request.form['password']) < 6:
            error = 'Type password longer than 5 char'
        else:
            try:
                sql = "INSERT INTO User SET Name_Surname = %s, Username = %s, Password = %s"
                mycursor.execute(sql, (request.form['Name_Surname'], request.form['Username'], md5(request.form['password'])))
                mydb.commit()
                if mycursor.rowcount:
                    next_page = request.args.get("next", url_for("home_page"))
                    return redirect(next_page)
                else:
                    error = 'There is a technical problem!'
            except:
                mydb.rollback()
    return render_template('register.html', error=error)


@login_required_admin
def new_restaurant_page():
    error = ''
    if request.method == 'POST':
        if request.form['Restaurant_Name'] == '':
            error = 'Please Write the Restaurant Name'
        elif request.form['Username'] == '':
            error = 'Type Customer Username'
        elif request.form['Customer_Name'] == '':
            error = 'Write Customer Name Surname'
        elif request.form['password'] == '' or request.form['re_password'] == '':
            error = 'Please Write Password'
        elif request.form['password'] != request.form['re_password']:
            error = 'Passwords do not match'
        elif hasRestaurantUser(request.form['Username']):
            error = 'This username is used'
        elif request.form['city'] == '------':
            error = 'Write City'
        elif request.form['District'] == '':
            error = 'Write District'
        elif request.form['Address'] == '':
            error = 'Write Address!'
        elif ' ' in (request.form['Username']):
            error = 'There cannot be space in your username'
        elif ' ' in request.form['password']:
            error = 'There cannot be space in your password'
        elif len(request.form['Username']) < 6:
            error = 'Type username longer than 5 char'
        elif len(request.form['password']) < 6:
            error = 'Type password longer than 5 char'
        
        else:
            try:
                sql = "INSERT INTO Restaurant SET Name = %s, Owner_Username = %s, Owner_Password = %s, Owner_Name = %s, City = %s, District = %s, Address = %s"
                mycursor.execute(sql, (request.form['Restaurant_Name'], request.form['Username'], md5(request.form['password']), request.form['Customer_Name'], request.form['city'], request.form['District'], request.form['Address']))
                mydb.commit()
                if mycursor.rowcount:
                    return redirect(url_for('home_page'))
                else:
                    error = 'There is a technical problem!'
            except:
                mydb.rollback()
                error = 'There is a technical problem!'

    return render_template('add_restaurant.html', error=error)

@login_required_user
def edit_password():
    error = ''
    
    if request.method == 'POST':
        password_new = md5(request.form["Old_Password"])
        if request.form['Old_Password'] == '':
            error = 'Please Write Name'
        elif request.form['New_Password'] == '':
            error = 'Type New Password'
        elif request.form['New_Password_Again'] == '':
            error = 'New Password Again'
        elif session['password'] != md5(request.form["Old_Password"]):
            error = 'This password is wrong'
        elif request.form['New_Password'] != request.form['New_Password_Again']:
            error = 'Passwords are not same'
        elif ' ' in request.form['New_Password']:
            error = 'There cannot be space in your password'
        elif len(request.form['New_Password']) < 6:
            error = 'Type password longer than 5 char'
        else:
            password_new = md5(request.form["New_Password"])
            try:
                query = """ \
                            UPDATE User \
                            SET Password = %s \
                            WHERE User_ID= %s 
                        """
                mycursor.execute(query, (password_new,session['user_id']))
                mydb.commit()
                session['password'] = password_new
                return redirect(url_for('about_page'))
            except:
                mydb.rollback()
                return redirect(url_for('about_page'))
    return render_template('update_password.html', error=error)

@login_required_user
def update_profile():
    error = ''
    if request.method == 'POST':
        if request.form['Username'] == '':
            error = 'Please Write Username'
        elif request.form['Name_Surname'] == '':
            error = 'Type Name Surname'
        elif hasUser(request.form['Username']) and request.form['Username'] != session['username']:
            error = 'This username is used'
        elif ' ' in (request.form['Username']):
            error = 'There cannot be space in your username'
        elif len(request.form['Username']) < 6:
            error = 'Type username longer than 5 char'
        else:
            try:
                query = """ \
                            UPDATE User \
                            SET Username = %s, \
                            Name_Surname = %s \
                            WHERE User_ID= %s 
                        """
                mycursor.execute(query, (request.form['Username'],request.form['Name_Surname'],session['user_id']))
                mydb.commit()
                session['username'] = request.form['Username']
                session['name_surname'] = request.form['Name_Surname']
            except:
                mydb.rollback()
            return redirect(url_for('about_page'))

    return render_template('edit_profile.html', error=error)

@login_required_owner
def update_restaurant_info():
    error = ''
    if request.method == 'POST':
        if request.form['Restaurant_Name'] == '':
            error = 'Please Write Restaurant Name'
        elif request.form['Customer_Name'] == '':
            error = 'Type Your Name'
        elif request.form['city'] == '':
            error = 'Type City'
        elif request.form['District'] == '':
            error = 'Type District'
        elif request.form['Address'] == '':
            error = 'Type Address'
        else:
            try:
                query = """ \
                            UPDATE Restaurant \
                            SET Name = %s, \
                            Address = %s, \
                            City = %s, \
                            District = %s, \
                            Owner_Name = %s \
                            WHERE Restaurant_ID= %s 
                        """
                mycursor.execute(query, (request.form['Restaurant_Name'],request.form['Address'],request.form['city'],request.form['District'],request.form['Customer_Name'],session['user_id'],))
                mydb.commit()
            except:
                mydb.rollback()
            return redirect(url_for('restaurant_detail_owner'))
    try:
        sql = "SELECT * FROM Restaurant WHERE Restaurant_ID = %s "
        mycursor.execute(sql, ( session['user_id'],))
        restaurant_info = mycursor.fetchone()
        return render_template('update_restaurant_info.html',restaurant_info=restaurant_info, error=error)
    except:
        error = 'Error while getting comment!'
        mydb.rollback()
        return render_template('update_restaurant_info.html', error=error)

@login_required_user
def edit_restaurant_comment(comment_key,restaurant_key_comment):
    error = ''
    if request.method == 'POST':
        if request.form['Comment'] == '':
            error = 'Please Write Comment'
        
        else:
            try:
                if request.form['submit_button'] == 'edit_comment':
                    query = """ \
                            UPDATE Comments \
                            SET Comment = %s \
                            WHERE Comment_ID= %s AND\
                            Restaurant_ID = %s
                        """
                    mycursor.execute(query, (request.form['Comment'],comment_key,restaurant_key_comment))
                    
                elif request.form['submit_button'] == 'delete_comment':
                    query = "DELETE FROM Comments WHERE Comment_ID = %s AND Restaurant_ID = %s"
                    mycursor.execute(query, (comment_key,restaurant_key_comment,))
                mydb.commit()
                return redirect(url_for('restaurant_detail_page',restaurant_key=restaurant_key_comment))
            except:
                mydb.rollback()
    try:
        sql = "SELECT * FROM Comments WHERE Comment_ID = %s AND Restaurant_ID = %s "
        mycursor.execute(sql, (comment_key, restaurant_key_comment,))
        comment = mycursor.fetchone()
        return render_template('edit_comment.html',comment=comment, error=error)
    except:
        error = 'Error while getting comment!'
        mydb.rollback()
        return render_template('edit_comment.html', error=error)

@login_required_user
def edit_food_comment(comment_key,food_key_comment,restaurant_key_comment):
    error = ''
    if request.method == 'POST':
        if request.form['Comment'] == '':
            error = 'Please Write Comment'
    
        else:
            try:
                if request.form['submit_button'] == 'edit_comment':
                    query = """ \
                            UPDATE Comments \
                            SET Comment = %s \
                            WHERE Comment_ID= %s AND\
                            Food_ID = %s
                        """
                    mycursor.execute(query, (request.form['Comment'],comment_key,food_key_comment))
                    
                elif request.form['submit_button'] == 'delete_comment':
                    query = "DELETE FROM Comments WHERE Comment_ID = %s AND Food_ID = %s"
                    mycursor.execute(query, (comment_key,food_key_comment,))
                mydb.commit()
                return redirect(url_for('food_detail_page',restaurant_key=restaurant_key_comment,food_key = food_key_comment))
            except:
                error = 'ERROR OCCURED!'
                mydb.rollback()
                return render_template('edit_comment.html', error=error)

    try:
        sql = "SELECT * FROM Comments WHERE Comment_ID = %s AND Food_ID = %s "
        mycursor.execute(sql, (comment_key, food_key_comment,))
        comment = mycursor.fetchone()
        return render_template('edit_comment.html',comment=comment, error=error)
    except:
        error = 'ERROR OCCURED!'
        mydb.rollback()
        return render_template('edit_comment.html', error=error)

@login_required_owner
def update_food(food_key):
    error = ''
    if request.method == 'POST':        
        if request.form['Food_Name'] == '':
            error = 'Please Write Food Name'
        elif request.form['Price'] == '':
            error = 'Type Price'
        else:
            try:
                query = """ \
                            UPDATE Food \
                            SET Food_Name = %s, \
                            Price = %s \
                            WHERE Food_ID = %s 
                            AND Restaurant_ID = %s\
                        """
                mycursor.execute(query, (request.form['Food_Name'],request.form['Price'],food_key,session['user_id']))
                mydb.commit()
                
                return redirect(url_for('edit_foods_page'))
            except:
                error = 'ERROR OCCURED!'
                mydb.rollback()
                return render_template('update_food.html', error=error)
    try:
        sql = "SELECT * FROM Food WHERE Food_ID = %s AND Restaurant_ID = %s"
        mycursor.execute(sql, (food_key, session['user_id'],))
        food = mycursor.fetchone()
        return render_template('update_food.html',food=food, error=error)
    except:
        error = 'ERROR OCCURED!'
        mydb.rollback()
        return render_template('update_food.html', error=error)

def logout_page():
    session.clear()
    return redirect(url_for('home_page'))

def has_this_food(foodname, restaurant_ID):
    try:
        sql = "SELECT Food_ID FROM Food WHERE Food_Name = %s and Restaurant_ID = %s "
        mycursor.execute(sql, (foodname, restaurant_ID,))
        post = mycursor.fetchone()
        return post
    except:
        return None

def hasUser(username):
    try:
        sql = "SELECT User_ID FROM User WHERE Username = %s"
        mycursor.execute(sql, (username,))
        post = mycursor.fetchone()
        return post
    except:
        return None

def hasRestaurantUser(username):
    try:
        sql = "SELECT Owner_Username FROM Restaurant WHERE Owner_Username = %s"
        mycursor.execute(sql, (username,))
        post = mycursor.fetchone()
        return post
    except:
        return None

def hasVoteRestaurant(Restaurant_ID):
    try:
        sql = "SELECT Vote FROM Votes WHERE Restaurant_ID = %s AND Sender_ID = %s"
        mycursor.execute(sql, (Restaurant_ID,session['user_id'],))
        post = mycursor.fetchone()
        return post
    except:
        return None

def hasVoteFood(Food_ID):
    try:
        sql = "SELECT Vote FROM Votes WHERE Food_ID = %s AND Sender_ID = %s"
        mycursor.execute(sql, (Food_ID,session['user_id'],))
        post = mycursor.fetchone()
        return post
    except:
        return None