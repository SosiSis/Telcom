import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from load_data import load_data_from_postgres, load_data_using_sqlalchemy
from sql_queries import execute_telecom_queries

# Define your SQL query
query = "SELECT * FROM xdr_data;"  # Replace with your actual table name

# Load data from PostgreSQL
df = load_data_from_postgres(query)

# Display the first few rows of the dataframe
if df is not None:
    print("Successfully loaded the data")
else:
    print("Failed to load data.")

# Dashboard Pages
st.sidebar.title("Dashboard Navigation")
page = st.sidebar.radio(
    "Go to", ["User Overview Analysis", "User Engagement Analysis", "Experience Analysis", "Satisfaction Analysis"]
)

# Page 1: User Overview Analysis
if page == "User Overview Analysis":
    st.title("User Overview Analysis")
    st.write("Analyze user activities and general metrics.")
    st.write(agg_data.describe())  # General overview of data

    # Example Plot
    st.bar_chart(agg_data[['Engagement Score', 'Experience Score']].mean())

# Page 2: User Engagement Analysis
elif page == "User Engagement Analysis":
    st.title("User Engagement Analysis")
    st.write("Top 10 Engaged Users")
    st.table(agg_data.nlargest(10, 'Engagement Score')[['MSISDN', 'Engagement Score']])

    # Engagement Clusters Visualization
    fig, ax = plt.subplots()
    sns.scatterplot(data=agg_data, x='Engagement Score', y='Experience Score', hue='Satisfaction Cluster', ax=ax)
    plt.title('Engagement vs Experience Clusters')
    st.pyplot(fig)

# Page 3: Experience Analysis
elif page == "Experience Analysis":
    st.title("Experience Analysis")
    st.write("TCP Retransmission and RTT Analysis by Handset Type")

    # Example distribution plot
    fig, ax = plt.subplots()
    sns.boxplot(data=agg_data, x='Handset Type', y='Experience Score', ax=ax)
    plt.xticks(rotation=90)
    st.pyplot(fig)

# Page 4: Satisfaction Analysis
elif page == "Satisfaction Analysis":
    st.title("Satisfaction Analysis")
    st.write("Top 10 Satisfied Users")
    st.table(agg_data.nlargest(10, 'Satisfaction Score')[['MSISDN', 'Satisfaction Score']])

    # Elbow method visualization
    fig, ax = plt.subplots()
    k_range = range(1, 11)
    wcss = [KMeans(n_clusters=k).fit(agg_data[['Engagement Score', 'Experience Score']]).inertia_ for k in k_range]
    ax.plot(k_range, wcss, marker='o')
    ax.set_title('Elbow Method for Optimal k')
    ax.set_xlabel('Number of Clusters')
    ax.set_ylabel('WCSS')
    st.pyplot(fig)

# Deploy the App
# Run with: `streamlit run your_dashboard.py`
