import requests, json, populartimes
import numpy as np
import pandas as pd
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from form import DetailForm, UserForm, UserLogin
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime, timedelta
from flask import Flask, redirect, url_for, request, render_template, session, flash
from flask_mail import Mail, Message
from flask_login import LoginManager, login_required
from flask_googlemaps import GoogleMaps, Map

# Create Flask App
app = Flask(__name__)
app.secret_key = "xb1\x058\xb8o\x82\xaf\xdb\xd5I"
app.config.from_pyfile('config.cfg')

# Get Google Places API: https://developers.google.com/places/web-service/get-api-key and replace
MyAPI_key = "AIzaSyDs1sK7EGAGGvPvRiWX_X4yYDUjTQb5MyI"

GoogleMaps(app,key=MyAPI_key)
mail = Mail(app)

key = 'xb1\x058\xb8o\x82\xaf\xdb\xd5I'
engine = create_engine("mysql+pymysql://root:pawan@localhost/covid")
db = scoped_session(sessionmaker(bind=engine))
s = URLSafeTimedSerializer(key)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "userlogin"

# URL for request to google place text search to find user address based on what is typed in
url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

# constant factor used later to calculate the area (longitude, latitude) to scan for stores
alpha = 180/(np.pi*6371000)


def get_coords(ip_address):
    try:
        response = requests.get("http://ip-api.com/json/{}".format(ip_address))
        js = response.json()
        latitude = js['lat']
        longitude = js['lon']
        place = [latitude, longitude]

        return place

    except Exception as e:
        return "Unknown"


@app.route('/')
def home():
    return render_template('homes.html')


@app.route("/userregister", methods=["GET", "POST"])
def register():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        fname = form.fname.data
        lname = form.lname.data
        email = form.email.data
        password = form.password.data
        confirm = form.confirm_password.data

        emaildata = db.execute("SELECT email FROM users WHERE email=:email", {"email": email}).fetchone()

        if emaildata is not None:
            flash("Email taken", "danger")
            return render_template("userregister.html", form=form)

        if password == confirm:
            db.execute("INSERT INTO users (first_name, last_name, email, pass) VALUES (:fname, :lname, :email, :password)", {
                       "fname": fname, "lname": lname, "email": email, "password": password})
            db.commit()

            email = request.form['email']
            token = s.dumps(email, salt='email-confirm')

            msg = Message('Confirm Email', sender='anhappysingh@gmail.com', recipients=[email])
            link = url_for('confirm_email', token=token, _external=True)

            msg.body = link
            mail.send(msg)
            flash("A confirmation email has been sent. Please confirm your email.", "success")
            return render_template("userregister.html", form=form)

        else:
            flash("Passwords do not match", "danger")
            return render_template("userregister.html",form=form)

    return render_template("userregister.html",form=form)


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=36000)
        flash("You are registered. Please login", "success")
        return redirect(url_for('userlogin'))
    except SignatureExpired:
        flash("The link has expired. Please login", "danger")
        return render_template("userregister.html")


@app.route("/userlogin", methods=["GET", "POST"])
def userlogin():
    form = UserLogin(request.form)
    if request.method == 'POST' and form.validate():

        email = request.form.get("email")
        password = request.form.get("password")

        emaildata = db.execute("SELECT email FROM users WHERE email=:email", {
            "email": email}).fetchone()
        passwordData = db.execute("SELECT pass FROM users WHERE email=:email", {
                                  "email": email}).fetchone()
        userTypeData = db.execute("SELECT userType FROM users WHERE email=:email AND userType=1", {
                                  "email": email}).fetchone()

        if emaildata is None:
            flash("Email not found. Please try again.", "danger")
            return render_template("userlogin.html", form=form)
        else:
            for password_data in passwordData:
                if password==password_data:
                    session["log"] = True
                    # login as admin if userTypeData returns a value which it only does if usertype equals 1
                    if userTypeData is not None:
                        flash("You are logged in as an admin.")
                        return redirect(url_for('admin'))
                    flash("You are logged in.")
                    session["USER"] = email
                    return redirect(url_for('userhome'))
                else:
                    flash("Incorrect password", "danger")
                    return render_template("userlogin.html",form=form)
    return render_template("userlogin.html",form=form)


