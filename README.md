# OCR of Bank Statements 
This Streamlit-based web application allows users to process and analyze various document types (Salary Slips, Checks, and Profit and Loss Statements) through Optical Character Recognition (OCR) and Large Language Model (LLM) integration.

---

## Table of Contents

1. [Setup and Requirements](#setup-and-requirements)  
2. [Running the App](#Running-the-app)
3. [File Description](#File-description)

---

## Setup and Requirements

#### 1. Clone the repository:
```bash
   git clone <repository-url>
   cd <project-directory>
```
#### 2.Install required dependencies:

```bash
   pip install -r requirements.txt
```
#### 3. Obtain the following API keys and credentials:

 1. Cohere API Key: Sign up at Cohere to get an API key for natural language processing.
 2. AWS Access Key & Secret: Set up AWS credentials in your environment or retrieve them from AWS IAM.
##### a. Setting Up an S3 Bucket

To store documents for processing, create and organize an S3 bucket with the following steps:

##### Step-by-Step Guide:

1. **Create an S3 Bucket**:
   - Go to AWS Console → S3 → Create Bucket.
   - Choose a unique name (e.g., `ocr-bucket-sample`) and a region (e.g., `eu-north-1`).

2. **Create Folder Structure**:
   - Inside the bucket, create these folders:
     - `Datasets/salaryslip/` (for salary slip images)
     - `Datasets/Checks/` (for check images)
     - `Datasets/profit_and_loss_statement/` (for profit and loss statement images)

3. **Upload Documents**:
   - Upload the respective documents (salary slips, checks, profit and loss statements) into their corresponding folders.

##### b. Region Name:
Ensure you use the correct AWS region in `app.py` based on where your bucket is located. For example:
```python
region_name = 'eu-north-1'
```

#### 4. Create a config.json file :

Create a `config.json` file in the project directory to store your API keys and AWS credentials. The file should have the following structure:

```json
{
    "COHERE_API_KEY": "<Your Cohere API Key>",
    "AWS_ACCESS_KEY_ID": "<Your AWS Access Key ID>",
    "AWS_SECRET_ACCESS_KEY": "<Your AWS Secret Access Key>"
}
```

## Running the App

#### 1. Start the Streamlit app:
To start the Streamlit app, run the following command:

```bash
streamlit run app.py
```
The web app will be accessible at http://localhost:8501/ in your browser.
## File Descriptions:
 1. **app.py**: Main Streamlit app file that orchestrates document fetching, OCR processing, LLM queries, and visualization.
 2. **config.json**: Configuration file containing the API keys and AWS credentials.
 3. **visualization.py**: Contains functions for generating bar plots and pie charts for visualizing the extracted data.
 4. **display_table.py**: Displays the extracted OCR data in a table format.
 5. **ocr_processing.py**: Contains the functions responsible for processing images using PaddleOCR and interacting with Cohere for data extraction and LLM response generation.
 6. **s3_extraction.py**: Handles fetching documents from AWS S3.

### Troubleshooting:
1. Ensure that the AWS credentials in config.json have the necessary permissions to access the S3 bucket.
2. Check the Cohere API key for proper access to the LLM services.
3. Make sure PaddleOCR is correctly installed and configured to handle different types of documents.
