import streamlit as st
import pandas as pd
import s3fs
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np
import seaborn as sns
import matplotlib.dates as mdates
import os
from scipy.stats import t

def load_data(bucket_name, folder_name, file_pattern):
    fs = s3fs.S3FileSystem(anon=False, key='AKIAZQ3DRYKPRAOKVOVY', secret='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')
    path = f'{bucket_name}/{folder_name}'
    files = fs.ls(path)
    csv_files = [f for f in files if file_pattern in f]
    df_list = []
    for file in csv_files:
        with fs.open(f'{file}') as f:
            df_list.append(pd.read_csv(f, encoding='ISO-8859-1'))
    return pd.concat(df_list, ignore_index=True)




def preprocess_data(df, product_type):
    df['product_type'] = product_type
    df['product_sku'] = df['product_sku'].astype(str).str.replace(',', '')
    df['stock_number_BC'] = df['stock_number_coquitlam'] + df['stock_number_richmond']
    df['stock_number_QC'] = df['stock_number_quebec'] + df['stock_number_boucherville'] + df['stock_number_montreal']
    df['stock_number_NS'] = df['stock_number_halifax']
    df['stock_number_ON'] = df['stock_number_ottawa'] + df['stock_number_nyork'] + df['stock_number_etobicoke'] + df['stock_number_vaughan'] + df['stock_number_burlington']
    df['stock_number_MB'] = df['stock_number_winnipeg']
    df['stock_number_AB'] = df['stock_number_edmonton'] + df['stock_number_calgary']
    return df

def data_analysis_page(bucket_name, artificial_folder, artificial_pattern, real_folder, real_pattern):
    st.title('Artificial and Real Plant Data Analysis in IKEA Stores')
    st.subheader('Artificial Plants Data')
    df_artificial = load_data(bucket_name, artificial_folder, artificial_pattern)
    df_artificial = preprocess_data(df_artificial, 'artificial')

    # Create a dropdown menu for selecting a store
    stock_columns = [col for col in df_artificial.columns if col.startswith('stock_number_')]
    store_options = [col.replace('stock_number_', '') for col in stock_columns]
    selected_store = st.selectbox('Select a store:', store_options)

    # Get the latest date for each product
    latest_dates = df_artificial.groupby('product_sku')['current_date'].max().reset_index()

    # Merge to get the latest stock number for each product
    latest_data = pd.merge(df_artificial, latest_dates, on=['product_sku', 'current_date'])

    # Display the latest date in the subheader
    latest_date = latest_data['current_date'].max()
    st.subheader(f'Latest Stock Numbers : {latest_date}')

    # Display the latest stock number for the selected store
    display_columns = ['product_sku', 'product_name', 'product_size', f'stock_number_{selected_store}']
    st.write(latest_data[display_columns])
    st.write('')
    st.subheader('Real Plants Data')
    df_real = load_data(bucket_name, real_folder, real_pattern)
    df_real = preprocess_data(df_real, 'real')
    df_real = df_real[
    df_real['product_name'].str.contains('potted plant', case=False) &
    ~df_real['product_name'].str.contains('artificial', case=False) &
    ~df_real['product_name'].str.contains('Artifi', case=False)
    ]
    
    df_real['current_date'] = pd.to_datetime(df_real['current_date'], format='%Y-%m-%d', errors='coerce')


    stock_columns = [col for col in df_real.columns if col.startswith('stock_number_')]
    store_options = [col.replace('stock_number_', '') for col in stock_columns]
    selected_store = st.selectbox('Select a store:', store_options)

    # Get the latest date for each product
    latest_dates = df_real.groupby('product_sku')['current_date'].max().reset_index()

    # Merge to get the latest stock number for each product
    latest_data = pd.merge(df_real, latest_dates, on=['product_sku', 'current_date'])

    # Display the latest date in the subheader
    latest_date = latest_data['current_date'].max().strftime('%Y-%m-%d')
    st.subheader(f'Latest Stock Numbers : {latest_date}')

    # Display the latest stock number for the selected store
    display_columns = ['product_sku', 'product_name', 'product_size', f'stock_number_{selected_store}']
    st.write(latest_data[display_columns])

    st.subheader('Combined Data')
    df_combined = pd.concat([df_artificial, df_real], ignore_index=True).drop_duplicates(keep='last')
    # st.write(df_combined.head())
    num_artificial = df_combined[df_combined['product_type'] == 'artificial']['product_sku'].nunique()
    num_real = df_combined[df_combined['product_type'] == 'real']['product_sku'].nunique()
    # Count the unique product_sku for artificial and real plants
    st.write('Number of Artificial Plants Products in IKEA : ', num_artificial)
    st.write('Number of Real Plants Products in IKEA : ', num_real)

    # Data to plot
    labels = 'Artificial Plants', 'Real Plants'
    sizes = [num_artificial, num_real]
    colors = ['#ff9999','#66b3ff'] 
    explode = (0.1, 0) 

    # Create a pie chart
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, pctdistance=0.85)

    # Draw a circle at the center of pie to make it look like a doughnut
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    # Equal aspect ratio ensures that pie is drawn as a circle
    ax1.axis('equal')  
    plt.tight_layout()

    # Display the doughnut chart in the Streamlit app
    st.pyplot(fig1)

