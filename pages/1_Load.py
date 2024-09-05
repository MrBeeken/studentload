# Load.py

from datetime import datetime

import gspread
import pandas as pd
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    # Redirect to Login page if not logged in
    st.title("Please log in first")
else:

    # Set page layout to centered (default)
    st.set_page_config(layout="centered")

    # Access secrets from Streamlit
    credentials_dict = st.secrets["google_api"]

    # Use the dictionary directly with gspread
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict)
    client = gspread.authorize(credentials)

    # Open your Google Sheet
    sheet = client.open("Entry_Form").worksheet("Students_HGH")

    # Fetch all existing data from the sheet
    existing_data = pd.DataFrame(sheet.get_all_records())

    # Ensure 'studid' column is treated as strings to avoid AttributeError
    if 'studid' in existing_data.columns:
        existing_data['studid'] = existing_data['studid'].astype(str)

    # Define dropdown options for fields
    school_options = ["Opsie A", "Opsie B", "Opsie C"]
    siblings_options = ["Yes", "No"]
    sport_options = ["Opsie A", "Opsie B", "Opsie C"]
    culture_options = ["Opsie A", "Opsie B", "Opsie C"]
    leader_options = ["Opsie A", "Opsie B", "Opsie C"]

    # Display the title
    st.title("Create New Student Record")

    # Input field for student ID
    student_id = st.text_input("Student ID")

    # Calculate gender and age based on ID
    if len(student_id) == 13:
        # Extract birth date from ID (YYMMDD format)
        birth_year = int(student_id[0:2])
        birth_month = int(student_id[2:4])
        birth_day = int(student_id[4:6])
        
        # Determine if the year is in the 1900s or 2000s
        current_year = datetime.now().year
        if birth_year > int(str(current_year)[2:]):
            birth_year += 1900
        else:
            birth_year += 2000
        
        # Calculate age
        birth_date = datetime(birth_year, birth_month, birth_day)
        age = current_year - birth_date.year - ((datetime.now().month, datetime.now().day) < (birth_month, birth_day))
        
        # Determine gender based on the 7th digit
        gender_digit = int(student_id[6])
        if gender_digit >= 5:
            gender = "Male"
        else:
            gender = "Female"
    else:
        age = None
        gender = None

    # Input fields for creating a new student
    student_name = st.text_input("Student Name").title()
    student_midlename = st.text_input("Student Middle Name").title()
    student_surname = st.text_input("Student Surname").title()
    school_from = st.selectbox("Primary School", school_options)
    maths_marks = st.number_input("Mathematics Average", min_value=0, max_value=100, value=50)
    english_marks = st.number_input("English Average", min_value=0, max_value=100, value=50)
    afr_marks = st.number_input("Afrikaans Average", min_value=0, max_value=100, value=50)
    siblings_status = st.selectbox("Siblings Status", siblings_options)
    sport_status = st.selectbox("Sport Status", sport_options)
    culture_status = st.selectbox("Culture Status", culture_options)
    leader_status = st.selectbox("Leader Status", leader_options)

    # Button to add a new student record
    if st.button("Create Student"):
        if student_id and student_name and student_surname and age is not None and gender is not None:
            # Calculate the average score
            average_score = round((maths_marks + english_marks + afr_marks) / 3, 2)

            # Prepare the new student data as a dictionary
            new_student = {
                "studid": student_id,
                "name": student_name,
                "midlename": student_midlename,
                "surname": student_surname,
                "gender": gender,  # Add gender calculated from ID
                "age": age,  # Add age calculated from ID
                "school": school_from,
                "maths": maths_marks,
                "english": english_marks,
                "afrikaans": afr_marks,
                "average": average_score,  # Add calculated average to the data
                "siblings": siblings_status,
                "sport": sport_status,
                "culture": culture_status,
                "leader": leader_status,
                "p-point": ""  # Placeholder for p-point if needed
            }

            # Convert the new student data to a DataFrame
            new_student_df = pd.DataFrame([new_student])

            # Append the new student data to the existing data in the DataFrame
            updated_df = pd.concat([existing_data, new_student_df], ignore_index=True)

            # Update the Google Sheet with the new student data
            sheet.update([updated_df.columns.values.tolist()] + updated_df.values.tolist())

            st.success(f"Student record for {student_name} has been added.")
        else:
            st.warning("Please fill in all the required fields.")
