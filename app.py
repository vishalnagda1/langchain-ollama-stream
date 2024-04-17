from dotenv import load_dotenv
from flask import Flask

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Import your routes
from src.modules.index import *  # noqa: F403, E402

if __name__ == "__main__":
    app.run(port=app.config.get("PORT"))
