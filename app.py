from flask import Flask, jsonify, request
from supabase import create_client, Client
import os
import pandas as pd
import numpy as np

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "Sistema funcionando em Python 3.13.4"})

@app.route("/data", methods=["POST"])
def process_data():
    data = request.json
    df = pd.DataFrame(data)
    df["sum"] = df.select_dtypes(include=[np.number]).sum(axis=1)
    return df.to_json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
