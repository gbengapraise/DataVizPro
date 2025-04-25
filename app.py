import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import base64
from pathlib import Path
from utils.data_processor import get_initial_dataframe_info
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.app_logo import add_logo
from streamlit_extras.colored_header import colored_header

# Set page configuration
st.set_page_config(
    page_title="Data Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to set animated background
def add_bg_from_url(url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url({url});
            background-size: cover;
        }}
        @keyframes gradient {{
            0% {{background-position: 0% 50%;}}
            50% {{background-position: 100% 50%;}}
            100% {{background-position: 0% 50%;}}
        }}
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.85);  /* Semi-transparent white overlay */
            z-index: -1;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Add animated background
add_bg_from_url("https://img.freepik.com/free-vector/gradient-network-connection-background_23-2148865392.jpg?w=2000")

# Add logo
try:
    from PIL import Image
    logo_path = "assets/logo.svg"
    add_logo(logo_path)
except Exception as e:
    st.sidebar.write("📊 Data Analysis Dashboard")

# Custom CSS for better font sizes and styling
st.markdown("""
<style>
    /* Main title font size */
    .main-title {
        font-size: 3.2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(90deg, #4CAF50, #2196F3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 10px;
    }
    
    /* Section headers */
    h2 {
        font-size: 2.2rem !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
    }
    
    /* Sub-section headers */
    h3 {
        font-size: 1.8rem !important;
        font-weight: 500 !important;
    }
    
    /* Regular text */
    p, .stMarkdown {
        font-size: 1.1rem !important;
        line-height: 1.5 !important;
    }
    
    /* Cards and containers styling */
    .stCard {
        border-radius: 15px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }
    
    .stCard:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        font-size: 1.2rem !important;
    }
    
    /* Button styling */
    .stButton>button {
        font-size: 1rem !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
    }
    
    /* Info containers */
    .st-emotion-cache-1y4p8pa {
        padding: 1.5rem !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

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
st.markdown('<h1 class="main-title">📊 Data Analysis Dashboard</h1>', unsafe_allow_html=True)

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
    
    # Create columns for main content and sample data section
    intro_col1, intro_col2 = st.columns([3, 2])
    
    with intro_col1:
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
        """)
    
    with intro_col2:
        with stylable_container(
            key="sample_data_card",
            css_styles="""
                {
                    border: 1px solid #4CAF50;
                    border-radius: 10px;
                    padding: 20px;
                    background-color: rgba(255, 255, 255, 0.7);
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }
            """
        ):
            st.markdown("### 📂 Try with Sample Data")
            st.markdown("No data to upload? Use our sample dataset to explore the dashboard's features!")
            
            if st.button("Load Sample Data", key="load_sample"):
                try:
                    sample_path = "assets/sample_data.csv"
                    sample_data = pd.read_csv(sample_path)
                    st.session_state.data = sample_data
                    st.session_state.uploaded_file_name = "sample_data.csv"
                    st.session_state.upload_status = "success"
                    st.session_state.data_cleaned = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading sample data: {str(e)}")
    
    st.markdown("**Upload a file from the sidebar or use the sample data to get started!**")
    
    # Example of what the dashboard can do
    st.subheader("Example Dashboard Features")
    
    # Use stylable containers for feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with stylable_container(
            key="vis_card",
            css_styles="""
                {
                    border: 1px solid #4CAF50;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    transition: transform 0.3s;
                }
                :hover {
                    transform: translateY(-5px);
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
                }
            """
        ):
            st.markdown("### 📊 Interactive Visualizations")
            st.markdown("""
                Create beautiful and interactive visualizations:
                - Scatter plots
                - Bar charts
                - Line graphs
                - Heatmaps
                - Pie charts
                - And more!
            """)
    
    with col2:
        with stylable_container(
            key="pred_card",
            css_styles="""
                {
                    border: 1px solid #2196F3;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    transition: transform 0.3s;
                }
                :hover {
                    transform: translateY(-5px);
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
                }
            """
        ):
            st.markdown("### 🔮 Predictive Analysis")
            st.markdown("""
                Apply machine learning models to your data:
                - Linear Regression
                - Random Forest
                - Logistic Regression
                - Feature importance
                - Model evaluation
                - Make predictions
            """)
    
    with col3:
        with stylable_container(
            key="explore_card",
            css_styles="""
                {
                    border: 1px solid #FF9800;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    transition: transform 0.3s;
                }
                :hover {
                    transform: translateY(-5px);
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
                }
            """
        ):
            st.markdown("### 🔍 Data Exploration")
            st.markdown("""
                Deeply understand your data with:
                - Summary statistics
                - Correlation analysis
                - Data type detection
                - Missing value identification
                - Outlier detection
                - Data distribution views
            """)
