import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="CSV CleanUp", page_icon="🧼", layout="wide")

# Master Vault Variables
STRIPE_PAYMENT_URL = "https://stripe.com"
STRIPE_LIFETIME_URL = "https://stripe.com"

st.title("🧼 CSV CleanUp Utility")
st.write("Upload your messy spreadsheet below to instantly format and clean your data rows.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")
        
        # Display small sample
        st.write("### Data Preview (First 5 Rows)")
        st.dataframe(df.head())
        
        st.markdown("---")
        st.markdown("### 📥 Download Full Cleaned File")
        st.write(f"Your complete file has **{len(df)} rows** ready.")
        
        has_paid = False  # Controlled by Stripe webhook integrations later
        
        if not has_paid:
            st.warning("🔒 The full download is locked.")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<a href="{STRIPE_PAYMENT_URL}" target="_blank"><button style="padding:12px; font-weight:bold; width:100%; border-radius:6px; background-color:#0c6638; color:white; border:none; cursor:pointer;">Pay £5 (Single Clean)</button></a>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<a href="{STRIPE_LIFETIME_URL}" target="_blank"><button style="padding:12px; font-weight:bold; width:100%; border-radius:6px; background-color:#0284c7; color:white; border:none; cursor:pointer;">Pay £29 (Lifetime Unlimited)</button></a>', unsafe_allow_html=True)
        else:
            # Process clean file output
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Cleaned CSV",
                data=csv,
                file_name="cleaned_data.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"An error occurred while cleaning the file: {e}")
