import streamlit as st
from PIL import Image
from paddleocr import PaddleOCR
import numpy as np
import cv2
import pandas as pd
import matplotlib.pyplot as plt
import cohere
import re
import json
import boto3
import os
import random
from io import BytesIO


# Import the function from the files
from visualization import visualize_data
from display_table import display_extracted_data
from ocr_processing import process_ocr_and_extract_data,process_prompt
from s3_extraction import fetch_documents_from_s3  


with open("config.json", "r") as f:
    config = json.load(f)

cohere_api_key = config["COHERE_API_KEY"]
aws_access_key_id = config["AWS_ACCESS_KEY_ID"]
aws_secret_access_key = config["AWS_SECRET_ACCESS_KEY"]

# Initialize PaddleOCR with angle classification for better text detection
paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Initialize Cohere API with the API key for natural language processing
co = cohere.Client(cohere_api_key)  # Replace with your actual Cohere API key

# Streamlit app title
st.title("Document OCR and Analysis")
region_name = 'eu-north-1'

# Initialize an S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

# Define your bucket name
bucket_name = 'ocr-bucket-rishi'

# Step 1: Select document type
uploaded_files = []
document_type = st.selectbox(
    "Select the document type to process:",
    ["Salary Slip", "Check", "Profit and Loss Statement"]
)

# Map document type to folder prefixes
folder_mapping = {
    "Salary Slip": "Datasets/salaryslip/",
    "Check": "Datasets/Checks/",
    "Profit and Loss Statement": "Datasets/profit_and_loss_statement/"
}
folder_prefix = folder_mapping[document_type]

# Step 2: Input number of documents to process
num_documents = st.number_input(
    "Enter the number of documents to process:",
    min_value=1,
    step=1
)

# # Button to trigger image selection
if st.button("Fetch Documents"):
    try:
        # Fetch documents from S3 using the function from the new file
        uploaded_files = fetch_documents_from_s3("ocr-bucket-rishi", folder_prefix, num_documents)

        # Store images in session state
        st.session_state["fetched_images"] = uploaded_files

        st.success(f"Successfully fetched {len(uploaded_files)} documents.")
    except ValueError as e:
        st.error(str(e))

# Display images in a collapsible section if they exist
if "fetched_images" in st.session_state and st.session_state["fetched_images"]:
    with st.expander("View Fetched Images"):
        for img in st.session_state["fetched_images"]:
            st.image(img, caption="Processed Image", use_container_width=True)



# Initialize session state to store OCR, processed results, LLM Response, Users Prompt
if "ocr_results" not in st.session_state:
    st.session_state["ocr_results"] = []  # Raw OCR results
if "net_salaries" not in st.session_state:
    st.session_state["net_salaries"] = []
if "gross_salaries" not in st.session_state:
    st.session_state["gross_salaries"] = []
if "basic_salaries" not in st.session_state:
    st.session_state["basic_salaries"] = []
if "total_revenue" not in st.session_state:
    st.session_state["total_revenue"] = []
if "net_income" not in st.session_state:
    st.session_state["net_income"] = []
if "account_numbers" not in st.session_state:
    st.session_state["account_numbers"] = []
if "amounts" not in st.session_state:
    st.session_state["amounts"] = []
if "bank_names" not in st.session_state:
    st.session_state["bank_names"] = []
if "llm_responses" not in st.session_state:
    st.session_state["llm_responses"] = []
if "llm_response" not in st.session_state:
    st.session_state["llm_response"] = None  
if "user_prompt" not in st.session_state:
    st.session_state["user_prompt"] = None  
if 'document_type' not in st.session_state:
    st.session_state.document_type = None


# Process OCR and data extraction only if files are uploaded and no previous results exist
if uploaded_files and not st.session_state["ocr_results"]:
    extracted_data = process_ocr_and_extract_data(uploaded_files, document_type, paddle_ocr, co)

    # Save data to session state
    st.session_state.update(extracted_data)

# Display extracted data in a table
display_extracted_data(document_type)



user_prompt = st.text_input("Ask a question about the extracted data:")

if user_prompt:
    if user_prompt != st.session_state["user_prompt"]:
        # Update session state with the new prompt
        st.session_state["user_prompt"] = user_prompt
    # Initialize the data_to_pass dictionary to hold all relevant data
    data_to_pass = {}

    # Check document type and select all relevant data
    if document_type == "Salary Slip":
        data_to_pass = {
            "net_salaries": st.session_state["net_salaries"],
            "gross_salaries": st.session_state["gross_salaries"],
            "basic_salaries": st.session_state["basic_salaries"]
        }
    
    elif document_type == "Profit and Loss Statement":
        data_to_pass = {
            "total_revenue": st.session_state["total_revenue"],
            "net_income": st.session_state["net_income"]
        }
    
    elif document_type == "Check":
        data_to_pass = {
            "amounts": st.session_state["amounts"]
        }

    # Call the process_prompt function with the user input and the extracted data
    result = process_prompt(user_prompt, data_to_pass,co)
    st.session_state["llm_response"] = result

    # Display the response from the LLM (or simulated response)
    st.write(result)
     # Create a downloadable text file with the result
    result_text = f"User Prompt: {user_prompt}\nResponse:\n{result}"
    st.download_button(
        label="Download Response as TXT",
        data=result_text,
        file_name="llm_response.txt",
        mime="text/plain"
    )
# Visualization section
st.subheader("Visualization")
if document_type == "Salary Slip":
    salary_type = st.selectbox("Select Salary Type", ["Net Salary", "Gross Salary", "Basic Salary"])
elif document_type == "Profit and Loss Statement":
    salary_type = st.selectbox("Select Financial Metric", ["Total Revenue", "Net Income"])
elif document_type == "Check":
    salary_type = "Amount"

# Choose plot type
plot_type = st.radio("Select Plot Type", ["Bar Plot", "Pie Chart"])

# Generate plot based on the selected options
if st.button("Generate Plot"):
    if document_type == "Salary Slip":
        if salary_type == "Net Salary":
            data = st.session_state["net_salaries"]
        elif salary_type == "Gross Salary":
            data = st.session_state["gross_salaries"]
        elif salary_type == "Basic Salary":
            data = st.session_state["basic_salaries"]
    elif document_type == "Profit and Loss Statement":
        if salary_type == "Total Revenue":
            data = st.session_state["total_revenue"]
        elif salary_type == "Net Income":
            data = st.session_state["net_income"]
    elif document_type == "Check":
        data = st.session_state["amounts"]
    visualize_data(data, salary_type, plot_type, document_type)

