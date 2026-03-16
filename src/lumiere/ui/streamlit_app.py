# dashboard/app.py

import streamlit as st
import requests
import pandas as pd

# === v4.0 "Steering Wheel" ===
# This dashboard is the "Google-level" (v4.0) frontend.
# It knows NOTHING about SVD, MLFlow, or .dat files.
# It only knows how to speak JSON to our v3.1 "Motor" (FastAPI).

# --- API Configuration ---
API_URL = "http://localhost:8000/recommend/"  # Note the trailing slash

# --- Streamlit UI Configuration ---
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Movie Recommendation System (v4.0)")
st.write(
    "This Streamlit 'Dashboard' (v4.0) consumes the FastAPI 'Motor' (v3.1). "
    "The API (SVD Model + Movie Titles) is running in a separate Docker container."
)

# --- User Input (The "Steering") ---
st.header("Get Recommendations")

# We need a valid UserID (from 1 to 6040, based on our users.dat)
user_id_input = st.number_input(
    "Enter your UserID (1 to 6040):",
    min_value=1,
    max_value=6040,
    value=42,  # Default to User 42
    step=1
)

# --- API Request and Response (The "Motor") ---
if st.button(f"🚀 Get Top 10 Recommendations for User {user_id_input}"):

    # Define the full URL to call the v3.1 API "Motor"
    predict_url = f"{API_URL}{user_id_input}"

    try:
        # 1. Send the GET request to the FastAPI "Motor"
        response = requests.get(predict_url)
        response.raise_for_status()  # Raise an exception for bad status codes (404, 500)

        # 2. Get the "Google-level" JSON response
        data = response.json()

        # 3. "Polish" the JSON (from app/schema.py) into a nice display
        st.success(f"Top 10 Recommendations for User **{data['UserID']}**:")

        # Convert the list of 'Movie' objects into a clean DataFrame
        recs_df = pd.DataFrame(data['Recommendations'])

        # Display the "polished" recommendations
        st.dataframe(
            recs_df,
            column_config={
                "MovieID": st.column_config.NumberColumn("Movie ID"),
                "Title": st.column_config.TextColumn("Movie Title"),
                "Genres": st.column_config.TextColumn("Genres"),
            },
            hide_index=True,
            use_container_width=True
        )

    except requests.exceptions.ConnectionError:
        st.error(
            "Connection Error: Could not connect to the API (v3.1).\n\n"
            "**Is the FastAPI Docker container (recsys-api:v3) running?**\n\n"
            "Please run the following command in a separate terminal:\n\n"
            "`docker run -d --rm -p 8000:80 -v ${pwd}/models:/app/models -v ${pwd}/data/processed:/app/data/processed -v ${pwd}/data/raw:/app/data/raw recsys-api:v3`"
        )
    except requests.exceptions.HTTPError as e:
        # Handle "kaos" errors from the API (like User 404 Not Found)
        if e.response.status_code == 404:
            st.error(f"HTTP Error 404: User ID {user_id_input} not found in the dataset.")
        else:
            st.error(f"An HTTP error occurred: {e}")

    except Exception as e:
        st.error(f"An unknown error occurred: {e}")