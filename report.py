import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_sqlalchemy import SQLAlchemy
from conf_utils import TIME_UPDATE, SENDER_ADDRESS, SENDER_PASSWORD
from main import db, Meal
import datetime
import schedule as schedule


def send_report(message_content, receiver_address):
    message = MIMEMultipart()
    message['From'] = SENDER_ADDRESS
    message['To'] = receiver_address
    message['Subject'] = 'meal_update'

    sender_address = SENDER_ADDRESS
    sender_pass = SENDER_PASSWORD

    message.attach(MIMEText(message_content, 'plain'))
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()


def check_update():
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)

    today = today.strftime("%d/%m/%Y %H:%M:%S")
    yesterday = yesterday.strftime("%d/%m/%Y %H:%M:%S")

    query = Meal.query.filter(Meal.creation_date <= today).filter(Meal.creation_date >= yesterday). \
        filter(Meal.update_date <= today).filter(Meal.update_date >= yesterday)

    list_of_meals = query.all()
    response = []
    for meal in list_of_meals:
        info = {"menu_id": meal.id, "name": meal.name, "description": meal.description, "price": meal.price,
                "time": meal.time, "vege": meal.vege, "creation_date": meal.creation_date,
                "update_date": meal.update_date}
        response.append(info)

    stmt = "SELECT email FROM users"

    emails = db.session.execute(stmt).fetchall()
    for email in emails:
        send_report(json.dumps(response, sort_keys=True, indent=4), email[0])


schedule.every().day.at(TIME_UPDATE).do(check_update())

while True:
    schedule.run_pending()
