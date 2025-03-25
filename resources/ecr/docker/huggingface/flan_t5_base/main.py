import os

from flask import Flask, request
from model import TextGenerationLLM

app = Flask(__name__)
llm = TextGenerationLLM(os.environ["MNT_DIR"])


@app.route("/predict", methods=["POST"])
def predict():
    prompt = request.data
    response = llm.predict(prompt)
    return response


if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0", debug=True)
