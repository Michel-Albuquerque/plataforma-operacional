from __future__ import annotations

import re
import shutil
from datetime import datetime
from pathlib import Path


PASTA = Path(
    r"C:\Users\BR0143306567\OneDrive - Enel Spa\Documentos\Michel"
    r"\Plataforma_HTML"
)
HTML = PASTA / "Emergencia.html"
MARCADOR = "TABELAS_TEMPO_REAL_ORDENACAO_EXCEL_V1"


HELPERS = r'''
/* TABELAS_TEMPO_REAL_ORDENACAO_EXCEL_V1 */
const REALTIME_TABLE_IDS=new Set([
  'rtTable','rtConh','rtImpactTable','rtTeams',
  'rtProcessSummary','rtVehicleSummary',
  'rtCallbackStatus','rtFeederTable'
]);
const tableExportRegistry=new Map();

function tableCellRawValue(column,row){
  try{
    if(typeof column.exportValue==='function')return column.exportValue(row);
    if(typeof column.sortValue==='function')return column.sortValue(row);
    if(typeof column.value==='function')return column.value(row);
    if(typeof column.html==='function'){
      const temp=document.createElement('div');
      temp.innerHTML=String(column.html(row)??'');
      return temp.textContent.trim();
    }
  }catch(error){
    console.warn('Falha ao obter valor da tabela:',error);
  }
  return '';
}

function tableColumnIsNumeric(column,rows){
  const values=rows
    .slice(0,Math.min(rows.length,80))
    .map(row=>normalizedSortValue(tableCellRawValue(column,row)))
    .filter(value=>value!==''&&value!==null&&value!==undefined);

  if(!values.length)return false;
  return values.filter(value=>typeof value==='number'&&Number.isFinite(value)).length>=Math.ceil(values.length*.7);
}

function orderedTableRows(containerId,columns,rows){
  const ordered=[...rows];
  const sortState=state.tableSort[containerId];
  if(!sortState||!columns[sortState.index])return ordered;

  const column=columns[sortState.index];
  const getter=column.sortValue||column.exportValue||column.value||
    (column.html?(row)=>tableCellRawValue(column,row):null);

  if(!getter)return ordered;

  ordered.sort((a,b)=>{
    const av=normalizedSortValue(getter(a));
    const bv=normalizedSortValue(getter(b));

    const aEmpty=av===''||av===null||av===undefined;
    const bEmpty=bv===''||bv===null||bv===undefined;
    if(aEmpty!==bEmpty)return aEmpty?1:-1;

    let comparison=0;
    if(typeof av==='number'&&typeof bv==='number'){
      comparison=av-bv;
    }else{
      comparison=String(av).localeCompare(
        String(bv),
        'pt-BR',
        {numeric:true,sensitivity:'base'}
      );
    }
    return sortState.dir==='asc'?comparison:-comparison;
  });
  return ordered;
}

function xmlEscape(value){
  return String(value??'')
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;')
    .replace(/'/g,'&apos;');
}

function excelColumnName(index){
  let name='';
  let current=index+1;
  while(current>0){
    const remainder=(current-1)%26;
    name=String.fromCharCode(65+remainder)+name;
    current=Math.floor((current-1)/26);
  }
  return name;
}

function excelSafeSheetName(value){
  const cleaned=String(value||'Tabela')
    .replace(/[\\/*?:[\]]/g,' ')
    .replace(/\s+/g,' ')
    .trim();
  return (cleaned||'Tabela').slice(0,31);
}

function excelSafeFileName(value){
  return String(value||'tabela')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g,'')
    .replace(/[^a-zA-Z0-9_-]+/g,'_')
    .replace(/^_+|_+$/g,'')
    .toLowerCase()||'tabela';
}

async function downloadTableXlsx(containerId){
  const config=tableExportRegistry.get(containerId);
  if(!config){
    toast('Tabela ainda não está disponível para exportação.','error');
    return;
  }
  if(typeof JSZip!=='function'){
    toast('Componente de exportação Excel não foi carregado.','error');
    return;
  }

  const {columns,rows,title}=config;
  const exportColumns=columns.filter(column=>column.exportable!==false);
  const ordered=orderedTableRows(containerId,columns,rows);
  const sheetName=excelSafeSheetName(title);

  const headerCells=exportColumns.map((column,index)=>{
    const ref=`${excelColumnName(index)}1`;
    return `<c r="${ref}" t="inlineStr" s="1"><is><t>${xmlEscape(column.label)}</t></is></c>`;
  }).join('');

  const dataRows=ordered.map((row,rowIndex)=>{
    const excelRow=rowIndex+2;
    const cells=exportColumns.map((column,columnIndex)=>{
      const ref=`${excelColumnName(columnIndex)}${excelRow}`;
      const raw=tableCellRawValue(column,row);
      const normalized=normalizedSortValue(raw);

      if(typeof normalized==='number'&&Number.isFinite(normalized)){
        return `<c r="${ref}" t="n"><v>${normalized}</v></c>`;
      }

      return `<c r="${ref}" t="inlineStr"><is><t xml:space="preserve">${xmlEscape(raw)}</t></is></c>`;
    }).join('');
    return `<row r="${excelRow}">${cells}</row>`;
  }).join('');

  const lastColumn=excelColumnName(Math.max(0,exportColumns.length-1));
  const lastRow=Math.max(1,ordered.length+1);

  const worksheet=`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <dimension ref="A1:${lastColumn}${lastRow}"/>
  <sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>
  <sheetFormatPr defaultRowHeight="15"/>
  <sheetData>
    <row r="1">${headerCells}</row>
    ${dataRows}
  </sheetData>
  <autoFilter ref="A1:${lastColumn}${lastRow}"/>
</worksheet>`;

  const workbook=`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="${xmlEscape(sheetName)}" sheetId="1" r:id="rId1"/></sheets>
</workbook>`;

  const styles=`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="2">
    <font><sz val="11"/><name val="Calibri"/></font>
    <font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Calibri"/></font>
  </fonts>
  <fills count="3">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF173D5B"/><bgColor indexed="64"/></patternFill></fill>
  </fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="2">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>
  </cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>`;

  const zip=new JSZip();
  zip.file('[Content_Types].xml',`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>`);
  zip.folder('_rels').file('.rels',`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>`);
  zip.folder('xl').file('workbook.xml',workbook);
  zip.folder('xl').folder('_rels').file('workbook.xml.rels',`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>`);
  zip.folder('xl').folder('worksheets').file('sheet1.xml',worksheet);
  zip.folder('xl').file('styles.xml',styles);

  const blob=await zip.generateAsync({
    type:'blob',
    mimeType:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    compression:'DEFLATE',
    compressionOptions:{level:6}
  });

  const link=document.createElement('a');
  link.href=URL.createObjectURL(blob);
  link.download=`${excelSafeFileName(title)}_${isoDate(new Date())}.xlsx`;
  document.body.appendChild(link);
  link.click();
  const objectUrl=link.href;
  link.remove();
  setTimeout(()=>URL.revokeObjectURL(objectUrl),1500);
  toast(`Excel exportado: ${fmtInt(ordered.length)} registro(s).`,'success');
}

function realtimeTableTitle(containerId){
  const titles={
    rtTable:'Resumo de incidências ativas',
    rtConh:'Top 5 ConH',
    rtImpactTable:'Maiores afetações',
    rtTeams:'Equipes com incidência ativa',
    rtProcessSummary:'Equipes atuando por processo',
    rtVehicleSummary:'Equipes por tipo de viatura',
    rtCallbackStatus:'Ativas com e sem callback',
    rtFeederTable:'Incidências ativas por alimentador'
  };
  return titles[containerId]||containerId;
}

function ensureRealtimeTableExportButton(containerId){
  if(!REALTIME_TABLE_IDS.has(containerId))return;
  const tableContainer=$(containerId);
  const panel=tableContainer?.closest('.panel');
  const header=panel?.querySelector(':scope > .panel-head');
  if(!header||header.querySelector(`[data-table-xlsx="${containerId}"]`))return;

  const button=document.createElement('button');
  button.type='button';
  button.className='btn small table-xlsx-btn';
  button.dataset.tableXlsx=containerId;
  button.innerHTML='⇩ Excel';
  button.title=`Exportar ${realtimeTableTitle(containerId)} em formato Excel`;
  button.addEventListener('click',()=>downloadTableXlsx(containerId));
  header.appendChild(button);
}
'''


