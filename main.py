import streamlit as st
import pandas as pd
import re
import io 

# 1. PAGE CONFIGURATION & PREMIUM STYLING
st.set_page_config(
    page_title="CSV CleanUp — Privacy-First Formatter",
    page_icon="🔒",
    layout="centered"
) 

st.markdown("""
    <style>
    .stButton>button { background-color: #0c6638; color: white; border-radius: 6px; width: 100%; }
    .stButton>button:hover { background-color: #074d29; color: white; }
    </style>
""", unsafe_allow_html=True)

# Replace with your actual Stripe Payment Link later
STRIPE_PAYMENT_URL = "https://buy.stripe.com/dRmdRa3jf7QAbC00aO6wE00"
STRIPE_LIFETIME_URL = "https://buy.stripe.com/14AeVe2fb1scgWk1eS6wE01"
st.title("🔒 CSV CleanUp")
st.subheader("Format messy spreadsheets for marketing platforms instantly. 100% private.")

# Detect Stripe payment parameter
has_paid = st.query_params.get("status") == "paid"

# 2. BULLETPROOF FILE CLEANING ENGINE
def clean_selected_column(df: pd.DataFrame, col_name: str, clean_type: str) -> pd.DataFrame:
    if df[col_name].dtype == 'object':
        df[col_name] = df[col_name].astype(str).str.strip()
        
    if clean_type == "Phone (UK format for Meta/Google)":
        def format_uk_phone(val):
            if pd.isna(val) or str(val).strip() in ['nan', 'None', '']: return val
            val_str = str(val).strip()
            if 'e+' in val_str.lower(): # Fix Excel scientific notation (e.g., 4.47E+11)
                try: val_str = f"{int(float(val_str))}"
                except: pass
            cleaned = re.sub(r'[\s().+-]', '', val_str)
            if cleaned.startswith('0') and not cleaned.startswith('00'):
                cleaned = '44' + cleaned[1:]
            elif cleaned.startswith('7') and len(cleaned) == 10:
                cleaned = '44' + cleaned
            return cleaned
        df[col_name] = df[col_name].apply(format_uk_phone)
        
    elif clean_type == "Email (Typo Fixer)":
        def fix_email_errors(val):
            if pd.isna(val) or str(val).strip() in ['nan', 'None', '']: return val
            email = str(val).lower().strip()
            typos = {r'.con$': '.com', r'.comn$': '.com', r'gnail.com$': 'gmail.com', r'gamil.com$': 'gmail.com', r'hotmial.com$': 'hotmail.com'}
            for broken, fixed in typos.items():
                email = re.sub(broken, fixed, email)
            return email
        df[col_name] = df[col_name].apply(fix_email_errors)
        
    elif clean_type == "Date (Standardize to YYYY-MM-DD)":
        parsed_dates = pd.to_datetime(df[col_name], errors='coerce', dayfirst=True)
        df[col_name] = parsed_dates.dt.strftime('%Y-%m-%d').fillna(df[col_name])
        
    return df

# 3. SMART FILE LOADER (Fixes the Hidden Encoding Crash)
uploaded_file = st.file_uploader("Drag and drop your messy CSV or XLSX file (Max 20MB)", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Protect server memory size limit
    if uploaded_file.size > 20 * 1024 * 1024:
        st.error("❌ File is too large. Please upload a file smaller than 20MB.")
    else:
        try:
            if uploaded_file.name.endswith('.csv'):
                try:
                    df = pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(uploaded_file, encoding='latin-1')
            else:
                df = pd.read_excel(uploaded_file)
                
            df.columns = [str(col).strip() for col in df.columns]
            st.success("📊 File loaded successfully!")
            
            # 4. COLUMN SELECTORS
            st.markdown("### 🛠️ Step 1: Tell us which columns to fix")
            all_columns = ["-- Skip / Do Not Clean --"] + list(df.columns)
            
            col1, col2, col3 = st.columns(3)
            with col1: phone_col = st.selectbox("Select Phone Column:", all_columns)
            with col2: email_col = st.selectbox("Select Email Column:", all_columns)
            with col3: date_col = st.selectbox("Select Date Column:", all_columns)
                
            if st.button("Clean Data"):
                cleaned_df = df.copy()
                if phone_col != "-- Skip / Do Not Clean --":
                    cleaned_df = clean_selected_column(cleaned_df, phone_col, "Phone (UK format for Meta/Google)")
                if email_col != "-- Skip / Do Not Clean --":
                    cleaned_df = clean_selected_column(cleaned_df, email_col, "Email (Typo Fixer)")
                if date_col != "-- Skip / Do Not Clean --":
                    cleaned_df = clean_selected_column(cleaned_df, date_col, "Date (Standardize to YYYY-MM-DD)")
                    
                st.session_state['cleaned_data'] = cleaned_df
                st.session_state['file_name'] = uploaded_file.name

            # 5. THE PREVIEW HOOK & REFRESH PROTECTION
            if 'cleaned_data' in st.session_state:
                st.markdown("---")
                st.markdown("### 👁️ Free Preview (First 5 Rows Cleaned)")
                st.dataframe(st.session_state['cleaned_data'].head(5))
                
                st.markdown("---")
                st.markdown("### 🔓 Download Full Cleaned File")
                st.write(f"Your complete file has **{len(df)} rows** ready.")
       
            
                    # Payment Verification Shield
    if not has_paid:
        st.warning("🔒 The full download is locked.")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<a href="{STRIPE_PAYMENT_URL}" target="_blank"><button style="padding:12px; font-weight:bold; width:100%; border-radius:6px; background-color:#0c6638; color:white; border:none; cursor:pointer;">Pay £5 (Single Clean)</button></a>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<a href="{STRIPE_LIFETIME_URL}" target="_blank"><button style="padding:12px; font-weight:bold; width:100%; border-radius:6px; background-color:#0284c7; color:white; border:none; cursor:pointer;">Pay £29 (Lifetime Unlimited)</button></a>', unsafe_allow_html=True)

 






                else:
                    st.balloons()
                    st.success("🎉 Payment Confirmed! Your download is unlocked.")
                    csv_buffer = io.StringIO()
                    st.session_state['cleaned_data'].to_csv(csv_buffer, index=False)
                    
                    st.download_button(
                        label="⬇️ Download Full Cleaned CSV",
                        data=csv_buffer.getvalue(),
                        file_name=f"cleaned_{st.session_state['file_name']}",
                        mime="text/css"
                    )
                    
        except Exception as e:
                    st.error("Sorry, this spreadsheet file layout appears to be corrupted or saved incorrectly. Please check the file type, re-save it and try uploading again!")
