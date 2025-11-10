# utils/helpers.py
def calc_vwap_from_ohlcv(ohlcv_list):
    if not ohlcv_list:
        return None
    typical = []
    vol = []
    for c in ohlcv_list:
        tp = (c["high"] + c["low"] + c["close"]) / 3.0
        typical.append(tp)
        vol.append(c.get("volume", 0.0))
    total_vol = sum(vol)
    if total_vol == 0:
        return float(typical[-1])
    vwap = sum(tp * v for tp, v in zip(typical, vol)) / total_vol
    return float(vwap)
