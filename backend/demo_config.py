# Demo configuration - defines notebooks and PDF files for demo setup

DEMO_USER = {
    "username": "demo",
    "password": "demo123",
    "email": "demo@policybot.local",
    "full_name": "Demo User",
}

DEMO_NOTEBOOKS = [
    {
        "notebook_id": "responsible_ai",
        "title": "Responsible AI",
        "description": "Developer guides and ethical AI frameworks",
        "pdfs": [
            "the-developer's-playbook-for-responsible-ai-in-india.pdf",
            "TN_Safe_Ethical_AI_policy_2020.pdf",
        ],
    },
    {
        "notebook_id": "tec_standards",
        "title": "TEC Standards",
        "description": "Technical standards and fairness assessment guidelines",
        "pdfs": [
            "TEC Standard for fairness assessment and rating of AI systems Final v5 2023_07_04.pdf",
        ],
    },
]

DEMO_PDF_DIR = "/app/demo_pdfs"
