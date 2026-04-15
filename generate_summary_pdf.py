#!/usr/bin/env python3
"""生成 PageIndex 单页中文摘要 PDF。"""

from fpdf import FPDF
import os


class SummaryPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        pass


pdf = SummaryPDF()
pdf.set_auto_page_break(auto=False)
pdf.add_page()

# 添加中文字体 (Arial Unicode 支持中文)
font_path = "/Library/Fonts/Arial Unicode.ttf"
pdf.add_font("CJKFont", "", font_path)
pdf.add_font("CJKFont", "B", font_path)
pdf.add_font("CJKFont", "I", font_path)
pdf.add_font("CJKFont", "BI", font_path)

page_width = 210
margin = 14
content_width = page_width - 2 * margin

DARK_BLUE = (15, 32, 67)
MEDIUM_BLUE = (41, 81, 140)
ACCENT_BLUE = (59, 130, 246)
DARK_GRAY = (31, 41, 55)
MEDIUM_GRAY = (107, 114, 128)
WHITE = (255, 255, 255)

y = margin

# 标题栏
pdf.set_fill_color(*DARK_BLUE)
pdf.rect(0, 0, page_width, 34, "F")
pdf.set_y(7)
pdf.set_font("CJKFont", "B", 22)
pdf.set_text_color(*WHITE)
pdf.cell(page_width, 12, "PageIndex \u2014\u2014 Vectify AI 无向量 RAG 系统", 0, 1, "C")
pdf.set_font("CJKFont", "", 10)
pdf.set_text_color(200, 210, 230)
pdf.cell(page_width, 8, "基于推理的文档检索，而非相似度搜索", 0, 1, "C")

y = 40


def section_title(text, y_pos):
    pdf.set_y(y_pos)
    pdf.set_fill_color(*ACCENT_BLUE)
    pdf.rect(margin, y_pos, content_width, 8, "F")
    pdf.set_font("CJKFont", "B", 11)
    pdf.set_text_color(*WHITE)
    pdf.cell(content_width, 8, f"  {text}", 0, 1, "L")
    return y_pos + 11


def bullet(text, y_pos, indent=22, size=9):
    pdf.set_y(y_pos)
    pdf.set_x(margin + indent)
    pdf.set_font("CJKFont", "", size)
    pdf.set_text_color(*DARK_GRAY)
    pdf.cell(5, 5, "\u2022", 0, 0)
    pdf.multi_cell(content_width - indent - 5, 4.5, text)
    return pdf.get_y()


def body_text(text, y_pos, size=9):
    pdf.set_y(y_pos)
    pdf.set_x(margin + 3)
    pdf.set_font("CJKFont", "", size)
    pdf.set_text_color(*DARK_GRAY)
    pdf.multi_cell(content_width - 6, 4.5, text)
    return pdf.get_y()


def two_col(left_text, right_text, y_pos, col_width=None):
    if col_width is None:
        col_width = (content_width - 8) / 2
    pdf.set_y(y_pos)
    pdf.set_x(margin)
    pdf.set_font("CJKFont", "B", 8.5)
    pdf.set_text_color(MEDIUM_BLUE)
    pdf.cell(col_width, 5, left_text, 0, 0)
    pdf.set_x(margin + col_width + 8)
    pdf.set_font("CJKFont", "", 8.5)
    pdf.set_text_color(*DARK_GRAY)
    pdf.cell(col_width, 5, right_text, 0, 1)
    return y_pos + 6


# 一、它是什么
y = section_title("\u4e00\u3001\u5b83\u662f\u4ec0\u4e48", y)
y = body_text(
    "PageIndex 是由 Vectify AI 开发的无向量、基于推理的 RAG（检索增强生成）系统。"
    "它不使用向量嵌入和相似度搜索，而是从长文档中构建分层树状索引，"
    "并利用大语言模型（LLM）在该结构上进行推理，实现精准的上下文感知检索。",
    y,
    size=9,
)

# 二、适用于谁
y = section_title("\u4e8c\u3001\u9002\u7528\u4e8e\u8c01", y + 2)
y = body_text(
    "金融分析师、法律专业人士、研究人员和开发者\u2014\u2014面向处理超长复杂文档"
    "（SEC 文件、监管文档、学术教材、技术手册）且超出 LLM 上下文限制的用户群体。"
    "在 FinanceBench 金融文档问答基准测试中达到 98.7% 的准确率。",
    y,
    size=9,
)

