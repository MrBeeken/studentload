# filter_page.py

from io import StringIO

import gspread
import pandas as pd
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    # Redirect to Login page if not logged in
    st.query_params.update({'pages': 'Login'})
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

    # Calculate min and max values for 'average' column
    min_average = int(existing_data['average'].min())
    max_average = int(existing_data['average'].max())

    # Display the title
    st.title("Filter Student Records")

    # Display the data table
    st.write("### All Student Records")
    st.dataframe(existing_data)

    # State management for filters
    if 'selected_schools' not in st.session_state:
        st.session_state['selected_schools'] = []

    # Use the calculated min and max values for slider range
    if 'selected_average_range' not in st.session_state:
        st.session_state['selected_average_range'] = (min_average, max_average)

    if 'sort_column' not in st.session_state:
        st.session_state['sort_column'] = 'None'

    if 'sort_order' not in st.session_state:
        st.session_state['sort_order'] = "Original"

    # Create three columns for filter options and buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        # Multiselect widget for filtering by primary school
        school_options = existing_data['school'].unique().tolist()  # Get unique schools from the data
        selected_schools = st.multiselect("Select Primary School(s) to Filter", school_options, default=st.session_state['selected_schools'])

        # Sorting options
        sort_column = st.selectbox("Select Column to Sort By", options=['None'] + existing_data.columns.tolist(), index=existing_data.columns.tolist().index(st.session_state['sort_column']) if st.session_state['sort_column'] in existing_data.columns else 0)
        sort_order = st.radio("Select Sorting Order", ("Ascending", "Descending", "Original"), index={"Original": 2, "Ascending": 0, "Descending": 1}[st.session_state['sort_order']])

    with col2:
        # Slider widget for filtering by average score
        selected_average_range = st.slider(
            "Select Average Score Range",
            min_value=min_average,
            max_value=max_average,
            value=st.session_state['selected_average_range']
        )

        # Selector for number of rows to print
        num_rows = st.number_input("Select Number of Rows to Print", min_value=1, max_value=len(existing_data), value=5)

    # Filter the data based on selected schools
    if selected_schools:
        filtered_data = existing_data[existing_data['school'].isin(selected_schools)]
    else:
        filtered_data = existing_data  # Show all data if no school is selected

    # Further filter the data based on the average score range
    filtered_data = filtered_data[
        (filtered_data['average'] >= selected_average_range[0]) & 
        (filtered_data['average'] <= selected_average_range[1])
    ]

    # Apply sorting to the filtered data
    if sort_column != 'None':
        if sort_order == "Ascending":
            filtered_data = filtered_data.sort_values(by=sort_column, ascending=True)
        elif sort_order == "Descending":
            filtered_data = filtered_data.sort_values(by=sort_column, ascending=False)

    # Display the sorted and filtered data table
    st.write("### Filtered Student Records")
    st.dataframe(filtered_data)

    with col3:
        # Button to print the filtered data
        if st.button("Print Filtered Data"):
            # Get the first 'num_rows' from the filtered data
            data_to_print = filtered_data.head(num_rows)
            
            # Convert the data to CSV format
            csv_data = data_to_print.to_csv(index=False)
            
            # Provide download button for CSV
            st.download_button(
                label="Download Filtered Data as CSV",
                data=csv_data,
                file_name='filtered_student_data.csv',
                mime='text/csv'
            )

        # Button to print the original data
        if st.button("Print Original Data"):
            # Convert the original data to CSV format
            original_csv_data = existing_data.to_csv(index=False)
            
            # Provide download button for CSV
            st.download_button(
                label="Download Original Data as CSV",
                data=original_csv_data,
                file_name='original_student_data.csv',
                mime='text/csv'
            )
