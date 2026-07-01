import streamlit as st
from fpdf import FPDF
import io
import os
from main import run_aso_process

st.set_page_config(page_title="ASO AI Agent", page_icon="📱", layout="wide")

# PDF Generation Function
def create_pdf(aso_copy, marketing, design):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "ASO AI Agent Report", ln=True, align="C")
    
    pdf.set_font("Arial", '', 12)
    
    sections = [
        ("ASO Copy (Title & Description)", aso_copy),
        ("Marketing Launch Strategy", marketing),
        ("UI/UX Screenshot Ideas", design)
    ]
    
    for title, content in sections:
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, title, ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", '', 11)
        
        # Replace complex markdown and non-latin-1 characters
        clean_content = content.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, clean_content)
        
    try:
        return pdf.output()
    except Exception as e:
        return pdf.output(dest='S').encode('latin-1')

st.title("🚀 App Store Optimization (ASO) AI Agent")
st.markdown("Enter your app's niche and the IDs of your top competitors to generate a complete ASO strategy, marketing plan, and screenshot designs.")

with st.sidebar:
    st.header("Configuration")
    st.info("Make sure you have set your API Keys in the `.env` file.")
    target_niche = st.text_input("Target Niche", value="OCR Scanner", help="E.g., OCR Scanner, Meditation App, Habit Tracker")
    competitors_input = st.text_area("Competitor App IDs (comma-separated)", value="com.adobe.scan.android, com.intsig.camscanner", help="E.g., com.adobe.scan.android, com.whatsapp")
    generate_btn = st.button("Generate ASO Strategy", type="primary")

if generate_btn:
    competitors_list = [c.strip() for c in competitors_input.split(",") if c.strip()]
    if not competitors_list:
        st.error("Please enter at least one competitor App ID.")
    elif not target_niche:
        st.error("Please enter a target niche.")
    else:
        with st.spinner("Our AI Agents are researching, writing, and designing... This may take a few minutes."):
            try:
                # Call our main logic
                results = run_aso_process(competitors_list, target_niche)
                
                st.success("ASO Strategy generated successfully!")
                
                # Display results in tabs
                tab1, tab2, tab3 = st.tabs(["✍️ ASO Copy", "📈 Marketing Plan", "🎨 UI/UX Design"])
                
                with tab1:
                    st.markdown("### App Titles & Descriptions")
                    st.markdown(results.get("aso_copy", "No data generated."))
                    
                with tab2:
                    st.markdown("### Launch Strategy & Ads")
                    st.markdown(results.get("marketing", "No data generated."))
                    
                with tab3:
                    st.markdown("### Screenshot Concepts")
                    st.markdown(results.get("design", "No data generated."))
                
                # Generate PDF
                pdf_bytes = create_pdf(
                    results.get("aso_copy", ""),
                    results.get("marketing", ""),
                    results.get("design", "")
                )
                
                if isinstance(pdf_bytes, bytearray):
                    pdf_bytes = bytes(pdf_bytes)
                elif isinstance(pdf_bytes, str):
                    pdf_bytes = pdf_bytes.encode('latin-1', 'replace')
                
                st.download_button(
                    label="📥 Download Full Report (PDF)",
                    data=pdf_bytes,
                    file_name="ASO_Strategy_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
