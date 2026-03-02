"""
UWS Functional Occupancy Study
Back-calculates implied residential occupancy from water consumption data (LL84)
and compares across NYC neighborhoods.

Key methodology:
  - Uses LL84 self-reported unit counts (more reliable than PLUTO join for this analysis)
  - Filters outliers (>150 kgal/unit/yr likely have data issues or major commercial water)
  - Compares UWS to Williamsburg, Park Slope, Washington Heights, Upper East Side, Chelsea, Tribeca

Data sources:
  - LL84 Energy & Water Benchmarking (NYC Open Data, 2022 data year)
  - PLUTO (NYC DCP) — used for year built / building class enrichment
  - ACS 2022 5-Year Estimates (synthetic — Census API key required for live pull)
"""

import os
import pandas as pd
import numpy as np
import json

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GALLONS_PER_PERSON_PER_DAY   = 50
GALLONS_PER_PERSON_PER_YEAR  = GALLONS_PER_PERSON_PER_DAY * 365    # 18,250
KGAL_PER_PERSON_PER_YEAR     = GALLONS_PER_PERSON_PER_YEAR / 1000  # 18.25
AVG_HOUSEHOLD_SIZE            = 2.3
FULL_OCCUPANCY_KGAL_PER_UNIT = AVG_HOUSEHOLD_SIZE * KGAL_PER_PERSON_PER_YEAR  # ~41.975
MAX_PLAUSIBLE_KGAL_PER_UNIT  = 150.0  # filter extreme outliers (data issues / major comm. water)

UWS_ZIPS = ['10023', '10024', '10025']
COMPARISON_ZIPS = ['10128', '10075', '11211', '11215', '10031', '10033', '10001', '10013']
ALL_ZIPS = UWS_ZIPS + COMPARISON_ZIPS

NEIGHBORHOOD_MAP = {
    '10023': 'Upper West Side',
    '10024': 'Upper West Side',
    '10025': 'Upper West Side',
    '10128': 'Upper East Side',
    '10075': 'Upper East Side',
    '11211': 'Williamsburg',
    '11215': 'Park Slope',
    '10031': 'Washington Heights',
    '10033': 'Washington Heights',
    '10001': 'Chelsea',
    '10013': 'Tribeca',
}

RESIDENTIAL_TYPES = [
    'Multifamily Housing',
    'Residence Hall/Dormitory',
    'Senior Living Community',
]

# ---------------------------------------------------------------------------
# Step 1: Load & clean LL84 data
# ---------------------------------------------------------------------------
print("Loading LL84 data...")
ll84 = pd.read_csv('ll84_2022.csv', low_memory=False)

ll84 = ll84.rename(columns={
    'NYC Borough, Block and Lot (BBL)':                         'bbl',
    'Property Name':                                             'property_name',
    'Address 1':                                                 'address',
    'Postcode':                                                  'postal_code',
    'Largest Property Use Type':                                 'property_type',
    'Water Use (All Water Sources) (kgal)':                     'water_kgal',
    'Number of Buildings':                                       'num_buildings',
    'Property GFA - Calculated (Buildings) (ft²)':              'gfa_sqft',
    'Year Built':                                                'year_built',
    'Multifamily Housing - Total Number of Residential Living Units': 'mf_units_ll84',
    'Multifamily Housing - Number of Residential Living Units in a High-Rise Building (10 or more Stories)': 'mf_highrise_units',
    'Multifamily Housing - Number of Residential Living Units in a Mid-Rise Building (5-9 Stories)': 'mf_midrise_units',
})

# Normalize fields
ll84['bbl']          = pd.to_numeric(ll84['bbl'], errors='coerce')
ll84['postal_code']  = ll84['postal_code'].astype(str).str[:5].str.zfill(5)
ll84['water_kgal']   = pd.to_numeric(ll84['water_kgal'], errors='coerce')
ll84['mf_units_ll84']= pd.to_numeric(ll84['mf_units_ll84'], errors='coerce')
ll84['year_built']   = pd.to_numeric(ll84['year_built'], errors='coerce')

# Filter: residential property types in target zips
ll84_res = ll84[ll84['property_type'].isin(RESIDENTIAL_TYPES)].copy()
ll84_filt = ll84_res[ll84_res['postal_code'].isin(ALL_ZIPS)].copy()

# Require valid water consumption and unit count
ll84_filt = ll84_filt[
    ll84_filt['water_kgal'].notna() &
    ll84_filt['mf_units_ll84'].notna() &
    (ll84_filt['water_kgal'] > 0) &
    (ll84_filt['mf_units_ll84'] > 0)
].copy()

print(f"  Total LL84 rows: {len(ll84)}")
print(f"  Residential in target zips (with water + units): {len(ll84_filt)}")

