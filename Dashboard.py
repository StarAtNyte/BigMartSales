import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')
import plotly.graph_objects as go

st.set_page_config(page_title="BigMart!!!", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: Bigmart Sales Data")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename)
else:
    df = pd.read_csv("train_preprocessed.csv")
    st.write("train_preprocessed.csv")

col1, col2 = st.columns((2))

df["Outlet_Establishment_Year"] = df["Outlet_Establishment_Year"].astype(int)

start_year = df["Outlet_Establishment_Year"].min()
end_year = df["Outlet_Establishment_Year"].max()


with col1:
    start_year_selected = st.number_input("Start Year (Outlet Establishment)", min_value=start_year, max_value=end_year, value=start_year)

with col2:
    end_year_selected = st.number_input("End Year (Outlet Establishment)", min_value=start_year, max_value=end_year, value=end_year)

df = df[(df["Outlet_Establishment_Year"] >= start_year_selected) & (df["Outlet_Establishment_Year"] <= end_year_selected)].copy()

# Sidebar filter
st.sidebar.header("Choose your filter: ")

filter_type = st.sidebar.radio("Select a filter type:", ["Outlet Type", "Outlet Size", "Outlet Location Type"])

if filter_type == "Outlet Type":
    outlet_type = st.sidebar.multiselect("Pick your Outlet Type", df["Outlet_Type"].unique())
    if not outlet_type:
        filtered_df = df
    else:
        filtered_df = df[df["Outlet_Type"].isin(outlet_type)]
elif filter_type == "Outlet Size":
    outlet_size = st.sidebar.multiselect("Pick your Outlet Size", df["Outlet_Size"].unique())
    if not outlet_size:
        filtered_df = df
    else:
        filtered_df = df[df["Outlet_Size"].isin(outlet_size)]
elif filter_type == "Outlet Location Type":
    outlet_location_type = st.sidebar.multiselect("Pick your Outlet Location Type", df["Outlet_Location_Type"].unique())
    if not outlet_location_type:
        filtered_df = df
    else:
        filtered_df = df[df["Outlet_Location_Type"].isin(outlet_location_type)]



# Category wise sales
category_df = filtered_df.groupby("Item_Category", as_index=False)["Item_Outlet_Sales"].sum()

# Outlet Type wise sales
outlet_type_df = filtered_df.groupby("Outlet_Type", as_index=False)["Item_Outlet_Sales"].sum()

# Plot Category wise Sales
with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Item_Category", y="Item_Outlet_Sales", text=['${:,.2f}'.format(x) for x in category_df["Item_Outlet_Sales"]],
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height=200)

# Plot Outlet Type wise Sales
with col2:
    st.subheader("Outlet Type wise Sales")
    fig = px.pie(outlet_type_df, values="Item_Outlet_Sales", names="Outlet_Type", hole=0.5)
    fig.update_traces(text=outlet_type_df["Outlet_Type"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns((2))

# Display Category View Data
with cl1:
    with st.expander("Category_ViewData"):
        st.write(df.style.background_gradient(cmap="Blues"))
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv",
                        help='Click here to download the data as a CSV file')

# Display Outlet Type View Data
with cl2:
    with st.expander("OutletType_ViewData"):
        st.write(outlet_type_df.style.background_gradient(cmap="Oranges"))
        csv = outlet_type_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="OutletType.csv", mime="text/csv",
                        help='Click here to download the data as a CSV file')





#Added Later
col3, col4 = st.columns((2))

with col3:
    fig2 = px.histogram(filtered_df, x="Item_Outlet_Sales", title="Histogram of Item Outlet Sales")
    st.plotly_chart(fig2, use_container_width=True)

with col4:
    fig3 = px.pie(filtered_df, names="Item_Category", title="Pie Chart of Item Categories")
    st.plotly_chart(fig3, use_container_width=True)



col5, col6 = st.columns((2))


with col5:
    
    fig = px.bar(filtered_df, x = "Item_Type", y = "Item_Outlet_Sales", 
                  title = "Total Sales by Item Type", hover_data=["Item_Outlet_Sales"],
                  template="gridon",height=500)
    st.plotly_chart(fig,use_container_width=True)



