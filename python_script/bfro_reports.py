import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="Bigfoot Sightings", layout="wide")

URL = "https://raw.githubusercontent.com/UIUC-iSchool-DataViz/is445_data/main/bfro_reports_fall2022.csv"

@st.cache_data
def load():
    df = pd.read_csv(URL, usecols=["state", "county", "season", "title", "latitude", "longitude", "date", "number", "classification", "temperature_high", "humidity"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    return df

df = load()

st.title("Bigfoot Sightings in North America")
st.caption("Data: Bigfoot Field Researchers Organization (BFRO) Reports via UIUC IS445 DataViz")

st.header("Visualization 1: Map of Bigfoot Sightings Reports in North America")

geo = df.dropna(subset=["latitude", "longitude", "year"])
geo = geo[(geo.longitude < -60) & (geo.latitude > 15)]

c1, c2 = st.columns(2)
yr_min, yr_max = int(geo.year.min()), int(geo.year.max())
years = c1.slider("Year Range", yr_min, yr_max, (1990, yr_max))
classes = c2.multiselect("Report Classification", sorted(geo.classification.unique()), default=["Class A"])

sub = geo[geo.year.between(*years) & geo.classification.isin(classes)]

states = alt.topo_feature("https://cdn.jsdelivr.net/npm/vega-datasets@2/data/us-10m.json", "states")
base = alt.Chart(states).mark_geoshape(fill="#f0f0f0", stroke="white").project("albersUsa")

points = alt.Chart(sub).mark_circle(size=25, opacity=0.6).encode(
    longitude="longitude:Q",
    latitude="latitude:Q",
    color=alt.Color(
        "classification:N", title="Class", scale=alt.Scale(
            domain=["Class A", "Class B", "Class C"],
            range=["#d95f02", "#1b9e77", "#7570b3"]
        )
    ),
    tooltip=["title:N", "state:N", "county:N", "date:T", "classification:N"],
).project(
    "albersUsa"
)

st.altair_chart((base + points).properties(width=800, height=450), use_container_width=True)
st.write(f"Showing {len(sub):,} reports.")
st.write("For this visualization I'm highlighting where there are Bigfoot sightings in North America, as well as the report's classification. " \
"There's a slider where the viewer can slide to look at specific years or time periods of Bigfoot sightings in North America. " \
"There's also a multiselect option where the audience can choose to look at specific classes, a pairing of classes, or all the classes at once. " \
"For the map I used a geographic point map with an Albers USA projection as it preserves the true land area across the US and minimizes distortion for mid-latitude regions that stretch east-to-west. " \
"Each point is a reported sighting of Bigfoot with an opacity of 0.6 and a circle shape, so that overlapping reports in denser regions will still show up rather than being hidden. " \
"Color for this plot encodes the BFRO's classification for each report, either Class, A, B, or C. It uses a categorical palette as the classes are distinct, unordered labels. " \
"The year slider and classification multiselect allows the viewer to select for what year(s) and classification they want to look at. " \
"The tooltip displays the title of the report, the state it was reported in, the county, the date, and the classification of the report when hovering over a point. " \
"If I had more time, I would like to change the visualization to allow the viewer to click a state and see the reports in more detail. " /
"As well as opting for color choices that would help people with color deficiencies to view the points better, and include Alaska and Canada in the visualization as right now they're left out.")

st.header("Visualization 2: When Sightings Are Reported")

by_month = (df.dropna(subset=["month"]).query("season != 'Unknown'").groupby(["month", "season"]).size().reset_index(name="reports"))
month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
by_month["month_name"] = by_month["month"].astype(int).map(lambda m: month_names[m-1])

sel = alt.selection_point(fields=["season"], bind="legend")
chart2 = alt.Chart(by_month).mark_bar().encode(
    x=alt.X("month_name:N", sort=month_names, title="Month"),
    y=alt.Y("reports:Q", title="Number of reports"),
    color=alt.Color(
        "season:N", 
        title="Season (click to filter)", 
        scale=alt.Scale(
            domain=["Winter", "Spring", "Summer", "Fall"], 
            range=["#4c78a8","#54a24b","#f58518","#b279a2"])),
    opacity=alt.condition(sel, alt.value(1), alt.value(0.15)),
    tooltip=["month_name:N", "season:N", "reports:Q"],
).add_params(sel).properties(height=400)
st.altair_chart(chart2, use_container_width=True)
st.write("For this visualization I'm highlighting when Bigfoot sightings occur, sorted by season and broken down by month. " \
"The viewer can see the breakdown of reports for each season. The main purpose of this visualization is to see during which seasons the majority of Bigfoot sightings get reported. " \
"I used a stacked bar chart that has month on the x-axis in calendar order and the number of reports on the y-axis. Color encodes each season using intuitive hues, so winter is blue, spring is green, summer is orange, and fall is purple. " \
"There's a binded legend off to the right of the stacked bar chart for the seasons, so by selecting a season it highlights that particular season for each month and fades the others so viewers can isolate one season to look at. " \
"The tooltip displays the month name, season, and number of reports when hovering over a particular season for a month. " \
"If I had more time, I would like to change this visualization so that I can explore more in depth about why peaks in reports happen in certain seasons. For example, Summer and Fall have more reports than the other two seasons. " \
"However, the reason for the increase in reports could be due to more people hiking and spending time outdoors rather than an increase in Bigfoot activity. I would also do another view by state visualization so that viewers can compare seasonal patterns of reports across different regions.")