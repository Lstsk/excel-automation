#!/usr/bin/env python3
"""
Comprehensive Test Suite for Smart Shipment Entry Tool
Tests various Chinese shipment inputs and validates Excel output formatting.
"""

import sys
import os
import unittest
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from llm_parser import ChineseShipmentParser, ShipmentData
from excel_processor import ExcelProcessor
from shipment_processor import ShipmentProcessingService
from config import get_config

class TestChineseShipmentParser(unittest.TestCase):
    """Test the Chinese shipment parser"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = ChineseShipmentParser(fallback_only=True)  # Use fallback for testing
    
    def test_basic_parsing(self):
        """Test basic shipment parsing"""
        test_input = "地板1托30$，快递中通，202242834846，入仓日期2025年7月5号"
        result = self.parser.parse_shipment_text(test_input)
        
        self.assertIn("地板", result.货物名称)
        self.assertEqual(result.单价, "30$")
        self.assertEqual(result.快递公司, "中通")
        self.assertEqual(result.快递单号, "202242834846")
        self.assertEqual(result.入仓日期, "2025-07-05")
    
    def test_multiple_shipments(self):
        """Test parsing multiple shipments"""
        test_input = """地板1托30$，快递中通，202242834846，入仓日期2025年7月5号
折叠按摩床一张25$，快递单号：76018395245100010001，入仓日期2025年7月4号"""
        
        results = self.parser.parse_multiple_shipments(test_input)
        self.assertEqual(len(results), 2)
        
        # Check first shipment
        self.assertIn("地板", results[0].货物名称)
        self.assertEqual(results[0].单价, "30$")
        
        # Check second shipment
        self.assertIn("折叠按摩床", results[1].货物名称)
        self.assertEqual(results[1].单价, "25$")
    
    def test_price_extraction(self):
        """Test various price formats"""
        test_cases = [
            ("商品30$", "30$"),
            ("商品25美金", "25$"),
            ("商品50元", "50$"),
            ("商品100.50$", "100.50$")
        ]
        
        for input_text, expected_price in test_cases:
            result = self.parser.parse_shipment_text(input_text)
            self.assertEqual(result.单价, expected_price, f"Failed for input: {input_text}")
    
    def test_courier_extraction(self):
        """Test courier company extraction"""
        test_cases = [
            ("商品，中通快递", "中通"),
            ("商品，顺丰", "顺丰"),
            ("商品，圆通快递", "圆通"),
            ("商品，申通", "申通")
        ]
        
        for input_text, expected_courier in test_cases:
            result = self.parser.parse_shipment_text(input_text)
            self.assertEqual(result.快递公司, expected_courier, f"Failed for input: {input_text}")
    
    def test_date_extraction(self):
        """Test date extraction and formatting"""
        test_cases = [
            ("商品，入仓日期2025年7月5号", "2025-07-05"),
            ("商品，2025-07-04入仓", "2025-07-04"),
            ("商品，7月6号入仓", f"{datetime.now().year}-07-06")
        ]
        
        for input_text, expected_date in test_cases:
            result = self.parser.parse_shipment_text(input_text)
            self.assertEqual(result.入仓日期, expected_date, f"Failed for input: {input_text}")

class TestExcelProcessor(unittest.TestCase):
    """Test the Excel processor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = ExcelProcessor()
        self.sample_shipments = [
            ShipmentData(
                货物名称="测试商品1",
                数量="1个",
                单价="30$",
                快递公司="中通快递",
                快递单号="123456789",
                入仓日期="2025-07-05"
            ),
            ShipmentData(
                货物名称="测试商品2",
                数量="2箱",
                单价="25$",
                快递公司="顺丰快递",
                快递单号="987654321",
                入仓日期="2025-07-04"
            )
        ]
    
    def test_template_loading(self):
        """Test Excel template loading"""
        wb, ws = self.processor.load_template()
        self.assertIsNotNone(wb)
        self.assertIsNotNone(ws)
    
    def test_price_cleaning(self):
        """Test price cleaning functionality"""
        test_cases = [
            ("30$", "30"),
            ("25美金", "25"),
            ("100.50$", "100.50"),
            ("", "")
        ]
        
        for input_price, expected in test_cases:
            result = self.processor.clean_price(input_price)
            self.assertEqual(result, expected, f"Failed for input: {input_price}")
    
    def test_courier_normalization(self):
        """Test courier name normalization"""
        test_cases = [
            ("中通", "中通快递"),
            ("顺丰", "顺丰快递"),
            ("中通快递", "中通快递"),  # Already normalized
            ("", "")
        ]
        
        for input_courier, expected in test_cases:
            result = self.processor.normalize_courier(input_courier)
            self.assertEqual(result, expected, f"Failed for input: {input_courier}")
    
    def test_shipment_validation(self):
        """Test shipment data validation"""
        # Valid shipment
        valid_shipment = ShipmentData(货物名称="测试商品", 单价="30$")
        errors = self.processor.validate_shipment_data(valid_shipment)
        self.assertEqual(len(errors), 0)
        
        # Invalid shipment (missing required field)
        invalid_shipment = ShipmentData(货物名称="", 单价="30$")
        errors = self.processor.validate_shipment_data(invalid_shipment)
        self.assertGreater(len(errors), 0)
    
    def test_excel_processing(self):
        """Test complete Excel processing"""
        output_path = self.processor.process_shipments(self.sample_shipments)
        
        # Check that file was created
        self.assertTrue(os.path.exists(output_path))
        
        # Clean up
        if os.path.exists(output_path):
            os.remove(output_path)