col7, col8 = st.columns((2))
cl7, cl8 = st.columns((2))

with col7:
    expander = st.expander("Outlet Size vs Sales")
    data = filtered_df[["Outlet_Size","Item_Outlet_Sales"]].groupby(by="Outlet_Size")["Item_Outlet_Sales"].sum()
    expander.write(data)
with cl7:
    st.download_button("Get Data", data = data.to_csv().encode("utf-8"),
                       file_name="SizeSales.csv", mime="text/csv")


result = filtered_df.groupby(by = filtered_df["Item_Category"])["Item_Outlet_Sales"].sum().reset_index()

with col6:
    fig1 = px.line(result, x = "Item_Category", y = "Item_Outlet_Sales", title="Total Sales By Item Category",
                   template="gridon")
    st.plotly_chart(fig1,use_container_width=True)


with col8:
    expander = st.expander("Sales By Item Category")
    data = result
    expander.write(data)

with cl8:
    st.download_button("Get Data", data = result.to_csv().encode("utf-8"),
                       file_name="ItemSales.csv", mime="text/csv")
    
st.divider()


# Group by Outlet_Type and calculate total sales and total units sold
result1 = filtered_df.groupby(by="Outlet_Type").agg({'Item_Outlet_Sales': 'sum', 'Item_Identifier': 'count'}).reset_index()
result1.columns = ['Outlet_Type', 'TotalSales', 'UnitsSold']

# Create the plot
fig3 = go.Figure()
fig3.add_trace(go.Bar(x=result1["Outlet_Type"], y=result1["TotalSales"], name="Total Sales"))
fig3.add_trace(go.Scatter(x=result1["Outlet_Type"], y=result1["UnitsSold"], mode="lines",
                          name="Units Sold", yaxis="y2"))

# Update layout
fig3.update_layout(
    title="Total Sales and Units Sold by Outlet Type",
    xaxis=dict(title="Outlet Type"),
    yaxis=dict(title="Total Sales", showgrid=False),
    yaxis2=dict(title="Units Sold", overlaying="y", side="right"),
    template="gridon",
    legend=dict(x=1, y=1.1)
)

# Display the plo

st.plotly_chart(fig3, use_container_width=True)

expander = st.expander("View Data for Sales by Units Sold")
expander.write(result1)
st.download_button("Get Data", data = result1.to_csv().encode("utf-8"), 
                       file_name = "Sales_by_UnitsSold.csv", mime="text/csv")
st.divider()



result2 = filtered_df.groupby(by=["Item_Weight", "Item_MRP"]).agg({'Item_Outlet_Sales': 'sum'}).reset_index()

# Create a scatter plot
fig4 = px.scatter(result2, x="Item_Weight", y="Item_MRP", size="Item_Outlet_Sales", color="Item_Outlet_Sales",
                  hover_name="Item_Outlet_Sales", size_max=50,
                  labels={"Item_Outlet_Sales": "Total Sales", "Item_Weight": "Item Weight", "Item_MRP": "Item MRP"})

# Update layout
fig4.update_layout(
    title="Total Sales by Item Weight and Item MRP",
    xaxis_title="Item Weight",
    yaxis_title="Item MRP",
    coloraxis_colorbar=dict(title="Total Sales"),
    template="gridon"
)

# Plot the scatter plot

st.subheader("Total Sales by Item Weight and Item MRP (Scatter Plot)")
st.plotly_chart(fig4, use_container_width=True)

st.divider()

cl9, cl10  = st.columns((2))

with cl9:
    result2 = filtered_df[["Item_Weight","Item_MRP","Item_Outlet_Sales"]].groupby(by=["Item_Weight","Item_MRP"])["Item_Outlet_Sales"].sum()
    expander = st.expander("View data for Total Sales by Item Weight and Item MRP")
    expander.write(result2)
    st.download_button("Get Data", data = result2.to_csv().encode("utf-8"),
                                        file_name="Sales_by_WeightandMRP.csv", mime="text.csv")


with cl10:
    expander = st.expander("View Sales Raw Data")
    expander.write(filtered_df)
    st.download_button("Get Raw Data", data = filtered_df.to_csv().encode("utf-8"),
                       file_name = "SalesRawData.csv", mime="text/csv")
st.divider()

