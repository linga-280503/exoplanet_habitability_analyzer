import math
from typing import Dict, Tuple

SUN_T = 5772.0

# Kopparapu HZ coefficients (S_eff = S_effSun + a*T + b*T^2 + c*T^3 + d*T^4),
# T = Teff - 5780 K; using columns: Moist Greenhouse (inner, i=3) and Maximum Greenhouse (outer, i=4).
# Values consolidated from community copies of the 2013/2014 papers/tools. (See README references.)
COEFF = {
    'moist_inner': {
        'SeffSun': 1.0140,
        'a': 8.1774e-5,
        'b': 1.7063e-9,
        'c': -4.3241e-12,
        'd': -6.6462e-16,
    },
    'max_outer': {
        'SeffSun': 0.3438,
        'a': 5.8942e-5,
        'b': 1.6558e-9,
        'c': -3.0045e-12,
        'd': -5.2983e-16,
    }
}


def hz_flux_bounds(teff: float) -> Tuple[float, float]:
    """Return (S_inner, S_outer) in Earth flux units using Kopparapu parameterization.
    teff in K.
    """
    T = teff - 5780.0
    def poly(p):
        return (p['SeffSun'] + p['a']*T + p['b']*T*T + p['c']*T*T*T + p['d']*T*T*T*T)
    return poly(COEFF['moist_inner']), poly(COEFF['max_outer'])


def estimate_luminosity_Lsun(st_rad: float=None, st_teff: float=None, st_lum: float=None) -> float:
    if st_lum and st_lum>0:
        return st_lum
    if st_rad and st_teff:
        return (st_rad**2) * (st_teff/SUN_T)**4
    return 1.0


def estimate_semi_major_axis_AU(pl_orbsmax: float=None, pl_orbper: float=None, st_mass: float=None) -> float:
    if pl_orbsmax and pl_orbsmax>0:
        return pl_orbsmax
    # Kepler's third law: a(AU) ≈ ( (P/365.25)^2 * Mstar )^(1/3)  (assuming Mp << Mstar)
    if pl_orbper and st_mass:
        return (( (pl_orbper/365.25)**2 * (st_mass) ))**(1/3)
    return None


def insolation_flux(L: float, a: float) -> float:
    if L is None or a is None or a<=0:
        return None
    return L/(a*a)


def equilibrium_temperature_K(L: float, a: float, albedo: float=0.3) -> float:
    # Simple zero-greenhouse approximation with Earth normalization
    if L is None or a is None or a<=0:
        return None
    return 278.5 * (L**0.25) / (a**0.5) * ((1.0 - albedo)**0.25)


def radius_earth(pl_rade: float=None, pl_radj: float=None) -> float:
    if pl_rade and pl_rade>0:
        return pl_rade
    if pl_radj and pl_radj>0:
        return pl_radj * 11.209  # 1 Rjup ~ 11.209 Re
    return None


def stellar_class_penalty(spt: str) -> float:
    # Favor G/K, modest for F, penalty for M due to activity/tidal locking risks (heuristic)
    if not spt:
        return 0.0
    s = spt.strip().upper()
    if s.startswith('G') or s.startswith('K'):
        return 1.0
    if s.startswith('F'):
        return 0.85
    if s.startswith('M'):
        return 0.75
    return 0.9


def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def score_planet(row: Dict) -> Dict:
    # Inputs
    teff = row.get('st_teff')
    a = estimate_semi_major_axis_AU(row.get('pl_orbsmax'), row.get('pl_orbper'), row.get('st_mass'))
    L = estimate_luminosity_Lsun(row.get('st_rad'), row.get('st_teff'), row.get('st_lum'))
    S = insolation_flux(L, a)
    rin = radius_earth(row.get('pl_rade'), row.get('pl_radj'))
    ecc = row.get('pl_orbeccen') or 0.0
    feh = row.get('st_metfe')
    spt = row.get('st_spectype')

    # HZ bounds
    S_inner, S_outer = (None, None)
    if teff:
        S_inner, S_outer = hz_flux_bounds(teff)

    # Scores (weights)
    # 1) Flux proximity (40)
    flux_score = 0.0
    in_hz = None
    if S and S_inner and S_outer:
        in_hz = (S_outer <= S <= S_inner)
        # Linear distance from Earth flux ideal (1.0) within [S_outer, S_inner]
        width = abs(S_inner - S_outer) or 1.0
        flux_score = clamp(100.0 * (1.0 - abs(S-1.0)/max(1e-6, max(abs(S_inner-1.0), abs(1.0-S_outer), 0.5*width))))
    # 2) Size (25): ideal 0.8–1.6 Re
    size_score = 0.0
    if rin:
        if 0.8 <= rin <= 1.6:
            size_score = 100.0
        elif 0.5 <= rin < 0.8:
            size_score = 100.0 * (rin-0.5)/(0.3)
        elif 1.6 < rin <= 2.5:
            size_score = 100.0 * (2.5-rin)/(0.9)
        else:
            size_score = 0.0
    # 3) Eccentricity (10): <=0.2 good, >0.6 bad
    e = abs(ecc or 0.0)
    if e <= 0.2:
        ecc_score = 100.0
    elif e >= 0.6:
        ecc_score = 0.0
    else:
        ecc_score = 100.0 * (0.6 - e) / 0.4
    # 4) Stellar class (10)
    sp_mult = stellar_class_penalty(spt or '')
    stellar_score = 100.0 * sp_mult
    # 5) Teq (10): ideal 240–320 K
    Teq = equilibrium_temperature_K(L, a)
    temp_score = 0.0
    if Teq:
        if 240 <= Teq <= 320:
            temp_score = 100.0
        elif 180 <= Teq < 240:
            temp_score = 100.0 * (Teq-180)/(60)
        elif 320 < Teq <= 380:
            temp_score = 100.0 * (380-Teq)/(60)
        else:
            temp_score = 0.0
    # 6) Metallicity (5): slight boost near solar
    met = feh if feh is not None else 0.0
    if -0.3 <= met <= 0.3:
        met_score = 100.0
    elif -0.7 <= met < -0.3:
        met_score = 100.0 * (met + 0.7)/(0.4)
    elif 0.3 < met <= 0.7:
        met_score = 100.0 * (0.7 - met)/(0.4)
    else:
        met_score = 0.0

    # Weighted sum
    score = (
        0.40*flux_score + 0.25*size_score + 0.10*ecc_score + 0.10*stellar_score + 0.10*temp_score + 0.05*met_score
    )
    score = clamp(score)

    if score >= 70:
        label = 'Likely'
    elif score >= 40:
        label = 'Possible'
    else:
        label = 'Unlikely'

    return {
        'a_AU': a,
        'L_Lsun': L,
        'S_earth': S,
        'S_inner': S_inner,
        'S_outer': S_outer,
        'Teq_K': Teq,
        'radius_Re': rin,
        'score': score,
        'label': label,
        'in_hz': in_hz,
        'subscores': {
            'flux': flux_score,
            'size': size_score,
            'ecc': ecc_score,
            'stellar': stellar_score,
            'temp': temp_score,
            'metallicity': met_score
        }
    }