class TestShipmentProcessingService(unittest.TestCase):
    """Test the complete shipment processing service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = ShipmentProcessingService(use_api=False)  # Use fallback mode
    
    def test_complete_workflow(self):
        """Test the complete processing workflow"""
        test_input = """地板1托30$，快递中通，202242834846，入仓日期2025年7月5号
折叠按摩床一张25$，快递单号：76018395245100010001，入仓日期2025年7月4号"""
        
        result = self.service.process_complete_workflow(test_input)
        
        # Check basic result structure
        self.assertIn('success', result)
        self.assertIn('parsed_shipments', result)
        self.assertIn('output_file', result)
        self.assertIn('statistics', result)
        
        # Check that shipments were parsed
        self.assertGreater(result['statistics']['shipments_parsed'], 0)
        
        # Clean up output file if created
        if result['output_file'] and os.path.exists(result['output_file']):
            os.remove(result['output_file'])
    
    def test_empty_input(self):
        """Test handling of empty input"""
        result = self.service.process_complete_workflow("")
        
        self.assertFalse(result['success'])
        self.assertIn('errors', result)
        self.assertGreater(len(result['errors']), 0)
    
    def test_processing_summary(self):
        """Test processing summary generation"""
        test_input = "地板1托30$，快递中通，202242834846，入仓日期2025年7月5号"
        result = self.service.process_complete_workflow(test_input)
        
        summary = self.service.get_processing_summary(result)
        self.assertIsInstance(summary, str)
        self.assertIn("Processing Status", summary)
        
        # Clean up
        if result['output_file'] and os.path.exists(result['output_file']):
            os.remove(result['output_file'])

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = ChineseShipmentParser(fallback_only=True)
        self.service = ShipmentProcessingService(use_api=False)
    
    def test_malformed_input(self):
        """Test handling of malformed input"""
        test_cases = [
            "随机文本没有结构",
            "123456789",
            "！@#￥%……&*（）",
            "English text mixed with 中文"
        ]
        
        for test_input in test_cases:
            result = self.parser.parse_shipment_text(test_input)
            # Should not crash, even if extraction is minimal
            self.assertIsInstance(result, ShipmentData)
    
    def test_very_long_input(self):
        """Test handling of very long input"""
        long_input = "地板1托30$，快递中通，" + "很长的描述" * 100
        result = self.parser.parse_shipment_text(long_input)
        self.assertIsInstance(result, ShipmentData)
    
    def test_special_characters(self):
        """Test handling of special characters"""
        test_input = "特殊商品！@#30$，快递中通，123456，入仓日期2025年7月5号"
        result = self.parser.parse_shipment_text(test_input)
        
        self.assertIn("特殊商品", result.货物名称)
        self.assertEqual(result.单价, "30$")

def run_performance_test():
    """Run performance tests"""
    print("\n" + "="*60)
    print("PERFORMANCE TESTS")
    print("="*60)
    
    service = ShipmentProcessingService(use_api=False)
    
    # Test with multiple shipments
    large_input = """地板1托30$，快递中通，202242834846，入仓日期2025年7月5号
折叠按摩床一张25$，快递单号：76018395245100010001，入仓日期2025年7月4号
电子产品2箱，单价50$，顺丰快递，单号12345678901234，2025-07-06入仓
家具3件，单价75$，圆通快递，单号98765432109876，2025-07-07入仓
服装5套，单价20$，申通快递，单号11223344556677，2025-07-08入仓""" * 5  # 25 shipments
    
    start_time = datetime.now()
    result = service.process_complete_workflow(large_input)
    end_time = datetime.now()
    
    processing_time = (end_time - start_time).total_seconds()
    
    print(f"Processed {result['statistics']['shipments_parsed']} shipments")
    print(f"Processing time: {processing_time:.2f} seconds")
    print(f"Average time per shipment: {processing_time/result['statistics']['shipments_parsed']:.3f} seconds")
    
    # Clean up
    if result['output_file'] and os.path.exists(result['output_file']):
        os.remove(result['output_file'])

def main():
    """Run all tests"""
    print("Smart Shipment Entry Tool - Comprehensive Test Suite")
    print("="*60)
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance tests
    run_performance_test()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)

if __name__ == "__main__":
    main()
