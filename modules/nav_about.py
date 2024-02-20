from . import app_constants
import streamlit as st
from modules import file_utils
from modules import app_logger,common_utils
from modules import app_st_session_utils, app_page_definitions

# Use the logger from app_config
app_logger = app_logger.app_logger


def app():
    app_logger.info("Starting Streamlit app - Configuration Tool")
    current_page = "nav_about"
    # Fetch page configuration from app_page_definitions
    page_config = app_page_definitions.PAGE_CONFIG.get(current_page, app_page_definitions.PAGE_CONFIG["default"])

    # Use configurations for title, caption, and greeting from page_config
    st.title(page_config["title"])
    st.caption(page_config["caption"])

    # Dropdown for AI Model Source Selection
    st.subheader("AI Model Source")
    st.write("Choose a model to get started. If you're limited by system resources, no worries! You can also use the OpenAI API. Simply obtain your API key and enjoy using the ZySec tool with ease.")
    model_source = st.selectbox("Select Model Source", ["OpenAI Endpoint", "Private Endpoint"])

    # Conditional Input Fields based on Model Source Selection
    if model_source == "OpenAI Endpoint":
        openai_api_key = st.text_input("OpenAI API Key", type="password", value=app_constants.openai_api_key)
        st.markdown(
            "Need an OpenAI API key? [Get it here](https://platform.openai.com/api-keys).", 
            unsafe_allow_html=True
        )
    else:
        local_model_uri = st.text_input("Private Model Base URL Endpoint (OpenAI Compatible)", value=app_constants.local_model_uri)
        models = file_utils.list_huggingface_models()
        if models:
            selected_model = st.selectbox("Select a Model", models)

    # Button to Update Configurations
    if st.button("Update Configuration"):
        if model_source == "OpenAI Endpoint":
            app_constants.openai_api_key = openai_api_key  # Update the OpenAI API key
            app_constants.local_model_uri = None  # Set base URL to None for OpenAI
            st.success("OpenAI configuration updated.")
        else:
            app_constants.local_model_uri = local_model_uri  # Update the Local Model URI
            st.success("Local model configuration updated.")
        
        # Session and Data Reset
        st.subheader("Session and Data Management")
        if st.button("Reset Session"):
            # Clear all items from the session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            # Reload the page to reflect the session reset
            app_st_session_utils.reload_page()

        if st.button("Reset Data"):
            common_utils.delete_files()
            app_logger.info("Data reset successfully.")
            st.success("Data reset successfully.")
            st.rerun()


    with st.expander("About ZySec and the Author"):
        st.markdown("""
            ### About ZySec
            ZySec is at the forefront of integrating **Cyber Security with Artificial Intelligence**, aiming to revolutionize how security professionals engage with technology. This project is driven by the aspiration to blend AI's innovative capabilities with the intricacies of cybersecurity, all while upholding the utmost standards of privacy.
            
            ZySec is not just a tool; it's a vision to elevate enterprise security functions, harnessing AI to propel these capabilities to new heights. We encourage you to explore our roadmap and see how ZySec is poised to transform the cybersecurity landscape.
            
            [🔗 View Our Road Map](https://github.com/ZySec-AI/ZySec/blob/main/roadmap.md)
            
            [🔗 Explore the Project on GitHub](https://github.com/ZySec-AI/ZySec.git)

            [🔗 Contact Us](https://docs.google.com/forms/d/e/1FAIpQLSdkqIjQUoUOorsWXVzgQhJ-vbp1OpN1ZI0u3u8fK_o-UxII2w/viewform)

            ### ZySec 7B Model
            **ZySec-v1-7B** stands as a pivotal innovation for security professionals, leveraging the advanced capabilities of HuggingFace's Zephyr language model series. This AI model is crafted to be an omnipresent cybersecurity ally, offering on-demand, expert guidance in cybersecurity issues. Picture ZySec-7B as an ever-present digital teammate, adept at navigating the complexities of security challenges. ZySec-7B's training spans over 30 unique domains, each enriched with thousands of data points, delivering unparalleled expertise.
            
            [🔗 Checkout Model on HuggingFace](https://huggingface.co/aihub-app/ZySec-7B-v1)

            ### About the Author - Venkatesh Siddi
            **Venkatesh Siddi** is a seasoned expert in the cybersecurity domain, beyond traditional cybersecurity, Venkatesh is deeply invested in leveraging **Artificial Intelligence and Machine Learning** to tackle complex cybersecurity challenges. He has led multiple projects involving big data, cloud security, and technology design.
                    
            [🔗 Connect with Venkatesh on LinkedIn](https://www.linkedin.com/in/venkycs/)

        """, unsafe_allow_html=True)