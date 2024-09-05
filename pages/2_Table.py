# second_page.py

import gspread
import pandas as pd
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    # Redirect to Login page if not logged in
    st.query_params.update({'page': 'Login'})
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
    st.title("Student Data Management")

    # Dropdown to select action: Update or Delete
    action = st.selectbox("Select Action", ["Select Action", "Update", "Delete"])

    # Text input to enter Student ID to delete or update
    student_id_input = st.text_input("Enter Student ID to " + action)

    # Validate if a valid student ID is entered
    if student_id_input and student_id_input in existing_data['studid'].values:
        # Retrieve the selected student record
        selected_record = existing_data[existing_data['studid'] == student_id_input].iloc[0]

        if action == "Update":
            st.subheader(f"Update Student Record: {student_id_input}")

            # Create two columns for input fields
            col1, col2 = st.columns(2)

            # Editable fields for updating the student record in two columns
            with col1:
                student_name = st.text_input("Student Name", selected_record["name"]).title()
                student_midlename = st.text_input("Student Middle Name", selected_record["midlename"]).title()
                student_surname = st.text_input("Student Surname", selected_record["surname"]).title()
                school_from = st.selectbox("Primary School", school_options, index=school_options.index(selected_record["school"]))
                maths_marks = st.number_input("Mathematics Average", value=int(selected_record["maths"]))
                english_marks = st.number_input("English Average", value=int(selected_record["english"]))
            with col2:
                afr_marks = st.number_input("Afrikaans Average", value=int(selected_record["afrikaans"]))
                siblings_status = st.selectbox("Siblings Status", siblings_options, index=siblings_options.index(selected_record["siblings"]))
                sport_status = st.selectbox("Sport Status", sport_options, index=sport_options.index(selected_record["sport"]))
                culture_status = st.selectbox("Culture Status", culture_options, index=culture_options.index(selected_record["culture"]))
                leader_status = st.selectbox("Leader Status", leader_options, index=leader_options.index(selected_record["leader"]))

            # Button to confirm update
            if st.button("Update Record"):
                # Calculate the average score
                average_score = round((maths_marks + english_marks + afr_marks) / 3, 2)

                # Update the record in the DataFrame
                index_to_update = existing_data[existing_data['studid'] == student_id_input].index[0]
                existing_data.at[index_to_update, 'name'] = student_name
                existing_data.at[index_to_update, 'midlename'] = student_midlename
                existing_data.at[index_to_update, 'surname'] = student_surname
                existing_data.at[index_to_update, 'school'] = school_from
                existing_data.at[index_to_update, 'maths'] = maths_marks
                existing_data.at[index_to_update, 'english'] = english_marks
                existing_data.at[index_to_update, 'afrikaans'] = afr_marks
                existing_data.at[index_to_update, 'siblings'] = siblings_status
                existing_data.at[index_to_update, 'sport'] = sport_status
                existing_data.at[index_to_update, 'culture'] = culture_status
                existing_data.at[index_to_update, 'leader'] = leader_status
                existing_data.at[index_to_update, 'average'] = average_score

                # Update the Google Sheet with the modified DataFrame
                sheet.update([existing_data.columns.values.tolist()] + existing_data.values.tolist())

                st.success(f"Student record for {student_id_input} has been updated.")

        elif action == "Delete":
            st.subheader(f"Delete Student Record: {student_id_input}")

            # Show details of the student record to be deleted
            st.write(f"**Name**: {selected_record['name']}")
            st.write(f"**Surname**: {selected_record['surname']}")
            st.write(f"**Primary School**: {selected_record['school']}")

            # Button to confirm deletion
            if st.button("Delete Record"):
                # Delete the selected record from the DataFrame
                existing_data = existing_data[existing_data['studid'] != student_id_input]

                # Find the row index in Google Sheets for deletion
                cell = sheet.find(student_id_input)
                if cell:
                    # Delete the row in Google Sheets
                    sheet.delete_rows(cell.row)

                    # Update the DataFrame after deletion
                    st.success(f"Student record for {student_id_input} has been deleted from the Google Sheet and DataFrame.")
                else:
                    st.error("Error: Could not find the student record in Google Sheets.")

    else:
        if student_id_input and action != "Select Action":
            st.warning("Please enter a valid Student ID.")

    # Display the title and data
    st.title("Student Data")

    # Number of records per page
    records_per_page = 20

    # Calculate total number of pages
    total_records = len(existing_data)
    total_pages = (total_records // records_per_page) + (1 if total_records % records_per_page != 0 else 0)

    # Create a selectbox for page selection
    page_number = st.number_input(
        "Select Page Number", min_value=1, max_value=total_pages, value=1, step=1
    )

    # Calculate the starting and ending indices of the records to display
    start_idx = (page_number - 1) * records_per_page
    end_idx = start_idx + records_per_page

    # Display the records for the current page
    st.write(f"Displaying records {start_idx + 1} to {min(end_idx, total_records)}")

    if not existing_data.empty:
        st.dataframe(existing_data.iloc[start_idx:end_idx])  # Display the records for the current page
    else:
        st.warning("No data available to display.")
