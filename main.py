import os
import random
from datetime import datetime, timedelta
import requests
import pydeck as pdk
import openai
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="My App",
    layout="wide",
    initial_sidebar_state="expanded"
)

openai.api_key = os.getenv('OPENAI_API_KEY')

example_destinations = [
    'Izmir', 'Istanbul', 'Ankara', 'Paris', 'London', 'New York', 'Tokyo', 'Sydney', 'Hong Kong',
    'Singapore', 'Warsaw', 'Mexico City', 'Palermo'
]
random_destination = random.choice(example_destinations)

now_date = datetime.now()

# round to nearest 15 minutes
now_date = now_date.replace(minute=now_date.minute // 15 * 15, second=0, microsecond=0)

# split into date and time objects
now_time = now_date.time()
now_date = now_date.date() + timedelta(days=1)


def generate_prompt(destination, arrival_to, arrival_date, arrival_time, departure_from,
                    departure_date, departure_time, additional_information, **kwargs):
    return f'''
Prepare trip schedule for {destination}, based on the following information:

* Arrival To: {arrival_to}
* Arrival Date: {arrival_date}
* Arrival Time: {arrival_time}

* Departure From: {departure_from}
* Departure Date: {departure_date}
* Departure Time: {departure_time}

* Additional Notes: {additional_information}
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
    st.session_state['output'] = '--'

st.title('AI Trip Planner')
st.subheader('Where planning made easy!')

with st.form(key='trip_form'):
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader('Location')
        origin = st.text_input('Destination', value=random_destination, key='destination')
        origin = st.text_input('Boarding Place', value=random_destination, key='Boarding Place')
        st.form_submit_button('Submit', on_click=submit)

    with c2:
        st.subheader('Arrival')

        st.selectbox('Arrival To',
                     ('Airport', 'Train Station', 'Bus Station', 'Ferry Terminal', 'Port', 'Other'),
                     key='arrival_to')
        st.date_input('Arrival Date', value=now_date, key='arrival_date')
        st.time_input('Arrival Time', value=now_time, key='arrival_time')

    with c3:
        st.subheader('Departure')

        st.selectbox('Departure From',
                     ('Airport', 'Train Station', 'Bus Station', 'Ferry Terminal', 'Port', 'Other'),
                     key='departure_from')
        st.date_input('Departure Date', value=now_date + timedelta(days=1), key='departure_date')
        st.time_input('Departure Time', value=now_time, key='departure_time')
    with st.expander("Additional Information"):
        st.text_area('', height=200, value='I want to visit as many places as possible! (respect time)', key='additional_information')

    st.subheader('Trip Schedule')
    st.write(st.session_state.output)

# Set up the initial parameters
# Render the Pydeck map in Streamlit
api_url = "https://maps.googleapis.com/maps/api/streetview"

def generate_street_view(lat, lon, size):
    params = {
        "size": f"{size}x{size}",
        "location": f"{lat},{lon}",
        "key": "AIzaSyAO1AHlJnhOpIPrmJ2tNoh7NZn9ObLTgYI"
    }
    response = requests.get(api_url, params=params)
    return response.content

def add_street_view(location, size=640):
    lat, lon = get_coordinates(location)
    view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=14, bearing=0, pitch=0)
    layer = pdk.Layer(
        "CustomLayer",
        data=None,
        get_position=lambda d: [lon, lat],
        get_image=lambda d: generate_street_view(lat, lon, size),
        get_size=lambda d: [size, size],
    )
    deck = pdk.Deck(map_style="mapbox://styles/mapbox/light-v9", initial_view_state=view_state, layers=[layer])
    st.pydeck_chart(deck)
def get_coordinates(location):
    # Use geocoding API to get the latitude and longitude of the location
    # return the latitude and longitude
    return 40.757, -73.985

# example usage
location = st.text_input('Destination', value='New York, NY')
add_street_view(location)
