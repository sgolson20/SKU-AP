import pandas as pd
import streamlit as st

@st.cache_data
def load_sku_database():
    # Use your raw GitHub file URL here
    file_url = "https://view.officeapps.live.com/op/view.aspx?src=https%3A%2F%2Fraw.githubusercontent.com%2Fsgolson20%2FSKU-AP%2Frefs%2Fheads%2Fmain%2FSKU%2520NUMBERS%2520FINAL%2520-%2520SO.xlsx&wdOrigin=BROWSELINK"
    
    # Load the Excel file directly from the URL
    xls = pd.ExcelFile(file_url)
    sku_lookup = {}
    all_descriptions = []
    
    for sheet in xls.sheet_names:
        try:
            # Read the 'SKU' and 'Description' columns from the file
            df = pd.read_excel(xls, sheet_name=sheet, usecols=lambda x: x.lower() in ['sku', 'description'])
            df = df.dropna(subset=['SKU', 'Description'])  # Remove rows with missing data
            sku_lookup.update(dict(zip(df['SKU'].astype(str), df['Description'].astype(str))))  # Add SKUs to the lookup dictionary
            all_descriptions.append(df['Description'].astype(str))  # Collect descriptions for reverse search
        except:
            continue
    
    description_df = pd.concat(all_descriptions, ignore_index=True)
    return sku_lookup, description_df

def main():
    st.title("SKU Lookup App")
    st.write("Enter a punch or die SKU to get its description, upload a list of SKUs, or search descriptions by shape or dimension.")

    # Load SKU data directly from the GitHub URL
    with st.spinner("Loading SKU data..."):
        sku_lookup, description_df = load_sku_database()

    # Single SKU lookup
    st.subheader("Single SKU Lookup")
    sku_input = st.text_input("Enter SKU:")
    if sku_input:
        description = sku_lookup.get(sku_input.strip(), "SKU not found.")
        st.markdown(f"**Description:** {description}")

    # Batch SKU lookup
    st.subheader("Batch SKU Lookup")
    batch_file = st.file_uploader("Upload Excel or CSV file with a column of SKUs", type=["xlsx", "csv"], key="batch")

    if batch_file:
        try:
            if batch_file.name.endswith(".csv"):
                batch_df = pd.read_csv(batch_file)
            else:
                batch_df = pd.read_excel(batch_file)

            sku_col = next((col for col in batch_df.columns if col.lower() == 'sku'), None)
            if sku_col is None:
                st.error("No 'SKU' column found in uploaded file.")
            else:
                batch_df['Description'] = batch_df[sku_col].astype(str).map(lambda x: sku_lookup.get(x.strip(), "SKU not found."))
                st.success("Batch lookup complete.")
                st.dataframe(batch_df)

                st.download_button(
                    label="Download Results as Excel",
                    data=batch_df.to_excel(index=False, engine='openpyxl'),
                    file_name="sku_lookup_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"Error processing file: {e}")

    # Reverse lookup
    st.subheader("Reverse Lookup: Search Descriptions")
    search_term = st.text_input("Enter keyword or dimension (e.g., '1/2', 'Hex', 'Rectangle punch'):", key="reverse")
    if search_term:
        results = description_df[description_df.str.contains(search_term, case=False, na=False)]
        if not results.empty:
            st.write(f"Found {len(results)} matching descriptions:")
            st.dataframe(results.reset_index(drop=True))
        else:
            st.write("No matching descriptions found.")

if __name__ == '__main__':
    main()