def forecast_visualization_page(df_real, df_artificial):
    st.title('Stock Number Forecast Visualization')
    product_type = st.selectbox('Select Product Type:', ['Artificial','Real'])
    if product_type == 'Real':
        df = df_real
    elif product_type == 'Artificial':
        df = df_artificial
    else:
        st.write("Invalid product type selected.")
        return
    product_skus = df['product_sku'].unique()
    selected_product_sku = st.selectbox('Select Product SKU:', product_skus)
    # Get product details for the selected product_sku
    selected_product = df[df['product_sku'] == selected_product_sku].iloc[0]
    product_name = selected_product['product_name']
    product_size = selected_product['product_size']
    image_url = selected_product['image_url']
    st.write(f"Selected Product: {product_name}")
    if pd.notna(product_size):
        st.write(f"Product Size: {product_size}")
    if pd.notna(image_url):
        st.image(image_url, caption='Product Image', width=200)  # Adjust width here
    store_locations = [col.split('_')[2] for col in df.columns if col.startswith('stock_number_')]
    selected_store_location = st.selectbox('Select Store Location:', store_locations)
    num_periods = st.slider('Number of Periods for Prediction', min_value=1, max_value=30, value=7)
    store_column = f'stock_number_{selected_store_location.lower()}'
    df['current_date'] = pd.to_datetime(df['current_date'],  format='%Y-%m-%d', errors='coerce')  # Convert to datetime, ignore NaT values
    df = df.dropna(subset=['current_date'])  # Drop rows with NaT values in current_date
    df_sku = df[(df['product_sku'] == selected_product_sku) & df[store_column].notnull()]   
    if not df_sku.empty:
        df_sku = df_sku[['product_sku', 'current_date', store_column]]
        df_sku.set_index('current_date', inplace=True)
        df_sku.sort_values('current_date', inplace=True)
        stock_series = df_sku[store_column]
        if not stock_series.empty:
            model = ARIMA(stock_series, order=(1,1,2))
            model_fit = model.fit()
            st.write(model_fit.summary())
            forecast = model_fit.forecast(steps=num_periods)
            st.write(f'Forecast for next {num_periods} periods:', forecast)
            plt.figure(figsize=(10, 6))
            plt.plot(stock_series.index, stock_series, label='Historical Stock Numbers')
            if not pd.isnull(stock_series.index[-1]):
                # Ensure the last date of the historical data is correct
                last_historical_date = stock_series.index[-1]
                #forecast_index = pd.date_range(start=stock_series.index[-1], periods=num_periods + 1, freq='W')[1:]
                forecast_index = pd.date_range(start=last_historical_date + pd.Timedelta(days=1), 
                               periods=num_periods, 
                               freq=stock_series.index.freq) # Use the same frequency as the historical data

                plt.plot(forecast_index, forecast, label='Forecast', color='red')
                plt.legend()
                plt.xlabel('Date')
                plt.ylabel('Stock Number')
                plt.title(f'Forecasting Stock Numbers for Product SKU {selected_product_sku} in {selected_store_location.capitalize()} Store')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(plt)
            else:
                st.write("The historical data contains an invalid date. Unable to generate forecast.")
        else:
            st.write("No stock data available for this SKU and store location.")
    else:
        st.write("Invalid SKU or no data available for the selected store location.")


from datetime import timedelta

