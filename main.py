from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime
import sys

from conf_utils import DATABASE_URI, IP, PORT
from logger import create_exception_log_message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db = SQLAlchemy(app)

auth = HTTPBasicAuth()

MealMenu = db.Table('meal_menu',
                    db.Column('id', db.Integer, primary_key=True),
                    db.Column('meal_id', db.Integer, db.ForeignKey('meal.id')),
                    db.Column('menu_id', db.Integer, db.ForeignKey('menu.id')))


class Menu(db.Model):
    __tablename__ = "menu"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    update_date = db.Column(db.DateTime, nullable=False, default=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    meals = db.relationship('Meal', secondary=MealMenu, lazy='subquery', backref=db.backref('menu', lazy=True))

    def __repr__(self):
        return f"Menu('{self.id}', '{self.name}', '{self.description}', '{self.creation_date}', '{self.update_date}', '{self.meals}') "


class Meal(db.Model):
    __tablename__ = "meal"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    update_date = db.Column(db.DateTime, nullable=False, default=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    time = db.Column(db.Integer, nullable=False)
    vege = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"Meal('{self.id}', '{self.name}', '{self.description}','{self.price}', '{self.creation_date}', '{self.update_date}', '{self.time}', '{self.vege}')"


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"User('{self.id}', '{self.email}', '{self.password}')"


@auth.verify_password
def verify_password(email, password):
    user = Users.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        return email


@app.route('/signup', methods=['POST'])
def signup():
    if request.is_json:
        try:
            req = request.get_json()
            email = req['email']
            password = req['password']
            new_user = Users(email=email, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()

        except Exception as ex:
            db.session.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            message = create_exception_log_message(exc_type, exc_tb, ex)
            return message, 500

        return jsonify({"user_id": new_user.id}), 201

    return jsonify({"error": "invalid input"}), 400


@app.route('/menu', methods=['POST'])
@auth.login_required
def add_new_menu():
    if request.is_json:
        try:
            req = request.get_json()
            name = req["name"]
            desc = req["description"]

            menu = Menu(name=name, description=desc)
            db.session.add(menu)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            message = create_exception_log_message(exc_type, exc_tb, ex)
            return message, 500

        return jsonify({"menu_id": menu.id}), 201
    else:
        return jsonify({"error": "invalid input"}), 400


@app.route('/menu/<int:menu_id>/meals', methods=['POST'])
@auth.login_required
def add_new_meal(menu_id):
    if request.is_json:
        try:
            req = request.get_json()
            name = req["name"]
            desc = req["description"]
            price = req["price"]
            time = req["time"]
            vege = req["vege"]

            meal = Meal(name=name, description=desc, price=price, time=time, vege=vege)

            db.session.add(meal)
            db.session.commit()

            statement = MealMenu.insert().values(meal_id=meal.id, menu_id=menu_id)
            db.session.execute(statement)
            db.session.commit()

        except Exception as ex:
            db.session.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            message = create_exception_log_message(exc_type, exc_tb, ex)
            return message, 500

        return jsonify({"meal_id": meal.id}), 201
    else:
        return jsonify({"error": "invalid input"}), 400


@app.route('/menu/<int:menu_id>', methods=['GET'])
def list_all_meals(menu_id):
    try:
        menu = Menu.query.filter_by(id=menu_id).first()
        menu_details = {"menu_id": menu.id, "name": menu.name, "description": menu.description,
                        "creation_date": menu.creation_date,
                        "update_date": menu.update_date,
                        "number_of_meals": len(menu.meals)}

        meals = []
        for meal in menu.meals:
            meal_detail = {"meal_id": meal.id, "name": meal.name, "description": meal.description, "price": meal.price,
                           "time": meal.time, "vege": meal.vege, "creation_date": meal.creation_date,
                           "update_date": meal.update_date}
            meals.append(meal_detail)

        menu_details.update({"meals": meals})

        return jsonify([menu_details]), 200

    except Exception as ex:
        db.session.rollback()
        exc_type, exc_obj, exc_tb = sys.exc_info()
        message = create_exception_log_message(exc_type, exc_tb, ex)
        return message, 500


@app.route('/meal/<int:meal_id>', methods=['PUT'])
@auth.login_required
def update_meal(meal_id):
    if request.is_json:
        try:
            req = request.get_json()
            name = req["name"]
            desc = req["description"]
            price = req["price"]
            time = req["time"]
            vege = req["vege"]

            old_meal = Meal.query.get(meal_id)
            old_meal.name = name
            old_meal.description = desc
            old_meal.price = price
            old_meal.time = time
            old_meal.vege = vege
            old_meal.update_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            db.session.commit()

            return jsonify({"meal_id": old_meal.id}), 201

        except Exception as ex:
            db.session.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            message = create_exception_log_message(exc_type, exc_tb, ex)
            return message, 500

    return jsonify({"error": "invalid input"}), 400


@app.route('/menu/', methods=['GET'])
def list_menu():
    try:
        name = request.args.get('name')
        created_before = request.args.get('createdBefore')
        created_after = request.args.get('createdAfter')
        updated_before = request.args.get('updatedBefore')
        updated_after = request.args.get('updatedAfter')
        by_name = request.args.get('byName')
        by_meal_count = request.args.get('byMealCount')

        query = Menu.query.filter(Menu.meals.any())
        if name is not None:
            query = query.filter(Menu.name.like('%{}%'.format(name)))

        if created_before is not None:
            query = query.filter(Menu.creation_date <= created_before)

        if created_after is not None:
            query = query.filter(Menu.creation_date >= created_after)

        if updated_before is not None:
            query = query.filter(Menu.update_date <= updated_before)

        if updated_after is not None:
            query = query.filter(Menu.update_date >= updated_after)

        if by_name == 'asc':
            query = query.order_by(Menu.name)
        elif by_name == 'desc':
            query = query.order_by(Menu.name.desc())

        list_of_menu = query.all()

        if by_meal_count == 'asc':
            list_of_menu = sorted(list_of_menu, key=lambda menu: len(menu.meals), reverse=False)
        if by_meal_count == 'desc':
            list_of_menu = sorted(list_of_menu, key=lambda menu: len(menu.meals), reverse=True)

        response = []
        for menu in list_of_menu:
            a = {"menu_id": menu.id, "name": menu.name, "description": menu.description,
                 "creation_date": menu.creation_date,
                 "update_date": menu.update_date,
                 "number_of_meals": len(menu.meals)}
            response.append(a)
        return jsonify(response), 200

    except Exception as ex:
        db.session.rollback()
        exc_type, exc_obj, exc_tb = sys.exc_info()
        message = create_exception_log_message(exc_type, exc_tb, ex)
        return message, 500


if __name__ == '__main__':
    if database_exists(DATABASE_URI):
        app.run(host=IP, port=PORT)
    else:
        print("DATABASE doesn't exist")
        create_database(DATABASE_URI)

        db.create_all()

        menu1 = Menu(name="kolczyki", description="złote")
        db.session.add(menu1)
        menu2 = Menu(name="lampa", description='ledowa')
        db.session.add(menu2)
        menu3 = Menu(name="myszka", description='logi')
        db.session.add(menu3)
        menu4 = Menu(name="danio", description='waniliowe')
        db.session.add(menu4)
        menu5 = Menu(name="szklanka", description='z ikei')
        db.session.add(menu5)
        menu6 = Menu(name="kaczka", description='motocyklowa')
        db.session.add(menu6)

        meal1 = Meal(name="nalesniki", description="z nutellą", price=12.5, time=34, vege=True)
        db.session.add(meal1)
        meal2 = Meal(name="pierogi", description="ruskie", price=55.43, time=90, vege=True)
        db.session.add(meal2)
        meal3 = Meal(name="tosty", description="z serem", price=23.44, time=89, vege=True)
        db.session.add(meal3)
        meal4 = Meal(name="schabowe", description="z kurczaka", price=23.90, time=5, vege=False)
        db.session.add(meal4)
        meal5 = Meal(name="zupa", description="pomidorowa", price=3.40, time=2, vege=True)
        db.session.add(meal5)
        meal6 = Meal(name="ryba", description="dorsz", price=15.78, time=10, vege=True)
        db.session.add(meal6)

        db.session.commit()

        statement = MealMenu.insert().values(meal_id=1, menu_id=1)
        db.session.execute(statement)
        statement = MealMenu.insert().values(meal_id=2, menu_id=1)
        db.session.execute(statement)
        statement = MealMenu.insert().values(meal_id=3, menu_id=2)
        db.session.execute(statement)
        statement = MealMenu.insert().values(meal_id=4, menu_id=2)
        db.session.execute(statement)
        statement = MealMenu.insert().values(meal_id=5, menu_id=2)
        db.session.execute(statement)
        statement = MealMenu.insert().values(meal_id=6, menu_id=4)
        db.session.execute(statement)

        db.session.commit()

        app.run(host=IP, port=PORT)
