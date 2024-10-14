# Importing Relevant Python Libraries
import pandas as pd
import plotly.express as px
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

# Load your dataset
@st.cache_data  # Use st.cache_data for caching the dataset to improve performance
def load_data():
    data = pd.read_csv(r"Imports_Exports_Dataset 2.csv")
    return data

data = load_data()

# Selecting a Random Sample from the dataset
sample = data.sample(n=3001, random_state=55013)

# Title of the dashboard
st.title('Interactive Imports and Exports Dashboard')

# Slicers for filtering the data
selected_import_export = st.sidebar.multiselect(
    'Select Import/Export Type',
    options=sample['Import_Export'].unique(),
    default=sample['Import_Export'].unique()
)

selected_category = st.sidebar.multiselect(
    'Select Categories',
    options=sample['Category'].unique(),
    default=sample['Category'].unique()
)

selected_payment_terms = st.sidebar.multiselect(
    'Select Payment Terms',
    options=sample['Payment_Terms'].unique(),
    default=sample['Payment_Terms'].unique()
)

# Filter data based on selections
filtered_data = sample[
    (sample['Import_Export'].isin(selected_import_export)) &
    (sample['Category'].isin(selected_category)) &
    (sample['Payment_Terms'].isin(selected_payment_terms))
]

# Show filtered data
st.subheader('Filtered Data')
st.write(filtered_data)

# Create a container for the visualizations
with st.container():
    # Transaction Counts Pie Chart
    transaction_counts = filtered_data['Import_Export'].value_counts()
    st.subheader('Percentage of Import and Export Transactions')
    fig1, ax1 = plt.subplots(figsize=(8, 4))  # Adjusted figure size for width
    ax1.pie(transaction_counts, labels=transaction_counts.index, autopct='%1.1f%%', startangle=90, colors=['lightblue', 'orange'])
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig1)  # Pass the figure to st.pyplot()

    # Payment Method Distribution Pie Chart
    payment_method_totals = filtered_data.groupby('Payment_Terms').size().reset_index(name='Count')
    fig2 = px.pie(payment_method_totals,
                   names='Payment_Terms',
                   values='Count',
                   title='Distribution of Transactions by Payment Method',
                   color_discrete_sequence=px.colors.qualitative.Plotly)
    st.plotly_chart(fig2)

# Transaction Value by Category Bar Chart
with st.container():
    category_totals = filtered_data.groupby('Category').agg({'Value': 'sum'}).reset_index()
    category_totals.rename(columns={'Value': 'Transaction Value'}, inplace=True)
    category_totals = category_totals.sort_values(by='Transaction Value', ascending=False)

    fig3 = px.bar(category_totals,
                   x='Category',
                   y='Transaction Value',
                   title='Total Transaction Value by Category (Descending Order)',
                   labels={'Transaction Value': 'Total Transaction Value', 'Category': 'Category'},
                   color='Category',
                   color_discrete_sequence=px.colors.qualitative.Plotly)
    st.plotly_chart(fig3)

# Correlation Matrix Heatmap
with st.container():
    non_categorical_vars = filtered_data[['Quantity', 'Value', 'Weight']]
    correlation_matrix = non_categorical_vars.corr()
    st.subheader('Correlation Matrix Heatmap')
    fig4, ax2 = plt.subplots(figsize=(8, 4))  # Adjusted figure size for width
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.5f', ax=ax2)
    ax2.set_title('Correlation Matrix')
    st.pyplot(fig4)  # Pass the figure to st.pyplot()

# Boxplot for top 10 products
with st.container():
    top_10_categories = sample['Product'].value_counts().nlargest(10).index
    top_10_sample = sample[sample['Product'].isin(top_10_categories)]
    fig5, ax3 = plt.subplots(figsize=(10, 4))  # Adjusted figure size for width
    sns.boxplot(x='Product', y='Value', data=top_10_sample, palette="bright", ax=ax3)
    ax3.set_title('Boxplot of Value by Top 10 Products')
    ax3.set_xticklabels(ax3.get_xticklabels(), rotation=90)
    st.pyplot(fig5)  # Pass the figure to st.pyplot()

# Average Value of Transactions by Month Line Chart
with st.container():
    sample['Date'] = pd.to_datetime(sample['Date'], format='%d-%m-%Y')
    sample['Month'] = sample['Date'].dt.month
    monthly_avg_value = sample.groupby(['Month', 'Import_Export'])['Value'].mean().unstack()

    fig6, ax4 = plt.subplots(figsize=(10, 4))  # Adjusted figure size for width
    for column in monthly_avg_value.columns:
        ax4.plot(monthly_avg_value.index, monthly_avg_value[column], marker='o', label=column)
    ax4.set_title('Average Value of Transactions by Month')
    ax4.set_xlabel('Month')
    ax4.set_ylabel('Average Transaction Value')
    ax4.grid(True)
    ax4.legend(title='Transaction Type')
    st.pyplot(fig6)  # Pass the figure to st.pyplot()

# Total Import and Export Values by Country Map Chart
with st.container():
    country_values = sample.groupby(['Country', 'Import_Export'])['Value'].sum().reset_index()
    country_values_pivot = country_values.pivot(index='Country', columns='Import_Export', values='Value').fillna(0)
    country_values_pivot['Total'] = country_values_pivot.sum(axis=1)

    fig7 = px.choropleth(country_values_pivot,
                          locations=country_values_pivot.index,
                          locationmode='country names',
                          color='Total',
                          hover_name=country_values_pivot.index,
                          title='Total Import and Export Values by Country',
                          color_continuous_scale=px.colors.sequential.Plasma,
                          labels={'Total': 'Total Value (in USD)'})
    st.plotly_chart(fig7)

    
