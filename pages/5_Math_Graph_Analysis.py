
import streamlit as st
import numpy as np
import cv2
import pytesseract
import matplotlib.pyplot as plt
import plotly.express as px
from sympy import symbols, solve, sympify
import io
from PIL import Image

# Page config
st.set_page_config(
    page_title="Math Graph Analysis",
    page_icon="🔢",
    layout="wide"
)

# Page title
st.title("🔢 Math Graph Analysis")
st.write("Upload a photo of your math graph question for analysis")

# File upload
uploaded_file = st.file_uploader("Upload image of math graph question", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    # Process image button
    if st.button("Analyze Image", type="primary"):
        with st.spinner("Processing image..."):
            # Convert image for OCR
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(gray)
            
            # Display extracted text
            with st.expander("📝 Extracted Question"):
                st.write(text)
            
            # Attempt to identify graph type and equation
            text_lower = text.lower()
            if any(term in text_lower for term in ['linear', 'straight line']):
                graph_type = "Linear"
                st.info("📈 Detected a linear equation")
            elif any(term in text_lower for term in ['quadratic', 'parabola']):
                graph_type = "Quadratic"
                st.info("📈 Detected a quadratic equation")
            else:
                graph_type = "Unknown"
                st.warning("📈 Could not determine graph type")
            
            # Generate sample points
            x = np.linspace(-10, 10, 100)
            
            # Example equation (replace with actual parsing)
            if graph_type == "Linear":
                y = 2*x + 1  # Example linear equation
                equation = "y = 2x + 1"
            elif graph_type == "Quadratic":
                y = x**2 + 2*x + 1  # Example quadratic equation
                equation = "y = x² + 2x + 1"
            else:
                y = x  # Default linear equation
                equation = "y = x"
            
            # Create columns for table and graph
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Values Table")
                # Generate table with selected points
                table_points = np.linspace(-5, 5, 11)
                if graph_type == "Linear":
                    table_values = 2*table_points + 1
                elif graph_type == "Quadratic":
                    table_values = table_points**2 + 2*table_points + 1
                else:
                    table_values = table_points
                
                df = pd.DataFrame({
                    'x': table_points,
                    'y': table_values
                })
                st.dataframe(df)
            
            with col2:
                st.subheader("📈 Graph")
                fig = px.line(x=x, y=y, title=f"Graph of {equation}")
                fig.update_layout(xaxis_title="x", yaxis_title="y")
                st.plotly_chart(fig, use_container_width=True)
            
            # Explanation section
            with st.expander("❓ Step-by-Step Explanation"):
                st.write(f"""
                1. **Graph Type**: {graph_type}
                2. **Equation**: {equation}
                3. **Key Points**:
                   - For x = 0, y = {float(y[50]):.2f}
                   - The graph is {'increasing' if y[-1] > y[0] else 'decreasing'}
                """)

else:
    st.info("Please upload an image to begin analysis")
