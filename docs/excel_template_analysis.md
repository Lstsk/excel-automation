# Excel Template Analysis

## Template File
- **File Name**: `环亚客户 LeShuiju自行申报货物表- - 2y - Copy.xlsx`
- **Sheet Name**: `环亚客户自行申报货物表`
- **Dimensions**: 28 rows × 12 columns

## Template Structure

### Header Section (Rows 1-6)
Contains recipient information:
- Row 1: 塞班收货人真实姓名 (Recipient Name) → "Le Shuiju" (Column D)
- Row 2: 塞班收货公司名字 (Company Name) → Empty
- Row 3: 塞班收货人电话号码 (Phone Number) → "16709896858" (Column D)
- Row 4: 塞班收货人/公司邮箱地址和区域 (Email/Address) → Empty
- Row 5: 塞班收货人/公司电子邮件 (Email) → Empty
- Row 6: 客户自行申报货物表 (Declaration Form Title)

### Data Table Headers (Rows 7-8)
**Row 7 (English Headers):**
- Column A: Number
- Column B: Unit
- Column C: Description
- Column D: Description
- Column E: Pkg Spec*Qty
- Column F: Unit Value
- Column G: Total Value
- Column H: Cbm (Optional)
- Column I: GW (Optional)
- Column J: Courier

**Row 8 (Chinese Headers):**
- Column A: 货物件数 (Item Number)
- Column B: 包装单位 (Package Unit)
- Column C: 中文品名 (Chinese Product Name)
- Column D: 英文品名 (English Product Name)
- Column E: 内部规格x数量 (Specification × Quantity)
- Column F: 美金单价 (USD Unit Price)
- Column G: 美金总价 (USD Total Price)
- Column H: 体积(可不填) (Volume - Optional)
- Column I: 毛重(可不填) (Gross Weight - Optional)
- Column J: 快递公司 (Courier Company)

### Sample Data (Rows 9-10)
**Row 9:**
- Case 1, 折叠按摩床, Folding Massage Table, 1, 25, =F9, 中通快递

**Row 10:**
- Case 2, 地板, Flooring, 1, 30, =F10, 中通快递

## Data Insertion Points

### Primary Data Area
- **Start Row**: Row 9 (first data row)
- **Data Columns**: A through J
- **Last Row with Data**: Row 16
- **Next Insertion Row**: Row 17

### Column Mapping for New Shipment Data

Based on the Chinese shipment input format, here's the mapping:

| Input Field | Chinese | Excel Column | Column Letter | Notes |
|-------------|---------|--------------|---------------|-------|
| 货物名称 | Product Name | C | C | Chinese product name |
| 数量/单位 | Quantity/Unit | E | E | Specification × Quantity |
| 单价 | Unit Price | F | F | USD unit price (extract number) |
| 快递公司 | Courier | J | J | Courier company name |
| 快递单号 | Tracking Number | - | - | Not in template, may need to add |
| 入仓日期 | Warehouse Date | - | - | Not in template, may need to add |

### Auto-Generated Fields
- **Column A**: Auto-generate case numbers (Case 1, Case 2, etc.)
- **Column B**: Package unit (可以留空或默认值)
- **Column D**: English product name (translate from Chinese or leave empty)
- **Column G**: Total value (formula =F{row} or calculated value)
- **Column H**: Volume (optional, can be empty)
- **Column I**: Gross weight (optional, can be empty)

## Processing Logic

### Input Processing
1. Parse Chinese shipment text
2. Extract: 货物名称, 单价, 快递公司, 快递单号, 入仓日期
3. Map to Excel columns
4. Generate case number
5. Insert into next available row

### Formula Handling
- Column G uses Excel formulas (=F9, =F10, etc.)
- Need to maintain formula references when inserting new rows

### Data Validation
- Ensure price is numeric (extract from "30$" format)
- Validate courier company names
- Handle missing or optional fields

## Implementation Notes

1. **Row Detection**: Find last used row dynamically
2. **Case Numbering**: Auto-increment case numbers (Case 1, Case 2, ...)
3. **Price Extraction**: Parse "$" or "美金" from price strings
4. **Formula Updates**: Update cell references in formulas when inserting
5. **Template Preservation**: Keep header structure intact
6. **Backup**: Create backup before modifications
