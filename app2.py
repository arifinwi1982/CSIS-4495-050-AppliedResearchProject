import streamlit as st
import pandas as pd
import s3fs
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime
from io import StringIO
import boto3
import s3fs

# Function to load data from S3
def load_data_from_s3(bucket_name, folder_name, file_pattern):
    fs = s3fs.S3FileSystem(anon=False)
    path = f'{bucket_name}/{folder_name}'
    files = fs.ls(path)
    csv_files = [f for f in files if file_pattern in f]
    df_list = []
    for file in csv_files:
        with fs.open(file) as f:
            df_list.append(pd.read_csv(f, encoding='ISO-8859-1'))
    df = pd.concat(df_list, ignore_index=True)
    return df

def perform_arima_forecast(df, sku, store_column, N=5):
    forecasts = {}
    df_sku = df[df['product_sku'] == sku].copy()
    df_sku['current_date'] = pd.to_datetime(df_sku['current_date'], errors='coerce')
    df_sku.set_index('current_date', inplace=True)
    df_sku.sort_values('current_date', inplace=True)

    df_sku_filtered = df_sku.dropna(subset=[store_column])
    if len(df_sku_filtered) > 2:
        stock_series = df_sku_filtered[store_column]
        model = ARIMA(stock_series, order=(1, 1, 1))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=N)
        forecasts[store_column] = forecast
    else:
        forecasts[store_column] = None
    return forecasts


def main():
    st.title('Streamlit App with S3 Data and ARIMA Forecasting')

    # Navigation
    page = st.sidebar.selectbox("Choose a page", ["Home", "ARIMA Forecast"])

    if page == "Home":
        # Display the home page with the DataFrame
        bucket_name = 'csis4495'
        folder_name = 'weekly_artificial_plants'
        file_pattern = 'weekly_products_artificial_plants_'
        df = load_data_from_s3(bucket_name, folder_name, file_pattern)
        if not df.empty:
            st.write(df)
        else:
            st.write("No data found.")
    elif page == "ARIMA Forecast":
        st.write("ARIMA Forecast Results")
        
        if 'df' not in st.session_state:
            st.warning("Please load data from the 'Home' page first.")
            return

        # User inputs for SKU, product name, and store selection
        sku_options = st.session_state.df['product_sku'].unique()
        selected_sku = st.selectbox('Select Product SKU:', sku_options)
        
        # Optionally, if product names are distinct and informative
        if 'product_name' in st.session_state.df.columns:
            df_filtered_by_sku = st.session_state.df[st.session_state.df['product_sku'] == selected_sku]
            product_names = df_filtered_by_sku['product_name'].unique()
            selected_product_name = st.selectbox('Select Product Name:', product_names)

        store_columns = [col for col in st.session_state.df.columns if 'stock_number' in col]
        selected_store = st.selectbox('Select Store Column:', store_columns)
        
        N = st.slider('Select number of periods to forecast:', min_value=3, max_value=10, value=5)
        
        if st.button("Forecast"):
            forecasts = perform_arima_forecast(st.session_state.df, selected_sku, selected_store, N=N)
            forecast = forecasts[selected_store]
            if forecast is not None:
                st.markdown(f"**Forecast for {selected_store}**")
                st.line_chart(forecast)
            else:
                st.markdown(f"**{selected_store}** - Insufficient data for forecasting.")

if __name__ == "__main__":
    st.session_state.df = load_data_from_s3('csis4495', 'weekly_artificial_plants', 'weekly_products_artificial_plants_')  # Preload data, adjust as necessary
    main()
