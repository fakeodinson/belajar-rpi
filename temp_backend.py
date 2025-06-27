# main.py
import time
# Import the FastAPI library
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Import the max6675 library file you downloaded
import max6675 as MAX6675

# --- Create the FastAPI app ---
app = FastAPI()

# --- CORS Middleware ---
# This is important! It allows your HTML file (served from nginx)
# to make requests to this Python server (running on a different port).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Your Thermocouple Hardware Setup ---
# This is taken directly from your max6675_dual.py file.
# Please ensure these GPIO pin numbers are correct for your wiring.
cs_1 = 22
sck_1 = 18
so_1 = 16
sensor_1 = MAX6675.max6675(cs_1, sck_1, so_1, 1)

cs_2 = 26
sck_2 = 24
so_2 = 23
sensor_2 = MAX6675.max6675(cs_2, sck_2, so_2, 1)


# --- API Endpoint ---
# This is the function that the HTML/JavaScript will call.
# The "@app.get('/temperatures')" line makes this function available at
# the URL http://your_pi_ip:8000/temperatures
@app.get("/temperatures")
def get_temperatures():
    """
    Reads the temperature from both thermocouples and returns them
    in a structured JSON format.
    """
    try:
        # Read temperature from both sensors
        temp_1 = sensor_1.get_temp()
        temp_2 = sensor_2.get_temp()
        
        # Give the readings a short delay to prevent errors
        time.sleep(0.5)

        # Return the data in a dictionary. FastAPI will convert it to JSON.
        # The keys "tc1" and "tc2" match what the HTML expects.
        return {"tc1": temp_1, "tc2": temp_2}

    except Exception as e:
        # If there's an error reading the sensor, return an error message
        return {"error": str(e)}

# A simple root endpoint to confirm the API is running
@app.get("/")
def read_root():
    return {"status": "Thermocouple API is running"}

