from . import app_constants
import streamlit as st
from modules import app_logger,app_st_session_utils, app_page_definitions

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


    # Subheader for Server Mode Selection
    st.subheader("Server Mode Selection")
    mode_to_index = {"private": 0, "demo": 1, "openai": 2}
    default_index = mode_to_index.get(app_constants.SYSTEM_DEPLOYMENT_MODE, 0)  # Default to "Local" if not found
    # Radio buttons for selecting the server mode
    server_mode = st.radio("Select Server Mode", ["Private", "ZySec Demo", "OpenAI"],index=default_index)

    # Initialize variables for settings
    model_uri, remote_model_uri, openai_api_key = None, None, None

    # Conditional rendering of settings and their descriptions based on the selected server mode
    if server_mode == "Private":
        st.markdown("### Local Settings")
        st.markdown("""
        **Private Mode** is for running the model directly on your machine or on a local server. 
        This mode is ideal if you have the necessary resources and want to keep data processing in-house. 
        You can also use a local instance deployed with a URL endpoint.
        """)
        model_uri = st.text_input("Private Model Base URL Endpoint (OpenAI Compatible). Example http://localhost:8000/v1", key="model_uri",value=app_constants.model_uri)
        st.info("Use update configuration for changes to be affected")


    elif server_mode == "ZySec Demo":
        st.markdown("### ZySec Demo Settings")
        st.markdown("""
        **ZySec Demo Mode** is designed for users who prefer to use ZySec's resources. 
        This mode provides free access to a deployed model managed by the ZySec team, 
        subject to availability. It's a great choice for trying out ZySec without any setup.
        """)
        remote_model_uri = st.text_input("Remote Model Base URL Endpoint",value=app_constants.ZYSEC_DEMO, key="remote_model_uri",disabled=True)
        st.info("Use update configuration for changes to be affected")

    elif server_mode == "OpenAI":
        st.markdown("### OpenAI Settings")
        st.markdown("""
        **OpenAI Mode** leverages the OpenAI's Large Language Models (LLM) for processing. 
        This mode allows you to integrate OpenAI's powerful AI capabilities while keeping 
        the rest of the functionalities security-centric. An OpenAI API key is required.
        """)
        openai_api_key = st.text_input("OpenAI API Key", type="password", key="openai_api_key",value=app_constants.openai_api_key)
        st.markdown(
            "Need an OpenAI API key? [Get it here](https://platform.openai.com/api-keys).", 
            unsafe_allow_html=True
        )
        st.info("Use update configuration for changes to be affected")

    # Update app_constants based on user input
    if st.button("Update Configuration"):
        if server_mode == "Private":
            app_constants.SYSTEM_DEPLOYMENT_MODE = "private"
            app_constants.model_uri = model_uri
            # Reset other modes' settings
            app_constants.openai_api_key = "NO-API-KEY-NEEDED"
            st.info("Use update configuration for changes to be affected")
        elif server_mode == "ZySec Demo":
            app_constants.SYSTEM_DEPLOYMENT_MODE = "demo"
            app_constants.model_uri = remote_model_uri
            # Reset other modes' setting
            app_constants.openai_api_key = "NO-API-KEY-NEEDED"
            st.info("Use update configuration for changes to be affected")
        elif server_mode == "OpenAI":
            app_constants.SYSTEM_DEPLOYMENT_MODE = "openai"
            app_constants.openai_api_key = openai_api_key
            # Reset other modes' settings
            app_constants.model_uri = None
            st.info("Use update configuration for changes to be affected")
        st.success("Configuration updated for " + server_mode + " mode.")

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

        # Session and Data Reset
    st.subheader("Clear Session")
    if st.button("Reset Session"):
        # Clear all items from the session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        # Reload the page to reflect the session reset
        app_st_session_utils.reload_page()
        st.rerun()