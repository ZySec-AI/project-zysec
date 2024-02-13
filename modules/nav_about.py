import time
from . import app_constants
import streamlit as st
import os
from modules import app_ai_model
from modules import app_logger,common_utils
from modules import app_st_session_utils

# Use the logger from app_config
app_logger = app_logger.app_logger


def app():
    app_logger.info("Starting Streamlit app - Configuration Tool")
    
    # Title and Description for System Controls Section
    st.title("⚙️ System Controls")
    st.caption("Here you can manage and control system settings. This includes configuring database connections, selecting AI models, and executing operational commands for the application.")

    current_page = "nav_about"  # Example current page

    # Initialize Session State
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = current_page
        st.session_state['page_loaded'] = False
        app_logger.info("Initialized session for about page.")

    # System Controls Expander
    with st.expander("System Controls"):
        # App Configuration
        st.subheader("App Configuration")
        st.text_input("MongoDB Connection String", type="password", value=app_constants.mongodb_uri)
        st.text_input("OpenAI Compatible URL", value=app_constants.local_model_uri)
        models = app_ai_model.list_huggingface_models()
        if models:
            selected_model = st.selectbox("Select a Model", models)
        
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