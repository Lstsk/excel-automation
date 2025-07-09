# 📦 Smart Shipment Entry Tool (LLM-Powered)

🎯 **Project Objective**: Create a smart, AI-powered tool that automatically extracts and translates Chinese shipment notes into your existing Excel template format with intelligent field completion.

## ✨ Key Features

### 🧠 AI-Powered Processing
- **Natural Language Input**: Paste Chinese shipment descriptions in natural language
- **GPT-4 Integration**: Uses OpenAI GPT-4 for accurate parsing (with regex fallback)
- **Smart Field Completion**: Automatically fills missing information where possible
- **Multi-Language Support**: Handles Chinese input with English translation

### 📊 Excel Integration
- **Template Preservation**: Works with your existing Excel template structure
- **Complete Column Mapping**: Supports all 12 columns including tracking numbers and dates
- **Auto-Backup**: Creates backups before modifications
- **Formula Preservation**: Maintains Excel formulas (e.g., total price calculations)

### 🔧 Intelligent Auto-Completion
- **Quantity Extraction**: Automatically extracts quantities from product names (1托, 2箱, etc.)
- **English Translation**: Auto-translates common Chinese product names
- **Date Formatting**: Converts dates to proper MM/DD format
- **Courier Normalization**: Standardizes courier company names
- **Missing Field Analysis**: Shows what's missing and why it's important

### 🌐 Web Interface
- **User-Friendly UI**: Clean Streamlit web interface
- **Batch Processing**: Handle multiple shipments at once
- **Real-time Feedback**: Shows processing status and auto-completion info
- **Download Integration**: Instant Excel file download
- **Processing History**: Track previous operations

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone or download the project
cd excel-automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key (Optional)
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key for better accuracy
# OPENAI_API_KEY=your_api_key_here
```
**Note**: The system works without an API key using intelligent regex fallback parsing.

### 3. Add Your Excel Template
- Place your Excel template in the root directory as `Template.xlsx`
- The system will automatically detect and use this template

### 4. Run the Application
```bash
streamlit run app.py
```
- Open your browser to `http://localhost:8501`
- Start processing shipments immediately!

## 📝 Usage Guide

### Input Format
Enter Chinese shipment descriptions, one per line. The system intelligently extracts:

| Field | Chinese | Example | Auto-Completion |
|-------|---------|---------|-----------------|
| Product Name | 货物名称 | 地板, 按摩床 | ○ Manual input |
| Quantity | 数量 | 1托, 2箱 | ✓ Extracted from product name |
| Price | 单价 | 30$, 25美金 | ✓ Currency normalization |
| Courier | 快递公司 | 中通, 顺丰 | ✓ Name standardization |
| Tracking | 快递单号 | 202242834846 | ○ Manual input |
| Date | 入仓日期 | 2025年7月5号 | ✓ Auto-format + today's date |
| English Name | 英文品名 | - | ✓ Common translations |

### Example Inputs
```
地板1托30$，快递中通，202242834846，入仓日期2025年7月5号
折叠按摩床一张25$，快递单号：76018395245100010001，入仓日期2025年7月4号
电子产品2箱，单价50$，顺丰快递，2025-07-06入仓
```

### Excel Output Structure
The system fills all 12 columns in your Excel template:

| Column | English Header | Chinese Header | Auto-Filled |
|--------|---------------|----------------|--------------|
| A | Number | 货物件数 | ✓ Case 1, Case 2... |
| B | Unit | 包装单位 | ○ Empty (not used) |
| C | Description | 中文品名 | ✓ From input |
| D | Description | 英文品名 | ✓ Auto-translated |
| E | Pkg Spec*Qty | 内部规格x数量 | ✓ Complete quantity (1托, 2箱) |
| F | Unit Value | 美金单价 | ✓ Cleaned price |
| G | Total Value | 美金总价 | ✓ Excel formula |
| H | Cbm (Optional) | 体积 | ○ Empty |
| I | GW (Optional) | 毛重 | ○ Empty |
| J | Courier | 快递公司 | ✓ Normalized |
| K | Courier No. | 快递单号 | ✓ From input |
| L | Receipt Date | 入仓日期月/日 | ✓ MM/DD format |

## 🏗️ Project Structure

```
excel-automation/
├── app.py                           # 🌐 Main Streamlit web application
├── Template.xlsx                    # 📋 Excel template file
├── src/
│   ├── config.py                   # ⚙️ Configuration management
│   ├── excel_processor.py          # 📊 Excel reading/writing + auto-completion
│   ├── llm_parser.py               # 🧠 OpenAI GPT + regex parsing
│   ├── shipment_processor.py       # ⚙️ Core workflow integration
│   └── template_analyzer.py        # 📋 Template structure analysis
├── tests/
│   └── test_comprehensive.py       # 🧪 Full test suite
├── docs/
│   ├── DEPLOYMENT_GUIDE.md         # 🚀 Deployment instructions
│   └── excel_template_analysis.md  # 📋 Template structure documentation
├── output/                         # 📁 Generated Excel files
│   └── backups/                    # 💾 Automatic backups
├── venv/                           # 🐍 Python virtual environment
├── requirements.txt                # 📦 Python dependencies
├── .gitignore                      # 🚫 Git ignore rules
└── README.md                       # 📖 This documentation
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
# Run all tests
python tests/test_comprehensive.py
```

**Test Results**: ✅ 16/16 tests passing, 0.002s per shipment processing time

## 🚀 Deployment Options

### Option 1: Local Desktop Use
- Run `streamlit run app.py` locally
- Access via `http://localhost:8501`
- Best for personal/team use

### Option 2: Streamlit Cloud (Recommended)
1. Push code to GitHub repository
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy with one click
4. Share public URL with team

### Option 3: Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🔧 Advanced Configuration

### Custom Excel Templates
Update `src/config.py` to use different templates:
```python
EXCEL_CONFIG = {
    "template_file": "your_template.xlsx",
    "sheet_name": "your_sheet_name",
    # ... column mappings
}
```

### API Configuration
```bash
# .env file
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo
```

## 🤝 Development

This project follows a modular architecture:
- **Parser Layer**: Handles Chinese text parsing and field extraction
- **Processing Layer**: Manages Excel operations and auto-completion
- **Service Layer**: Integrates all components with workflow management
- **UI Layer**: Provides web interface and user interaction
