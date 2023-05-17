import os
import random
from datetime import datetime, timedelta
import openai
import streamlit as st
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
import gmaps.datasets
import streamlit as st
from geonamescache import GeonamesCache
# Load the list of world cities
load_dotenv()

st.set_page_config(
    page_title="Voyagical",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set theme colors
st.markdown(
    """
    <style>
    .stApp {
        background-color: #266cb1;
        color: #edf5e1;
    }
    .stSidebar .sidebar-content {
        background-color: #05386b;
        color: #05386B;
    }
    .stButton button, .stButton button:focus {
        background-color: #edf5e1;
        color: #266cb1;
    }
    </style>
    """,
    unsafe_allow_html=True
)


gmaps = googlemaps.Client(key='AIzaSyAxr14Xw4OxqlDfH30MxnsKC3Qjo1X5MgQ')
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
    if not (validate_place(BoardingPlace) and validate_place(destination)):
        st.error("Please select a valid boarding or destination place.")
    return f'''

Give a creative trip plan from {BoardingPlace} to {destination} for starting date from {departure_date} to arrival date {arrival_date} with a budget of {budget} along with suggestions of the best places to stay, food and activities. Make sure to look up the most efficient route and the estimated cost of transportation and also include  {additional_information} along with that provide a provison to return to {BoardingPlace}. The answer should be informative and easy to understand. Add titles to each section and make sure to include the most important information.

After generating the trip plan provide the summary of places to visit, Also provide an estimated cost of the entire journey.
'''.strip()

gc = GeonamesCache()
cities = gc.get_cities()

# Extract the city names from the list
city_names = [city['name'] for city in cities.values()]

# Create a dropdown menu with the list of city names

# Define a function to validate that the user selects a city from the list
def validate_place(place):
    if place in city_names:
        return True
    else:
        return False

# Validate the user's selections



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

st.write("<h1 style='text-align: center;'>Voyagical</h1>", unsafe_allow_html=True)

st.write("<h2 style='text-align: center;'>Where planning made easy!</h2>", unsafe_allow_html=True)
with st.form(key='trip_form'):
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader('Location')
        origin = st.selectbox("Select your boarding place:", city_names, index=random.randint(0, len(city_names)-1), key='BoardingPlace')
        origin = st.selectbox("Select your destination:", city_names, index=random.randint(0, len(city_names)-1), key='destination')
        origin = st.slider('Select your budget range:', 100, 10000, (500, 5000), 100, key='budget')
    with c3:
        st.subheader('Arrival')

        st.selectbox('Arrival To',
                     ('Roadways', 'Train Station', 'Bus Station', 'Airport', 'Port'),
                     key='arrival_to')
        st.date_input('Arrival Date', value=now_date + timedelta(days=1), key='arrival_date')
        st.time_input('Arrival Time', value=now_time, key='arrival_time')
    with c2:
        st.subheader('Departure')

        st.selectbox('Departure From',
                     ('Roadways', 'Train Station', 'Bus Station', 'Airport', 'Port'),
                     key='departure_from')
        st.date_input('Departure Date', value=now_date, key='departure_date')
        st.time_input('Departure Time', value=now_time, key='departure_time')
    with st.expander("Additional Information (optional)",expanded=True):
        st.text_area('', height=200, value='I want to visit as many places as possible! (respect time)', key='additional_information')
    if st.form_submit_button('Submit'):
        # Call the `submit` function to process the form data and generate the output
        submit()
        st.subheader('Here is your trip Schedule')
    st.write(st.session_state.output)


gmaps = googlemaps.Client(key='AIzaSyAxr14Xw4OxqlDfH30MxnsKC3Qjo1X5MgQ')

# Get a random destination
# Ask user for travel destination
destination = st.text_input("Enter your specific place to see a 360 degree view of the place", value=random_destination)

# Get the location of the destination
try:
    location = gmaps.geocode(destination)[0]['geometry']['location']
except:
    location = {'lat': random.uniform(-90, 90), 'lng': random.uniform(-180, 180)}

# Load street view
if st.button("Load street view"):
    html = f'<iframe width="100%" height="800px" src="https://www.google.com/maps/embed/v1/streetview?key=AIzaSyAxr14Xw4OxqlDfH30MxnsKC3Qjo1X5MgQ&location={location["lat"]},{location["lng"]}&heading=210&pitch=10" frameborder="0" allowfullscreen></iframe>'
    st.markdown(html, unsafe_allow_html=True)

# Display map and tourist spots
if destination:
    # Get popular tourist spots and landmarks near the destination
    places = gmaps.places_nearby(
        location=(location['lat'], location['lng']), 
        radius=5000, 
        type='tourist_attraction'
    )

    try:
        # Create map with markers for tourist spots
        markers = [(place['name'], place['geometry']['location']['lat'], place['geometry']['location']['lng']) for place in places['results']]
        map_fig = gmaps.figure(center=(location['lat'], location['lng']), zoom_level=12)
        marker_layer = gmaps.marker_layer(markers, info_box_content=[marker[0] for marker in markers])
        map_fig.add_layer(marker_layer)
        st.write(map_fig)
        st.write(" ")
        st.write(" ")
        st.write(" ")
        
    except AttributeError:
        # If map cannot be loaded, display images of tourist spots
        st.header(f"Here are some images of the places nearby {destination}.")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        photos = [(place['name'], place['photos'][0]['photo_reference']) for place in places['results'] if 'photos' in place]

        if photos:
            num_photos = len(photos)
            num_photos_per_col = num_photos // 2  # calculate number of photos to be displayed in each column
            if num_photos % 2 == 1:
                num_photos_per_col += 1  # if there are an odd number of photos, add one more to make it even
            col1, col2 = st.columns(2)
            for i, photo in enumerate(photos):
                if i < num_photos_per_col:
                    col = col1
                else:
                    col = col2
                with col:
                    st.write(f"### {photo[0]}")
                    st.image(f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo[1]}&key=AIzaSyAxr14Xw4OxqlDfH30MxnsKC3Qjo1X5MgQ", use_column_width=True)
        else:
            st.write("No images available.")