import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from utils.data_processor import get_initial_dataframe_info

# Set page configuration
st.set_page_config(
    page_title="Data Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'data' not in st.session_state:
    st.session_state.data = None
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None
if 'upload_status' not in st.session_state:
    st.session_state.upload_status = None
if 'data_cleaned' not in st.session_state:
    st.session_state.data_cleaned = False

# Theme toggle
if 'theme' not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    if st.session_state.theme == "light":
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"

# Function to process uploaded file
def process_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                data = pd.read_csv(uploaded_file)
            elif file_extension in ['xls', 'xlsx']:
                data = pd.read_excel(uploaded_file)
            elif file_extension == 'json':
                data = pd.json_normalize(json.loads(uploaded_file.read()))
            else:
                st.error(f"Unsupported file format: {file_extension}. Please upload a CSV, Excel, or JSON file.")
                return None
            
            st.session_state.data = data
            st.session_state.uploaded_file_name = uploaded_file.name
            st.session_state.upload_status = "success"
            st.session_state.data_cleaned = False
            return data
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.session_state.upload_status = "error"
            return None
    return None

# Main Application Layout
st.title("📊 Data Analysis Dashboard")

# Sidebar
with st.sidebar:
    st.title("Settings")
    
    # Theme toggle
    theme_col1, theme_col2 = st.columns([3, 1])
    with theme_col1:
        st.write("Toggle Theme:")
    with theme_col2:
        st.button("🌓", on_click=toggle_theme, help="Switch between light and dark mode")
    
    st.divider()
    
    # File upload
    st.subheader("1. Upload Your Data")
    uploaded_file = st.file_uploader(
        "Choose a CSV, Excel, or JSON file",
        type=['csv', 'xlsx', 'xls', 'json'],
        help="Upload your data file here. Supported formats: CSV, Excel, JSON"
    )
    
    if st.button("Process Data", key="process_data"):
        with st.spinner("Processing data..."):
            if uploaded_file is not None:
                process_uploaded_file(uploaded_file)
            else:
                st.error("Please upload a file first!")
    
    if st.session_state.upload_status == "success":
        st.success(f"✅ File '{st.session_state.uploaded_file_name}' successfully loaded!")
    elif st.session_state.upload_status == "error":
        st.error("❌ Error processing file. Please check the file format and try again.")

# Main Content
if st.session_state.data is not None:
    # Data Preview
    st.header("Data Preview")
    st.dataframe(st.session_state.data.head(10), use_container_width=True)
    
    # Basic Data Information
    st.header("Basic Data Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dataset Shape")
        st.write(f"Rows: {st.session_state.data.shape[0]}")
        st.write(f"Columns: {st.session_state.data.shape[1]}")
        
        st.subheader("Data Types")
        st.write(st.session_state.data.dtypes)
    
    with col2:
        st.subheader("Summary Statistics")
        numeric_data = st.session_state.data.select_dtypes(include=[np.number])
        if not numeric_data.empty:
            st.write(numeric_data.describe())
        else:
            st.info("No numeric columns found for summary statistics.")
    
    # Data Quality Check
    st.header("Data Quality Check")
    
    col3, col4 = st.columns(2)
    
    with col3:
        missing_values = st.session_state.data.isnull().sum()
        st.subheader("Missing Values")
        if missing_values.sum() > 0:
            st.write(missing_values[missing_values > 0])
        else:
            st.success("No missing values found!")
    
    with col4:
        st.subheader("Duplicate Rows")
        duplicate_count = st.session_state.data.duplicated().sum()
        if duplicate_count > 0:
            st.write(f"Number of duplicate rows: {duplicate_count}")
        else:
            st.success("No duplicate rows found!")
    
    # Next Steps Navigation
    st.header("Next Steps")
    st.info("""
    Now that your data is loaded, you can:
    1. Go to the **Data Cleaning** page to handle missing values and duplicates
    2. Proceed to **Data Analysis** for statistical analysis
    3. Create visualizations in the **Data Visualization** page
    4. Try predictive analysis in the **Predictive Analysis** page
    
    Use the sidebar navigation to switch between pages.
    """)
    
    # Initial data info for other pages
    get_initial_dataframe_info(st.session_state.data)
    
else:
    # Landing page when no data is loaded
    st.header("Welcome to the Data Analysis Dashboard")
    
    st.markdown("""
    ### Get started with data analysis in just a few steps:
    
    1. **Upload your data** using the file uploader in the sidebar
    2. **Clean your data** by handling missing values and duplicates
    3. **Analyze your data** with statistical methods
    4. **Visualize your insights** with various chart types
    5. **Make predictions** with machine learning models
    
    ### Supported file formats:
    - CSV (.csv)
    - Excel (.xlsx, .xls)
    - JSON (.json)
    
    ### Features:
    - ✅ Data cleaning and preprocessing
    - 📊 Multiple visualization options
    - 📈 Statistical analysis
    - 🔮 Predictive modeling
    - 💾 Download capabilities for processed data
    
    Upload a file from the sidebar to get started!
    """)
    
    # Example of what the dashboard can do
    st.subheader("Example Dashboard Features")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://raw.githubusercontent.com/streamlit/streamlit/develop/examples/app/streamlit_app.py.png", 
                 caption="Interactive Visualizations")
    with col2:
        st.image("https://raw.githubusercontent.com/streamlit/streamlit/develop/examples/app/linear_regression.py.png", 
                 caption="Predictive Analysis")
    with col3:
        st.image("https://raw.githubusercontent.com/streamlit/streamlit/develop/examples/app/uber_map.py.png", 
                 caption="Data Exploration")
