import logging

logger = logging.getLogger(__name__)

PM25_BREAKPOINTS = [
    (  0,  50,   0.0,  15.4, "Good"),
    ( 51, 100,  15.5,  40.4, "Moderate"),
    (101, 150,  40.5,  65.4, "Unhealthy for Sensitive Groups"),
    (151, 200,  65.5, 150.4, "Unhealthy"),
    (201, 300, 150.5, 250.4, "Very Unhealthy"),
    (301, 400, 250.5, 350.4, "Acutely Unhealthy"),
    (401, 500, 350.5, 500.4, "Emergency"),
]

PM10_BREAKPOINTS = [
    (  0,  50,   0,  54, "Good"),
    ( 51, 100,  55, 154, "Moderate"),
    (101, 150, 155, 254, "Unhealthy for Sensitive Groups"),
    (151, 200, 255, 354, "Unhealthy"),
    (201, 300, 355, 424, "Very Unhealthy"),
    (301, 400, 425, 504, "Acutely Unhealthy"),
    (401, 500, 505, 604, "Emergency"),
]

def _find_breakpoint(concentration: float, table: list) -> tuple | None:
    """
    Search the breakpoint table for the band that the given
    concentration falls into.

    Returns the matching (PSI_lo, PSI_hi, C_lo, C_hi, category)
    tuple, or None if the concentration is out of range.
    """
    for entry in table:
        psi_lo, psi_hi, c_lo, c_hi, category = entry
        if c_lo <= concentration <= c_hi:
            return entry
    return None

def _interpolate(concentration: float, table: list, pollutant_name: str) -> tuple[int, str] | tuple[None, None]:
    """
    Apply the PSI linear interpolation formula for one pollutant.

    PSI = [(PSI_hi - PSI_lo) / (C_hi - C_lo)] × (C_p - C_lo) + PSI_lo

    Returns (psi_score: int, category: str), or (None, None)
    if the concentration is outside all defined breakpoint bands.
    """
    entry = _find_breakpoint(concentration, table)

    if entry is None:
        logger.warning(
            "%s concentration %.2f µg/m³ is outside all breakpoint bands — "
            "cannot compute PSI sub-index",
            pollutant_name,
            concentration,
        )
        return None, None

    psi_lo, psi_hi, c_lo, c_hi, category = entry

    # Linear interpolation
    psi = ((psi_hi - psi_lo) / (c_hi - c_lo)) * (concentration - c_lo) + psi_lo

    return round(psi), category

def compute_aqi(pm25: float, pm10: float) -> dict:
    """
    Compute the overall AQI from PM2.5 and PM10 readings.

    The overall AQI is defined as the MAXIMUM sub-index across
    all pollutants — the worst pollutant drives the final score.

    Args:
        pm25:  PM2.5 concentration in µg/m³ (24-hr average)
        pm10:  PM10  concentration in µg/m³ (24-hr average)

    Returns a dict with the following keys:
        aqi          – final AQI score (int)
        category     – health category string of the dominant pollutant
        dominant     – which pollutant produced the highest sub-index
        psi_pm25     – individual PSI sub-index for PM2.5
        psi_pm10     – individual PSI sub-index for PM10
    """
    psi_pm25, cat_pm25 = _interpolate(pm25, PM25_BREAKPOINTS, "PM2.5")
    psi_pm10, cat_pm10 = _interpolate(pm10, PM10_BREAKPOINTS, "PM10")

    sub_indices = []
    if psi_pm25 is not None:
        sub_indices.append(("PM2.5", psi_pm25, cat_pm25))
    if psi_pm10 is not None:
        sub_indices.append(("PM10",  psi_pm10, cat_pm10))
    if not sub_indices:
        # Both pollutants were out of range — return a safe fallback
        logger.error(
            "Could not compute AQI: both PM2.5 (%.2f) and PM10 (%.2f) "
            "are outside breakpoint tables",
            pm25, pm10,
        )
        return {
            "aqi":      None,
            "category": "Unknown",
            "dominant": None,
            "psi_pm25": None,
            "psi_pm10": None,
        }
    
    dominant_name, overall_aqi, overall_category = max(sub_indices, key=lambda x: x[1])

    logger.debug(
        "PSI — PM2.5: %s  PM10: %s  →  Overall AQI: %d (%s)  [driven by %s]",
        psi_pm25, psi_pm10, overall_aqi, overall_category, dominant_name,
    )

    return {
        "aqi":      overall_aqi,
        "category": overall_category,
        "dominant": dominant_name,
        "psi_pm25": psi_pm25,
        "psi_pm10": psi_pm10,
    }

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format="%(levelname)s — %(message)s")

    result = compute_aqi(pm25=48.2, pm10=112)

    print("\n── AQI Computation Result ──────────────────")
    print(f"  PSI (PM2.5)  : {result['psi_pm25']}")
    print(f"  PSI (PM10)   : {result['psi_pm10']}")
    print(f"  Overall AQI  : {result['aqi']}")
    print(f"  Category     : {result['category']}")
    print(f"  Driven by    : {result['dominant']}")
    print("────────────────────────────────────────────\n")
