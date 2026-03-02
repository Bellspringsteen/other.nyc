# UWS Data Projects

Two independent analyses of the Upper West Side using NYC open data. Both were researched, coded, and written by Claude (Anthropic).

---

## `water/` — Full Buildings, Missing Families

**Live:** [labsbell.com/uwswater/](http://www.labsbell.com/uwswater/)

Uses NYC Local Law 84 annual water benchmarking data to back-calculate how many people are actually living in UWS buildings. The headline finding: UWS pre-war apartments were built for families of 4–5, but water usage implies most are occupied by couples. Washington Heights — same building vintage, similar unit sizes — has twice the population density per square foot.

**Key numbers:** 17,401 large pre-war UWS units · 40% occupied by couples or fewer · ~29,000 "missing" people vs. Washington Heights density · 1.91 vs. 3.85 people per 1,000 sqft

**Run it:**
```bash
pip install pandas numpy
# Download ll84_2022.csv and pluto.csv (see links below) into water/
python water/analysis.py        # writes water/uws_data.json
# open water/index.html in a browser
```

**Data sources:**
- [LL84 Benchmarking 2022 — NYC Open Data](https://data.cityofnewyork.us/Environment/Energy-and-Water-Data-Disclosure-for-Local-Law-84-/usc3-8zwd) → save as `water/ll84_2022.csv`
- [MapPLUTO — NYC DCP](https://www.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page) → save as `water/pluto.csv` and `water/pluto_brooklyn.csv`

---

## `steam/` — Con Edison Steam Coverage

**Live:** [labsbell.com/uwssteam/](http://www.labsbell.com/uwssteam/)

Maps which Manhattan buildings use Con Edison's district steam system, using the same LL84 dataset. Shows coverage by neighborhood, building era, and size — and where steam heat drops off as you move uptown.

**Run it:**
```bash
pip install pandas numpy
# Reuses water/ll84_2022.csv — copy or symlink it into steam/
python steam/steam_analysis.py  # writes steam/steam_data.json
# open steam/steam.html in a browser
```

---

*Large CSV files are gitignored. The HTML pages embed their output JSON and run fully client-side with no build step.*
