# ZySec: Private Security Co-Pilot

Welcome to ZySec AI, where artificial intelligence meets cybersecurity. Project ZySec, powered by the innovative ZySec 7B model, is reshaping the cybersecurity landscape with AI-driven solutions.

# [🔗 View Demo](https://huggingface.co/spaces/ZySec-AI/ZySec)

## Key Features

1. **AI-Driven Cybersecurity:** Experience the full potential of the ZySec 7B model, a specialized AI tool for cybersecurity.
2. **24/7 Expert Assistance:** Constant support with expert guidance, ensuring seamless operations during SOC shifts.
3. **Playbook Access:** Quickly search and access your playbooks and documents, streamlining the information retrieval process.
4. **Standards Explorer:** Quickly search and access various standards, like a expert well-versed with any standards.
5. **Ongoing Internet Research:** Benefit from AI-enabled extensive internet research for comprehensive insights (Note: Internet use is optional and for this feature only).

### About ZySec AI

ZySec AI leads the charge in integrating **Cyber Security with Artificial Intelligence**. Our vision is to transform how security professionals leverage technology. ZySec AI is more than just a tool; it is a holistic approach to enhancing security operations, merging AI's innovative power with the unique challenges of cybersecurity, while prioritizing privacy.

- [🔗 View Our Road Map](https://github.com/ZySec-AI/ZySec/blob/main/roadmap.md)
- [🔗 Explore the Project on GitHub](https://github.com/ZySec-AI/ZySec.git)
- [🔗 Contact Us](https://docs.google.com/forms/d/e/1FAIpQLSdkqIjQUoUOorsWXVzgQhJ-vbp1OpN1ZI0u3u8fK_o-UxII2w/viewform)

*Note: ZySec AI is designed to operate without internet connectivity, ensuring complete privacy. The only exception is the optional internet research feature.*

### ZySec 7B Model

**ZySec 7B**, the cornerstone of ZySec AI, is built on HuggingFace's Zephyr language model series. Custom-designed for cybersecurity, it offers an expert level of knowledge and insights. The model is extensively trained across more than 30 unique domains, ensuring its effectiveness and reliability in the cybersecurity field.

- [🔗 Checkout Model on HuggingFace](https://huggingface.co/aihub-app/ZySec-7B-v1)

## Deployment Options

You have the flexibility to run the ZySec AI application either locally on your computer or remotely on a GPU instance, depending on your preferences and resource availability.

- **Local Deployment:** Suitable for development, testing, or light usage. Follow the instructions in the previous sections to set up and run the application on your local machine.

- **Remote Deployment on a GPU Instance:** For better performance, especially when handling larger workloads or requiring faster processing, consider deploying on a GPU instance. Use the VLLM (Very Large Language Model) deployment mode for optimal performance in a GPU environment.

  Here is the model that can be deployed on a GPU instance for enhanced performance: [ZySec-7B-v1 on Hugging Face](https://huggingface.co/aihub-app/ZySec-7B-v1). This model is specifically optimized for GPU-based deployments and offers significant performance improvements over CPU-based setups.

### Notes

- Ensure that the remote GPU instance has the necessary hardware requirements and software dependencies installed.
- Adjust the deployment scripts (`start_web_ui.sh` and `start_model_server.sh`) as needed to suit the remote environment, particularly for handling GPU resources.
- Test the application thoroughly in the GPU environment to ensure stability and performance meet your expectations.


## Getting Started

### Setting Up the Streamlit Application

1. **Clone the Repository:** Start by cloning the ZySec AI repository from GitHub to your local machine.

   Clone the project

      ```bash
      git clone https://github.com/ZySec-AI/ZySec.git

2. **Install Dependencies and Run the Web UI:** Navigate to the cloned directory, set the script as executable, and run it to start the Streamlit application.

      ```bash
      cd ZySec
      chmod +x start_web_ui.sh
      ./start_web_ui.sh

3. **Starting the Model Server**: Before running the model server, ensure that the llama-cpp-server is installed. You can install it using pip:
      ```bash
      pip3 install 'llama-cpp-python[server]'
      chmod +x start_model_server.sh
      ./start_model_server.sh

***You can run locally on the same computer or remotely on GPU instance depending on your preferences. For better performance use VLLM deployment mode in GPU instance.***

4. **Explore the Application:** Interact with the various features of ZySec AI through the Streamlit interface.
5. **Contributing:** For those interested in contributing, please refer to our contact page for more information.

## About ZySec AI and the Author

<details>
<summary>About Project ZySec AI</summary>

## License

ZySec AI is released under the Apache License, Version 2.0 (Apache-2.0), a permissive open-source license. This license allows you to freely use, modify, distribute, and sell your own versions of this work, under the terms of the license.

[🔗 View the Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0)

## Acknowledgements

Special thanks to the HuggingFace and LangChain communities for their inspiration and contributions to the field of AI. Their pioneering work continues to inspire projects like ZySec AI.

### About the Author - Venkatesh Siddi

**Venkatesh Siddi** is a notable expert in cybersecurity, integrating **Artificial Intelligence and Machine Learning** into complex security challenges. His expertise extends to big data, cloud security, and innovative technology design.

- [🔗 Connect with Venkatesh on LinkedIn](https://www.linkedin.com/in/venkycs/)

</details>
