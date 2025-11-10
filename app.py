from flask import Flask, render_template
import monitor_vwap_real as monitor

app = Flask(__name__)

@app.route("/")
def index():
    data = {}
    for asset, records in monitor.prices.items():
        if isinstance(records, list) and records:
            data[asset] = records[-1]  # último preço
        elif isinstance(records, pd.DataFrame):
            data[asset] = records.iloc[-1].to_dict()
        else:
            data[asset] = {"price": None, "time": None}
    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
