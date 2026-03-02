"""
Con Edison Steam System — UWS Coverage Analysis
Uses LL84 Energy Benchmarking data (which includes district steam consumption)
plus PLUTO for the total building universe.
"""

import re
import json
import numpy as np
import pandas as pd

# ─── 1. Load LL84, isolate steam customers ───────────────────────────────────

ll84 = pd.read_csv("ll84_2022.csv", low_memory=False)

ll84["steam_kbtu"] = pd.to_numeric(ll84["District Steam Use (kBtu)"], errors="coerce")
ll84["zip"]        = ll84["Postcode"].astype(str).str[:5].str.zfill(5)

steam = ll84[ll84["steam_kbtu"] > 0].copy()
mhtn  = steam[(steam["Borough"] == "MANHATTAN") | (steam["City"] == "Manhattan")].copy()

print(f"Total LL84 rows:           {len(ll84):,}")
print(f"District-steam users:      {len(steam):,}")
print(f"  — Manhattan:             {len(mhtn):,}")

# ─── 2. Neighborhood mapping ─────────────────────────────────────────────────

NEIGHBORHOOD_ZIPS = {
    "Upper West Side":        ["10023", "10024", "10025"],
    "Upper East Side":        ["10021", "10028", "10065", "10075", "10128"],
    "Midtown West / 34-59":   ["10019", "10036", "10018", "10023"],   # 10023 counted in UWS
    "Midtown East / 34-59":   ["10022", "10017", "10167", "10168", "10169", "10170", "10171", "10177"],
    "Chelsea / Hell's Kitchen":["10001", "10011"],
    "Flatiron / Gramercy":    ["10010", "10016"],
    "Murray Hill":            ["10016", "10017"],
    "Financial District":     ["10004", "10005", "10006", "10007", "10038", "10041", "10280", "10281"],
    "Tribeca / SoHo":         ["10013", "10012", "10014"],
    "East Village / LES":     ["10003", "10009", "10002"],
    "Upper Manhattan (96th+)":["10026", "10027", "10030", "10031", "10037", "10039",
                               "10032", "10033", "10034", "10035", "10040"],
}

# Build flat reverse lookup (first match wins, so order matters)
ZIP_TO_HOOD = {}
for hood, zips in NEIGHBORHOOD_ZIPS.items():
    for z in zips:
        if z not in ZIP_TO_HOOD:
            ZIP_TO_HOOD[z] = hood

mhtn["neighborhood"] = mhtn["zip"].map(ZIP_TO_HOOD).fillna("Other Manhattan")

# ─── 3. Count steam buildings & usage by neighborhood ────────────────────────

by_hood = (
    mhtn.groupby("neighborhood")
    .agg(
        steam_buildings  = ("zip", "count"),
        total_steam_kbtu = ("steam_kbtu", "sum"),
        median_steam_kbtu= ("steam_kbtu", "median"),
    )
    .reset_index()
    .sort_values("steam_buildings", ascending=False)
)

print("\nSteam buildings by neighborhood:")
print(by_hood.to_string(index=False))

# ─── 4. PLUTO — building universe ────────────────────────────────────────────

pluto = pd.read_csv("pluto.csv", low_memory=False,
                    usecols=["bbl", "zipcode", "unitsres", "bldgclass",
                              "bldgarea", "yearbuilt", "ownername"])
pluto["zip"]      = pluto["zipcode"].astype(str).str[:5].str.zfill(5)
pluto["bldgarea"] = pd.to_numeric(pluto["bldgarea"], errors="coerce")
pluto["unitsres"] = pd.to_numeric(pluto["unitsres"], errors="coerce").fillna(0)

# Large buildings (LL84 threshold is 25,000 sq ft)
large_mhtn = pluto[
    (pluto["zip"].str.startswith("10")) &
    (pluto["bldgarea"] >= 25_000)
].copy()
large_mhtn["neighborhood"] = large_mhtn["zip"].map(ZIP_TO_HOOD).fillna("Other Manhattan")

