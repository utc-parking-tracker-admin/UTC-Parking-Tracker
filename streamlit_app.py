import streamlit as st
import firebase_admin
from firebase_admin import firestore
import folium
from streamlit_folium import st_folium

def main():

    # check for presence of default app
    if not firebase_admin._apps:
        # connection to Firestore
        db = db_connection()

    st.title("UTC Parking Tracker")

    # Display total number of spots available
    st.write(
        "# Available spots:"
    )

    # Display a grid of spaces (?)

    # location of lot
    m = folium.Map(location=[35.046235, -85.2967971], zoom_start=16)
    folium.Marker(
        [39.949610, -75.150282], popup="Lot 12", tooltip="Lot 12"
    ).add_to(m)

    # render map
    st_data = st_folium(m, width=725)

    # return time stamp
    time = db_query(db, "Lot 12", "Totals")["time"]
    st.write("Data last updated: " + time)

    st.write("Created by Ashley Carrera, Sophia Duke, Samuel Hunt, and Nathan Parnaby")

def db_connection():
    # initialize app with Application Default credentials from private key
    app = firebase_admin.initialize_app()
    # database from which to pull parking data
    db = firestore.client()
    return db

# added cache tag to keep from always reading during dev
# will eventually change to read every x seconds
@st.cache_data
def db_query(db:firestore, collection:str, document:str):
    # reference to collection and document
    c = db.collection(collection)
    doc = c.document(document)

    # return the data as a dict
    data = doc.get().to_dict()
    return data

main()
