# Transforming CyberSecurity with AI Innovation: ZySec AI

Welcome to ZySec AI, where artificial intelligence meets cybersecurity. Our project, powered by the innovative ZySec 7B model, is reshaping the cybersecurity landscape with AI-driven solutions.

## Key Features

1. **AI-Driven Cybersecurity:** Experience the full potential of the ZySec 7B model, a specialized AI tool for cybersecurity.
2. **24/7 Expert Assistance:** Constant support with expert guidance, ensuring seamless operations during SOC shifts.
3. **Instant Playbook Access:** Quickly search and access your playbooks and documents, streamlining the information retrieval process.
4. **Ongoing Internet Research:** Benefit from AI-enabled extensive internet research for comprehensive insights (Note: Internet use is optional and for this feature only).

## About ZySec AI and the Author

<details>
<summary>About ZySec AI and the Author</summary>

### About ZySec AI

ZySec AI leads the charge in integrating **Cyber Security with Artificial Intelligence**. Our vision is to transform how security professionals leverage technology. ZySec AI is more than just a tool; it is a holistic approach to enhancing security operations, merging AI's innovative power with the unique challenges of cybersecurity, while prioritizing privacy.

- [🔗 View Our Road Map](https://github.com/ZySec-AI/ZySec/blob/main/roadmap.md)
- [🔗 Explore the Project on GitHub](https://github.com/ZySec-AI/ZySec.git)
- [🔗 Contact Us](https://docs.google.com/forms/d/e/1FAIpQLSdkqIjQUoUOorsWXVzgQhJ-vbp1OpN1ZI0u3u8fK_o-UxII2w/viewform)

### ZySec 7B Model

**ZySec 7B**, the cornerstone of ZySec AI, is built on HuggingFace's Zephyr language model series. Custom-designed for cybersecurity, it offers an expert level of knowledge and insights. The model is extensively trained across more than 30 unique domains, ensuring its effectiveness and reliability in the cybersecurity field.

- [🔗 Checkout Model on HuggingFace](https://huggingface.co/aihub-app/ZySec-7B-v1)

### About the Author - Venkatesh Siddi

**Venkatesh Siddi** is a notable expert in cybersecurity, integrating **Artificial Intelligence and Machine Learning** into complex security challenges. His expertise extends to big data, cloud security, and innovative technology design.

- [🔗 Connect with Venkatesh on LinkedIn](https://www.linkedin.com/in/venkycs/)

</details>

## Getting Started

### Setting Up the Streamlit Application

1. **Clone the Repository:** Start by cloning the ZySec AI repository from GitHub to your local machine.

Clone the project

```bash
  git clone https://github.com/ZySec-AI/ZySec.git
```
2. **Install Dependencies:** Navigate to the cloned directory and install necessary dependencies using `pip install -r requirements.txt`.

    Go to the project directory

    ```bash
      cd ZySec
    ```
    Make python virtual environment

    ```bash
      python -m venv .
    ```

    Activate virtual environment

    ```bash
      source bin/activate
    ```

    Install dependencies

    ```bash
      pip install -r requirements
    ```
    Install model server

    ```bash
    ./start_model_server.sh
    ```


3. **Launch the App:** Run the app with the command `streamlit run app.py`. This will start the Streamlit server and the application should open in your default web browser.

Start Web UI

```bash
streamlit run app.py
```

4. **Explore the Application:** Interact with the various features of ZySec AI through the Streamlit interface.
5. **Contributing:** For those interested in contributing, please refer to our contact page for more information.

*Note: ZySec AI is designed to operate without internet connectivity, ensuring complete privacy. The only exception is the optional internet research feature.*

## License

ZySec AI is released under the Apache License, Version 2.0 (Apache-2.0), a permissive open-source license. This license allows you to freely use, modify, distribute, and sell your own versions of this work, under the terms of the license.

[🔗 View the Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0)

## Acknowledgements

Special thanks to the HuggingFace and LangChain communities for their inspiration and contributions to the field of AI and cybersecurity. Their pioneering work continues to inspire projects like ZySec AI.