NEW_RENDER_TABLE = r'''function renderTable(containerId,columns,rows,{limit=300,empty='Sem registros',rowClass=null,footerRow=null,sortable=false}={}){
  const el=$(containerId);
  if(!el)return;

  const forceSortable=REALTIME_TABLE_IDS.has(containerId);
  const allowSort=sortable||forceSortable;
  const title=realtimeTableTitle(containerId);

  tableExportRegistry.set(containerId,{
    columns,
    rows:[...rows],
    title
  });

  ensureRealtimeTableExportButton(containerId);

  if(!rows.length){
    el.innerHTML=`<div style="padding:25px;text-align:center;color:#7b8a95">${esc(empty)}</div>`;
    return;
  }

  const ordered=orderedTableRows(containerId,columns,rows);
  const sortState=state.tableSort[containerId];
  const shown=ordered.slice(0,limit);

  const footer=footerRow
    ?`<tfoot><tr>${columns.map(c=>`<td class="${c.class||''}">${c.html?c.html(footerRow):esc(c.value?c.value(footerRow)??'':'')}</td>`).join('')}</tr></tfoot>`
    :'';

  const headers=columns.map((column,index)=>{
    const canSort=allowSort&&column.sortable!==false&&Boolean(
      column.sortValue||column.exportValue||column.value||column.html
    );

    if(!canSort){
      return `<th class="${column.class||''}">${esc(column.label)}</th>`;
    }

    const active=sortState&&sortState.index===index;
    const arrow=active?(sortState.dir==='desc'?'▼':'▲'):'↕';
    const numeric=tableColumnIsNumeric(column,rows);
    const firstDirection=numeric?'do maior para o menor':'em ordem alfabética';

    return `<th class="sortable-header ${column.class||''}">
      <button type="button"
        class="sort-header-btn ${column.class||''} ${active?'active':''}"
        data-table-sort="${index}"
        title="Ordenar ${active?(sortState.dir==='desc'?'do menor para o maior':'do maior para o menor'):firstDirection}">
        <span>${esc(column.label)}</span>
        <span class="sort-arrow">${arrow}</span>
      </button>
    </th>`;
  }).join('');

  el.innerHTML=`<table>
    <thead><tr>${headers}</tr></thead>
    <tbody>${shown.map((row,index)=>`<tr class="${rowClass?rowClass(row):''}" data-row="${index}">
      ${columns.map(column=>`<td class="${column.class||''}">${column.html?column.html(row):esc(column.value?column.value(row)??'':'')}</td>`).join('')}
    </tr>`).join('')}</tbody>
    ${footer}
  </table>
  ${rows.length>limit?`<div style="padding:8px;color:#6c7b86">Exibindo ${fmtInt(limit)} de ${fmtInt(rows.length)} registros. Ordene pelos cabeçalhos ou exporte o Excel completo.</div>`:''}`;

  if(allowSort){
    qsa('[data-table-sort]',el).forEach(button=>button.addEventListener('click',()=>{
      const index=Number(button.dataset.tableSort);
      const current=state.tableSort[containerId];
      let direction;

      if(current&&current.index===index){
        direction=current.dir==='desc'?'asc':'desc';
      }else{
        direction=tableColumnIsNumeric(columns[index],rows)?'desc':'asc';
      }

      state.tableSort[containerId]={index,dir:direction};

      if(REALTIME_TABLE_IDS.has(containerId)&&state.activeTab==='realtime'){
        renderRealtime();
      }else{
        renderTable(containerId,columns,rows,{limit,empty,rowClass,footerRow,sortable});
      }
    }));
  }
}'''


