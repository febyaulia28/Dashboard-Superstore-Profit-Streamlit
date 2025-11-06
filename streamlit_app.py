import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

#konfigurasi  halaman
st.set_page_config(
    page_title="Dashboard Analisis Penjualan Superstore",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

#load dataset
@st.cache_data
def load_data():
    return pd.read_csv("Sample - Superstore.csv", encoding='latin-1')

#load data penjualan
df_sales = load_data()
df_sales["Order Date"] = pd.to_datetime(df_sales["Order Date"])
df_sales["Ship Date"] = pd.to_datetime(df_sales["Ship Date"])

#sidebar
st.sidebar.title("🔍 Filter Data")

# Range tanggal sesuai data
min_date = df_sales["Order Date"].min()
max_date = df_sales["Order Date"].max()

start_date, end_date = st.sidebar.date_input(
    "Rentang Waktu:",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

kategori = st.sidebar.multiselect(
    "Pilih Kategori Produk:",
    options=df_sales["Category"].unique(),
    default=df_sales["Category"].unique()
)

region = st.sidebar.multiselect(
    "Pilih Wilayah:",
    options=df_sales["Region"].unique(),
    default=df_sales["Region"].unique()
)

#Filter
df_filtered = df_sales[
    (df_sales["Order Date"].between(pd.to_datetime(start_date), pd.to_datetime(end_date))) &
    (df_sales["Category"].isin(kategori)) &
    (df_sales["Region"].isin(region))
].copy()
df_filtered["Bulan"] = df_filtered["Order Date"].dt.to_period("M").astype(str)

# Header
st.title("📊 Dashboard Analisis Profit Superstore")
st.markdown("Analisis performa profit berdasarkan waktu, wilayah, dan kategori produk.")

#KPI
total_sales = df_filtered["Sales"].sum()
total_profit = df_filtered["Profit"].sum()
avg_discount = df_filtered["Discount"].mean()
total_orders = df_filtered["Order ID"].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Penjualan", f"${total_sales:,.0f}")
col2.metric("🏦 Total Profit", f"${total_profit:,.0f}")
col3.metric("🏷️ Rata-rata Diskon", f"{avg_discount*100:.2f}%")
col4.metric("📦 Total Order", f"{total_orders:,}")

st.markdown("---")

#Tren Profit
st.subheader("📈 Tren Profit Bulanan")
monthly_profit = (
    df_filtered.groupby("Bulan")["Profit"]
    .sum()
    .reset_index()
)
fig1 = px.line(
    monthly_profit,
    x="Bulan",
    y="Profit",
    markers=True,
    title="Performa Profit Bulanan",
    template="plotly_white"
)
st.plotly_chart(fig1, use_container_width=True)

#profit per region
col5, col6 = st.columns(2)

with col5:
    st.subheader("🌍 Profit per Wilayah")
    region_profit = (
        df_filtered.groupby("Region")[["Sales", "Profit"]]
        .sum()
        .reset_index()
    )
    fig2 = px.bar(
        region_profit,
        x="Region",
        y="Profit",
        color="Region",
        text_auto=True,
        title="Total Profit per Wilayah",
        template="plotly_white"
    )
    st.plotly_chart(fig2, use_container_width=True)
# sale n profit
with col6:
    st.subheader("💡Sales dan Profit per Wilayah")
    region_perf = (
        df_filtered.groupby("Region")[["Sales", "Profit"]]
        .sum()
        .reset_index()
    )

    fig3 = px.scatter(
        region_perf,
        x="Sales",
        y="Profit",
        color="Region",
        size="Sales",
        hover_data=["Sales", "Profit"],
        title="Hubungan antara Sales dan Profit per Wilayah",
        template="plotly_white"
    )
    st.plotly_chart(fig3, use_container_width=True)

#profit per kategori produk
st.subheader("💼 Profit Berdasarkan Kategori Produk")
category_profit = (
    df_filtered.groupby("Category")[["Sales", "Profit"]]
    .sum()
    .sort_values(by="Profit", ascending=False)
    .reset_index()
)
fig4 = px.bar(
    category_profit,
    x="Category",
    y="Profit",
    color="Category",
    text_auto=True,
    template="plotly_white",
    title="Profit per Kategori Produk"
)
st.plotly_chart(fig4, use_container_width=True)

#Top produk
st.subheader("🏆 10 Produk Paling Menguntungkan")
top_product = (
    df_filtered.groupby("Product Name")["Profit"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)
fig5 = px.bar(
    top_product,
    x="Profit",
    y="Product Name",
    orientation="h",
    color="Profit",
    text_auto=True,
    title="Top 10 Produk Berdasarkan Profit",
    template="plotly_white"
)
st.plotly_chart(fig5, use_container_width=True)