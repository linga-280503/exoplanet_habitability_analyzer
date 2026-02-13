import pandas as pd
import math

COLMAP = {
    'name':'name',
    'pl_name':'name',
    'pl_rade':'pl_rade',
    'pl_radj':'pl_radj',
    'pl_orbsmax':'pl_orbsmax',
    'pl_orbper':'pl_orbper',
    'pl_orbeccen':'pl_orbeccen',
    'st_teff':'st_teff',
    'st_rad':'st_rad',
    'st_lum':'st_lum',
    'st_mass':'st_mass',
    'st_metfe':'st_metfe',
    'st_spectype':'st_spectype',
    'ra':'ra','ra_deg':'ra',
    'dec':'dec','dec_deg':'dec',
}

NEEDED = ['name','st_teff']


def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # normalize columns
    cols = {c: c.strip().lower() for c in df.columns}
    df.rename(columns=cols, inplace=True)
    out = {}
    for c in df.columns:
        key = COLMAP.get(c)
        if key:
            out[c] = key
    df.rename(columns=out, inplace=True)
    # ensure required columns exist
    for k in ['name','st_teff']:
        if k not in df.columns:
            df[k] = None
    return df