large_by_hood = (
    large_mhtn.groupby("neighborhood")
    .agg(
        large_buildings      = ("bbl", "count"),
        large_res_buildings  = ("bbl", lambda x: (large_mhtn.loc[x.index, "unitsres"] > 0).sum()),
        total_res_units      = ("unitsres", "sum"),
    )
    .reset_index()
)

summary = by_hood.merge(large_by_hood, on="neighborhood", how="outer").fillna(0)
summary["adoption_pct"] = (
    summary["steam_buildings"] / summary["large_buildings"] * 100
).clip(0, 200).round(1)

summary = summary.sort_values("steam_buildings", ascending=False)
print("\nSummary with adoption rates:")
print(summary[["neighborhood","steam_buildings","large_buildings","adoption_pct"]].to_string(index=False))

# ─── 5. UWS deep-dive: extract street numbers ────────────────────────────────

uws = mhtn[mhtn["neighborhood"] == "Upper West Side"].copy()

def extract_cross_street(address):
    """
    Pull the cross-street number from addresses like:
      '100 W 72ND ST', '65 W 90 STREET', '100 West 92nd Street'
    Returns None for pure avenue addresses (Amsterdam Ave, Broadway, etc.)
    """
    if pd.isna(address):
        return None
    a = str(address).upper()
    # 'W 72' / 'WEST 72' with optional ordinal suffix
    m = re.search(r'\bW(?:EST)?\s+(\d+)(?:ST|ND|RD|TH)?\b', a)
    if m:
        n = int(m.group(1))
        if 59 <= n <= 110:
            return n
    # Standalone ordinal: '72ND', '90TH' etc.
    m = re.search(r'\b(\d{2,3})(?:ST|ND|RD|TH)\b', a)
    if m:
        n = int(m.group(1))
        if 59 <= n <= 110:
            return n
    return None

uws["cross_street"] = uws["Address 1"].apply(extract_cross_street)

def street_band(n):
    if pd.isna(n): return "Unknown"
    n = int(n)
    if   n < 65: return "59th–64th St"
    elif n < 70: return "65th–69th St"
    elif n < 75: return "70th–74th St"
    elif n < 80: return "75th–79th St"
    elif n < 85: return "80th–84th St"
    elif n < 90: return "85th–89th St"
    elif n < 96: return "90th–95th St"
    else:        return "96th+ St"

uws["street_band"] = uws["cross_street"].apply(street_band)

band_order = ["59th–64th St","65th–69th St","70th–74th St","75th–79th St",
              "80th–84th St","85th–89th St","90th–95th St","96th+ St","Unknown"]
uws_by_band = (
    uws.groupby("street_band")
    .agg(steam_buildings=("zip","count"), total_steam_kbtu=("steam_kbtu","sum"))
    .reindex(band_order)
    .fillna(0)
    .reset_index()
)
uws_by_band["steam_buildings"] = uws_by_band["steam_buildings"].astype(int)

print("\nUWS steam buildings by 5-block band:")
print(uws_by_band.to_string(index=False))

# ─── 6. Building-type breakdown ──────────────────────────────────────────────

prop_type_col = "Primary Property Type - Self Selected"

mhtn["building_category"] = mhtn[prop_type_col].apply(
    lambda x: (
        "Multifamily Residential"  if "Multifamily" in str(x) else
        "College / University"     if "College" in str(x) else
        "Hotel"                    if "Hotel" in str(x) else
        "Office"                   if "Office" in str(x) else
        "Hospital / Healthcare"    if "Hospital" in str(x) or "Health" in str(x) else
        "K-12 School"              if "K-12" in str(x) else
        "Cultural / Performing"    if "Museum" in str(x) or "Performing" in str(x) or "Cultural" in str(x) else
        "Other / Mixed"
    )
)

