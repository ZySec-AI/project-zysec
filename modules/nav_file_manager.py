#nav_file_manager.py

from . import app_constants
import streamlit as st
from modules import app_logger, app_page_definitions,file_utils,common_utils
import os, json

# Use the logger from app_config
app_logger = app_logger.app_logger
system_content_file = app_constants.SYSTEM_CONTENT_DATA
work_dir = os.path.join(app_constants.WORKSPACE_DIRECTORY, "docs")

def app():
    app_logger.info("Starting Streamlit app - File Manager")
    current_page = "nav_file_manager"

    # Fetch page configuration
    page_config = app_page_definitions.PAGE_CONFIG.get(current_page, app_page_definitions.PAGE_CONFIG["default"])

    # Page setup
    st.title(page_config["title"])
    st.caption(page_config["caption"])
    with open(system_content_file, "r") as file:
        content_data = json.load(file)
    processed_paths = common_utils.read_processed_log()
    if 'download_states' not in st.session_state:
        st.session_state['download_states'] = {}
    if 'learn_states' not in st.session_state:
        st.session_state['learn_states'] = {}
    for index, item in enumerate(content_data):
        name = item["name"]
        url = item["url"]
        content_type = item["content_type"]
        unique_identifier = f"{index}_{name}_{url.replace('http://', '').replace('https://', '')}"  # Ensure the identifier is unique

        # Create a row of columns for each item
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

        # Display the name as a hyperlink in the first column
        col1.markdown(f"[{name}]({url})")

        # Display the content type in the second column
        col2.write(content_type)

        file_path = os.path.join(work_dir, file_utils.sanitize_filename(url))
        file_exists = os.path.exists(file_path)
        file_processed = file_path in processed_paths

        # Checkboxes in the third and fourth columns
        download_key = f"download_{unique_identifier}"
        learn_key = f"learn_{unique_identifier}"

        # Initialize session state for checkboxes if not already set
        if download_key not in st.session_state['download_states']:
            st.session_state['download_states'][download_key] = file_exists
        if learn_key not in st.session_state['learn_states']:
            st.session_state['learn_states'][learn_key] = file_processed

        # Logic for enabling/disabling checkboxes
        download_disabled = file_exists
        learn_disabled = not file_exists or file_processed

        # Display checkboxes
        download_checked = col3.checkbox("Download", value=st.session_state['download_states'][download_key], key=download_key, disabled=download_disabled)
        learn_checked = col4.checkbox("Learn It", value=st.session_state['learn_states'][learn_key], key=learn_key, disabled=learn_disabled)

        # Check if the state of checkboxes changed
        if download_checked != st.session_state['download_states'][download_key]:
            if download_checked:
                file_utils.perform_file_operation(item, "download")
            st.session_state['download_states'][download_key] = download_checked

        if learn_checked != st.session_state['learn_states'][learn_key]:
            if learn_checked:
                file_utils.perform_file_operation(item, "learn")
            st.session_state['learn_states'][learn_key] = learn_checked


    with st.expander("Manage Content in the System", expanded=True):
        st.markdown("""
            **Content Types:** 
            - **Policies:** Guidelines for operations, organizational or industry-wide. 
            - **Playbooks:** How-to guides and procedures for operational guidance. 
            - **Standards:** Compliance with regulatory or industry best practices. 
            - **Reference Docs:** In-depth information like technical manuals and research, however, they go into playbooks.
        """)

        selected_content_type = st.selectbox("Select Content Type", ["Select Type"] + app_constants.CONTENT_TYPE)
        
        if selected_content_type and selected_content_type != 'Select Type':
            upload_choice = st.radio("Choose an option", ("Upload File", "Enter File Details Manually"))

            if upload_choice == "Upload File":
                uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx', 'txt', 'html'])

                if uploaded_file is not None:
                    # Check if the file has already been processed in this session
                    if 'processed_files' not in st.session_state:
                        st.session_state['processed_files'] = set()

                    file_details = (uploaded_file.name, uploaded_file.size)

                    if file_details not in st.session_state['processed_files']:
                        with st.spinner("Processing your file..."):
                            file_utils.handle_content_update(uploaded_file=uploaded_file, selected_content_type=selected_content_type)
                        st.session_state['processed_files'].add(file_details)
                        st.success("File processed.")
                    else:
                        st.info("This file has already been processed in this session.")

            elif upload_choice == "Enter File Details Manually":
                with st.form("file_details_form"):
                    manual_name = st.text_input("Document Name")
                    manual_url = st.text_input("Download URL")
                    submit_button = st.form_submit_button("Submit")

                    if submit_button and manual_url and manual_name:
                        # Use session state to check if the form details have already been submitted
                        form_details = (manual_name, manual_url)

                        if 'submitted_forms' not in st.session_state:
                            st.session_state['submitted_forms'] = set()

                        if form_details not in st.session_state['submitted_forms']:
                            file_utils.handle_content_update(manual_name=manual_name, manual_url=manual_url, selected_content_type=selected_content_type)
                            st.session_state['submitted_forms'].add(form_details)
                            st.success("Form details processed.")
                        else:
                            st.info("These details have already been submitted in this session.")


    st.write("Using below clear option, you can clear all data in the system and start fresh to index and upload information!")
    if st.button("Clear Data"):
        file_utils.delete_files()
        st.write("All data cleared.")
        st.rerun()