CSS = r'''
/* Ajustes das tabelas do Tempo Real */
.layout-main-aside{align-items:start}
.layout-main-aside>.panel{align-self:start;height:auto}
.table-xlsx-btn{margin-left:auto;flex:0 0 auto;background:#fff;color:#173d5b;border-color:rgba(255,255,255,.72)}
.panel-head:not(.green):not(.blue) .table-xlsx-btn{background:#fff;color:#173d5b;border-color:#cbd8e1}
.table-xlsx-btn:hover{filter:brightness(.96)}
.sortable-header{padding:0}
.sort-header-btn{width:100%;min-height:32px;border:0;background:transparent;color:inherit;font:inherit;font-weight:800;padding:7px 8px;display:flex;align-items:center;justify-content:space-between;gap:7px;cursor:pointer;text-align:left;white-space:nowrap}
.sort-header-btn.num{justify-content:flex-end}
.sort-header-btn:hover,.sort-header-btn.active{background:#dce9f2;color:#173d5b}
.sort-arrow{font-size:10px;opacity:.78}
'''


def replace_render_table(text: str) -> str:
    start = text.find("function renderTable(")
    if start < 0:
        raise RuntimeError("Função renderTable não encontrada.")

    end_marker = "\nfunction openDetails("
    end = text.find(end_marker, start)
    if end < 0:
        raise RuntimeError("Final da função renderTable não encontrado.")

    return text[:start] + NEW_RENDER_TABLE + text[end:]


