from flask import Flask, render_template
from monitor_vwap_real import get_all_data

app = Flask(__name__)

@app.route("/")
def dashboard():
    all_data = get_all_data()
    processed_data = {}
    for name, df in all_data.items():
        if not df.empty:
            processed_data[name] = {
                "last_price": round(df['Close'].iloc[-1], 2),
                "vwap": round(df['VWAP'].iloc[-1], 2)
            }
        else:
            processed_data[name] = {
                "last_price": "N/A",
                "vwap": "N/A"
            }
    return render_template("dashboard.html", data=processed_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
