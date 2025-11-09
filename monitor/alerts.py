def check_threshold(df, threshold=101):
    alerts = []
    for idx, row in df.iterrows():
        if row["price"] > threshold:
            alerts.append({"index": idx, "price": row["price"], "alert": "Price above threshold"})
    return alerts
