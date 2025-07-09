#!/usr/bin/env python3
"""
Core Shipment Processing Logic
Integrates LLM parsing with Excel processing for the complete workflow.
"""

import os
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import asdict

from llm_parser import ChineseShipmentParser, ShipmentData
from excel_processor import ExcelProcessor
from config import get_config, validate_config

class ShipmentProcessingService:
    """Main service for processing Chinese shipment descriptions into Excel"""
    
    def __init__(self, use_api: bool = True, template_path: Optional[str] = None):
        """
        Initialize the shipment processing service
        
        Args:
            use_api: Whether to use OpenAI API (False for fallback-only mode)
            template_path: Path to Excel template file
        """
        self.config = get_config()
        self.use_api = use_api
        
        # Initialize components
        self.parser = ChineseShipmentParser(fallback_only=not use_api)
        self.excel_processor = ExcelProcessor(template_path)
        
        # Validate configuration
        if not validate_config():
            print("Warning: Configuration validation failed")
    
    def process_text_input(self, text_input: str) -> Tuple[List[ShipmentData], List[str]]:
        """
        Process raw text input containing shipment descriptions
        
        Args:
            text_input: Raw text with one or more shipment descriptions
            
        Returns:
            Tuple of (parsed_shipments, error_messages)
        """
        errors = []
        
        if not text_input or not text_input.strip():
            errors.append("Empty input provided")
            return [], errors
        
        try:
            # Parse multiple shipments from text
            shipments = self.parser.parse_multiple_shipments(text_input)
            
            if not shipments:
                errors.append("No valid shipment data could be extracted from input")
                return [], errors
            
            # Auto-complete and validate each shipment
            validated_shipments = []
            completion_info = []

            for i, shipment in enumerate(shipments):
                # Analyze missing fields
                missing_fields = self.excel_processor.analyze_missing_fields(shipment)

                # Auto-complete missing fields
                enhanced_shipment = self.excel_processor.auto_complete_shipment(shipment)

                # Validate the enhanced shipment
                validation_errors = self.excel_processor.validate_shipment_data(enhanced_shipment)

                if validation_errors:
                    errors.extend([f"Shipment {i+1}: {error}" for error in validation_errors])
                else:
                    validated_shipments.append(enhanced_shipment)

                    # Track what was auto-completed
                    if missing_fields:
                        completion_info.append({
                            "shipment_index": i+1,
                            "missing_fields": missing_fields,
                            "auto_completed": True
                        })

            # Add completion info to result for user awareness
            if completion_info:
                for info in completion_info:
                    missing_list = list(info["missing_fields"].keys())
                    errors.append(f"Shipment {info['shipment_index']}: Auto-completed missing fields: {', '.join(missing_list)}")
            
            return validated_shipments, errors
            
        except Exception as e:
            errors.append(f"Error processing input: {str(e)}")
            return [], errors
    
    def process_shipments_to_excel(self, shipments: List[ShipmentData], output_path: Optional[str] = None) -> Tuple[str, List[str]]:
        """
        Process validated shipments and save to Excel
        
        Args:
            shipments: List of validated ShipmentData objects
            output_path: Optional output file path
            
        Returns:
            Tuple of (output_file_path, error_messages)
        """
        errors = []
        
        if not shipments:
            errors.append("No shipments to process")
            return "", errors
        
        try:
            # Create backup of template if it exists
            if os.path.exists(self.excel_processor.template_path):
                backup_path = self.excel_processor.create_backup(self.excel_processor.template_path)
                print(f"Template backup created: {backup_path}")
            
            # Process shipments to Excel
            output_file = self.excel_processor.process_shipments(shipments, output_path)
            
            return output_file, errors
            
        except Exception as e:
            errors.append(f"Error creating Excel file: {str(e)}")
            return "", errors
    
    def process_complete_workflow(self, text_input: str, output_path: Optional[str] = None) -> Dict:
        """
        Complete workflow: parse text input and generate Excel file
        
        Args:
            text_input: Raw Chinese shipment descriptions
            output_path: Optional output file path
            
        Returns:
            Dictionary with processing results and metadata
        """
        result = {
            "success": False,
            "input_text": text_input,
            "parsed_shipments": [],
            "output_file": "",
            "errors": [],
            "warnings": [],
            "statistics": {
                "total_input_length": len(text_input) if text_input else 0,
                "shipments_parsed": 0,
                "shipments_processed": 0,
                "processing_mode": "API" if self.use_api else "Fallback"
            }
        }
        
        try:
            # Step 1: Parse input text
            shipments, parse_errors = self.process_text_input(text_input)
            result["errors"].extend(parse_errors)
            result["parsed_shipments"] = [asdict(s) for s in shipments]
            result["statistics"]["shipments_parsed"] = len(shipments)
            
            if not shipments:
                return result
            
            # Step 2: Process to Excel
            output_file, excel_errors = self.process_shipments_to_excel(shipments, output_path)
            result["errors"].extend(excel_errors)
            result["output_file"] = output_file
            result["statistics"]["shipments_processed"] = len(shipments) if output_file else 0
            
            # Step 3: Determine success (more lenient criteria)
            # Success if we have output file and at least some valid shipments
            other_errors = [e for e in result["errors"] if "Auto-completed" not in e]
            result["success"] = bool(output_file and shipments and not other_errors)
            
            # Add warnings for common issues
            if result["success"] and result["statistics"]["processing_mode"] == "Fallback":
                result["warnings"].append("Processed using fallback mode - consider setting up OpenAI API for better accuracy")
            
            return result
            
        except Exception as e:
            result["errors"].append(f"Unexpected error in workflow: {str(e)}")
            return result
    
    def get_processing_summary(self, result: Dict) -> str:
        """
        Generate a human-readable summary of processing results
        
        Args:
            result: Result dictionary from process_complete_workflow
            
        Returns:
            Formatted summary string
        """
        summary_lines = []
        
        # Header
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        summary_lines.append(f"Processing Status: {status}")
        summary_lines.append("=" * 50)
        
        # Statistics
        stats = result["statistics"]
        summary_lines.append(f"Input Length: {stats['total_input_length']} characters")
        summary_lines.append(f"Processing Mode: {stats['processing_mode']}")
        summary_lines.append(f"Shipments Parsed: {stats['shipments_parsed']}")
        summary_lines.append(f"Shipments Processed: {stats['shipments_processed']}")
        
        # Output file
        if result["output_file"]:
            summary_lines.append(f"Output File: {result['output_file']}")
        
        # Parsed shipments preview
        if result["parsed_shipments"]:
            summary_lines.append("\nParsed Shipments:")
            for i, shipment in enumerate(result["parsed_shipments"], 1):
                product = shipment.get("货物名称", "Unknown")
                price = shipment.get("单价", "N/A")
                courier = shipment.get("快递公司", "N/A")
                summary_lines.append(f"  {i}. {product} - {price} - {courier}")
        
        # Errors
        if result["errors"]:
            summary_lines.append("\nErrors:")
            for error in result["errors"]:
                summary_lines.append(f"  ❌ {error}")
        
        # Warnings
        if result["warnings"]:
            summary_lines.append("\nWarnings:")
            for warning in result["warnings"]:
                summary_lines.append(f"  ⚠️ {warning}")
        
        return "\n".join(summary_lines)

def test_complete_workflow():
    """Test the complete workflow"""
    print("Testing Complete Shipment Processing Workflow")
    print("=" * 60)
    
    # Test input
    test_input = """地板1托30$，快递中通，202242834846，入仓日期2025年7月5号
折叠按摩床一张25$，快递单号：76018395245100010001，入仓日期2025年7月4号
电子产品2箱，单价50$，顺丰快递，单号12345678901234，2025-07-06入仓"""
    
    # Initialize service (fallback mode for testing)
    service = ShipmentProcessingService(use_api=False)
    
    # Process complete workflow
    result = service.process_complete_workflow(test_input)
    
    # Print summary
    summary = service.get_processing_summary(result)
    print(summary)
    
    # Print detailed result
    print("\n" + "=" * 60)
    print("Detailed Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_complete_workflow()
