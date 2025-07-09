#!/usr/bin/env python3
"""
LLM Parser Module
Uses OpenAI GPT to parse Chinese shipment descriptions and extract structured data.
"""

import json
import re
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class ShipmentData:
    """Structured shipment data"""
    货物名称: str = ""           # Product name
    数量: str = ""              # Quantity (includes unit, e.g., "1托", "2箱")
    单价: str = ""              # Unit price
    快递公司: str = ""           # Courier company
    快递单号: str = ""           # Tracking number
    入仓日期: str = ""           # Warehouse date
    英文品名: str = ""           # English product name (optional)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "货物名称": self.货物名称,
            "数量": self.数量,
            "单价": self.单价,
            "快递公司": self.快递公司,
            "快递单号": self.快递单号,
            "入仓日期": self.入仓日期,
            "英文品名": self.英文品名
        }

class ChineseShipmentParser:
    """Parser for Chinese shipment descriptions using OpenAI GPT"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = None, fallback_only: bool = False):
        """
        Initialize the parser

        Args:
            api_key: API key (if None, will use environment variable)
            model: Model to use (if None, will use environment variable or default)
            fallback_only: If True, only use regex fallback parsing (for testing)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4")
        self.base_url = os.getenv("OPENAI_BASE_URL")  # Support custom base URL for DeepSeek
        self.fallback_only = fallback_only

        if not fallback_only and not self.api_key:
            print("Warning: API key not found. Falling back to regex-only parsing.")
            self.fallback_only = True

        if not self.fallback_only:
            # Initialize client with custom base URL if provided (for DeepSeek)
            client_kwargs = {"api_key": self.api_key}
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            self.client = OpenAI(**client_kwargs)
        else:
            self.client = None
        
        # Advanced system prompt for comprehensive shipment data extraction
        self.system_prompt = """你是一位专业的国际物流数据提取专家，负责从中文货物申报信息中提取标准结构化数据。

---

### 🎯 你的任务：

从每条中文货物描述中，提取以下6个关键字段。请根据语义进行智能识别和标准化处理，确保输出格式准确、清晰。

---

### 📦 提取字段说明：

1. **货物名称 (Product Name)**
   - 提取核心商品名称，排除数量、价格等修饰词。
   - 示例：
     - “地板1托30$” → `"地板"`
     - “折叠按摩床一张25美金” → `"折叠按摩床"`

2. **数量 (Quantity)**
   - 仅提取数字部分，不含单位。
   - 支持阿拉伯数字和中文数字自动转为阿拉伯数字。
   - 示例：
     - “1托” → `"1"`
     - “一张” → `"1"`
     - “三件” → `"3"`

3. **单位 (Unit)**
   - 提取数量后的计量单位词，如：托、张、箱、件、套等。
   - 示例：
     - “1托” → `"托"`
     - “一张” → `"张"`

4. **单价 (Unit Price)**
   - 提取价格数字 + 货币单位。
   - 统一输出格式为：`"数字$"`
   - 示例：
     - “30$”、"25美金" → `"30$"`、`"25$"`

5. **快递公司 (Courier Company)**
   - 提取并标准化常见快递公司名称。
   - 示例：中通、顺丰、圆通、申通、韵达、百世、德邦、京东、EMS

6. **快递单号 (Tracking Number)**
   - 提取10位以上的数字或字母数字组合作为快递单号。
   - 示例：202242834846、SF1234567890、YT987654321

7. **入仓日期 (Receipt Date)**
   - 提取日期并标准化为 `YYYY-MM-DD` 格式
   - 示例：
     - “2025年7月5号” → `"2025-07-05"`
     - “7月6号” → 假设当前年为2025 → `"2025-07-06"`

8. **英文品名 (English Product Name)**
   - 根据中文品名智能翻译为对应英文名。
   - 示例参考：
     - 地板 → Flooring
     - 按摩床 → Massage Table
     - 折叠按摩床 → Folding Massage Table
     - 电子产品 → Electronic Products
     - 家具 → Furniture
     - 工具 → Tools
     - 化妆品 → Cosmetics

---

### 🧠 智能处理要求：

- 允许模糊匹配、同义替换和常识推断
- 支持多样化表达方式
- 日期缺年默认当前年份
- 中文数字自动转换为阿拉伯数字

---

### 📤 输出要求：

- 结果必须为 **标准 JSON 格式**
- 所有字段均包含，即使为空也保留字段
- 不添加任何解释性文字
- 日期格式为严格的 `"YYYY-MM-DD"`
- 价格统一为美元符号 `$` 结尾的格式

---

### ✅ 输出模板：

```json
{
  "货物名称": "",
  "数量": "",
  "单价": "",
  "快递公司": "",
  "快递单号": "",
  "入仓日期": "",
  "英文品名": ""
}
"""

    def parse_shipment_text(self, text: str) -> ShipmentData:
        """
        Parse Chinese shipment description text

        Args:
            text: Chinese shipment description

        Returns:
            ShipmentData object with extracted information
        """
        # If fallback_only mode or no API key, skip API call
        if self.fallback_only or not self.api_key:
            return self._fallback_parse("", text)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=500,
                timeout=10  # 10 second timeout
            )

            # Extract the response content
            content = response.choices[0].message.content.strip()

            # Clean markdown formatting if present
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json
            if content.startswith('```'):
                content = content[3:]   # Remove ```
            if content.endswith('```'):
                content = content[:-3]  # Remove trailing ```
            content = content.strip()

            # Try to parse JSON response
            try:
                data = json.loads(content)
                return ShipmentData(
                    货物名称=data.get("货物名称", ""),
                    数量=data.get("数量", ""),
                    单价=data.get("单价", ""),
                    快递公司=data.get("快递公司", ""),
                    快递单号=data.get("快递单号", ""),
                    入仓日期=data.get("入仓日期", ""),
                    英文品名=data.get("英文品名", "")
                )
            except json.JSONDecodeError as e:
                # If JSON parsing fails, try to extract using regex
                return self._fallback_parse(content, text)

        except Exception as e:
            # Fallback to regex-based parsing
            return self._fallback_parse("", text)
    
    def _fallback_parse(self, llm_response: str, original_text: str) -> ShipmentData:
        """
        Fallback parsing using regex patterns
        
        Args:
            llm_response: Response from LLM (may be malformed)
            original_text: Original input text
            
        Returns:
            ShipmentData with extracted information
        """
        data = ShipmentData()

        # Extract complete quantity with unit
        qty_unit_pattern = r'(\d+|一|二|三|四|五|六|七|八|九|十)(托|箱|个|件|张|套|台|只|条|包|袋|瓶|罐)'
        qty_unit_match = re.search(qty_unit_pattern, original_text)
        if qty_unit_match:
            quantity, unit = qty_unit_match.groups()
            # Convert Chinese numbers to Arabic
            chinese_to_arabic = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
                               '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'}
            num = chinese_to_arabic.get(quantity, quantity)
            data.数量 = f"{num}{unit}"
        
        # Extract price (look for patterns like "30$", "25美金", "50元")
        price_pattern = r'(\d+(?:\.\d+)?)\s*[美金$元]'
        price_match = re.search(price_pattern, original_text)
        if price_match:
            data.单价 = price_match.group(1) + "$"
        
        # Extract tracking number (long sequences of digits)
        tracking_pattern = r'\b\d{10,}\b'
        tracking_match = re.search(tracking_pattern, original_text)
        if tracking_match:
            data.快递单号 = tracking_match.group()
        
        # Extract courier company
        courier_patterns = [
            r'(中通|顺丰|圆通|申通|韵达|百世|德邦|京东|菜鸟)',
            r'(中通快递|顺丰快递|圆通快递)'
        ]
        for pattern in courier_patterns:
            courier_match = re.search(pattern, original_text)
            if courier_match:
                data.快递公司 = courier_match.group(1)
                break
        
        # Extract date (various Chinese date formats)
        date_patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})[日号]',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            r'(\d{1,2})月(\d{1,2})[日号]'
        ]
        for pattern in date_patterns:
            date_match = re.search(pattern, original_text)
            if date_match:
                if len(date_match.groups()) == 3:
                    year, month, day = date_match.groups()
                    data.入仓日期 = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                elif len(date_match.groups()) == 2:
                    # Assume current year
                    import datetime
                    current_year = datetime.datetime.now().year
                    month, day = date_match.groups()
                    data.入仓日期 = f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"
                break
        
        # Try to extract product name (everything before price/courier info)
        # This is a more robust heuristic
        text_parts = original_text.split('，')
        if text_parts:
            potential_product = text_parts[0].strip()
            # Remove common prefixes and suffixes
            potential_product = re.sub(r'^(货物|商品|产品)[:：]?', '', potential_product)
            # Remove price from product name if it got included
            potential_product = re.sub(r'\d+(?:\.\d+)?[美金$元]', '', potential_product)
            # Remove quantity from product name
            potential_product = re.sub(r'(\d+|一|二|三|四|五|六|七|八|九|十)(托|箱|个|件|张|套|台|只|条|包|袋|瓶|罐)', '', potential_product)
            potential_product = potential_product.strip()

            if potential_product and len(potential_product) > 1:
                data.货物名称 = potential_product
        
        return data
    
    def parse_multiple_shipments(self, text: str) -> List[ShipmentData]:
        """
        Parse multiple shipment descriptions from text

        Args:
            text: Text containing multiple shipment descriptions

        Returns:
            List of ShipmentData objects
        """
        # Split by newlines first (most common separator)
        lines = text.strip().split('\n')

        shipments = []
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:  # Only process substantial lines
                shipment = self.parse_shipment_text(line)
                # Only add if we extracted meaningful product name and it's not just metadata
                if (shipment.货物名称 and
                    len(shipment.货物名称) >= 2 and  # Allow 2+ character product names (e.g., "地板")
                    not shipment.货物名称.startswith(('入仓日期', '快递单号', '单号', '单价'))):
                    shipments.append(shipment)

        return shipments

def test_parser():
    """Test the parser with sample data"""
    parser = ChineseShipmentParser()
    
    test_cases = [
        "地板1托30$，快递中通，202242834846，入仓日期2025年7月5号",
        "折叠按摩床一张25$，快递单号：76018395245100010001，入仓日期2025年7月4号",
        "电子产品2箱，单价50美金，顺丰快递，单号12345678901234，2025-07-06入仓"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {test_case}")
        
        result = parser.parse_shipment_text(test_case)
        print(f"Output: {json.dumps(result.to_dict(), ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    test_parser()
