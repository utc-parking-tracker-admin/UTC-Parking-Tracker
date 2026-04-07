import streamlit as st
import firebase_admin
from firebase_admin import firestore
import folium
from streamlit_folium import st_folium
from datetime import timezone
import pytz

TOTAL_SPACES = 82

def main():

    # connection to Firestore
    db = db_connection()
    
    st.title("UTC Parking Tracker")

    # get parking data
    data = db_query(db, "Lot 12", "Totals")

    if not data or "error" in data:
        st.error("Parking data is currently unavailable.")
        occupied = None
        available = None
        time = "Unavailable"
    else:
        occupied = data.get("occupied", 0)
        available = TOTAL_SPACES - occupied

        time = data["time"]
        est = pytz.timezone("US/Eastern")

        # ensure UTC
        if time.tzinfo is None:
            time = time.replace(tzinfo=timezone.utc)

        # convert to Eastern
        time = time.astimezone(est)

        # format
        time = time.strftime("%Y-%m-%d %I:%M:%S %p")

    # display values
    if available is not None:
        st.write("# Available spots: " + str(available))
        st.write("Occupied spots: " + str(occupied))

        if available > 40:
            st.success("Plenty of parking available")
        elif available > 15:
            st.warning("Parking lot is filling up")
        else:
            st.error("Parking lot is almost full")
    else:
        st.write("# Available spots: Unavailable")
        st.write("Occupied spots: Unavailable")

    # map
    address_link = "<a href='https://maps.app.goo.gl/EgeZWvWBKXv84muh6' target='blank'>Get Directions</a>"
    m = folium.Map(location=[35.046235, -85.2967971], zoom_start=18)
    folium.Marker(
        [35.046235, -85.2967971],
        popup=address_link,
        tooltip="Lot 12"
    ).add_to(m)

    st_folium(m, width=725)

    st.write("Data last updated: " + str(time))
    st.write("Created by Ashley Carrera, Sophia Duke, Samuel Hunt, and Nathan Parnaby")


def db_connection():
    cred = firebase_admin.credentials.Certificate(dict(st.secrets["gcp_service_account"]))
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db


def db_query(_db: firestore, collection: str, document: str):
    c = _db.collection(collection)
    doc = c.document(document)

    snapshot = doc.get()

    if not snapshot.exists:
        return {"error": "Document does not exist"}

    return snapshot.to_dict()


main()
