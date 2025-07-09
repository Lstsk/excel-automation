#!/usr/bin/env python3
"""
Configuration settings for the Smart Shipment Entry Tool
"""

import os
from typing import Dict, Any

# OpenAI Configuration
OPENAI_CONFIG = {
    "model": os.getenv("OPENAI_MODEL", "gpt-4"),
    "temperature": 0.1,
    "max_tokens": 500,
    "timeout": 30
}

# Excel Template Configuration
EXCEL_CONFIG = {
    "template_file": "Template.xlsx",
    "sheet_name": "环亚客户自行申报货物表",
    "data_start_row": 9,  # First row where shipment data begins
    "header_row": 8,      # Row with Chinese headers
    "columns": {
        "case_number": "A",      # 货物件数 (Number)
        "package_unit": "B",     # 包装单位 (Unit)
        "chinese_name": "C",     # 中文品名 (Description - Chinese)
        "english_name": "D",     # 英文品名 (Description - English)
        "quantity": "E",         # 内部规格x数量 (Pkg Spec*Qty)
        "unit_price": "F",       # 美金单价 (Unit Value)
        "total_price": "G",      # 美金总价 (Total Value)
        "volume": "H",           # 体积(可不填) (Cbm Optional)
        "weight": "I",           # 毛重(可不填) (GW Optional)
        "courier": "J",          # 快递公司 (Courier)
        "courier_no": "K",       # 快递单号 (Courier No.)
        "receipt_date": "L"      # 入仓日期月/日 (Receipt Date)
    }
}

# Field Mapping from LLM output to Excel columns
FIELD_MAPPING = {
    "货物名称": "chinese_name",
    "数量/单位": "quantity",
    "单价": "unit_price",
    "快递公司": "courier",
    "快递单号": "courier_no",    # Now mapped to column K
    "入仓日期": "receipt_date",  # Now mapped to column L
    "英文品名": "english_name"
}

# Default values for Excel fields
DEFAULT_VALUES = {
    "package_unit": "",  # Usually empty
    "volume": "",        # Optional
    "weight": "",        # Optional
    "english_name": ""   # Can be empty if not provided
}

# Output Configuration
OUTPUT_CONFIG = {
    "output_dir": "output",
    "backup_dir": "output/backups",
    "filename_format": "updated_declaration_{timestamp}.xlsx",
    "timestamp_format": "%Y%m%d_%H%M%S"
}

# Validation Rules
VALIDATION_RULES = {
    "required_fields": ["货物名称"],  # Only product name is truly required
    "price_pattern": r"^\d+(?:\.\d{1,2})?$",  # Numeric price after cleaning
    "date_format": "%Y-%m-%d",
    "max_product_name_length": 100,  # Increased for longer product names
    "max_courier_name_length": 30,
    "min_fields_for_success": 2  # At least product name + one other field
}

# Courier Company Mappings (normalize variations)
COURIER_MAPPINGS = {
    "中通": "中通快递",
    "顺丰": "顺丰快递", 
    "圆通": "圆通快递",
    "申通": "申通快递",
    "韵达": "韵达快递",
    "百世": "百世快递",
    "德邦": "德邦快递",
    "京东": "京东快递",
    "菜鸟": "菜鸟快递"
}

def get_config() -> Dict[str, Any]:
    """Get complete configuration"""
    return {
        "openai": OPENAI_CONFIG,
        "excel": EXCEL_CONFIG,
        "field_mapping": FIELD_MAPPING,
        "defaults": DEFAULT_VALUES,
        "output": OUTPUT_CONFIG,
        "validation": VALIDATION_RULES,
        "courier_mappings": COURIER_MAPPINGS
    }

def validate_config() -> bool:
    """Validate configuration settings"""
    # Check if template file exists
    template_path = EXCEL_CONFIG["template_file"]
    if not os.path.exists(template_path):
        print(f"Warning: Template file not found: {template_path}")
        return False
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set")
        return False
    
    # Create output directories if they don't exist
    os.makedirs(OUTPUT_CONFIG["output_dir"], exist_ok=True)
    os.makedirs(OUTPUT_CONFIG["backup_dir"], exist_ok=True)
    
    return True

if __name__ == "__main__":
    config = get_config()
    print("Configuration loaded successfully:")
    for key, value in config.items():
        print(f"  {key}: {type(value).__name__}")
    
    print(f"\nValidation: {'✓ Passed' if validate_config() else '✗ Failed'}")
