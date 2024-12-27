import pandas as pd
import streamlit as st

def display_extracted_data(document_type):
    """
    Display extracted data in a table based on the document type.

    Parameters:
    - document_type (str): The type of document (e.g., "Salary Slip", "Profit and Loss Statement", "Check").
    """

    st.subheader("Extracted Data")

    if st.session_state.get("ocr_results"):
        
        # Display LLM response in a collapsible section
        if "llm_responses" in st.session_state and st.session_state["llm_responses"]:
            with st.expander("View Raw LLM Responses"):
                for i, response in enumerate(st.session_state["llm_responses"], 1):
                    st.markdown(f"### Response for Document {i}")
                    st.text(response)

        extracted_data = {}
        
        if document_type == "Salary Slip":
            extracted_data = {
                "Slip": [f"Slip {i+1}" for i in range(len(st.session_state.get("net_salaries", [])))],
                "Net Salary": st.session_state.get("net_salaries", []),
                "Gross Salary": st.session_state.get("gross_salaries", []),
                "Basic Salary": st.session_state.get("basic_salaries", [])
            }
        elif document_type == "Profit and Loss Statement":
            extracted_data = {
                "Slip": [f"Slip {i+1}" for i in range(len(st.session_state.get("total_revenue", [])))],
                "Total Revenue": st.session_state.get("total_revenue", []),
                "Net Income": st.session_state.get("net_income", [])
            }
        elif document_type == "Check":
            extracted_data = {
                "Check": [f"Check {i+1}" for i in range(len(st.session_state.get("amounts", [])))],
                "Account Number": st.session_state.get("account_numbers", []),
                "Amount": st.session_state.get("amounts", []),
                "Bank Name": st.session_state.get("bank_names", [])
            }

        # Convert to DataFrame and display
        if extracted_data:
            extracted_df = pd.DataFrame(extracted_data)
            st.write(extracted_df)
        else:
            st.write("No extracted data available.")
