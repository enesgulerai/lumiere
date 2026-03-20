import os
import streamlit as st
import requests
import pandas as pd

# --- API Configuration ---
# Fetch the backend URL from Docker environment variables
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
API_URL = f"{BACKEND_URL}/recommend/"

# --- Streamlit UI Configuration ---
st.set_page_config(
    page_title="Lumiere Recommendations",
    layout="wide"
)

st.title("Lumiere Movie Recommendation System")
st.markdown(
    "This UI consumes the FastAPI microservice. "
    "The API (ONNX Model + Redis Cache) is running in a separate Docker container."
)

# --- User Input ---
st.header("Get Recommendations")

user_id_input = st.number_input(
    "Enter your UserID (1 to 6040):",
    min_value=1,
    max_value=6040,
    value=42,
    step=1
)

# --- API Request and Response ---
if st.button(f"Get Top 10 Recommendations for User {user_id_input}"):
    predict_url = f"{API_URL}{user_id_input}"

    try:
        with st.spinner("Fetching recommendations..."):
            response = requests.get(predict_url)
            response.raise_for_status()

        data = response.json()

        # Display performance metrics
        source = data.get('source', 'Unknown')
        latency = data.get('latency_ms', 0.0)
        
        col1, col2 = st.columns(2)
        if source == "Redis Cache":
            col1.success(f"Source: {source}")
        else:
            col1.info(f"Source: {source}")
        col2.metric("Latency", f"{latency} ms")

        st.markdown(f"### Top 10 Recommendations for User **{data['UserID']}**:")

        recs_df = pd.DataFrame(data['Recommendations'])

        st.dataframe(
            recs_df,
            column_config={
                "MovieID": st.column_config.NumberColumn("Movie ID", format="%d"),
                "Title": st.column_config.TextColumn("Movie Title"),
                "Genres": st.column_config.TextColumn("Genres"),
            },
            hide_index=True,
            use_container_width=True
        )

    except requests.exceptions.ConnectionError:
        st.error(
            f"Connection Error: Could not connect to the Backend API at {BACKEND_URL}.\n\n"
            "Ensure the backend Docker container is running."
        )
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            st.error(f"HTTP Error 404: User ID {user_id_input} not found in the historical data.")
        else:
            st.error(f"An HTTP error occurred: {e.response.text}")
    except Exception as e:
        st.error(f"An unknown error occurred: {e}")