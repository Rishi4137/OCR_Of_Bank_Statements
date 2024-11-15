# Financial-Document-OCR
An OCR project designed to extract  data from financial documents like pay slips, transaction history, and bank statements.



---

## Table of Contents

1. [Setup and Requirements](#setup-and-requirements)  
2. [Usage Instructions](#usage-instructions)  

---

## Setup and Requirements

### 1. Install Required Libraries

Install the necessary Python libraries:

```bash
pip install requests beautifulsoup4 bing-image-downloader boto3 Pillow matplotlib
```
## 2.Set up your AWS credentials
```bash
aws configure
```
## 3.Usage Instructions

### 1. Run Web Scraping Code
- Modify the `url` variable to your target webpage URL.
- Add any keywords in the `keywords` list to match your specific requirements.

### 2. Run Bing Image Downloader
- Set the `search_terms` list to the desired search terms for financial documents.
- Adjust parameters as needed, such as the `limit` for the number of images per term.

### 3. Upload to Amazon S3
- Update the following in the script to match your AWS S3 settings:
  - `aws_access_key_id`
  - `aws_secret_access_key`
  - `region_name`
  - `bucket_name`
  - `folder_prefix`

### 4. Download Images from S3
- Run the final section of the script to retrieve images from your S3 bucket for local use.
- Process the downloaded dataset for analysis or visualization.

