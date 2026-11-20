"""Fontes do sistema, sem redistribuicao; medidas compartilhadas pela composicao."""
import math
import os
from functools import lru_cache
from pathlib import Path
from PIL import ImageFont

PRESETS = {
    'title': (52,'bold'), 'subtitle': (30,'semibold'), 'body_text': (29,'regular'),
    'caption': (25,'regular'), 'highlight': (34,'semibold'), 'student_name': (40,'semibold'),
}
FONT_FILES = {'Arial': ('arial.ttf','arialbd.ttf','arialbd.ttf'),
              'Segoe UI': ('segoeui.ttf','seguisb.ttf','segoeuib.ttf'),
              'Georgia': ('georgia.ttf','georgiab.ttf','georgiab.ttf'),
              'DejaVu Sans': ('DejaVuSans.ttf','DejaVuSans-Bold.ttf','DejaVuSans-Bold.ttf')}
WEIGHTS = ('regular','semibold','bold')


@lru_cache(maxsize=128)
def font(size, family='Arial', weight='regular'):
    if family not in FONT_FILES or weight not in WEIGHTS: raise ValueError('Fonte invalida.')
    name = FONT_FILES[family][WEIGHTS.index(weight)]
    for candidate in (str(Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'/name), name):
        try: return ImageFont.truetype(candidate, size)
        except OSError: pass
    raise ValueError('Fonte selecionada nao esta disponivel neste computador.')


@lru_cache(maxsize=1)
def families():
    available = []
    for family in FONT_FILES:
        try:
            for weight in WEIGHTS: font(20,family,weight)
            available.append(family)
        except ValueError: pass
    return available


def preset(kind):
    size, weight = PRESETS.get(kind,(29,'regular'))
    return dict(font_family=(families() or ['Arial'])[0],font_size=size,weight=weight,color='#243442',
                align='left',line_height=1.3,letter_spacing=0,padding=8,wrap=True)


def validate(style):
    if style.get('font_family','Arial') not in FONT_FILES or style.get('weight','regular') not in WEIGHTS:
        raise ValueError('Familia ou peso invalido.')
    for key, default, low, high in [('line_height',1.3,1,3),('letter_spacing',0,-2,20),('padding',4,0,200)]:
        value = style.get(key,default)
        if type(value) not in (int,float) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError('Espacamento invalido.')
    if type(style.get('wrap',True)) is not bool: raise ValueError('Quebra invalida.')


@lru_cache(maxsize=8192)
def advance(face, char):
    return face.getlength(char)


def measure(text, draw, face, spacing):
    return sum(advance(face,c) for c in text)+max(0,len(text)-1)*spacing


def layout(text, draw, face, width, wrap=True, spacing=0):
    result=[]
    for paragraph in text.split('\n'):
        if not wrap:
            result.append(paragraph); continue
        line=''
        for word in paragraph.split(' '):
            trial = (line+' ' if line else '')+word
            if line and measure(trial,draw,face,spacing)>width:
                result.append(line); line=''
            if line: line+=' '
            for char in word:
                if line and measure(line+char,draw,face,spacing)>width:
                    result.append(line);line=''
                line+=char
        result.append(line)
    return result


def draw_spaced(draw, position, text, face, fill, spacing):
    x,y=position
    # Ancora ascendente comum preserva a linha de base e os acentos.
    for char in text:
        draw.text((x,y),char,font=face,fill=fill,anchor='la')
        x += advance(face,char)+spacing