def popular_products_page(df_combined, df_artificial, df_real):
    st.title('Popular Products Analysis')   
    # Product type selection
    product_type = st.selectbox('Select product type:', ['Both', 'Artificial', 'Real'])
    # Filter the combined DataFrame based on the selected product type
    if product_type == 'Artificial':
        df_combined = df_artificial
    elif product_type == 'Real':
        df_real = df_real[
        df_real['product_name'].str.contains('potted plant', case=False) &
        ~df_real['product_name'].str.contains('artificial', case=False) &
        ~df_real['product_name'].str.contains('Artifi', case=False)]
        df_combined = df_real
    # Convert 'current_date' to datetime and drop rows with NaT values
    df_combined['current_date'] = pd.to_datetime(df_combined['current_date'],  infer_datetime_format=True, errors='coerce')
    df_combined.dropna(subset=['current_date'], inplace=True)
    # Find min and max dates to create the range of weeks
    min_date = df_combined['current_date'].min()
    max_date = df_combined['current_date'].max()
    # Generate a list of date ranges (start of week - end of week)
    date_ranges = ["Overall"]  # Start with an 'Overall' option
    current_start_date = min_date - pd.to_timedelta(min_date.weekday(), unit='d')  # Align to the start of the week
    while current_start_date <= max_date:
        end_date = current_start_date + pd.to_timedelta(6, unit='d')
        date_ranges.append(f"{current_start_date.strftime('%b %d')} - {end_date.strftime('%b %d')}")
        current_start_date += pd.to_timedelta(1, unit='W')
    # Dropdown to select the weekly date range
    selected_week = st.selectbox('Select weekly date range for analysis:', date_ranges)
    if selected_week == "Overall":
        df_filtered = df_combined.copy()  # Use all data if 'Overall' is selected
    else:
        start_str, end_str = selected_week.split(' - ')
        # Ensure the year is included in the date string for proper conversion to datetime
        start_date = pd.to_datetime(start_str + f", {min_date.year}", format='%b %d, %Y')
        end_date = pd.to_datetime(end_str + f", {min_date.year}", format='%b %d, %Y')
        # Ensure that end_date covers the entire day
        end_date = end_date + pd.to_timedelta(23, unit='h') + pd.to_timedelta(59, unit='m') + pd.to_timedelta(59, unit='s')
        # Filter the dataset based on the selected date range
        df_filtered = df_combined[(df_combined['current_date'] >= start_date) & (df_combined['current_date'] <= end_date)]
    # Allow selection of overall or specific store for analysis
    store_options = ['All Stores'] + [col.split('_')[2] for col in df_filtered.columns if col.startswith('stock_number_')]
    selected_store = st.selectbox('Select store location for analysis:', store_options)
    # Copy the filtered DataFrame to prevent modifications to the original
    df_popular = df_filtered.copy()
    df_popular['product_sku'] = df_popular['product_sku'].astype(str).str.replace(',', '')
    if selected_store != 'All Stores':
        stock_column = f'stock_number_{selected_store}'
    else:
        # If 'Overall' is selected, sum the stock numbers from all stores for each product
        stock_columns = [col for col in df_filtered.columns if col.startswith('stock_number_')]
        df_popular['stock_number_overall'] = df_popular[stock_columns].sum(axis=1)
        stock_column = 'stock_number_overall'
    # Calculate the difference in stock level from one record to the next for each product
    df_popular['stock_change'] = df_popular.groupby('product_sku')[stock_column].diff()

    # A positive stock change indicates a restocking event
    df_popular['is_restocked'] = df_popular['stock_change'] > 0

    # Count restocking events for each product
    restock_counts = df_popular.groupby('product_sku')['is_restocked'].sum().reset_index()

    # Merge to get product names, sizes, and types without changing the original DataFrame

    merge_columns = ['product_sku', 'product_name', 'product_size']
    if 'product_type' in df_popular.columns:
        merge_columns.append('product_type')
    restock_counts_with_details = restock_counts.merge(
        df_popular[merge_columns].drop_duplicates(),
        on='product_sku',
        how='left'
    )
    # Sort products by restocking frequency in descending order
    restock_counts_sorted = restock_counts_with_details.sort_values(by='is_restocked', ascending=False)
    # Select the top 10 products based on restocking frequency
    display_columns = ['product_sku', 'product_name', 'product_size', 'is_restocked']
    top_10_replenished_products = restock_counts_sorted.head(10)[display_columns]
    top_10_replenished_products['product_sku'] = top_10_replenished_products['product_sku'].str.replace(',', '')
    st.write(f"Top 10 replenished products at {selected_store} for the week {selected_week}:", top_10_replenished_products)  
    restock_counts_sorted['product_info'] = restock_counts_sorted['product_sku'].astype(str) + ' - ' + restock_counts_sorted['product_name']
    top_10 = restock_counts_sorted.head(10)
    # Sort the DataFrame based on 'is_restocked' in descending order
    # Create a vertical bar chart with Seaborn with a different color for each bar using the combined 'product_info'
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x='product_info', y='is_restocked', data=top_10, ax=ax, palette='deep')
    # Rotate product info labels for better visibility
    plt.xticks(rotation=45, ha='right')
    # Set labels and title
    ax.set_xlabel('Product SKU - Product Name')
    ax.set_ylabel('Number of Times Restocked')
    ax.set_title('Top 10 Replenished Products Sorted by Restock Frequency')
    # Streamlit function to display the figure
    st.pyplot(fig)



