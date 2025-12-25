import fitz
import sys
import os

# استقبال مسار الملف
input_pdf = sys.argv[1]
output_pdf = input_pdf.replace('.pdf', '_processed.pdf')

# مسارات الصور المائية (في نفس المجلد)
watermark1 = "1.jpg"
watermark2 = "2.pdf"

try:
    doc = fitz.open(input_pdf)
    new_doc = fitz.open()
    
    img1_doc = fitz.open(watermark1)
    img2_doc = fitz.open(watermark2)
    
    font = fitz.Font("hebo")
    
    for page in doc:
        page_rect = page.rect
        blocks = page.get_text("blocks")
        new_page = new_doc.new_page(
            width=page_rect.width,
            height=page_rect.height
        )
        
        if not blocks:
            new_page.show_pdf_page(new_page.rect, doc, page.number)
        else:
            min_x = min(b[0] for b in blocks)
            min_y = min(b[1] for b in blocks)
            max_x = max(b[2] for b in blocks)
            max_y = max(b[3] for b in blocks)
            content_width = max_x - min_x
            content_height = max_y - min_y
            offset_x = (page_rect.width - content_width) / 2 - min_x
            offset_y = (page_rect.height - content_height) / 2 - min_y
            
            target_rect = fitz.Rect(
                offset_x,
                offset_y,
                offset_x + page_rect.width,
                offset_y + page_rect.height
            )
            
            new_page.show_pdf_page(target_rect, doc, page.number)
        
        # العلامة المائية الأولى
        img1_page = img1_doc[0]
        img1_rect = img1_page.rect
        scale1 = 0.65
        img1_width = img1_rect.width * scale1
        img1_height = img1_rect.height * scale1
        vertical_pos1 = 10
        horizontal_pos1 = (page_rect.width - img1_width) / 2
        
        watermark1_rect = fitz.Rect(
            horizontal_pos1,
            vertical_pos1,
            horizontal_pos1 + img1_width,
            vertical_pos1 + img1_height
        )
        new_page.insert_image(watermark1_rect, filename=watermark1)
        
        # العلامة المائية الثانية
        img2_page = img2_doc[0]
        img2_rect = img2_page.rect
        scale2 = 0.18
        img2_width = img2_rect.width * scale2
        img2_height = img2_rect.height * scale2
        footer_y = page_rect.height - 20
        vertical_pos2 = footer_y - img2_height - 35
        horizontal_pos2 = page_rect.width - img2_width - 50
        
        watermark2_rect = fitz.Rect(
            horizontal_pos2,
            vertical_pos2,
            horizontal_pos2 + img2_width,
            vertical_pos2 + img2_height
        )
        new_page.show_pdf_page(watermark2_rect, img2_doc, 0)
        
        # الهوامش
        tw = fitz.TextWriter(page_rect)
        fontsize = 9
        
        left_text = "Tel: +966-13-8021397"
        tw.append((50, footer_y), left_text, font=font, fontsize=fontsize)
        
        center_text = "www.mofcogroup.com"
        text_length = font.text_length(center_text, fontsize=fontsize)
        center_x = (page_rect.width - text_length) / 2
        tw.append((center_x, footer_y), center_text, font=font, fontsize=fontsize)
        
        right_text = "P.O.Box.15 Alkhobar 31952"
        text_length = font.text_length(right_text, fontsize=fontsize)
        right_x = page_rect.width - text_length - 50
        tw.append((right_x, footer_y), right_text, font=font, fontsize=fontsize)
        
        tw.write_text(new_page)
    
    img1_doc.close()
    img2_doc.close()
    doc.close()
    new_doc.save(output_pdf)
    new_doc.close()
    
    print(output_pdf)
    
except Exception as e:
    print(f"ERROR: {str(e)}", file=sys.stderr)
    sys.exit(1)
