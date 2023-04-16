import os
import random
from datetime import datetime, timedelta
import pydeck as pdk
from PIL import Image
import ipywidgets.embed
from ipywidgets import HBox
import openai
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import googlemaps
import googlemaps.exceptions
import googlemaps.convert
import googlemaps.directions
import googlemaps.distance_matrix
import googlemaps.elevation
import googlemaps.geocoding
import googlemaps.geolocation
import googlemaps.places
import googlemaps.roads
from googlemaps.exceptions import HTTPError
import gmaps.datasets
from io import BytesIO

load_dotenv()

st.set_page_config(
    page_title="My App",
    layout="wide",
    initial_sidebar_state="expanded"
)
gmaps = googlemaps.Client(key='AIzaSyAO1AHlJnhOpIPrmJ2tNoh7NZn9ObLTgYI')
openai.api_key = os.getenv('OPENAI_API_KEY')
example_destinations = [''
]
random_destination = random.choice(example_destinations)

now_date = datetime.now()
budget=int()
# round to nearest 15 minutes
now_date = now_date.replace(minute=now_date.minute // 15 * 15, second=0, microsecond=0)

# split into date and time objects
now_time = now_date.time()
now_date = now_date.date() + timedelta(days=1)


def generate_prompt(BoardingPlace,destination, arrival_to, arrival_date, arrival_time, departure_from,
                    departure_date, departure_time, additional_information,budget, **kwargs):
    if not destination or not arrival_to or not departure_from or not arrival_date or not arrival_time or not departure_date or not departure_time:
        raise ValueError("Arrival destination cannot be empty or None.")
    if not departure_from:
        raise ValueError("Departure location cannot be empty or None.")
    return f'''

Plan a trip from {BoardingPlace} to {destination} for starting date from {departure_date} to arrival date {arrival_date} with a budget of {budget} along with suggestions of the best places to stay, food and activities. Make sure to look up the most efficient route and the estimated cost of transportation and also include  {additional_information} while planning the trip.
(Followups)[Creative suggestions] and print each days work in a seperate line.
'''.strip()



def submit():
    prompt = generate_prompt(**st.session_state)

    # generate output
    output = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        temperature=0.45,
        top_p=1,
        frequency_penalty=2,
        presence_penalty=0,
        max_tokens=1024
    )
    st.session_state['output'] = output['choices'][0]['text']
# Initialization
if 'output' not in st.session_state:
    st.session_state['output'] = ''

st.write("<h1 style='text-align: center;'>AI Trip Planner</h1>", unsafe_allow_html=True)

st.write("<h3 style='text-align: center;'>Where planning made easy!</h2>", unsafe_allow_html=True)
st.subheader('Let’s plan a magical trip! Please provide your budget, starting and destination place, and number of days and let Voyagical do the rest.')

with st.form(key='trip_form'):
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader('Location')
        origin = st.text_input('Destination', value=random_destination, key='destination')
        origin = st.text_input('Boarding Place', value=random_destination, key='BoardingPlace')
        origin = st.text_input('Budget', value=budget, key='budget')

    with c2:
        st.subheader('Arrival')

        st.selectbox('Arrival To',
                     ('Airport', 'Train Station', 'Bus Station', 'Ferry Terminal', 'Port', 'Roadways'),
                     key='arrival_to')
        st.date_input('Arrival Date', value=now_date, key='arrival_date')
        st.time_input('Arrival Time', value=now_time, key='arrival_time')
    with c3:
        st.subheader('Departure')

        st.selectbox('Departure From',
                     ('Airport', 'Train Station', 'Bus Station', 'Ferry Terminal', 'Port', 'Roadways'),
                     key='departure_from')
        st.date_input('Departure Date', value=now_date + timedelta(days=1), key='departure_date')
        st.time_input('Departure Time', value=now_time, key='departure_time')
    with st.expander("Additional Information (optional)",expanded=True):
        st.text_area('', height=200, value='I want to visit as many places as possible! (respect time)', key='additional_information')
        st.write(st.session_state.output)

    if st.form_submit_button('Submit'):
        # Call the `submit` function to process the form data and generate the output
        submit()
        c1.empty()
        c2.empty()
        c3.empty()
        st.empty()

        # Show the Trip Schedule and output elements
        st.subheader('Here is your trip Schedule')
        st.write(st.session_state.output)
        st.subheader('Have a wonderful Journey!')


destination = st.text_input("Enter your preferred travel destination:",value=random_destination)
try:
    location = gmaps.geocode(destination)[0]['geometry']['location']
except:
    location = {'lat': random.uniform(-90, 90), 'lng': random.uniform(-180, 180)}

# Set up Google Maps API key
st.text("Click the button to load the street view")
if st.button("Load street view"):
    html = f'<iframe width="100%" height="800px" src="https://www.google.com/maps/embed/v1/streetview?key=AIzaSyAO1AHlJnhOpIPrmJ2tNoh7NZn9ObLTgYI&location={location["lat"]},{location["lng"]}&heading=210&pitch=10" frameborder="0" allowfullscreen></iframe>'
    st.markdown(html, unsafe_allow_html=True)

# Create map component to display popular tourist spots and landmarks near the destination
# Create map component to display popular tourist spots and landmarks near the destination
# Create map component to display popular tourist spots and landmarks near the destination

# set up API key and create client object
# define Google Maps client
# get the location coordinates of the destination
if destination:
    gmaps.configure(api_key='AIzaSyAO1AHlJnhOpIPrmJ2tNoh7NZn9ObLTgYI')
    location = gmaps.geocode(destination)[0]['geometry']['location']

    # create map component to display popular tourist spots and landmarks near the destination
    places = gmaps.places_nearby(
        location=(location['lat'], location['lng']), 
        radius=5000, 
        type='tourist_attraction'
    )
    markers = [(place['name'], place['geometry']['location']['lat'], place['geometry']['location']['lng']) for place in places['results']]
    map_fig = gmaps.figure(center=(location['lat'], location['lng']), zoom_level=12)
    marker_layer = gmaps.marker_layer(markers, info_box_content=[marker[0] for marker in markers])
    map_fig.add_layer(marker_layer)
    st.write(map_fig)