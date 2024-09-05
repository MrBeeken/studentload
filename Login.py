# Login.py

import bcrypt  # For password hashing
import gspread
import pandas as pd
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

# Set page layout to centered
st.set_page_config(layout="centered")

# Access secrets from Streamlit
credentials_dict = st.secrets["google_api"]

# Use the dictionary directly with gspread
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict)
client = gspread.authorize(credentials)

# Open your Google Sheet for user information
user_sheet = client.open("Entry_Form").worksheet("Users_HGH")
users_data = pd.DataFrame(user_sheet.get_all_records())

# Function to check if login credentials are correct
def is_login_valid(username, password):
    user_record = users_data[users_data['username'] == username]
    if not user_record.empty:
        stored_password_hash = user_record.iloc[0]['password'].encode('utf-8')  # Get the hashed password
        # Check the entered password against the stored hashed password
        return bcrypt.checkpw(password.encode('utf-8'), stored_password_hash)
    return False

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'username' not in st.session_state:
    st.session_state['username'] = ""

# Hide sidebar if not logged in
if not st.session_state['logged_in']:
    st.sidebar.empty()  # Hide the sidebar

    # Login Section
    st.title("Login")

    # Login fields
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    # Login button
    if st.button("Login"):
        if is_login_valid(login_username, login_password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = login_username
            st.success("Logged in successfully!")

            # Redirect to 1_Load.py by setting query params
            st.switch_page("pages/1_Load.py")
            #st.query_params.update({'page': '1_Load'})  # Set the page to '1_Load.py'

            # JavaScript to force a reload to the updated page
            st.markdown(f"""
                <script>
                    window.location.href = window.location.origin + "/?page=1_Load";
                </script>
                """, unsafe_allow_html=True)
        else:
            st.error("Invalid username or password. Please try again.")
else:
    # If already logged in, redirect to Load.py
    st.query_params.update({'pages': '1_Load'})
    st.markdown(f"""
        <script>
            window.location.href = window.location.origin + "/?page=1_Load";
        </script>
        """, unsafe_allow_html=True)