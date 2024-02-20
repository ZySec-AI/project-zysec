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
    file_data = file_utils.load_file_metadata(system_content_file)
    update_required = False  # Flag to track if metadata update is required

    # Check real-time file existence and update status
    for file_entry in list(file_data):  # Using list() to create a copy for safe iteration
        file_path = os.path.join(app_constants.WORKSPACE_DIRECTORY, 'docs', file_utils.sanitize_filename(file_entry["url"]))
        file_exists = os.path.exists(file_path)
        file_entry["downloaded_status"] = file_exists
        file_entry["indexed_status"] = file_exists

        # Remove entry if it's a local file and does not exist
        is_remote_file = file_entry["url"].startswith("http://") or file_entry["url"].startswith("https://")
        if not is_remote_file and not file_exists:
            file_data.remove(file_entry)
            update_required = True  # Update required if any file entry is removed

    # Save updated statuses if needed
    if update_required:
        file_utils.save_file_metadata(file_data, system_content_file)
        file_data = file_utils.load_file_metadata(system_content_file)  # Reload file metadata

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
                download_disabled = not is_remote_file or file_entry.get("downloaded_status", False)
                download_checked = st.checkbox("Download", key=download_key, value=file_entry.get("downloaded_status", False), disabled=download_disabled)
                if download_checked and not file_entry["downloaded_status"] and is_remote_file:
                    sanitized_filename = file_utils.sanitize_filename(file_entry["url"].split('/')[-1])
                    local_path = os.path.join(app_constants.WORKSPACE_DIRECTORY, 'docs', sanitized_filename)
                    if file_utils.download_file(file_entry["url"], local_path, system_content_file):
                        file_entry["downloaded_status"] = True
                        file_entry["local_path"] = local_path  # Update local path with sanitized filename
                        update_required = True
                    else:
                        st.error(f"Failed to download '{sanitized_filename}'.")

            with col4:
                enable_key = f"enable_{idx}"
                try:
                    file_path = file_entry["local_path"]
                    file_exists = os.path.exists(file_path)
                except:
                    pass
                if file_exists:
                    indexed_status = file_entry.get("indexed_status", False)
                    print(file_path,indexed_status)
                    enable_checked = st.checkbox("Learn It", key=enable_key, value=indexed_status, disabled=indexed_status)

                    if enable_checked and indexed_status:
                        file_entry["indexed_status"] = True
                        update_required = True
                        file_utils.perform_file_operation(file_path, "enable")

    else:
        st.write("No files found.")

    # Save updated file metadata if changes have been made
    if update_required:
        file_utils.save_file_metadata(file_data, system_content_file)
        file_data = file_utils.load_file_metadata(system_content_file)  # Reload file metadata

    # File Upload Section
    with st.expander("Upload New File"):
        selected_content_type = st.selectbox("Select Content Type", app_constants.CONTENT_TYPE)

        # Check if a content type has been selected
        if selected_content_type and selected_content_type != 'Select Type':
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

        else:
            st.write("Please select a content type to enable file upload.")

    if update_required:
        file_utils.save_file_metadata(file_data, system_content_file)
        file_data = file_utils.load_file_metadata(system_content_file)  # Reload file metadata after update

    st.write("Using below clear option, you can clear all data in the system and start fresh to index and upload information!")
    if st.button("Clear Data"):
        file_utils.delete_files()
        st.write("All data cleared.")
        st.rerun()

# End of app function