# 三、它做什么
y = section_title(
    "\u4e09\u3001\u5b83\u505a\u4ec0\u4e48\uff08\u6838\u5fc3\u529f\u80fd\uff09", y + 2
)
features = [
    "无向量数据库 \u2014\u2014 利用文档结构和 LLM 推理，而非向量相似度搜索。",
    "无人工分块 \u2014\u2014 文档按自然层次结构组织，非人工切割。",
    "类人检索 \u2014\u2014 模拟专家通过树搜索浏览复杂文档的方式。",
    "可解释、可追溯 \u2014\u2014 基于推理的检索，附带页码和章节引用。",
    "PDF 和 Markdown 支持 \u2014\u2014 解析两种格式，自动检测目录（TOC）。",
    "自我纠错 \u2014\u2014 通过 LLM 抽样验证目录准确性，支持重试修复。",
    "基于视觉的 RAG \u2014\u2014 无需 OCR，直接处理 PDF 页面图像。",
]
for f in features:
    y = bullet(f, y, indent=22, size=8.5)
    y += 0.3

# 四、如何工作（架构）
y = section_title("\u56db\u3001\u5982\u4f55\u5de5\u4f5c\uff08\u67b6\u6784\uff09", y + 2)

y = two_col("语言：", "Python 3", y)
y = two_col("LLM 集成：", "OpenAI 兼容 API（Qwen 模型）", y)
y = two_col("PDF 解析：", "PyPDF2 + PyMuPDF (fitz)", y)
y = two_col("分词：", "HuggingFace AutoTokenizer（本地 Qwen）", y)
y = two_col("异步：", "asyncio 并发 LLM 调用", y)
y = two_col("配置：", "YAML (config.yaml) + python-dotenv", y)
y += 1

pdf.set_y(y)
pdf.set_x(margin + 3)
pdf.set_font("CJKFont", "B", 8.5)
pdf.set_text_color(MEDIUM_BLUE)
pdf.cell(content_width - 6, 5, "数据流（PDF 处理）：", 0, 1)
y = pdf.get_y()

flow_steps = [
    "1. 逐页提取文本（PyPDF2/PyMuPDF）",
    "2. 检测目录（基于 LLM，3 种模式）",
    "3. 构建带物理页码的扁平目录列表",
    "4. 通过 LLM 抽样验证目录准确性",
    "5. 自我纠错：重试修复错误页码映射",
    "6. 扁平列表转换为嵌套 JSON 树",
    "7. 递归拆分过大的节点",
    "8. 可选：添加摘要、节点 ID、文档描述",
]
for step in flow_steps:
    y = bullet(step, y, indent=22, size=8)
    y += 0.3

# 五、如何运行
y = section_title(
    "\u4e94\u3001\u5982\u4f55\u8fd0\u884c\uff08\u5feb\u901f\u5f00\u59cb\uff09", y + 2
)

steps = [
    "安装依赖：pip3 install --upgrade -r requirements.txt",
    "设置密钥：创建 .env 文件，写入 CHATGPT_API_KEY=你的密钥",
    "运行 PDF：python3 run_pageindex.py --pdf_path /path/to/doc.pdf",
    "运行 Markdown：python3 run_pageindex.py --md_path /path/to/doc.md",
    "输出结果：./results/<文档名>_structure.json",
]
for s in steps:
    y = bullet(s, y, indent=22, size=8.5)
    y += 0.3

y += 1
pdf.set_y(y)
pdf.set_x(margin + 3)
pdf.set_font("CJKFont", "I", 8)
pdf.set_text_color(*MEDIUM_GRAY)
pdf.multi_cell(
    content_width - 6,
    4,
    "可选参数：--model, --max-pages-per-node, --max-tokens-per-node, "
    "--if-add-node-summary, --if-add-node-text, --if-thinning。"
    "详见 README.md。许可证：MIT。",
)

# 保存
output_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "PageIndex_Summary.pdf"
)
pdf.output(output_path)
print(f"PDF 已保存至: {output_path}")