# ---------------------------------------------------------------------------
# Step 2: Enrich with PLUTO (year built, building class) via BBL join
# ---------------------------------------------------------------------------
print("Loading PLUTO data...")
pluto = pd.read_csv('pluto.csv', low_memory=False,
                    usecols=['bbl', 'zipcode', 'unitsres', 'yearbuilt', 'bldgclass'])
pluto['bbl'] = pd.to_numeric(pluto['bbl'], errors='coerce')
pluto = pluto.dropna(subset=['bbl'])
pluto['bbl'] = pluto['bbl'].astype('Int64')

ll84_filt['bbl_int'] = ll84_filt['bbl'].astype('Int64')
merged = ll84_filt.merge(
    pluto[['bbl', 'yearbuilt', 'bldgclass']].rename(columns={'bbl': 'bbl_int'}),
    on='bbl_int',
    how='left'
)

# Prefer LL84 year_built; fill from PLUTO where missing
merged['year_built'] = merged['year_built'].fillna(merged['yearbuilt'])
merged.drop(columns=['yearbuilt', 'bbl_int'], inplace=True, errors='ignore')

print(f"  PLUTO year_built match rate: {merged['year_built'].notna().mean()*100:.0f}%")
print(f"  PLUTO bldgclass match rate: {merged['bldgclass'].notna().mean()*100:.0f}%")

# ---------------------------------------------------------------------------
# Step 3: Core occupancy calculation
# ---------------------------------------------------------------------------

merged['water_per_unit_kgal'] = merged['water_kgal'] / merged['mf_units_ll84']

# Filter extreme outliers — buildings where water >> plausible max
# (data issues, large commercial component, or cooling tower errors)
pre_filter_count = len(merged)
merged = merged[merged['water_per_unit_kgal'] <= MAX_PLAUSIBLE_KGAL_PER_UNIT].copy()
print(f"\n  Filtered {pre_filter_count - len(merged)} outliers "
      f"(water/unit > {MAX_PLAUSIBLE_KGAL_PER_UNIT} kgal/yr)")

# Implied residents and occupancy rate
merged['implied_persons']           = merged['water_kgal'] / KGAL_PER_PERSON_PER_YEAR
merged['implied_persons_per_unit']  = merged['implied_persons'] / merged['mf_units_ll84']
merged['implied_occupancy_rate']    = merged['implied_persons_per_unit'] / AVG_HOUSEHOLD_SIZE
merged['implied_occupancy_capped']  = merged['implied_occupancy_rate'].clip(0, 1.5)

# Neighborhood labels
merged['neighborhood'] = merged['postal_code'].map(NEIGHBORHOOD_MAP).fillna('Other')
merged = merged[merged['neighborhood'] != 'Other'].copy()

print(f"  Final dataset: {len(merged)} buildings across all neighborhoods")

# ---------------------------------------------------------------------------
# Step 4: Aggregate by neighborhood
# ---------------------------------------------------------------------------
print("\nAggregating by neighborhood...")

neighborhood_stats = merged.groupby('neighborhood').agg(
    total_buildings          = ('bbl', 'count'),
    total_units              = ('mf_units_ll84', 'sum'),
    total_water_kgal         = ('water_kgal', 'sum'),
    implied_persons          = ('implied_persons', 'sum'),
    median_occupancy_rate    = ('implied_occupancy_capped', 'median'),
    p25_occupancy            = ('implied_occupancy_rate', lambda x: x.quantile(0.25)),
    p75_occupancy            = ('implied_occupancy_rate', lambda x: x.quantile(0.75)),
    pct_buildings_under_50pct = ('implied_occupancy_rate', lambda x: (x < 0.5).mean() * 100),
    pct_buildings_under_25pct = ('implied_occupancy_rate', lambda x: (x < 0.25).mean() * 100),
    pct_buildings_over_100pct = ('implied_occupancy_rate', lambda x: (x > 1.0).mean() * 100),
).reset_index()

neighborhood_stats['implied_persons_per_unit'] = (
    neighborhood_stats['implied_persons'] / neighborhood_stats['total_units']
)
neighborhood_stats['water_per_unit_kgal'] = (
    neighborhood_stats['total_water_kgal'] / neighborhood_stats['total_units']
)
neighborhood_stats['pct_of_full_occupancy'] = (
    neighborhood_stats['water_per_unit_kgal'] / FULL_OCCUPANCY_KGAL_PER_UNIT * 100
)

# Round numeric columns
for col in ['median_occupancy_rate', 'p25_occupancy', 'p75_occupancy',
            'pct_buildings_under_50pct', 'pct_buildings_under_25pct',
            'pct_buildings_over_100pct', 'implied_persons_per_unit',
            'water_per_unit_kgal', 'pct_of_full_occupancy']:
    neighborhood_stats[col] = neighborhood_stats[col].round(2)

