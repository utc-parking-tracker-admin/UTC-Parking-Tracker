# imports
import streamlit as st
import firebase_admin
from firebase_admin import firestore
import folium
from streamlit_folium import st_folium
from datetime import timezone
import pytz

TOTAL_SPACES = 82 # constant number of spos in the lot (excluding the row closest to the building)

def main():

    # connection to Firestore
    db = db_connection()
    
    st.title("UTC Parking Tracker") # title of web page

    # get parking data
    data = db_query(db, "Lot 12", "Totals")

    if not data or "error" in data: # if a failure occurs while retrieving data
        st.error("Parking data is currently unavailable.")
        occupied = None
        available = None
        time = "Unavailable"
    else: # no error in data
        occupied = data.get("occupied", 0) # retrieve number of occupied spaces from db (default value = 0)
        available = TOTAL_SPACES - occupied # count of open spaces

        time = data["time"] # return timestamp from db
        est = pytz.timezone("US/Eastern") # Eastern timezone

        # ensure UTC
        if time.tzinfo is None:
            time = time.replace(tzinfo=timezone.utc)

        # convert to Eastern
        time = time.astimezone(est)
        time = time.strftime("%Y-%m-%d %I:%M:%S %p")

    # display values
    if available is not None:
        st.write("# Available spots: " + str(available))
        st.write("Occupied spots: " + str(occupied))

        # display qualitative description of availability
        if available > 40:
            st.success("Plenty of parking available")
        elif available > 15:
            st.warning("Parking lot is filling up")
        else:
            st.error("Parking lot is almost full")
    else: # display "Unavailable" if there is an error
        st.write("# Available spots: Unavailable")
        st.write("Occupied spots: Unavailable")

    # map
    address_link = "<a href='https://maps.app.goo.gl/EgeZWvWBKXv84muh6' target='blank'>Get Directions</a>" # Google maps link to lot
    m = folium.Map(location=[35.046235, -85.2967971], zoom_start=18)
    folium.Marker(
        [35.046235, -85.2967971],
        popup=address_link,
        tooltip="Lot 12"
    ).add_to(m) # add marker to map

    st_folium(m, width=725)

    # display timestamp and credits
    st.write("Data last updated: " + str(time)) 
    st.write("Created by Ashley Carrera, Sophia Duke, Samuel Hunt, and Nathan Parnaby")

# connect to database
def db_connection():
    cred = firebase_admin.credentials.Certificate(dict(st.secrets["gcp_service_account"])) # retrieve credentials from Streamlit Secrets
    if not firebase_admin._apps: # check if app already exists
        firebase_admin.initialize_app(cred) # start Firebase app
    db = firestore.client() # connect to the Firestore database
    return db

# query the db (note: Firestore is no SQL)
def db_query(_db: firestore, collection: str, document: str):
    c = _db.collection(collection) # collection in the db (top level of hierarchy)
    doc = c.document(document) # document in the db (collection consists of documents)

    snapshot = doc.get() # retrieve the fields from the document

    if not snapshot.exists: # error if snapshot fails 
        return {"error": "Document does not exist"}

    return snapshot.to_dict() # return the values as as dictionary

main()
