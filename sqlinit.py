from flask import Flask, render_template, request, session, logging, url_for, redirect, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

engine = create_engine("mysql+pymysql://root:pawan@localhost/covid")
db = scoped_session(sessionmaker(bind=engine))

import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="pawan",  # you workbench local host password
    auth_plugin='mysql_native_password',
    database='covid'
)

mycursor = mydb.cursor()

mycursor.execute("SHOW TABLES")

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

if __name__ == "__main__":
    app.secret_key = "key"
    app.run(debug=True)