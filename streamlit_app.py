import streamlit as st
import firebase_admin
from firebase_admin import firestore
import folium
from streamlit_folium import st_folium
import json

def main():

    # connection to Firestore
    db = db_connection()

    st.title("UTC Parking Tracker")

    # Display total number of spots available
    st.write(
        "# Available spots:"
    )

    # Display a grid of spaces (?)

    # location of lot
    address_link = "<a href='https://maps.app.goo.gl/EgeZWvWBKXv84muh6' target='blank'>Get Directions</a>"
    m = folium.Map(location=[35.046235, -85.2967971], zoom_start=18)
    folium.Marker(
        [35.046235, -85.2967971], popup=address_link, tooltip="Lot 12"
    ).add_to(m)

    # render map
    st_data = st_folium(m, width=725)

    # return time stamp
    time = db_query(db, "Lot 12", "Totals")["time"]
    time = time.strftime("%Y-%m-%d %H:%M:%S")
    st.write("Data last updated: " + time)

    st.write("Created by Ashley Carrera, Sophia Duke, Samuel Hunt, and Nathan Parnaby")

def db_connection():
    # get private key from streamlit secrets
    cred = firebase_admin.credentials.Certificate(dict(st.secrets["gcp_service_account"]))
    # check for presence of default app
    if not firebase_admin._apps:
        # initialize app with credentials
        firebase_admin.initialize_app(cred)
    # database from which to pull parking data
    db = firestore.client()
    return db

# added cache tag to keep from always reading during dev
# will eventually change to read every x seconds
@st.cache_data
def db_query(_db:firestore, collection:str, document:str):
    # reference to collection and document
    c = _db.collection(collection)
    doc = c.document(document)

    # return the data as a dict
    data = doc.get().to_dict()
    return data

main()