@app.route("/forgetpassword", methods=["GET", "POST"])
def forget_password():
    if request.form.get("email"):
        email = request.form['email']

        emaildata = db.execute("SELECT email FROM users WHERE email=:email", {
            "email": email}).fetchone()

        if emaildata is None:
            flash("Email not found. Please try again.", "danger")
            return render_template("forgetpassword.html")
        else:
            new_password = (str('new_password'))
            db.execute("UPDATE users SET pass=:password WHERE email=:email", {
                       "password": new_password, "email": email})
            db.commit()
            msg = Message('Forget Password',
                          sender='anhappysingh@gmail.com', recipients=[email])
            msg.body = 'Your new password is: new_password'

            mail.send(msg)
            flash("Your password was sent to your email.", "success")
            return redirect(url_for('userlogin'))
    return render_template("forgetpassword.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You are logged out", "success")
    return redirect(url_for('userlogin'))

@app.errorhandler(401)
def page_not_found(e):
    return render_template('error.html')

@app.route('/error')
def error():
    return render_template('error.html')


@app.route('/stop')
def stop():
    return render_template('stop.html')


@app.route("/admin")
def admin():
    return render_template("adminlogin.html")


@app.route("/userhome", methods=['GET','POST'])
def userhome():
    if request.form.get("packet"):
        packets = request.form['packet']

        if packets<1:
            flash("Invalid Quantity", "danger")
        if packets>6:
            flash("Maximum 6 from one user", "danger")

    # ipaddr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    # loc = get_coords(ipaddr)

    ipaddr = '157.37.154.227'
    loc = get_coords(ipaddr)

    mymap = Map(
        identifier="view-side",
        lat=loc[0],
        lng=loc[1],
        markers=[{
             'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
             'lat': loc[0],
             'lng': loc[1],
             'infobox': "<b>Your current location</b>"
          }
        ])

    return render_template("userhome.html", mymap= mymap)


# Run Store Search and Selection
@app.route('/details', methods=['GET', 'POST'])
def detail():
    form = DetailForm(request.form)
    if request.method == 'POST' and form.validate():
        # Import User Input
        user_address = form.user_address.data
        store_type = form.store_type.data
        radius = form.radius.data 

        radius = int(radius)
        
        # Find the google place from the user_address input
        user_address_res = requests.get(url + 'query=' + user_address + '&key=' + MyAPI_key)
        x = user_address_res.json()

        user_location = x["results"][0]["geometry"]["location"]

        user_latitude = user_location["lat"]
        user_longitude = user_location["lng"]
        
        # Define search area around the user location
        delta = radius*alpha

        p1 = (user_latitude-delta, user_longitude-delta)
        p2 = (user_latitude+delta, user_longitude+delta)

        if store_type == 'supermarket':
            results = populartimes.get(MyAPI_key, ["grocery_or_supermarket"], p1, p2, radius=radius, all_places=False, n_threads=1)
        
        if store_type == 'pharmacy':
            results = populartimes.get(MyAPI_key, ["pharmacy"], p1, p2, radius=radius, all_places=False, n_threads=10)

        # Find out the current time at the user's location (can only be found by a place details request)
        user_location_id = x["results"][0]["reference"]

        url_details = "https://maps.googleapis.com/maps/api/place/details/json?"
        user_location_details_res = requests.get(url_details+"key="+MyAPI_key+"&place_id=" + user_location_id)
        y = user_location_details_res.json()

        utc_offset = y["result"]["utc_offset"]
        time_now = datetime.utcnow()+timedelta(hours=utc_offset/60)
        
        # Create a list of stores with their activity data (current if available, otherwise average at current time)
        # Closed stores (activity=0) are omitted
        store_list = []

        for item in results:
            if "current_popularity" in item:
                store_list.append([item["current_popularity"], item["name"], item["id"]])
            else:
                temp = item["populartimes"][time_now.weekday()]["data"][time_now.hour]
                if temp != 0:
                    store_list.append([temp, item["name"], item["id"]])
        
        # If no Stores are found give out an error
        if len(store_list) == 0:
            # return 'there has been an error: No data available for this choice'
            return redirect(url_for('error'))
        
        # Select the store with the least activity and get its ID and name
        df = pd.DataFrame(store_list)
        store_place_id = df.iloc[df[0].idxmin(), 2]
        store_name = df.iloc[df[0].idxmin(), 1]
        
        # Create google maps link based of store_place_id
        store_gmap_url = "https://www.google.com/maps/place/?q=place_id:" + store_place_id

        return render_template('stop.html', value=store_name, key=store_gmap_url)

    else:
        return render_template('details.html', form=form)


@login_manager.user_loader
def load_user(userid):
    return db.query.get(userid)


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
