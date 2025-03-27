# New Section: SKU Lookup App

"""
Goal:
Build a simple app or script that takes a punch or die SKU and returns the corresponding product description.

Requirements:
1. Input: SKU (e.g., "VPL-RND-0375" or "313-OBL-0500-0750")
2. Output: Description (e.g., "3/8 Round punch, no keyways" or "1/2 x 3/4 Oblong die")
3. Must support both punches and dies
4. Description generation logic must match existing formatting rules:
   - Use simplified mixed fractions (e.g., "1 1/32")
   - Format: [Width (and Length if applicable)] + [Shape] + [punch/die] + [keyway description if punch]

Options:
- Option A: Python script with a CSV/Excel lookup file
- Option B: Web app (Flask or Streamlit)
- Option C: Excel + VBA formula-based tool

Phase 1 Plan (Python CLI version):
- Load SKU master spreadsheet (CSV/Excel)
- Parse it into a dictionary: {SKU: Description}
- User inputs a SKU, app returns the description or error if not found

Phase 2 Plan (Optional):
- Upgrade to Streamlit app
- Add batch lookup (e.g., upload list of SKUs)
- Possibly allow reverse lookup (search by dimension/shape)
"""

import pandas as pd
import streamlit as st

@st.cache_data
def load_sku_database(filepath):
    xls = pd.ExcelFile(filepath)
    sku_lookup = {}
    all_descriptions = []
    for sheet in xls.sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name=sheet, usecols=lambda x: x.lower() in ['sku', 'description'])
            df = df.dropna(subset=['SKU', 'Description'])
            sku_lookup.update(dict(zip(df['SKU'].astype(str), df['Description'].astype(str))))
            all_descriptions.append(df['Description'].astype(str))
        except:
            continue
    description_df = pd.concat(all_descriptions, ignore_index=True)
    return sku_lookup, description_df

def main():
    st.title("SKU Lookup App")
    st.write("Enter a punch or die SKU to get its description, upload a list of SKUs, or search descriptions by shape or dimension.")

    uploaded_file = st.file_uploader("Upload SKU Master Excel File", type=["xlsx"])

    if uploaded_file:
        with st.spinner("Loading SKU data..."):
            sku_lookup, description_df = load_sku_database(uploaded_file)

        # Single lookup
        st.subheader("Single SKU Lookup")
        sku_input = st.text_input("Enter SKU:")
        if sku_input:
            description = sku_lookup.get(sku_input.strip(), "SKU not found.")
            st.markdown(f"**Description:** {description}")

        # Batch lookup
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
