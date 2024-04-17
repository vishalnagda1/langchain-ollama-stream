import json
import os

from dotenv import load_dotenv
from flask import Flask, Response, request, stream_with_context
from langchain_community.llms import Ollama

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://0.0.0.0:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")

llm = Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)


def generate_tokens(question):
    for chunks in llm.stream(question):
        yield chunks


@app.route("/users/chat", methods=["POST"])
def ask_ai():
    def generate_json(question):
        with app.app_context():  # Ensure we're within the application context
            full_content = ""
            for token in generate_tokens(question):
                full_content += token
                json_data = {"model": OLLAMA_MODEL, "content": token, "done": False}
                json_str = json.dumps(json_data)  # Convert JSON data to a string
                json_bytes = json_str.encode("utf-8")  # Encode JSON string to bytes
                yield json_bytes
                yield b"\n"  # Yield newline as bytes

            # Once streaming is finished, yield one last JSON object with "done" set to True
            json_data = {
                "model": OLLAMA_MODEL,
                "full_content": full_content,
                "done": True,
            }
            json_str = json.dumps(json_data)  # Convert JSON data to a string
            json_bytes = json_str.encode("utf-8")  # Encode JSON string to bytes
            yield json_bytes

    request_data = request.json
    question = request_data.get("question")
    return Response(
        stream_with_context(generate_json(question)), mimetype="application/json"
    )


if __name__ == "__main__":
    app.run(debug=True)
