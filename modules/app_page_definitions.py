#app_page_definitions.py
PAGE_CONFIG = {
    "nav_private_ai": {
        "title": "Cyber Security AI",
        "caption": "🔐 Engage with AI for cybersecurity insights and solutions.",
        "greeting": "Hello! I'm ZySec, your AI assistant in Cyber Security.",
        "system_role": "You are ZySec, an AI Assistant specialized in Cyber Security, developed by the ZySec.AI team to provide expert insights and solutions in cybersecurity.",
        "persistent_db": "./workspace/db/cybersecurity_chroma_db"
    },
    "nav_standards": {
        "title": "Explore Industry Standards",
        "caption": "🔍 Discover and learn about various industry standards. Upload documents to get insights.",
        "greeting": "Welcome to the Standards Exploration! Upload documents for analysis and easy retrieval.",
        "system_role": "You are ZySec, functioning as a Standards Assistant. Your expertise lies in assisting users with understanding and navigating various standards, particularly in cybersecurity.",
        "persistent_db": "./workspace/db/standards_chroma_db"
    },
    "nav_playbooks": {
        "title": "Playbook Analysis",
        "caption": "📘 Dive into your playbooks. Upload and analyze them for detailed insights.",
        "greeting": "Ready to analyze your playbook? Start by uploading your document.",
        "system_role": "You are ZySec, an AI Assistant designed to extract specific answers and insights from playbooks and documents, aiding users in navigating through complex information.",
        "persistent_db": "./workspace/db/playbooks_chroma_db"
    },
    "nav_researcher": {
        "title": "AI Research Assistant",
        "caption": "🔬 Utilize AI for deep research and information gathering.",
        "greeting": "Hello! I'm ZySec, your AI assistant here to assist you with comprehensive research.",
        "system_role": "You are ZySec, acting as a Research Assistant. Your task is to assist users with comprehensive research support, offering information and insights for various queries.",
        "persistent_db": "./workspace/db/researcher_chroma_db"
    },
    "nav_summarize": {
        "title": "Content Summarization",
        "caption": "📝 Get concise summaries of extensive content.",
        "greeting": "Hello! I'm ZySec, your AI assistant specialized in content summarization.",
        "system_role": "You are ZySec, an AI Assistant specialized in content summarization. Your role is to efficiently condense English content, providing clear and concise summaries.",
        "persistent_db": "./workspace/db/summarization_chroma_db"
    },
    "nav_explore_ai": {
        "title": "Explore AI",
        "caption": "🤖 Embark on a journey through the world of AI. Learn, interact, and experiment.",
        "greeting": "Welcome to AI Exploration! Begin your journey into AI learning and application.",
        "persistent_db": "./workspace/db/explore_ai_chroma_db"
    },
        "default": {
        "title": "Playbook Analysis",
        "caption": "📘 Dive into your playbooks. Upload and analyze them for detailed insights.",
        "greeting": "Ready to analyze your playbook? Start by uploading your document.",
        "system_role": "You are ZySec, an AI Assistant designed to extract specific answers and insights from playbooks and documents, aiding users in navigating through complex information.",
        "persistent_db": "./workspace/db/playbooks_chroma_db"
    },
    # Add other pages as needed
}
