
import streamlit as st
import numpy as np
import cv2
import pytesseract
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
from sympy import symbols, solve, sympify
import io
from PIL import Image, ImageEnhance

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
    
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize image while maintaining aspect ratio
    max_size = (800, 800)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Convert to numpy array for OpenCV processing
    img_array = np.array(image)
    
    # Apply advanced image enhancements
    # Convert to LAB color space for better processing
    lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
    l_channel, a, b = cv2.split(lab)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(l_channel)
    
    # Merge enhanced L-channel back with A and B channels
    limg = cv2.merge((cl,a,b))
    
    # Convert back to RGB color space
    enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    
    # Apply denoising
    enhanced = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)
    
    # Apply sharpening
    kernel = np.array([[-1,-1,-1],
                      [-1, 9,-1],
                      [-1,-1,-1]]) / 9
    enhanced = cv2.filter2D(enhanced, -1, kernel)
    
    # Fine-tune contrast and brightness
    enhanced = cv2.convertScaleAbs(enhanced, alpha=1.2, beta=10)
    
    # Convert back to PIL Image
    enhanced_image = Image.fromarray(enhanced)
    
    # Display original and enhanced images side by side
    col1, col2 = st.columns(2)
    with col1:
        st.write("Original Image")
        st.image(image, use_container_width=True)
    with col2:
        st.write("Enhanced Image")
        st.image(enhanced_image, use_container_width=True)
    
    # Use enhanced image for further processing
    image = enhanced_image
    
    # Image enhancement options
    st.subheader("Image Enhancement")
    enhance_col1, enhance_col2 = st.columns(2)
    
    with enhance_col1:
        brightness = st.slider("Brightness", 0.0, 2.0, 1.0, 0.1)
        contrast = st.slider("Contrast", 0.0, 2.0, 1.0, 0.1)
    
    with enhance_col2:
        sharpness = st.slider("Sharpness", 0.0, 2.0, 1.0, 0.1)
        denoise = st.slider("Denoise", 0.0, 1.0, 0.0, 0.1)
    
    # Process image button
    if st.button("Enhance and Analyze Image", type="primary"):
        with st.spinner("Processing image..."):
            # Convert PIL Image to OpenCV format
            img_array = np.array(image)
            
            # Apply enhancements
            img_array = cv2.convertScaleAbs(img_array, alpha=contrast, beta=brightness*50)
            
            if denoise > 0:
                img_array = cv2.fastNlMeansDenoisingColored(img_array, None, denoise*10, denoise*10, 7, 21)
            
            # Convert back to PIL Image for sharpness
            enhanced_image = Image.fromarray(img_array)
            if sharpness != 1.0:
                enhanced_image = ImageEnhance.Sharpness(enhanced_image).enhance(sharpness)
            
            # Display enhanced image
            st.image(enhanced_image, caption="Enhanced Image", use_container_width=True)
            
            # Convert enhanced image for OCR
            img_array = np.array(enhanced_image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
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
            
            # Create sections for table and graphs
            st.subheader("📊 Values Table")
            # Generate initial table with selected points
            table_points = np.linspace(-5, 5, 11)
            if graph_type == "Linear":
                table_values = 2*table_points + 1
            elif graph_type == "Quadratic":
                table_values = table_points**2 + 2*table_points + 1
            else:
                table_values = table_points
            
            # Create editable dataframe
            df = pd.DataFrame({
                'x': table_points,
                'y': table_values
            })
            
            # Make the dataframe editable
            edited_df = st.data_editor(df, num_rows="dynamic")
            
            # Create tabs for different graph types
            graph_tabs = st.tabs(["Line Graph", "Plus Graph", "L Graph"])
            
            with graph_tabs[0]:
                st.subheader("📈 Line Graph")
                fig1 = px.line(edited_df, x='x', y='y', title=f"Line Graph of {equation}")
                fig1.update_layout(xaxis_title="x", yaxis_title="y")
                st.plotly_chart(fig1, use_container_width=True)
            
            with graph_tabs[1]:
                st.subheader("➕ Plus Graph")
                fig2 = px.scatter(edited_df, x='x', y='y', title=f"Plus Graph of {equation}")
                fig2.update_traces(marker=dict(symbol='plus', size=15))
                fig2.update_layout(xaxis_title="x", yaxis_title="y")
                st.plotly_chart(fig2, use_container_width=True)
            
            with graph_tabs[2]:
                st.subheader("⌊ L Graph")
                fig3 = go.Figure()
                # Add horizontal lines
                for i in range(len(edited_df)):
                    fig3.add_shape(
                        type="line",
                        x0=edited_df['x'].iloc[i],
                        y0=0,
                        x1=edited_df['x'].iloc[i],
                        y1=edited_df['y'].iloc[i],
                        line=dict(color="blue", width=2)
                    )
                    fig3.add_shape(
                        type="line",
                        x0=0,
                        y0=edited_df['y'].iloc[i],
                        x1=edited_df['x'].iloc[i],
                        y1=edited_df['y'].iloc[i],
                        line=dict(color="blue", width=2)
                    )
                fig3.update_layout(
                    title=f"L Graph of {equation}",
                    xaxis_title="x",
                    yaxis_title="y",
                    showlegend=False
                )
                st.plotly_chart(fig3, use_container_width=True)
            
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
