import streamlit as st
import matplotlib.pyplot as plt

def visualize_data(data, salary_type, plot_type, document_type):
    """
    Function to visualize the provided data based on the selected salary/metric type
    and plot type.

    Parameters:
    - data (list): The data to visualize.
    - salary_type (str): The salary/metric type (e.g., 'Net Salary', 'Total Revenue').
    - plot_type (str): The type of plot ('Bar Plot' or 'Pie Chart').
    - document_type (str): The type of document (e.g., 'Salary Slip', 'Profit and Loss Statement').
    """
    
    # Clean and prepare data for plotting
    clean_data = []
    for val in data:
        if val is None:
            clean_data.append(0)
        else:
            try:
                if isinstance(val, str):
                    val = val.replace(",", "").replace("$", "")
                clean_data.append(float(val))
            except (ValueError, AttributeError):
                clean_data.append(0)

    # Plot the data
    if clean_data:
        st.write(f"### Visualization for {salary_type}")
        fig, ax = plt.subplots(figsize=(8, 6))

        if plot_type == "Bar Plot":
            ax.bar(range(len(clean_data)), clean_data, color="skyblue", edgecolor="black")
            ax.set_title(f"{salary_type} - Bar Plot")
            ax.set_ylabel("Amount")
            ax.set_xlabel("Entries")
            ax.set_xticks(range(len(clean_data)))
            labels = (
                [f"Slip {i+1}" for i in range(len(clean_data))] 
                if document_type != "Check" else [f"Check {i+1}" for i in range(len(clean_data))]
            )
            ax.set_xticklabels(labels)
        elif plot_type == "Pie Chart":
            ax.pie(clean_data, autopct="%1.1f%%", colors=plt.cm.Paired.colors, startangle=140)
            ax.set_title(f"{salary_type} - Pie Chart")

        st.pyplot(fig)
    else:
        st.write(f"No data available for {salary_type}.")
