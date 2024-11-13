from .constants import instrument_info


def get_instrument_info(instrument: str):
    instrument = instrument[:-4].upper()
    if instrument in instrument_info.keys():
        return instrument_info[instrument]
    return None