def add_sortable_to_realtime_calls(text: str) -> str:
    start = text.find("function renderRealtime(){")
    end = text.find("\nfunction renderIncidents()", start)
    if start < 0 or end < 0:
        raise RuntimeError("Bloco renderRealtime não encontrado.")

    block = text[start:end]

    replacements = {
        "],sorted,{limit:500});": "],sorted,{limit:500,sortable:true});",
        "],conh,{limit:5});": "],conh,{limit:5,sortable:true});",
        "],teamStats,{limit:200});": "],teamStats,{limit:200,sortable:true});",
        "],feeders,{limit:200});": "],feeders,{limit:200,sortable:true});",
        "empty:'Nenhuma incidência ativa com afetação informada'});":
            "empty:'Nenhuma incidência ativa com afetação informada',sortable:true});",
    }
    for old, new in replacements.items():
        block = block.replace(old, new)

    block = block.replace(
        "{label:'Reincidência',html:r=>{const rec=recurrenceInfo(r);return rec?",
        "{label:'Reincidência',sortValue:r=>{const rec=recurrenceInfo(r);return rec?rec.label:'';},html:r=>{const rec=recurrenceInfo(r);return rec?",
    )
    block = block.replace(
        "{label:'Status execução',html:r=>badge(",
        "{label:'Status execução',sortValue:r=>r.executionStatus||'',html:r=>badge(",
    )
    block = block.replace(
        "{label:'Entrada',value:r=>brDate(r.startDate,true)}",
        "{label:'Entrada',value:r=>brDate(r.startDate,true),sortValue:r=>r.startDate}",
    )
    block = block.replace(
        "{label:'Duração',value:r=>`${fmt1(realtimeAgeHours(r,now))}h`,class:'num'}",
        "{label:'Duração',value:r=>`${fmt1(realtimeAgeHours(r,now))}h`,sortValue:r=>realtimeAgeHours(r,now),class:'num'}",
    )
    block = block.replace(
        "{label:'OSM',html:r=>badge(isOsm(r)?'SIM':'NÃO',isOsm(r)?'blue':'neutral')}",
        "{label:'OSM',sortValue:r=>isOsm(r)?1:0,html:r=>badge(isOsm(r)?'SIM':'NÃO',isOsm(r)?'blue':'neutral')}",
    )
    block = block.replace(
        "{label:'Clientes',value:r=>fmtInt(r.clientsCurrent),class:'num'}",
        "{label:'Clientes',value:r=>fmtInt(r.clientsCurrent),sortValue:r=>r.clientsCurrent,class:'num'}",
    )
    block = block.replace(
        "{label:'ConH',value:r=>fmtInt(realtimeConH(r,now)),class:'num'}",
        "{label:'ConH',value:r=>fmtInt(realtimeConH(r,now)),sortValue:r=>realtimeConH(r,now),class:'num'}",
    )
    block = block.replace(
        "{label:'Callback',html:r=>{const c=callbackSummary(r);return",
        "{label:'Callback',sortValue:r=>callbackSummary(r).count,html:r=>{const c=callbackSummary(r);return",
    )

    return text[:start] + block + text[end:]


def main() -> None:
    if not HTML.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {HTML}")

    text = HTML.read_text(encoding="utf-8")

    if MARCADOR in text:
        print("As melhorias de ordenação e exportação já estão instaladas.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = PASTA / f"Emergencia_backup_antes_tabelas_{timestamp}.html"
    shutil.copy2(HTML, backup)

    position = text.find("function renderTable(")
    if position < 0:
        raise RuntimeError("Função renderTable não encontrada.")
    text = text[:position] + HELPERS + "\n" + text[position:]

    text = replace_render_table(text)
    text = add_sortable_to_realtime_calls(text)

    if "</style>" not in text:
        raise RuntimeError("Fechamento </style> não encontrado.")
    text = text.replace("</style>", CSS + "\n</style>", 1)

    temporary = PASTA / "Emergencia.__tabelas_tmp__.html"
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(HTML)

    print("=" * 78)
    print("TABELAS DO TEMPO REAL ATUALIZADAS")
    print("=" * 78)
    print(f"HTML atualizado: {HTML}")
    print(f"Backup criado: {backup}")
    print("Alterações:")
    print("  - ordenação em todas as colunas das tabelas do Tempo Real")
    print("  - primeiro clique: números decrescente; textos alfabético")
    print("  - botão Excel individual em cada tabela")
    print("  - exportação .xlsx com todos os registros da tabela")
    print("  - remoção do espaço vazio abaixo do resumo de incidências ativas")


if __name__ == "__main__":
    main()
