"""Package reviewed slide renders and the separate disclosure."""
from pathlib import Path
from io import BytesIO

import pymupdf as fitz
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEST = ROOT / 'presentation'
STAGING = ROOT / '.local/redesign/output'

with fitz.open() as slides:
    for index in range(1, 9):
        page = slides.new_page(width=960, height=540)
        with Image.open(STAGING / f'slide-{index}.png') as slide:
            buffer = BytesIO()
            slide.convert('RGB').save(buffer, format='JPEG', quality=95, subsampling=0)
            page.insert_image(page.rect, stream=buffer.getvalue())
    slides.set_metadata({'title':'VK Заказ рядом', 'author':'Теневое Правительство'})
    slides.save(DEST / 'Теневое Правительство_strategy_msk.pdf', deflate=True)

title, body = (HERE / 'ai-disclosure.md').read_text(encoding='utf-8').strip().split('\n\n', 1)
with fitz.open() as disclosure:
    page = disclosure.new_page(width=595, height=842)
    page.insert_font(fontname='GolosText', fontfile=str(HERE / 'assets/GolosText-Regular.ttf'))
    page.insert_font(fontname='GolosBold', fontfile=str(HERE / 'assets/GolosText-Bold.ttf'))
    page.draw_rect(fitz.Rect(0, 0, 595, 12), fill=(0.0, .46, 1.0), color=None)
    page.insert_text((43, 69), title.removeprefix('# '), fontname='GolosBold', fontsize=23)
    remaining = page.insert_textbox(fitz.Rect(43, 104, 552, 794), body, fontname='GolosText', fontsize=11, lineheight=1.40)
    assert remaining >= 0, f'Disclosure text overflow: {remaining}'
    disclosure.subset_fonts()
    disclosure.save(DEST / 'Теневое Правительство_AI_disclosure.pdf', deflate=True)
