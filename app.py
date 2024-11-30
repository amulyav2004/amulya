import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import serial
import time

# Initialize serial port for hardware connection
serial_port = 'COM9'  # Update with the correct serial port (change to the actual port used by ESP8266)
try:
    ser = serial.Serial(serial_port, 9600, timeout=1)
    st.success(f"Serial port {serial_port} connected successfully.")
except Exception as e:
    ser = None
    st.error(f"Error: Could not open serial port {serial_port}. Please check the connection.")

# Function to fetch GPS and distance data from the serial port
def get_data_from_serial(max_attempts=5):
    if ser:
        for attempt in range(max_attempts):
            try:
                # Read the data from the serial port
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                st.write(f"Raw Data: {line}")  # Debugging line
                data = line.split(',')
                if len(data) >= 5:
                    latitude = float(data[0])  # Latitude
                    longitude = float(data[1])  # Longitude
                    distance1 = float(data[2])  # Distance from sensor 1
                    distance2 = float(data[3])  # Distance from sensor 2
                    distance3 = float(data[4])  # Distance from sensor 3
                    return latitude, longitude, distance1, distance2, distance3
                time.sleep(1)  # Wait before retrying
            except Exception as e:
                st.warning(f"Attempt {attempt + 1}: Error reading data: {e}")
        st.error("Failed to fetch data after multiple attempts.")
    else:
        st.error(f"Serial port {serial_port} is not available.")
    return None, None, None, None, None

# Streamlit App Title
st.title("Smart Parking Tracker")

# Fetch GPS and Distance Data
st.write("### Fetching Location and Distance Data")
latitude, longitude, distance1, distance2, distance3 = get_data_from_serial()

if latitude and longitude:
    st.write(f"Current Location: Latitude {latitude}, Longitude {longitude}")
else:
    st.write("Error fetching GPS data. Using default location for demonstration.")
    latitude, longitude = 13.394968, 77.728851  # Default coordinates
    st.warning("Using default coordinates (13.394968, 77.728851)")

# Display Location on Map
st.write("### Map View of Your Location")
m = folium.Map(location=[latitude, longitude], zoom_start=15)
folium.Marker([latitude, longitude], popup="Your Location").add_to(m)
st_folium(m, width=700, height=500)

# Display Distance Data
st.write("### Sensor Data")
st.write(f"Distance from Sensor 1: {distance1} cm")
st.write(f"Distance from Sensor 2: {distance2} cm")
st.write(f"Distance from Sensor 3: {distance3} cm")

# Send Data to IoT System
iot_endpoint = st.text_input("Enter IoT Endpoint URL:", "https://example-iot-cloud.com/api/coordinates")
if st.button("Send Location and Data to IoT"):
    try:
        data = {"latitude": latitude, "longitude": longitude, "distance1": distance1, "distance2": distance2, "distance3": distance3}
        response = requests.post(iot_endpoint, json=data)
        if response.status_code == 200:
            st.success("Data sent successfully!")
            st.write("Response:", response.json())
        else:
            st.error(f"Failed to send data. Status code: {response.status_code}")
            st.write("Response:", response.text)
    except Exception as e:
        st.error("Error sending data to IoT system.")
        st.write(e)