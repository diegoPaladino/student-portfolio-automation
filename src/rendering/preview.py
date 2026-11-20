"""Composição em memória: sem PDF ou exportação de dados reais."""
from PIL import Image, ImageDraw, ImageFont, ImageOps
from src import core, observability as obs
from src import pedagogy
from src.rendering import typography
from src.template_editor.model import validate_template, background_path, resolve_requirement


def font(size):
    for name in ('arial.ttf','DejaVuSans.ttf'):
        try: return ImageFont.truetype(name,size)
        except OSError: pass
    return ImageFont.load_default()


def fit_photo(photo,size,fit='contain',focus=(.5,.5)):
    photo=ImageOps.exif_transpose(photo).convert('RGBA')
    if fit=='cover': return ImageOps.fit(photo,size,method=Image.Resampling.LANCZOS,centering=focus)
    contained=ImageOps.contain(photo,size,method=Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',size,(255,255,255,0))
    canvas.alpha_composite(contained,((size[0]-contained.width)//2,(size[1]-contained.height)//2))
    return canvas


def wrap_text(text,draw,face,width):
    lines=[]
    for paragraph in text.split('\n'):
        line=''
        for char in paragraph:
            if line and draw.textlength(line+char,font=face)>width:
                lines.append(line);line=''
            line+=char
        lines.append(line)
    return lines


@obs.operation
def render_preview(template,student_id=None,width=1080):
    validate_template(template)
    if type(width) is not int or not 200<=width<=1600: raise ValueError('Largura de prévia inválida.')
    student=None
    if student_id is not None:
        students=core.rows('SELECT name FROM students WHERE id=?',(student_id,))
        if not students: raise ValueError('Aluno não encontrado.')
        student=students[0]
    source_width=template['background']['width']; source_height=template['background']['height']
    height=round(width*source_height/source_width)
    if width*height>20_000_000: raise ValueError('Prévia muito alta. Reduza a largura.')
    with Image.open(background_path(template['background']['file'])) as im:
        canvas=ImageOps.exif_transpose(im).convert('RGBA').resize((width,height),Image.Resampling.LANCZOS)
    warnings=[]
    draw=ImageDraw.Draw(canvas)
    for region in template['regions']:
        x=round(region['x']*width);y=round(region['y']*height)
        w=max(1,round(region['width']*width));h=max(1,round(region['height']*height))
        if region['type']=='photo':
            photo=None
            if student_id is not None:
                requirement=resolve_requirement(region['source']['requirement_id'])['id']
                evidence=core.rows("SELECT p.path FROM evidence e JOIN photos p ON p.id=e.photo_id WHERE e.student_id=? AND e.requirement_id=? AND e.state='Aprovada'",(student_id,requirement))
                if evidence:
                    with Image.open(core.photo_path(evidence[0]['path'])) as im: photo=im.copy()
            if photo is not None:
                canvas.alpha_composite(fit_photo(photo,(w,h),region.get('fit','contain'),(region.get('focus_x',.5),region.get('focus_y',.5))),(x,y))
            else:
                label='FOTO SINTÉTICA — SEM VALOR DE EVIDÊNCIA' if student_id is None else 'EVIDÊNCIA APROVADA AUSENTE'
                draw.rectangle((x,y,x+w-1,y+h-1),fill='#edf2f7',outline='#596b7d',width=2)
                draw.text((x+5,y+5),label,font=font(max(9,round(17*width/1080))),fill='#243442')
                warnings.append(f"{region['id']}: {label}")
        else:
            source=region['source'];kind=source.get('kind')
            if kind=='pedagogical':
                text,_=pedagogy.resolve_text(source['field_id'],student_id)
                text=pedagogy.personalize(text,student['name'].split()[0] if student else None)
                if not student and '______' in text:
                    warnings.append(f"{region['id']}: campo individual pendente (sublinhado preservado).")
            elif kind=='student_name': text=student['name'].split()[0] if student else 'CRIANÇA DEMONSTRATIVA'
            elif kind=='project_title': text=core.rows('SELECT title FROM projects WHERE id=?',(template['project_id'],))[0]['title']
            else: text=source.get('text','')
            style=region.get('text_style',{})
            size=max(1,round(style.get('font_size',32)*width/1080))
            face=typography.font(size,style.get('font_family','Arial'),style.get('weight','regular'))
            layer=Image.new('RGBA',(w,h),(0,0,0,0));pen=ImageDraw.Draw(layer)
            scale=width/1080
            padding=round(style.get('padding',4)*scale)
            spacing=style.get('letter_spacing',0)*scale
            usable=max(1,w-2*padding)
            lines=typography.layout(text,pen,face,usable,style.get('wrap',True),spacing)
            ascent,descent=face.getmetrics()
            line_height=max(ascent+descent,round(size*style.get('line_height',1.3)))
            overflow=(len(lines)*line_height+2*padding>h or any(typography.measure(line,pen,face,spacing)>usable for line in lines))
            if overflow: warnings.append(f"{region['id']}: texto excede a região e foi cortado na prévia. Aumente a região ou ajuste a fonte; o texto salvo está completo.")
            if not text.strip(): warnings.append(f"{region['id']}: TEXTO AUSENTE — preencha ou associe um campo.")
            for i,line in enumerate(lines[:h//line_height+1]):
                length=typography.measure(line,pen,face,spacing)
                offset={'left':padding,'center':(w-length)/2,'right':w-length-padding}[style.get('align','left')]
                typography.draw_spaced(pen,(offset,padding+i*line_height),line,face,style.get('color','#243442'),spacing)
            canvas.alpha_composite(layer,(x,y))
            if overflow:
                draw.rectangle((x,y,x+w-1,y+h-1),outline='#d32f2f',width=max(1,round(3*scale)))
            if not text.strip():
                draw.rectangle((x,y,x+w-1,y+h-1),outline='#d32f2f',width=2)
                draw.text((x+2,y+2),'TEXTO AUSENTE',font=font(max(9,round(17*scale))),fill='#d32f2f')
    return canvas.convert('RGB'),warnings