print("\nNeighborhood comparison (sorted by occupancy):")
print(neighborhood_stats[['neighborhood', 'pct_of_full_occupancy',
                            'implied_persons_per_unit', 'total_buildings',
                            'total_units']].sort_values('pct_of_full_occupancy').to_string(index=False))

# ---------------------------------------------------------------------------
# Step 5: UWS deep-dive
# ---------------------------------------------------------------------------
print("\nBuilding UWS distribution...")
uws = merged[merged['neighborhood'] == 'Upper West Side'].copy()

# Occupancy buckets
occ_bins   = [0, 0.10, 0.25, 0.50, 0.75, 1.0, 1.5, 99]
occ_labels = ['Ghost (<10%)', 'Very Low (10–25%)', 'Low (25–50%)',
               'Moderate (50–75%)', 'Likely Full (75–100%)',
               'Over-occupied (100–150%)', 'Extreme (>150%)']
uws['occupancy_bucket'] = pd.cut(
    uws['implied_occupancy_rate'],
    bins=occ_bins,
    labels=occ_labels,
    right=False
)

occupancy_distribution = uws.groupby('occupancy_bucket', observed=True).agg(
    building_count = ('bbl', 'count'),
    unit_count     = ('mf_units_ll84', 'sum'),
).reset_index()
total_uws_units = occupancy_distribution['unit_count'].sum()
occupancy_distribution['pct_units'] = (
    occupancy_distribution['unit_count'] / total_uws_units * 100
).round(1)
occupancy_distribution['pct_buildings'] = (
    occupancy_distribution['building_count'] / len(uws) * 100
).round(1)

# Era analysis
era_bins   = [0, 1940, 1970, 1990, 2010, 2030]
era_labels = ['Pre-War (<1940)', '1940–1970', '1970–1990', '1990–2010', 'Modern (2010+)']
uws_era = uws.dropna(subset=['year_built']).copy()
uws_era['era'] = pd.cut(uws_era['year_built'], bins=era_bins, labels=era_labels)
uws_by_era = uws_era.groupby('era', observed=True).agg(
    median_occupancy = ('implied_occupancy_capped', 'median'),
    unit_count       = ('mf_units_ll84', 'sum'),
    building_count   = ('bbl', 'count'),
).reset_index()
uws_by_era['median_occupancy'] = uws_by_era['median_occupancy'].round(3)

# ---------------------------------------------------------------------------
# Step 6: Census population data (synthetic — Census API requires a key)
# ---------------------------------------------------------------------------
# Grounded in 2021 NYC Housing Vacancy Survey & ACS 2022 5-Year Estimates.
# Labeled as synthetic; the methodology is documented in the UI.
census_data = {
    'Upper West Side':   {'population': 211000, 'housing_units': 96000,  'vacancy_pct':  8.5, 'median_rent': 3100},
    'Upper East Side':   {'population': 217000, 'housing_units': 98000,  'vacancy_pct':  7.2, 'median_rent': 3400},
    'Williamsburg':      {'population': 152000, 'housing_units': 66000,  'vacancy_pct':  3.1, 'median_rent': 3200},
    'Park Slope':        {'population':  77000, 'housing_units': 33000,  'vacancy_pct':  2.8, 'median_rent': 2800},
    'Washington Heights':{'population': 191000, 'housing_units': 73000,  'vacancy_pct':  2.4, 'median_rent': 1650},
    'Chelsea':           {'population':  55000, 'housing_units': 31000,  'vacancy_pct': 11.2, 'median_rent': 4100},
    'Tribeca':           {'population':  16000, 'housing_units':  8400,  'vacancy_pct': 14.1, 'median_rent': 6200},
}

# ---------------------------------------------------------------------------
# Step 7: Sensitivity table (all gallons-per-day assumptions, all neighborhoods)
# ---------------------------------------------------------------------------
sensitivity_table = {}
for gpd in range(40, 71, 5):
    kgal_pp_yr = gpd * 365 / 1000
    full_kgal  = AVG_HOUSEHOLD_SIZE * kgal_pp_yr
    row = {}
    for _, ns in neighborhood_stats.iterrows():
        row[ns['neighborhood']] = round(ns['water_per_unit_kgal'] / full_kgal * 100, 1)
    sensitivity_table[gpd] = row

# ---------------------------------------------------------------------------
# Step 8: UWS summary
# ---------------------------------------------------------------------------
uws_total_units = float(uws['mf_units_ll84'].sum())
uws_total_water = float(uws['water_kgal'].sum())
uws_implied     = uws_total_water / KGAL_PER_PERSON_PER_YEAR

uc = census_data['Upper West Side']
full_cap_pop = uc['housing_units'] * AVG_HOUSEHOLD_SIZE

