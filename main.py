import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import os
import warnings


warnings.filterwarnings("ignore")


st.set_page_config(page_title="Superstore", page_icon=":bar_chart:", layout="wide")

st.title(":bar_chart: Sample SuperStore EDA")
st.markdown(
    "<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True
)

fl = st.file_uploader(":file_folder: Upload a file", type=(["xlsx", "xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_excel(filename)
else:
    os.chdir(
        "C://Users//emher//Documents//Data Engineer//STREAMLIT//1+Project+Superstore//data"
    )
    df = pd.read_excel("superstore.xls")  # if csv use encoding= "ISO-8859-1"

col1, col2 = st.columns((2))

# Getting min and max date
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

# Time Filter
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# Region Filter
st.sidebar.header("Choose your filter:")
region = st.sidebar.multiselect("Pick your region", df["Region"].unique())
df2 = df[df["Region"].isin(region)] if region else df.copy()

# State Filter
state = st.sidebar.multiselect("Pick your state", df2["State"].unique())
df3 = df2[df2["State"].isin(state)] if state else df2.copy()

# City Filter
city = st.sidebar.multiselect("Pick your city", df3["City"].unique())

# Apply Filters
filtered_df = df3
if city:
    filtered_df = filtered_df[filtered_df["City"].isin(city)]
elif state:
    filtered_df = filtered_df[filtered_df["State"].isin(state)]
elif region:
    filtered_df = filtered_df[filtered_df["Region"].isin(region)]

# Grouping and ploting by category
category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(
        category_df,
        x="Category",
        y="Sales",
        text=["${:,.2f}".format(x) for x in category_df["Sales"]],
        template="seaborn",
    )
    st.plotly_chart(fig, use_container_width=True, height=200)

# Ploting by Region
with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text=filtered_df["Region"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# Downloading data from graphics
with col1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Data",
            data=csv,
            file_name="Category.csv",
            mime="text/csv",
            help="Click here to download data as csv.",
        )

with col2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Greens"))
        csv = region.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Data",
            data=csv,
            file_name="Region.csv",
            mime="text/csv",
            help="Click here to download data as csv.",
        )

# Time series Analisys
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader("Time Series Analysis")
linechart = pd.DataFrame(
    filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y:%b"))["Sales"]
    .sum()
    .reset_index()
)
fig2 = px.line(
    linechart,
    x="month_year",
    y="Sales",
    labels={"Sales": "Amount"},
    height=500,
    width=1000,
    template="gridon",
)
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Time Series Data"):
    st.write(linechart.style.background_gradient(cmap="Oranges"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Data",
        data=csv,
        file_name="TimeSeries.csv",
        mime="text/csv",
        help="Click here to download data as csv.",
    )

# Create Tree Map based on Region, Category and SubCategory
st.subheader("hierarchical view of Sales using Treemap")
fig3 = px.treemap(
    filtered_df,
    path=["Region", "Category", "Sub-Category"],
    values="Sales",
    hover_data=["Sales"],
    color="Sub-Category",
)
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Segment wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader("Category wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

# Ading Expander Tables
st.subheader(":point_right: Month wise sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region", "State", "City", "Category"]]
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_cateogry_year = pd.pivot_table(
        data=filtered_df, values="Sales", index=["Sub-Category"], columns="month"
    )
    st.write(sub_cateogry_year.style.background_gradient(cmap="Blues"))

# Creating a Scatter Plot
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1["layout"].update(
    title="Relationship between Sales and Profits",
    titlefont=dict(size=20),
    xaxis=dict(title="Sales", titlefont=dict(size=19)),
    yaxis=dict(title="Profit", titlefont=dict(size=19)),
)
st.plotly_chart(data1, use_container_width=True)

# View the data
with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

# Download original Dataset
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
            "Download Data",
            data=csv,
            file_name="Data.csv",
            mime="text/csv",
            help="Click here to download data as csv.",
        )