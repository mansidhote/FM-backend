import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "PROJECT_NAME": os.getenv("PROJECT_NAME", "Personal Finance Mentor API"),
    "API_VERSION": "/api/v1",
    "GOOGLE_AI_API_KEY": os.getenv("GOOGLE_AI_API_KEY", ""),
}
