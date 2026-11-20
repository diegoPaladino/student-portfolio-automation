export default function(component) {
 const {parentElement, data, setTriggerValue} = component;
 const root=parentElement.querySelector('#editor');
 let state=root._editorState;
 if(!state || state.token!==data.token) {
  state={token:data.token,regions:structuredClone(data.regions),selected:null,zoom:1,mode:'select',newType:'photo',newField:null};
  root._editorState=state;
 }
 root.replaceChildren();
 const el=(tag,text,parent=root)=>{const e=document.createElement(tag);if(text)e.textContent=text;parent.append(e);return e;};
 const projectBar=el('div');projectBar.className='toolbar project-bar';
 const projectLabel=el('label','Projeto desta tela',projectBar);
 const projectSelect=el('select',null,projectLabel);projectSelect.setAttribute('aria-label','Projeto desta tela');
 data.projects.forEach(p=>el('option',p.label,projectSelect).value=p.id);projectSelect.value=String(data.project_id);
 const projectButton=el('button','Aplicar projeto',projectBar);projectButton.type='button';
 projectButton.onclick=()=>setTriggerValue('project',{project_id:Number(projectSelect.value),regions:state.regions});
 el('p','Ao aplicar outro projeto, os vínculos equivalentes acompanham a troca. Confira os textos e salve o template.');
 const catalog=el('div');catalog.className='text-catalog';
 el('strong','Textos disponíveis neste projeto',catalog);
 function fieldOptions(select){
  const groups=new Map();
  data.fields.forEach(f=>{if(!groups.has(f.group)){const group=el('optgroup',null,select);group.label=f.group;groups.set(f.group,group);}
   el('option',`${f.label} · ${f.text.replace(/\s+/g,' ').slice(0,85)} · ${f.id}`,groups.get(f.group)).value=f.id;});
 }
 const regionLabel=el('label','Região para receber o texto',catalog);
 const catalogRegion=el('select',null,regionLabel);catalogRegion.setAttribute('aria-label','Região para receber o texto');
 catalogRegion.onchange=()=>{state.selected=catalogRegion.value;paint();properties();};
 const contentLabel=el('label','Texto do projeto',catalog);
 const catalogField=el('select',null,contentLabel);catalogField.setAttribute('aria-label','Texto do projeto');fieldOptions(catalogField);
 if(!data.fields.some(f=>f.id===state.catalogField))state.catalogField=data.fields[0]?.id||'';
 catalogField.value=state.catalogField;
 const content=el('textarea',null,catalog);content.readOnly=true;content.setAttribute('aria-label','Prévia do texto do projeto');
 const updateContent=()=>{content.value=data.fields.find(f=>f.id===state.catalogField)?.text||'';};
 catalogField.onchange=()=>{state.catalogField=catalogField.value;updateContent();};updateContent();
 const applyText=el('button','Aplicar texto à região selecionada',catalog);applyText.type='button';
 applyText.onclick=()=>{
  const r=state.regions.find(r=>r.id===state.selected);const field=data.fields.find(f=>f.id===state.catalogField);
  if(!r||r.type==='photo'||!field){status.textContent='Selecione uma região de texto e um conteúdo do projeto.';return;}
  r.source={kind:'pedagogical',field_id:field.id};paint();properties();
  status.textContent=`${field.label} aplicado. Atualize a prévia e salve o template.`;
 };
 const toolbar=el('div',null);toolbar.className='toolbar';
 const status=el('p','Desenhe um retângulo ou selecione uma região. As alterações ficam em rascunho até salvar.');
 const viewport=el('div',null);viewport.className='viewport';viewport.tabIndex=0;viewport.setAttribute('aria-label','Área visual do template');
 const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');viewport.append(svg);
 svg.setAttribute('viewBox',`0 0 ${data.width} ${data.height}`);svg.style.touchAction='none';svg.setAttribute('aria-label','Imagem e regiões');
 const image=document.createElementNS(svg.namespaceURI,'image');image.setAttribute('href',data.image);image.setAttribute('width',data.width);image.setAttribute('height',data.height);svg.append(image);
 const overlay=document.createElementNS(svg.namespaceURI,'g');svg.append(overlay);
 const panel=el('div',null);panel.className='panel';
 const button=(text,action,parent=toolbar)=>{const b=el('button',text,parent);b.type='button';b.onclick=action;return b;};
 const fieldLabel=r=>r.source?.kind==='pedagogical'?`${data.fields.find(f=>f.id===r.source.field_id)?.label||'Texto'} · ${r.source.field_id}`:r.type==='photo'?(data.requirements.find(q=>q.id===r.source.requirement_id)?.alias||r.source.requirement_id):r.source?.kind==='student_name'?'Nome do aluno':r.source?.kind==='project_title'?'Título do projeto':'Texto informado';
 const defaultSource=type=>type==='photo'?{kind:'approved_photo',requirement_id:state.newField||data.requirements[0]?.id||''}:state.newField?{kind:'pedagogical',field_id:state.newField}:{kind:type==='student_name'?'student_name':'literal',text:''};
 const choose=el('label','Tipo antes de desenhar',toolbar);
 const newType=el('select',null,choose);newType.setAttribute('aria-label','Tipo antes de desenhar');
 data.types.forEach(type=>el('option',type,newType).value=type);newType.value=state.newType;
 const bindingLabel=el('label','Campo da nova região',toolbar);
 const newBinding=el('select',null,bindingLabel);newBinding.setAttribute('aria-label','Campo da nova região');
 function newFields(){
  newBinding.replaceChildren();
  const choices=state.newType==='photo'?data.requirements.map(q=>[q.id,`${q.alias} · ${q.description}`]):[['','Texto informado / nome do aluno'],...data.fields.map(f=>[f.id,`${f.id} · ${f.type}`])];
  if(state.newType==='photo')choices.forEach(([id,label])=>el('option',label,newBinding).value=id);
  else {el('option','Texto livre / nome do aluno',newBinding).value='';fieldOptions(newBinding);}
  const preferred=state.newType==='photo'?data.requirements[0]?.id:(data.fields.find(f=>f.type===state.newType)?.id||'');
  if(!choices.some(([id])=>id===state.newField))state.newField=preferred||'';
  newBinding.value=state.newField;
 }
 newType.onchange=()=>{state.newType=newType.value;state.newField=null;newFields();};
 newBinding.onchange=()=>state.newField=newBinding.value;newFields();
 const updateZoom=()=>{svg.style.width=Math.round(Math.min(760,data.width)*state.zoom)+'px';svg.style.height=Math.round(Math.min(760,data.width)*state.zoom*data.height/data.width)+'px';zoom.value=String(state.zoom);};
 button('Selecionar / mover',()=>{state.mode='select';status.textContent='Arraste uma região para mover; use o quadrado no canto inferior direito para redimensionar.';});
 button('Desenhar região',()=>{state.mode='draw';status.textContent='Arraste sobre a arte para criar uma região.';});
 const zoom=el('input',null,toolbar);zoom.type='range';zoom.min='.02';zoom.max='3';zoom.step='.01';zoom.value=state.zoom;zoom.setAttribute('aria-label','Zoom');zoom.oninput=()=>{state.zoom=Number(zoom.value);updateZoom();};
 button('Ver arte inteira',()=>{state.zoom=Math.max(.02,Math.min(1,550*data.width/(Math.min(760,data.width)*data.height)));updateZoom();viewport.scrollTo(0,0);});
 button('Excluir região',()=>{state.regions=state.regions.filter(r=>r.id!==state.selected);state.selected=null;paint();properties();});
 button('Salvar template',()=>setTriggerValue('save',{regions:state.regions}));
 button('Atualizar prévia',()=>setTriggerValue('preview',{regions:state.regions}));
 button('Preencher textos do projeto',()=>setTriggerValue('fill',{regions:state.regions}));
 const snap=(value,min,max)=>Math.max(min,Math.min(max,value));
 const point=e=>{const box=svg.getBoundingClientRect();return {x:snap((e.clientX-box.left)/box.width,0,1),y:snap((e.clientY-box.top)/box.height,0,1)};};
 function paint(){
  catalogRegion.replaceChildren();el('option','Selecione uma região de texto',catalogRegion).value='';
  state.regions.filter(r=>r.type!=='photo').forEach((r,i)=>el('option',`${i+1}. ${r.type} — ${fieldLabel(r)}`,catalogRegion).value=r.id);
  catalogRegion.value=state.selected||'';
  applyText.disabled=!state.regions.some(r=>r.id===state.selected&&r.type!=='photo');
  overlay.replaceChildren();
  state.regions.forEach(r=>{
   const g=document.createElementNS(svg.namespaceURI,'g');overlay.append(g);
   const rect=document.createElementNS(svg.namespaceURI,'rect');g.append(rect);
   Object.entries({x:r.x*data.width,y:r.y*data.height,width:r.width*data.width,height:r.height*data.height,fill:state.selected===r.id?'#26a69a44':'#4c75cc22',stroke:state.selected===r.id?'#08786e':'#365caf','stroke-width':2,'vector-effect':'non-scaling-stroke'}).forEach(([k,v])=>rect.setAttribute(k,v));rect.dataset.id=r.id;rect.style.cursor='move';
   const title=document.createElementNS(svg.namespaceURI,'text');title.textContent=`${r.type} — ${fieldLabel(r)}`;title.setAttribute('x',r.x*data.width+5);title.setAttribute('y',r.y*data.height+22);title.setAttribute('font-size','20');title.style.pointerEvents='none';g.append(title);
   if(state.selected===r.id){const handle=document.createElementNS(svg.namespaceURI,'rect');const size=Math.max(12,data.width/60);Object.entries({x:(r.x+r.width)*data.width-size,y:(r.y+r.height)*data.height-size,width:size,height:size,fill:'#08786e'}).forEach(([k,v])=>handle.setAttribute(k,v));handle.dataset.id=r.id;handle.dataset.handle='resize';handle.style.cursor='nwse-resize';g.append(handle);}
  });
 }
 function properties(){
  panel.replaceChildren();
  const selector=el('select',null,panel);selector.setAttribute('aria-label','Região selecionada');
  el('option','Selecione uma região',selector).value='';state.regions.forEach((r,i)=>{el('option',`${i+1}. ${r.type} — ${fieldLabel(r)}`,selector).value=r.id;});selector.value=state.selected||'';selector.onchange=()=>{state.selected=selector.value;paint();properties();};
  const r=state.regions.find(r=>r.id===state.selected);if(!r)return;
  r.text_style={...data.presets[r.type],...(r.text_style||{})};
  function select(label,values,value,change){const l=el('label',label,panel);const s=el('select',null,l);s.setAttribute('aria-label',label);values.forEach(([v,t])=>{el('option',t,s).value=v;});s.value=value;s.onchange=()=>change(s.value);return s;}
  function number(label,value,min,max,step,change){const l=el('label',label,panel);const n=el('input',null,l);n.type='number';n.min=min;n.max=max;n.step=step;n.value=value;n.setAttribute('aria-label',label);n.onchange=()=>{const v=Number(n.value);if(Number.isFinite(v)&&v>=min&&v<=max){change(v);paint();properties();}else{n.value=value;status.textContent='Valor fora dos limites.';}};}
  select('Tipo',data.types.map(t=>[t,t]),r.type,v=>{
   r.sources_by_type=r.sources_by_type||{};r.sources_by_type[r.type]=structuredClone(r.source);
   const wasPhoto=r.type==='photo';r.type=v;
   if(r.sources_by_type[v])r.source=structuredClone(r.sources_by_type[v]);
   else if(v==='photo')r.source={kind:'approved_photo',requirement_id:data.requirements[0]?.id||''};
   else if(wasPhoto)r.source={kind:v==='student_name'?'student_name':'literal',text:''};
   status.textContent='Tipo alterado. Origens anteriores e estilo preservados; confira o vínculo. Use Aplicar estilo sugerido se desejar.';
   paint();properties();});
  for(const [k,label,max] of [['x','X (%)',1-r.width],['y','Y (%)',1-r.height],['width','Largura (%)',1-r.x],['height','Altura (%)',1-r.y]]) number(label,+(r[k]*100).toFixed(4),(k==='width'||k==='height') ? .1 : 0,max*100,.1,v=>r[k]=v/100);
  if(r.type==='photo'){
   select('Requisito pedagógico',data.requirements.map(q=>[q.id,`${q.alias} · ${q.description}`]),r.source.requirement_id,v=>{r.source.requirement_id=v;paint();properties();});
   select('Enquadramento',[['contain','contain — foto inteira'],['cover','cover — preencher e recortar']],r.fit,v=>r.fit=v);
   number('Foco horizontal (%)',r.focus_x*100,0,100,1,v=>r.focus_x=v/100);number('Foco vertical (%)',r.focus_y*100,0,100,1,v=>r.focus_y=v/100);
  }else{
   select('Origem do texto',[['pedagogical','Campo pedagógico da professora'],['literal','Texto informado'],['project_title','Título do projeto'],['student_name','Nome do aluno']],r.source.kind,v=>{if(v==='literal'&&r.source.kind==='pedagogical'&&r.source.text===undefined)r.source.text=data.fields.find(f=>f.id===r.source.field_id)?.text||'';r.source.kind=v;if(v==='pedagogical'&&!r.source.field_id)r.source.field_id=data.fields.find(f=>f.type===r.type)?.id||data.fields[0]?.id;paint();properties();});
   if(r.source.kind==='pedagogical'){
    const fieldSelect=select('Campo pedagógico',[],r.source.field_id,v=>{r.source.field_id=v;paint();properties();});
    fieldOptions(fieldSelect);fieldSelect.value=r.source.field_id;
    const field=data.fields.find(f=>f.id===r.source.field_id);
    const original=el('textarea',null,el('label','Conteúdo associado (edite abaixo da prévia)',panel));original.value=field?.text||'';original.readOnly=true;original.setAttribute('aria-label','Conteúdo associado');
   }
   if(r.source.kind==='literal'){const label=el('label','Texto',panel);const input=el('textarea',null,label);input.value=r.source.text||'';input.maxLength=10000;input.setAttribute('aria-label','Texto');input.oninput=()=>r.source.text=input.value;}
   number('Fonte (referência 1080 px)',r.text_style.font_size,8,200,1,v=>r.text_style.font_size=v);
   select('Família tipográfica',data.fonts.map(f=>[f,f]),r.text_style.font_family||'Arial',v=>r.text_style.font_family=v);
   select('Peso',[['regular','Regular'],['semibold','Seminegrito'],['bold','Negrito']],r.text_style.weight||'regular',v=>r.text_style.weight=v);
   number('Altura de linha',r.text_style.line_height||1.3,1,3,.1,v=>r.text_style.line_height=v);
   number('Espaçamento entre letras',r.text_style.letter_spacing||0,-2,20,.1,v=>r.text_style.letter_spacing=v);
   number('Margens internas (px em 1080)',r.text_style.padding??4,0,200,1,v=>r.text_style.padding=v);
   select('Quebra automática',[['true','Sim'],['false','Não']],String(r.text_style.wrap??true),v=>r.text_style.wrap=v==='true');
   button('Aplicar estilo sugerido',()=>{r.text_style=structuredClone(data.presets[r.type]);properties();},panel);
   select('Alinhamento',[['left','Esquerda'],['center','Centro'],['right','Direita']],r.text_style.align,v=>r.text_style.align=v);
   const l=el('label','Cor do texto',panel);const c=el('input',null,l);c.type='color';c.value=r.text_style.color;c.oninput=()=>r.text_style.color=c.value;
  }
  const index=state.regions.indexOf(r);button('Trazer para frente',()=>{state.regions.splice(index,1);state.regions.push(r);paint();properties();},panel);
  button('Enviar para trás',()=>{state.regions.splice(index,1);state.regions.unshift(r);paint();properties();},panel);
 }
 let drag=null;
 svg.onpointerdown=e=>{
  if(e.button!==0)return;e.preventDefault();const p=point(e);
  if(state.mode==='draw'){
   if(state.regions.length>=100){status.textContent='Limite de 100 regiões.';return;}
   if(state.newType==='photo'&&!data.requirements.length){status.textContent='Esta seção não possui requisitos fotográficos.';return;}
   const id=crypto.randomUUID();const r={id,type:state.newType,x:p.x,y:p.y,width:.001,height:.001,source:defaultSource(state.newType),fit:'contain',focus_x:.5,focus_y:.5,text_style:structuredClone(data.presets[state.newType])};
   state.regions.push(r);state.selected=id;drag={mode:'draw',start:p,id};
  }else if(e.target.dataset.id){state.selected=e.target.dataset.id;const r=state.regions.find(r=>r.id===state.selected);drag={mode:e.target.dataset.handle?'resize':'move',start:p,id:r.id,old:{...r}};}
  else{state.selected=null;}
  svg.setPointerCapture(e.pointerId);paint();properties();
 };
 svg.onpointermove=e=>{
  if(!drag)return;const p=point(e);const r=state.regions.find(r=>r.id===drag.id);const dx=p.x-drag.start.x,dy=p.y-drag.start.y;
  if(drag.mode==='draw'){r.x=Math.min(p.x,drag.start.x);r.y=Math.min(p.y,drag.start.y);r.width=Math.max(.001,Math.abs(dx));r.height=Math.max(.001,Math.abs(dy));}
  else if(drag.mode==='move'){r.x=snap(drag.old.x+dx,0,1-r.width);r.y=snap(drag.old.y+dy,0,1-r.height);}
  else{r.width=snap(drag.old.width+dx,.001,1-r.x);r.height=snap(drag.old.height+dy,.001,1-r.y);}
  paint();
 };
 svg.onpointerup=()=>{if(drag){const r=state.regions.find(r=>r.id===drag.id);if(drag.mode==='draw'&&(r.width<.003||r.height<.003))state.regions=state.regions.filter(r=>r.id!==drag.id);drag=null;state.mode='select';paint();properties();}};
 svg.onpointercancel=()=>{drag=null;paint();properties();};
 updateZoom();paint();properties();
 return ()=>{svg.onpointerdown=null;svg.onpointermove=null;svg.onpointerup=null;};
}
