import re
import cv2
import numpy as np
from PIL import Image


def process_prompt(user_prompt, extracted_data,co):
    # Here you can call your LLM or logic for processing the query with the extracted data.
    # For now, it's a placeholder to simulate a response.
    
    # Example: Just returning a simulated response based on the prompt
    response = f"Processing query: '{user_prompt}' with the extracted data."
    
    # You can integrate with Cohere or other LLM here for the actual response
    #For example, sending the user prompt and extracted data to Cohere:
    response = co.generate(
        model="command",
        prompt=f"Answer the following question based on the extracted data: {user_prompt}\nExtracted Data: {extracted_data}",
        max_tokens=150
    )
    
    return response.generations[0].text.strip()


def process_ocr_and_extract_data(uploaded_files, document_type, paddle_ocr, co):
    """
    Processes OCR on uploaded files and extracts structured data based on document type.
    
    Parameters:
    - uploaded_files: List of uploaded files.
    - document_type: Type of document (e.g., "Salary Slip", "Profit and Loss Statement", "Check").
    - paddle_ocr: Instance of PaddleOCR for OCR processing.
    - co: Cohere API client instance for text processing.
    
    Returns:
    - A dictionary containing extracted structured data for the document type.
    - A list of LLM responses for each processed document.
    """
    # Initialize temporary lists for storing extracted data
    net_salaries, gross_salaries, basic_salaries = [], [], []
    total_revenue, net_income = [], []
    account_numbers, amounts, bank_names = [], [], []
    llm_responses = []  # Store LLM responses for each file

    # Function to clean and validate numerical values
    # Function to clean and validate numerical values
    def clean_value(value):
        if value is not None:  # Ensure the value is not None
            value = str(value)  # Convert to string
            cleaned_value = re.sub(r"[^\d.]", "", value)
            if cleaned_value.replace('.', '', 1).isdigit():
                return float(cleaned_value)
        return None

   #Function to extract amount using fallback
    def extract_amount_from_text(text):
        """Extracts numeric amount from OCR text."""
        amount_patterns = [
            r"[₹\*]?\s?[\d,]+\.?\d*\s?\/?-?",  # Matches ₹1,23,456.78, ***1,23,500/- or ₹123456
            r"₹\s?[\d,]+\.?\d*",  # Matches ₹1,23,456.78 or ₹123456
            r"Rs\.?\s?[\d,]+\.?\d*",  # Matches Rs. 123456 or Rs 1,23,456
            r"INR\s?[\d,]+\.?\d*"  # Matches INR 123456 or INR 1,23,456
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = re.sub(r"[^\d.]", "", match.group())  # Remove everything except digits and decimal point
                return float(amount) if amount else None
        return None

    # Process each uploaded file
    ocr_results = []
    for uploaded_file in uploaded_files:
        # Convert file to image
        if isinstance(uploaded_file, Image.Image):
            image = uploaded_file
        else:
            image = Image.open(uploaded_file)
        image_cv2 = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Perform OCR
        paddle_results = paddle_ocr.ocr(np.array(image))
        ocr_results.append(paddle_results)

        # Extract text lines
        texts = [line[1][0] for line in paddle_results[0]]
        extracted_text = " ".join(texts)

#         # Prepare Cohere prompt
#         prompt = f"Extract the following information from the text: {extracted_text}\n\n"
#         if document_type == "Salary Slip":
#             prompt += "Find and return the values for: Net Salary, Gross Salary, Basic Salary."
#         elif document_type == "Profit and Loss Statement":
#             prompt += "Find and return the values for: Total Revenue, Net Income."
#         elif document_type == "Check":
#             prompt += "Find and return the values for: Account Number, Amount (in Rupees), Bank Name."

        # Prepare Cohere prompt
        prompt = f"Extract the following information from the given text:\n\n{extracted_text}\n\n"
        
        if document_type == "Salary Slip":
            prompt += (
                "Please extract  the following salary components in the format 'Field: Value':\n"
                "- Net Salary\n"
                "- Gross Salary\n"
                "- Basic Salary\n"
                "Make sure to extract values in the proper format (e.g., numeric values for salaries)."
                "If a field is not found, return 'None',dont give unncessary text."
            )
        elif document_type == "Profit and Loss Statement":
            prompt += (
                "Please extract the following financial components in the format 'Field: Value':\n"
                "-Total Revenue\n"
                "-Net Income\n"
                "Ensure to extract numeric values for both and return 'None' if any component is missing,dont give unncessary text."
            )
        elif document_type == "Check":
            prompt += (
                "Please extract the following details in the format 'Field: Value':\n"
                "- Account Number\n"
                "- Amount \n"
                "- Bank Name\n"
                "For Amount, ensure it is in numeric format (e.g., '₹1,000' or 'Rs. 1,000')."
                "If any field is missing, return 'None',dont give unncessary text."
            )

                # Call Cohere API
        # Call Cohere API
        response = co.generate(
            model='command',
            prompt=prompt,
            max_tokens=200
        )
        
        # Store raw LLM response
        result_text = response.generations[0].text.strip()
        llm_responses.append(result_text)
        
        # Initialize data storage dictionary
        temp_data = {
            "Net Salary": None, "Gross Salary": None, "Basic Salary": None,
            "Total Revenue": None, "Net Income": None, 
            "Account Number": None, "Amount": None, "Bank Name": None
        }
        
        # Extract numeric values from the LLM response for the Salary Slip
 
        if document_type == "Salary Slip":
            for field in ["Net Salary", "Gross Salary", "Basic Salary"]:
                # Improved pattern to handle various formatting options
                pattern = rf"{field}:\s*(Rs\.|₹|INR|Rupees|[\$\€])?\s*([\d,]+\.?\d*)"
                match = re.search(pattern, result_text)
                if match:
                    # Extract the value (considering grouping or decimals)
                    value = match.group(2) if match.group(2) else match.group(1)
                    temp_data[field] = clean_value(value)
        # Extract numeric values for Profit and Loss Statement
        elif document_type == "Profit and Loss Statement":
            for field in ["Total Revenue", "Net Income"]:
                # Improved pattern to handle commas in values
                pattern = rf"{field}\s*(\(.*\))?[:\-]?\s*(?:\$|₹|Rs\.?)?\s*([\,?\d]+\.?\d*)"
                match = re.search(pattern, result_text)
                if match:
                    # Extract and convert value to a number (considering commas)
                    value = float(match.group(2).replace(",", ""))
                    temp_data[field] = value
        
        # Extract data from Checks (Account Number, Amount, Bank Name)
        elif document_type == "Check":
            check_fields = {
                "Account Number": r"Account Number:\s*([\w\d\-]+)",  # Extracts the account number
                "Amount": r"Amount:\s*(?:Rs\.?|₹|$)?\s*([\d,]+\.?\d*)",  # Handles "Rs.", currency symbols, commas, and decimals
                "Bank Name": r"Bank Name:\s*(.+)"                   # Extracts the bank name
            }
            for field, pattern in check_fields.items():
                match = re.search(pattern, result_text, re.IGNORECASE)
                if match:
                    if field == "Amount":
                        # Clean and extract the amount using the clean_value function
                        temp_data[field] = clean_value(match.group(1))
                    else:
                        # For other fields, directly extract and strip the value
                        temp_data[field] = match.group(1).strip()
        
        #     # In case Amount field is missing, extract it from the OCR text
        #     if "Amount" in check_fields and temp_data.get("Amount") is None:
        #         temp_data["Amount"] = extract_amount_from_text(" ".join(texts))
        
        # Ensure numeric fields are correctly validated and cleaned
        if temp_data["Amount"] is not None:
            temp_data["Amount"] = clean_value(temp_data["Amount"])
        
        # Append extracted data for later use
        if document_type == "Salary Slip":
            net_salaries.append(temp_data["Net Salary"])
            gross_salaries.append(temp_data["Gross Salary"])
            basic_salaries.append(temp_data["Basic Salary"])
        elif document_type == "Profit and Loss Statement":
            total_revenue.append(temp_data["Total Revenue"])
            net_income.append(temp_data["Net Income"])
        elif document_type == "Check":
            account_numbers.append(temp_data["Account Number"])
            amounts.append(temp_data["Amount"])
            bank_names.append(temp_data["Bank Name"])


    # Return extracted data and LLM responses
    return {
        "ocr_results": ocr_results,
        "net_salaries": net_salaries,
        "gross_salaries": gross_salaries,
        "basic_salaries": basic_salaries,
        "total_revenue": total_revenue,
        "net_income": net_income,
        "account_numbers": account_numbers,
        "amounts": amounts,
        "bank_names": bank_names,
        "llm_responses": llm_responses
    }