def discount_analysis_page(df_analysis):
    st.title('Discount Analysis')
    # Convert price columns to numeric
    df_analysis['product_price_old'] = pd.to_numeric(df_analysis['product_price_old'].str.replace('$', ''), errors='coerce')
    df_analysis['product_price_new'] = pd.to_numeric(df_analysis['product_price_new'].str.replace('$', ''), errors='coerce')
    # Calculate discount percentage and identify discounted products
    df_analysis['discount_percentage'] = ((df_analysis['product_price_old'] - df_analysis['product_price_new']) / df_analysis['product_price_old']) * 100
    df_analysis['has_discount'] = df_analysis['discount_percentage'] > 0
    # Allow selection of store location for analysis
    store_options = [col.split('_')[2] for col in df_analysis.columns if 'stock_number_' in col]
    selected_store = st.selectbox('Select a store location for analysis:', store_options)
    stock_column = f'stock_number_{selected_store}'
    # Calculate daily stock change for the selected store
    df_analysis.sort_values(by=['product_sku', 'current_date'], inplace=True)
    df_analysis[f'daily_stock_change_{selected_store}'] = df_analysis.groupby('product_sku')[stock_column].diff().fillna(0)
    # Since sales are indicated by a decrease in stock, consider only negative changes
    df_analysis[f'daily_sales_{selected_store}'] = df_analysis[f'daily_stock_change_{selected_store}'].apply(lambda x: -x if x < 0 else 0)
    # Filter for sales data
    df_sales = df_analysis[df_analysis[f'daily_sales_{selected_store}'] > 0]
    # Calculate average daily sales for discounted and non-discounted products
    average_sales_discounted = df_sales[df_sales['has_discount']][f'daily_sales_{selected_store}'].mean()
    average_sales_non_discounted = df_sales[~df_sales['has_discount']][f'daily_sales_{selected_store}'].mean()
    # Calculate the average discount percentage for discounted products
    average_discount_percentage = df_sales[df_sales['has_discount']]['discount_percentage'].mean()
    # Count the number of samples for discounted and non-discounted products
    sample_count_discounted = df_sales[df_sales['has_discount']].shape[0]
    sample_count_non_discounted = df_sales[~df_sales['has_discount']].shape[0]
    # Perform t-test
    t_statistic, p_value = stats.ttest_ind(
        df_sales[df_sales['has_discount']][f'daily_sales_{selected_store}'], 
        df_sales[~df_sales['has_discount']][f'daily_sales_{selected_store}'], 
        equal_var=False, nan_policy='omit'
    )
    # Output the results
    st.subheader('Analysis Results')
    # Discounted products information
    discounted_info = pd.DataFrame({
        'Metric': ['Average Discount Percentage', 'Sample Size', 'Average Daily Sales'],
        'Value': [
            f"{average_discount_percentage:.2f}%",
            sample_count_discounted,
            f"{average_sales_discounted:.2f}"
        ]
    })
    st.write('Discounted Products Information')
    st.write(discounted_info)
    # Non-discounted products information
    non_discounted_info = pd.DataFrame({
        'Metric': ['Sample Size', 'Average Daily Sales'],
        'Value': [
            sample_count_non_discounted,
            f"{average_sales_non_discounted:.2f}"
        ]
    })
    st.write('Non-Discounted Products Information')
    st.write(non_discounted_info)
    st.image('https://microbenotes.com/wp-content/uploads/2023/08/Two-Sample-T-Test-Formula.jpeg', caption='Two-Sample T-Test', width = 300)
    # T-test results
    alpha = 0.05
    # Determine the significance conclusion
    if p_value < alpha:
        conclusion = f"Reject the null hypothesis. There is a significant difference in average daily sales between discounted and non-discounted products at {selected_store}."
    else:
        conclusion = f"Fail to reject the null hypothesis. There is no significant difference in average daily sales between discounted and non-discounted products at {selected_store}."

    # Create the DataFrame for t-test results
    t_test_results = pd.DataFrame({
        'Metric': ['T-Statistic', 'P-Value'],
        'Value': [
            f"{t_statistic:.4f}",
            p_value
        ]
    })
    st.write('Hypothesis :')
    st.write(f'Null Hypothesis : There is a significant difference in average daily sales between discounted and non-discounted products at {selected_store}.')
    st.write(f'Alternative Hypothesis : There is no significant difference in average daily sales between discounted and non-discounted products at {selected_store}.')
   
    # Display the t-test results
    st.write('T-Test Results')
    st.write(t_test_results)
    st.write('Conclusion :')
    st.write(conclusion)

    import plotly.graph_objects as go

    degrees_of_freedom = sample_count_non_discounted + sample_count_discounted - 2
    # Determine critical value for a two-tailed t-test
    confidence_level = 0.95
    alpha = 1 - confidence_level
    critical_value = stats.t.ppf(1 - alpha / 2, df=degrees_of_freedom)

    # Generate x values for the t-distribution curve
    x = np.linspace(-4, 4, 1000)
    # Generate the t-distribution curve
    y = stats.t.pdf(x, df=degrees_of_freedom)

    # Initialize the plotly figure
    fig = go.Figure()
    # Plotting the t-distribution curve
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='T-distribution'))
    # Adding vertical lines for critical values and t-statistic
    fig.add_shape(type="line", x0=-critical_value, y0=0, x1=-critical_value, y1=max(y),
                line=dict(color='red', width=2, dash='dash'), name=f'Critical Value: {-critical_value:.2f}')
    fig.add_shape(type="line", x0=critical_value, y0=0, x1=critical_value, y1=max(y),
                line=dict(color='red', width=2, dash='dash'), name=f'Critical Value: {critical_value:.2f}')
    fig.add_shape(type="line", x0=t_statistic, y0=0, x1=t_statistic, y1=max(y),
                line=dict(color='green', width=2), name=f'T-statistic: {t_statistic:.2f}')
    # Filling the rejection regions
    fig.add_trace(go.Scatter(x=np.concatenate([x[x > critical_value], x[x < -critical_value]]),
                            y=np.concatenate([y[x > critical_value], y[x < -critical_value]]),
                            fill='toself', fillcolor='rgba(255, 0, 0, 0.3)',line=dict(color='rgba(255, 0, 0, 0)'),name='Rejection Region'))
    # Adding the p-value annotation
    fig.add_annotation(x=t_statistic, y=0,text=f"p-value: {p_value:.3e}",showarrow=True, arrowhead=1,xshift=10, yshift=10)
    # Adding the alpha level annotation
    fig.add_annotation(
        x=-critical_value, y=0.02, 
        text=f"alpha: {alpha:.2f}",
        showarrow=True, arrowhead=1,
        ax=-20, ay=30
    )   
    # Layout settings
    fig.update_layout(title='T-Distribution with T-Test Result',
                    xaxis_title='T-Statistic',
                    yaxis_title='Probability Density',
                    showlegend=True)
    fig.add_annotation(
        x=t_statistic, y=stats.t.pdf(t_statistic, df=degrees_of_freedom),
        text=f"t-statistic: {t_statistic:.2f}",
        showarrow=True, arrowhead=1,
        ax=-50, ay=-160  # Adjust these for the arrow position if needed
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ("Data Dashboard", "Stock Number Forecast Visualization", "Popular Products Analysis", "Discount Analysis"))

    bucket_name = 'csis4495'
    artificial_folder = 'weekly_artificial_plants'
    real_folder = 'weekly_real_plants'
    artificial_pattern = 'weekly_products_artificial_plants_'
    real_pattern = 'weekly_products_real_plants_'

    if choice == "Data Dashboard":
        df_artificial = load_data(bucket_name, artificial_folder, artificial_pattern)
        df_real = load_data(bucket_name, real_folder, real_pattern)
        data_analysis_page(bucket_name, artificial_folder, artificial_pattern, real_folder, real_pattern)
    elif choice == "Stock Number Forecast Visualization":
        df_artificial = load_data(bucket_name, artificial_folder, artificial_pattern)
        df_real = load_data(bucket_name, real_folder, real_pattern)
        forecast_visualization_page(df_real, df_artificial)
    elif choice == "Popular Products Analysis":
        df_artificial = load_data(bucket_name, artificial_folder, artificial_pattern)
        df_real = load_data(bucket_name, real_folder, real_pattern)
        df_combined = pd.concat([df_artificial, df_real], ignore_index=True).drop_duplicates(keep='last')
        popular_products_page(df_combined, df_artificial, df_real)
    elif choice == "Discount Analysis":
        df_artificial = load_data(bucket_name, artificial_folder, artificial_pattern)
        df_real = load_data(bucket_name, real_folder, real_pattern)
        df_combined = pd.concat([df_artificial, df_real], ignore_index=True).drop_duplicates(keep='last')
        discount_analysis_page(df_combined)
if __name__ == "__main__":
    main()
