#!/usr/bin/env python3
"""
Smart Shipment Entry Tool - Streamlit Web Interface
Main application for processing Chinese shipment descriptions into Excel format.
"""

import streamlit as st
import os
import json
from datetime import datetime
import pandas as pd

# Add src to path for imports
import sys
sys.path.append('src')

from shipment_processor import ShipmentProcessingService
from config import get_config, validate_config

# Page configuration
st.set_page_config(
    page_title="Smart Shipment Entry Tool",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'processing_history' not in st.session_state:
        st.session_state.processing_history = []
    if 'current_result' not in st.session_state:
        st.session_state.current_result = None

def display_header():
    """Display the application header"""
    st.title("📦 Smart Shipment Entry Tool")
    st.markdown("### AI-Powered Chinese Shipment Processing")
    st.markdown("Convert Chinese shipment descriptions into structured Excel format automatically.")
    
    # Configuration status
    config_valid = validate_config()
    api_key_set = bool(os.getenv("OPENAI_API_KEY"))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        status = "✅" if config_valid else "⚠️"
        st.metric("Configuration", status)
    with col2:
        api_status = "✅ API Mode" if api_key_set else "⚠️ Fallback Mode"
        st.metric("Processing Mode", api_status)
    with col3:
        template_exists = os.path.exists(get_config()["excel"]["template_file"])
        template_status = "✅" if template_exists else "❌"
        st.metric("Excel Template", template_status)

def display_sidebar():
    """Display the sidebar with settings and information"""
    st.sidebar.header("⚙️ Settings")
    
    # Processing mode selection
    use_api = st.sidebar.checkbox(
        "Use OpenAI API",
        value=bool(os.getenv("OPENAI_API_KEY")),
        help="Enable for better parsing accuracy. Requires OpenAI API key."
    )
    
    # Template file info
    st.sidebar.header("📄 Template Information")
    config = get_config()
    template_file = config["excel"]["template_file"]
    
    if os.path.exists(template_file):
        st.sidebar.success(f"✅ Template loaded: {os.path.basename(template_file)}")
    else:
        st.sidebar.error(f"❌ Template not found: {template_file}")
    
    # Processing history
    st.sidebar.header("📊 Processing History")
    if st.session_state.processing_history:
        for i, entry in enumerate(reversed(st.session_state.processing_history[-5:])):
            timestamp = entry.get('timestamp', 'Unknown')
            status = "✅" if entry.get('success') else "❌"
            shipments_count = entry.get('shipments_processed', 0)
            st.sidebar.text(f"{status} {timestamp}: {shipments_count} items")
    else:
        st.sidebar.text("No processing history yet")
    
    return use_api

def display_input_section():
    """Display the input section"""
    st.header("📝 Input Shipment Descriptions")
    
    # Example text
    example_text = """地板1托30$，快递中通，202242834846，入仓日期2025年7月5号
折叠按摩床一张25$，快递单号：76018395245100010001，入仓日期2025年7月4号
电子产品2箱，单价50$，顺丰快递，单号12345678901234，2025-07-06入仓"""
    
    # Input methods
    input_method = st.radio(
        "Choose input method:",
        ["Text Input", "Use Example", "File Upload"],
        horizontal=True
    )
    
    text_input = ""
    
    if input_method == "Text Input":
        text_input = st.text_area(
            "Paste your Chinese shipment descriptions here:",
            height=150,
            placeholder="地板1托30$，快递中通，202242834846，入仓日期2025年7月5号\n折叠按摩床一张25$，快递单号：76018395245100010001，入仓日期2025年7月4号"
        )
    
    elif input_method == "Use Example":
        st.info("Using example shipment data for demonstration")
        text_input = example_text
        st.text_area("Example data:", value=example_text, height=100, disabled=True)
    
    elif input_method == "File Upload":
        uploaded_file = st.file_uploader(
            "Upload a text file with shipment descriptions",
            type=['txt'],
            help="Upload a .txt file containing Chinese shipment descriptions"
        )
        if uploaded_file:
            text_input = str(uploaded_file.read(), "utf-8")
            st.text_area("File content:", value=text_input, height=100, disabled=True)
    
    return text_input

def display_processing_section(text_input, use_api):
    """Display the processing section and handle processing"""
    st.header("⚙️ Processing")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        process_button = st.button("🚀 Process Shipments", type="primary", use_container_width=True)
    
    with col2:
        clear_button = st.button("🗑️ Clear Results", use_container_width=True)
    
    if clear_button:
        st.session_state.current_result = None
        st.rerun()
    
    if process_button and text_input.strip():
        with st.spinner("Processing shipment descriptions..."):
            try:
                # Initialize service with fallback if API has issues
                try:
                    service = ShipmentProcessingService(use_api=use_api)
                except Exception as e:
                    st.warning(f"API initialization failed: {str(e)}. Using fallback mode.")
                    service = ShipmentProcessingService(use_api=False)

                # Process the input
                result = service.process_complete_workflow(text_input)
                
                # Store result
                st.session_state.current_result = result
                
                # Add to history
                history_entry = {
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'success': result['success'],
                    'shipments_processed': result['statistics']['shipments_processed'],
                    'processing_mode': result['statistics']['processing_mode']
                }
                st.session_state.processing_history.append(history_entry)
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Processing failed: {str(e)}")
    
    elif process_button and not text_input.strip():
        st.warning("Please enter some shipment descriptions to process.")

def display_results_section():
    """Display processing results"""
    if not st.session_state.current_result:
        return
    
    result = st.session_state.current_result
    
    st.header("📊 Processing Results")
    
    # Status indicator
    if result['success']:
        st.success("✅ Processing completed successfully!")
    else:
        st.error("❌ Processing failed")
    
    # Statistics
    stats = result['statistics']
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Input Length", f"{stats['total_input_length']} chars")
    with col2:
        st.metric("Shipments Parsed", stats['shipments_parsed'])
    with col3:
        st.metric("Shipments Processed", stats['shipments_processed'])
    with col4:
        st.metric("Processing Mode", stats['processing_mode'])
    
    # Parsed shipments preview
    if result['parsed_shipments']:
        st.subheader("📦 Parsed Shipments")
        
        # Convert to DataFrame for better display
        df_data = []
        for i, shipment in enumerate(result['parsed_shipments'], 1):
            df_data.append({
                "Item": i,
                "Product Name (货物名称)": shipment.get('货物名称', ''),
                "Quantity (数量)": shipment.get('数量', ''),
                "Unit (单位)": shipment.get('单位', ''),
                "Price (单价)": shipment.get('单价', ''),
                "Courier (快递公司)": shipment.get('快递公司', ''),
                "Tracking (快递单号)": shipment.get('快递单号', ''),
                "Date (入仓日期)": shipment.get('入仓日期', ''),
                "English Name (英文品名)": shipment.get('英文品名', '')
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
    
    # Download section
    if result['success'] and result['output_file']:
        st.subheader("📥 Download Results")
        
        if os.path.exists(result['output_file']):
            with open(result['output_file'], 'rb') as file:
                file_data = file.read()
            
            filename = os.path.basename(result['output_file'])
            st.download_button(
                label="📊 Download Excel File",
                data=file_data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
            
            st.info(f"File saved locally: {result['output_file']}")
        else:
            st.error("Output file not found")
    
    # Field completion info
    auto_completion_errors = [error for error in result['errors'] if 'Auto-completed missing fields' in error]
    if auto_completion_errors:
        st.subheader("🔧 Auto-Completed Fields")
        st.info("The system automatically filled in missing information where possible:")
        for error in auto_completion_errors:
            st.write(f"• {error}")

    # Other errors (excluding auto-completion info)
    other_errors = [error for error in result['errors'] if 'Auto-completed missing fields' not in error]
    if other_errors:
        st.subheader("❌ Errors")
        for error in other_errors:
            st.error(error)

    if result['warnings']:
        st.subheader("⚠️ Warnings")
        for warning in result['warnings']:
            st.warning(warning)

def display_help_section():
    """Display help and usage information"""
    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        ### Input Format
        Enter Chinese shipment descriptions, one per line. Each description should contain:
        - **Product name** (货物名称): What you're shipping
        - **Price** (单价): Cost with currency (30$, 25美金, etc.)
        - **Courier** (快递公司): Shipping company (中通, 顺丰, etc.)
        - **Tracking number** (快递单号): Package tracking number
        - **Date** (入仓日期): Warehouse entry date
        
        ### Example Format
        ```
        地板1托30$，快递中通，202242834846，入仓日期2025年7月5号
        折叠按摩床一张25$，快递单号：76018395245100010001，入仓日期2025年7月4号
        ```
        
        ### Features
        - **AI-Powered**: Uses OpenAI GPT-4 for accurate parsing (when API key is provided)
        - **Fallback Mode**: Regex-based parsing when API is not available
        - **Excel Integration**: Automatically fills your existing Excel template
        - **Batch Processing**: Handle multiple shipments at once
        - **Download**: Get the updated Excel file instantly
        """)

def main():
    """Main application function"""
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Display sidebar and get settings
    use_api = display_sidebar()
    
    # Main content
    text_input = display_input_section()
    
    display_processing_section(text_input, use_api)
    
    display_results_section()
    
    display_help_section()
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit and OpenAI GPT-4")

if __name__ == "__main__":
    main()
