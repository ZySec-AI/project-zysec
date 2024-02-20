from . import app_constants
import streamlit as st
from modules import file_utils, app_logger, app_page_definitions, app_to_vectorstore
import os

# Use the logger from app_config
app_logger = app_logger.app_logger

def app():
    app_logger.info("Starting Streamlit app - File Manager")
    current_page = "nav_file_manager"

    # Fetch page configuration
    page_config = app_page_definitions.PAGE_CONFIG.get(current_page, app_page_definitions.PAGE_CONFIG["default"])

    # Page setup
    st.title(page_config["title"])
    st.caption(page_config["caption"])

    # Load file data
    system_content_file = app_constants.SYSTEM_CONTENT_DATA
    file_data = file_utils.load_file_metadata()
    update_required = False  # Flag to track if metadata update is required

    if 'checkbox_states' not in st.session_state:
        st.session_state.checkbox_states = [False] * len(file_data)
    else:
        # Adjust the length of checkbox_states to match file_data
        current_length = len(st.session_state.checkbox_states)
        new_length = len(file_data)
        if new_length > current_length:
            # Extend the list with False for new file entries
            st.session_state.checkbox_states.extend([False] * (new_length - current_length))

    # Check real-time file existence and update status
    for idx, file_entry in enumerate(file_data):
        file_path = os.path.join(app_constants.WORKSPACE_DIRECTORY, 'docs', file_utils.sanitize_filename(file_entry["url"]))
        file_exists = os.path.exists(file_path)
        file_entry["downloaded_status"] = file_exists

        # Initialize checkbox states based on the current indexed status
        st.session_state.checkbox_states[idx] = file_entry.get("indexed_status", False)

        # Remove entry if it's a local file and does not exist
        is_remote_file = file_entry["url"].startswith("http://") or file_entry["url"].startswith("https://")
        if not is_remote_file and not file_exists:
            file_data.remove(file_entry)
            update_required = True

    # Save updated statuses if needed
    if update_required:
        file_utils.save_file_metadata(file_data)
        file_data = file_utils.load_file_metadata()

    # Display file data and manage files
    if file_data:
        for idx, file_entry in enumerate(file_data):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                link_url = file_entry.get("url", "#")
                st.markdown(f"[{file_entry['name']}]({link_url})", unsafe_allow_html=True)
            with col2:
                st.text(file_entry.get("content_type", "Other"))

            # Download checkbox logic
            with col3:
                is_remote_file = file_entry["url"].startswith("http://") or file_entry["url"].startswith("https://")
                download_key = f"download_{idx}"
                already_downloaded = file_entry.get("downloaded_status", False)
                download_disabled = not is_remote_file or already_downloaded
                download_checked = st.checkbox("Download", key=download_key, value=already_downloaded, disabled=download_disabled)

                if download_checked and not already_downloaded and is_remote_file:
                    sanitized_filename = file_utils.sanitize_filename(file_entry["url"].split('/')[-1])
                    local_path = os.path.join(app_constants.WORKSPACE_DIRECTORY, 'docs', sanitized_filename)
                    
                    if file_utils.download_file(file_entry["url"], local_path):
                        file_entry["downloaded_status"] = True
                        file_entry["local_path"] = local_path  # Update local path with sanitized filename
                        update_required = True
                    else:
                        st.error(f"Failed to download '{sanitized_filename}'.")

            with col4:
                enable_key = f"enable_{idx}"
                file_path = file_entry.get("local_path")
                file_exists = file_path and os.path.exists(file_path)

                if file_exists:
                    current_status = st.session_state.checkbox_states[idx]
                    enable_checked = st.checkbox("Learn It", key=enable_key, value=current_status, disabled=current_status)

                    if enable_checked and not current_status:
                        file_entry["indexed_status"] = True
                        st.session_state.checkbox_states[idx] = True
                        update_required = True
                        file_utils.perform_file_operation(file_path, "enable")
                else:
                    # Optionally, log a warning or handle cases where file path doesn't exist
                    app_logger.warning(f"File path does not exist or is not set for file: {file_entry.get('name')}")

    else:
        st.write("No files found.")

    # Save updated file metadata if changes have been made
    if update_required:
        file_utils.save_file_metadata(file_data)
        file_data = file_utils.load_file_metadata()

    # File Upload and Manual Entry Section
    with st.expander("Manage Content to System", expanded=True):
        st.markdown("Add Content: feature enables you to conveniently upload playbooks or directly input web links, facilitating the indexing information in their respective sections.")
        selected_content_type = st.selectbox("Select Content Type", ["Select Type"] + app_constants.CONTENT_TYPE)

        if selected_content_type and selected_content_type != 'Select Type':
            upload_choice = st.radio("Choose an option", ("Upload File", "Enter File Details Manually"))

            if upload_choice == "Upload File":
                uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx', 'txt', 'html'])
                if uploaded_file is not None:
                    with st.spinner("Processing your file..."):
                        sanitized_filename = file_utils.sanitize_filename(uploaded_file.name)
                        uploads_directory = os.path.join(app_constants.WORKSPACE_DIRECTORY, 'docs')
                        saved_file_path = file_utils.save_uploaded_file(uploaded_file, uploads_directory, sanitized_filename)
                        new_file_entry = {
                            "name": sanitized_filename,
                            "url": saved_file_path,
                            "downloaded_status": True,
                            "local_path": saved_file_path,
                            "indexed_status": False,
                            "content_type": selected_content_type
                        }
                        file_data.append(new_file_entry)
                        update_required = True

            elif upload_choice == "Enter File Details Manually":
                with st.form("file_details_form"):
                    manual_name = st.text_input("Document Name")
                    manual_url = st.text_input("Download URL")
                    submit_button = st.form_submit_button("Submit")

                    if submit_button and manual_name and manual_url:
                        new_file_entry = {
                            "name": manual_name,
                            "url": manual_url,
                            "downloaded_status": False,
                            "local_path": "",
                            "indexed_status": False,
                            "content_type": selected_content_type
                        }
                        file_data.append(new_file_entry)
                        update_required = True

        else:
            st.write("Please select a content type to enable file upload or manual entry.")


    if update_required:
        file_utils.save_file_metadata(file_data)
        file_data = file_utils.load_file_metadata()

    st.write("Using below clear option, you can clear all data in the system and start fresh to index and upload information!")
    if st.button("Clear Data"):
        file_utils.delete_files()
        st.write("All data cleared.")
        st.rerun()