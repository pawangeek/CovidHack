import requests, json, populartimes
import numpy as np
import pandas as pd
from form import DetailForm
from datetime import datetime, timedelta
from flask import Flask, redirect, url_for, request, render_template

# Create Flask App
app = Flask(__name__)

# Get Google Places API: https://developers.google.com/places/web-service/get-api-key and replace
MyAPI_key = "AIzaSyDs1sK7EGAGGvPvRiWX_X4yYDUjTQb5MyI"

# URL for request to google place text search to find user address based on what is typed in
url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

# constant factor used later to calculate the area (longitude, latitude) to scan for stores
alpha = 180/(np.pi*6371000)


def get_coords(ip_address):
    try:
        response = requests.get("http://ip-api.com/json/{}".format(ip_address))
        js = response.json()
        latitute = js['lat']
        longitude = js['lon']
        l=[latitute,longitude]

        return l

    except Exception as e:
        return "Unknown"

@app.route('/')
def home():
	return render_template('homes.html')

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/stop')
def stop():
    return render_template('stop.html')

# Run Store Search and Selection
@app.route('/details',methods = ['GET', 'POST'])
def detail():
    form = DetailForm(request.form)
    if request.method == 'POST' and form.validate():
        # Import User Input
        user_address = form.user_address.data
        store_type = form.store_type.data
        radius = form.radius.data 

        radius = int(radius)
        
        # Find the google place from the user_address input
        user_address_res = requests.get(url + 'query=' + user_address +    '&key=' + MyAPI_key)
        x = user_address_res.json()

        user_location = x["results"][0]["geometry"]["location"]

        user_latitude = user_location["lat"]
        user_longitude = user_location["lng"]
        
        # Define search area around the user location
        delta = radius*alpha

        p1 = (user_latitude-delta, user_longitude-delta)
        p2 = (user_latitude+delta, user_longitude+delta)
        
        # Depending on the place type - find places with populartimes data within the given radius around the user's location
        if store_type == 'supermarket':
            results = populartimes.get(MyAPI_key,["grocery_or_supermarket"],p1,p2,radius = radius, all_places=False,n_threads = 1)
        
        if store_type == 'pharmacy':
            results = populartimes.get(MyAPI_key,["pharmacy"],p1,p2,radius = radius, all_places=False,n_threads = 10)

        # Find out the current time at the user's location (can only be found by a place details request)
        user_location_id = x["results"][0]["reference"]

        url_details = "https://maps.googleapis.com/maps/api/place/details/json?"
        user_location_details_res = requests.get(url_details+"key="+MyAPI_key+"&place_id="+ user_location_id)
        y = user_location_details_res.json()

        utc_offset=y["result"]["utc_offset"]
        time_now = datetime.utcnow()+timedelta(hours=utc_offset/60)
        
        # Create a list of stores with their activity data (current if available, otherwise average at current time)
        # Closed stores (activity=0) are omitted
        store_list = []

        for item in results:
            if "current_popularity" in item:
                store_list.append([item["current_popularity"],item["name"],item["id"]])
            else:
                temp = item["populartimes"][time_now.weekday()]["data"][time_now.hour]
                if temp!=0:
                    store_list.append([temp,item["name"],item["id"]])
        
        # If no Stores are found give out an error
        if len(store_list) == 0:
            #return 'there has been an error: No data available for this choice'
            return redirect(url_for('error'))
        
        # Select the store with the least activity and get its ID and name
        df=pd.DataFrame(store_list)
        min_activity_index = df[0].idxmin()
        store_place_id=df.iloc[df[0].idxmin(),2]
        store_name = df.iloc[df[0].idxmin(),1]
        
        # Create google maps link based of store_place_id
        store_gmap_url = "https://www.google.com/maps/place/?q=place_id:" + store_place_id

        return render_template('stop.html', value=store_name)

    else:
        return render_template('details.html', form=form) 

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug = True)