from market_specs import get_info as _ms_get_info


def get_instrument_info(instrument: str):
    if len(instrument) == 8:
        type_ = get_asset_type(instrument)
        tick_size = 0.01 if type_ == "STOCK" else 0.001
        digits = 2 if type_ == "STOCK" else 3
        return {"tick_size": tick_size, "hands": 100, "digits": digits}
    return _ms_get_info(instrument)


def get_asset_type(instrument: str):
    if instrument.startswith("sh") or instrument.startswith("sz"):
        code = instrument[2:]
        if code.startswith("0") or code.startswith("3") or code.startswith("6"):
            return "STOCK"
        else:
            return "ETF"
    else:
        return "FUTURE"