type_by_hood = (
    mhtn.groupby(["neighborhood", "building_category"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

# UWS-specific type breakdown
uws_types = uws[prop_type_col].value_counts().to_dict()
print("\nUWS building types using steam:")
for t, n in uws_types.items():
    print(f"  {t}: {n}")

# ─── 7. UWS steam usage vs boiler fuel ───────────────────────────────────────
# From LL84: how many UWS large buildings use oil vs gas vs steam
all_large_uws = ll84[
    ll84["Postcode"].astype(str).str[:5].str.zfill(5).isin(["10023","10024","10025"])
].copy()
all_large_uws["steam_kbtu"] = pd.to_numeric(all_large_uws["District Steam Use (kBtu)"], errors="coerce").fillna(0)
all_large_uws["gas_kbtu"]   = pd.to_numeric(all_large_uws["Natural Gas Use (kBtu)"], errors="coerce").fillna(0)
all_large_uws["oil2_kbtu"]  = pd.to_numeric(all_large_uws["Fuel Oil #2 Use (kBtu)"], errors="coerce").fillna(0)
all_large_uws["oil4_kbtu"]  = pd.to_numeric(all_large_uws["Fuel Oil #4 Use (kBtu)"], errors="coerce").fillna(0)
all_large_uws["oil_kbtu"]   = all_large_uws["oil2_kbtu"] + all_large_uws["oil4_kbtu"]

def heat_source(row):
    s = row["steam_kbtu"]
    g = row["gas_kbtu"]
    o = row["oil_kbtu"]
    total = s + g + o
    if total == 0:
        return "No Data"
    shares = {"Steam": s, "Natural Gas": g, "Fuel Oil": o}
    primary = max(shares, key=shares.get)
    if shares[primary] / total < 0.5:
        return "Mixed"
    return primary

all_large_uws["primary_heat"] = all_large_uws.apply(heat_source, axis=1)
heat_breakdown = all_large_uws["primary_heat"].value_counts().to_dict()
print("\nUWS large building heat sources (LL84):")
for k, v in heat_breakdown.items():
    print(f"  {k}: {v}")

# ─── 8. Individual UWS steam buildings for the lookup table ──────────────────

uws_export = uws[[
    "Property Name", "Address 1", "zip", "cross_street", "street_band",
    prop_type_col, "steam_kbtu", "Year Built",
    "Property GFA - Calculated (Buildings) (ft²)"
]].copy()
uws_export.columns = [
    "name", "address", "zip", "cross_street", "street_band",
    "property_type", "steam_kbtu", "year_built", "gfa_sqft"
]
uws_export["steam_mmbtu"] = (uws_export["steam_kbtu"] / 1000).round(0)
uws_export["cross_street"] = uws_export["cross_street"].apply(
    lambda x: int(x) if pd.notna(x) else None
)
uws_export = uws_export.sort_values("address")

# ─── 9. Export JSON ──────────────────────────────────────────────────────────

def clean(obj):
    """Convert numpy types to native Python."""
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return None if np.isnan(obj) else float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, float) and np.isnan(obj):
        return None
    return obj

results = clean({
    "meta": {
        "data_source": "LL84 Energy & Water Benchmarking 2022 (NYC Open Data)",
        "pluto_source": "PLUTO 23v3 (NYC DCP)",
        "note": "District steam customers identified from LL84 'District Steam Use (kBtu)' > 0",
        "steam_network_west_terminus": "96th Street",
        "steam_network_east_terminus": "89th Street",
        "total_pipe_miles": 105,
        "system_started": 1882,
    },
    "total_manhattan_steam_buildings": int(len(mhtn)),
    "total_steam_buildings_all_boroughs": int(len(steam)),
    "by_neighborhood": summary.to_dict(orient="records"),
    "uws": {
        "total_steam_buildings": int(len(uws)),
        "by_zip": {
            "10023": int((uws["zip"] == "10023").sum()),
            "10024": int((uws["zip"] == "10024").sum()),
            "10025": int((uws["zip"] == "10025").sum()),
        },
        "by_street_band": uws_by_band.to_dict(orient="records"),
        "property_types": {str(k): int(v) for k, v in uws_types.items()},
        "heat_sources_all_large_bldgs": {str(k): int(v) for k, v in heat_breakdown.items()},
        "buildings": uws_export.to_dict(orient="records"),
    },
    "type_by_neighborhood": mhtn.groupby(["neighborhood","building_category"]).size().reset_index(name="n").to_dict(orient="records"),
})

with open("steam_data.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nDone. Wrote steam_data.json")
print(f"  Manhattan steam buildings: {len(mhtn)}")
print(f"  UWS steam buildings:       {len(uws)}")
