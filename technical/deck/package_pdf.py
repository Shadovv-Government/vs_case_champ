"""Export the eight-slide submission and its supporting documents."""
from io import BytesIO
import json
from pathlib import Path

from PIL import Image
from reportlab import rl_config
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from report import register_fonts, write_supporting_pdfs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DESTINATION = ROOT / 'presentation'
STAGING = ROOT / '.local/redesign/output'
TEAM = 'Теневое Правительство'
SLIDES = 8
PDF_WIDTH, PDF_HEIGHT = 960, 540
PX_TO_PT = .75
TEXT_INSET = 9.6 * PX_TO_PT


def slide_text():
    boxes = [[] for _ in range(SLIDES)]
    inspection = STAGING / 'candidate.pptx.inspect.ndjson'
    for line in inspection.read_text(encoding='utf-8').splitlines():
        item = json.loads(line)
        if item['kind'] == 'textbox' and item.get('text'):
            boxes[item['slideIndex']].append(item)
    if any(not page for page in boxes):
        raise ValueError('The presentation inspector did not return text for each slide')
    return boxes


def wrap_text(value, font, size, width):
    for paragraph in value.splitlines():
        line = ''
        for word in paragraph.split(' '):
            candidate = f'{line} {word}' if line else word
            if line and stringWidth(candidate, font, size) > width:
                yield line
                line = word
            else:
                line = candidate
        if line:
            yield line


def add_searchable_text(canvas, boxes):
    # Invisible text uses the same words and boxes as the editable slides.
    canvas.saveState()
    for item in boxes:
        position, style = item['position'], item['style']
        x, top, width, height = (position[key] * PX_TO_PT for key in ('left', 'top', 'width', 'height'))
        x += TEXT_INSET
        width -= 2 * TEXT_INSET
        size = style['fontSize'] * PX_TO_PT
        font = 'GolosCaseBold' if style.get('bold') else 'GolosCase'
        lines = list(wrap_text(item['text'], font, size, width))
        leading = size * 1.18
        baseline = PDF_HEIGHT - top - height / 2 + (len(lines)-1) * leading / 2 - size * .3
        alignment = style.get('alignment')
        text = canvas.beginText()
        text.setFont(font, size)
        text.setTextRenderMode(3)
        for index, line in enumerate(lines):
            free = width - stringWidth(line, font, size)
            indent = free / 2 if alignment == 'center' else free if alignment == 'right' else 0
            text.setTextOrigin(x + indent, baseline - index * leading)
            text.textOut(line)
        canvas.drawText(text)
    canvas.restoreState()


def write_slides(destination):
    pages = [STAGING / f'slide-{index}.png' for index in range(1, SLIDES+1)]
    for page in pages:
        if not page.is_file():
            raise FileNotFoundError(f'Run build.mjs before packaging: {page}')
    buffer = BytesIO()
    slides = Canvas(buffer, pagesize=(PDF_WIDTH, PDF_HEIGHT), invariant=True)
    slides.setTitle('VK Заказ рядом')
    slides.setAuthor(TEAM)
    for index, (page, boxes) in enumerate(zip(pages, slide_text()), 1):
        jpeg = BytesIO()
        with Image.open(page) as slide:
            slide.convert('RGB').save(jpeg, format='JPEG', quality=94, subsampling=0)
        slides.drawImage(ImageReader(jpeg), 0, 0, width=PDF_WIDTH, height=PDF_HEIGHT)
        key = f'slide-{index}'
        slides.bookmarkPage(key)
        slides.addOutlineEntry(f'{index}. {boxes[0]["text"]}', key)
        add_searchable_text(slides, boxes)
        slides.showPage()
    slides.save()
    if buffer.tell() >= 15_000_000:
        raise ValueError('Submission PDF exceeds the form limit of 15 MB')
    destination.write_bytes(buffer.getvalue())


def main():
    rl_config.useA85 = False
    register_fonts()
    evidence = json.loads((HERE / 'evidence.json').read_text(encoding='utf-8'))
    disclosure = (HERE / 'ai-disclosure.md').read_text(encoding='utf-8')
    write_slides(DESTINATION / f'{TEAM}_strategy_msk.pdf')
    write_supporting_pdfs(DESTINATION, TEAM, evidence, disclosure)


if __name__ == '__main__':
    main()
