from flask import Flask, session
import views
from flask_login import LoginManager
import mysql.connector
import dbinit


def create_app():

    app = Flask(__name__)

    app.config.from_object("settings")

    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/restaurants", view_func=views.restaurants_page, methods=["GET", "POST"])
    app.add_url_rule("/restaurants/<int:restaurant_key>", view_func=views.restaurant_detail_page, methods=["GET", "POST"])
    app.add_url_rule("/restaurants/<int:restaurant_key>/<int:food_key>", view_func=views.food_detail_page, methods=["GET", "POST"])
    app.add_url_rule("/search", view_func=views.search_page)
    app.add_url_rule("/about", view_func=views.about_page, methods=["GET", "POST"])
    app.add_url_rule(
        "/login", view_func=views.login_page, methods=["GET", "POST"]
    )
    app.add_url_rule(
        "/register", view_func=views.register_page, methods=["GET", "POST"]
    )
    app.add_url_rule(
        "/new_restaurant", view_func=views.new_restaurant_page, methods=["GET", "POST"]
    )
    app.add_url_rule(
        "/delete_restaurant", view_func=views.delete_restaurant_page, methods=["GET", "POST"]
    )

    app.add_url_rule(
        "/add_food", view_func=views.add_food_page, methods=["GET", "POST"]
    )

    app.add_url_rule(
        "/edit_foods", view_func=views.edit_foods_page, methods=["GET", "POST"]
    )

    app.add_url_rule(
        "/edit_foods/<int:food_key>", view_func=views.update_food, methods=["GET", "POST"]
    )

    app.add_url_rule(
        "/edit_password", view_func=views.edit_password, methods=["GET", "POST"]
    )

    app.add_url_rule(
        "/update_profile", view_func=views.update_profile, methods=["GET", "POST"]
    )

    app.add_url_rule(
        "/delete_users", view_func=views.delete_users, methods=["GET", "POST"]
    )

    app.add_url_rule(
        "/edit_restaurant_comment/<int:restaurant_key_comment>/<int:comment_key>", view_func=views.edit_restaurant_comment, methods=["GET", "POST"]
    )

    app.add_url_rule(
        "/edit_food_comment/<int:restaurant_key_comment>/<int:food_key_comment>/<int:comment_key>", view_func=views.edit_food_comment, methods=["GET", "POST"]
    )

    app.add_url_rule(
        "/my_restaurant_details", view_func=views.restaurant_detail_owner, methods=["GET", "POST"]
    )

    app.add_url_rule(
        "/update_restaurant", view_func=views.update_restaurant_info, methods=["GET", "POST"]
    )


    app.add_url_rule("/logout", view_func=views.logout_page)


    
    app.config['db'] = dbinit.initialize()
    return app

app = create_app()

if __name__ == "__main__":
    app.run()