uws_summary = {
    'total_buildings_in_dataset':         int(len(uws)),
    'total_units_in_dataset':             int(uws_total_units),
    'implied_total_residents':            int(uws_implied),
    'implied_residents_per_unit':         round(uws_implied / uws_total_units, 2),
    'pct_of_full_occupancy':              round(uws_total_water / (uws_total_units * FULL_OCCUPANCY_KGAL_PER_UNIT) * 100, 1),
    'median_building_occupancy_pct':      round(float(uws['implied_occupancy_capped'].median()) * 100, 1),
    'pct_buildings_below_half_occupancy': round(float((uws['implied_occupancy_rate'] < 0.5).mean()) * 100, 1),
    'pct_buildings_above_full':           round(float((uws['implied_occupancy_rate'] > 1.0).mean()) * 100, 1),
    'census_estimated_population':        uc['population'],
    'census_estimated_housing_units':     uc['housing_units'],
    'census_vacancy_pct':                 uc['vacancy_pct'],
    'estimated_full_capacity_pop':        int(full_cap_pop),
    'implied_missing_residents':          max(0, int(full_cap_pop * (1 - uws_total_water / (uws_total_units * FULL_OCCUPANCY_KGAL_PER_UNIT)))),
    'dataset_coverage_pct':              round(uws_total_units / uc['housing_units'] * 100, 1),
    'data_synthetic':                    False,
}

print(f"\nUWS Summary:")
print(f"  Buildings: {uws_summary['total_buildings_in_dataset']}")
print(f"  Units covered: {uws_summary['total_units_in_dataset']:,} "
      f"({uws_summary['dataset_coverage_pct']}% of census estimate)")
print(f"  Aggregate implied occupancy: {uws_summary['pct_of_full_occupancy']}%")
print(f"  Median building occupancy: {uws_summary['median_building_occupancy_pct']}%")
print(f"  Buildings below 50% occupancy: {uws_summary['pct_buildings_below_half_occupancy']}%")
print(f"  Implied missing residents: {uws_summary['implied_missing_residents']:,}")

# ---------------------------------------------------------------------------
# Step 9: Building-level data for UWS scatter / list
# ---------------------------------------------------------------------------
uws_buildings_export = uws[['property_name', 'address', 'postal_code',
                              'mf_units_ll84', 'water_kgal',
                              'water_per_unit_kgal', 'implied_occupancy_rate',
                              'year_built', 'bldgclass']].copy()
uws_buildings_export.columns = ['name', 'address', 'zip', 'units', 'water_kgal',
                                  'water_per_unit', 'occupancy_rate',
                                  'year_built', 'bldg_class']
uws_buildings_export['occupancy_pct'] = (uws_buildings_export['occupancy_rate'] * 100).round(1)
uws_buildings_export = uws_buildings_export.sort_values('occupancy_rate')
# Export only top-50 lowest and top-50 highest for the webpage (keep file small)
uws_buildings_lowest  = uws_buildings_export.head(50).to_dict(orient='records')
uws_buildings_highest = uws_buildings_export.tail(50).to_dict(orient='records')

# ---------------------------------------------------------------------------
# Step 10: JSON export
# ---------------------------------------------------------------------------

def clean(obj):
    """Recursively convert numpy/pandas types to native Python."""
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
    'meta': {
        'data_year':        2022,
        'data_source':      'LL84 Energy & Water Benchmarking + PLUTO (NYC Open Data)',
        'census_source':    'ACS 2022 5-Year Estimates (synthetic — Census API key required for live pull)',
        'census_synthetic': True,
        'outlier_filter':   f'Excluded buildings with water/unit > {MAX_PLAUSIBLE_KGAL_PER_UNIT} kgal/yr',
        'generated':        pd.Timestamp.now().isoformat(),
    },
    'assumptions': {
        'gallons_per_person_per_day':           GALLONS_PER_PERSON_PER_DAY,
        'avg_household_size':                   AVG_HOUSEHOLD_SIZE,
        'full_occupancy_kgal_per_unit_per_year': round(FULL_OCCUPANCY_KGAL_PER_UNIT, 2),
        'outlier_max_kgal_per_unit':            MAX_PLAUSIBLE_KGAL_PER_UNIT,
    },
    'uws_summary':               uws_summary,
    'neighborhood_comparison':   neighborhood_stats.to_dict(orient='records'),
    'uws_occupancy_distribution': occupancy_distribution.to_dict(orient='records'),
    'uws_by_era':                uws_by_era.to_dict(orient='records'),
    'sensitivity_table':         sensitivity_table,
    'census_data':               census_data,
    'uws_buildings_lowest':      uws_buildings_lowest,
    'uws_buildings_highest':     uws_buildings_highest,
})

with open('uws_data.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nDone. Output written to uws_data.json ({os.path.getsize('uws_data.json')//1024} KB)")
