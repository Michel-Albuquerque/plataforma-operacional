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
MARCADOR = "GRAFICOS_EMPILHADOS_COMPLETOS_RISCO_V3"


CSS = r'''
/* GRAFICOS_EMPILHADOS_COMPLETOS_RISCO_V3 */
.emg-chart-subtitle{
  margin:2px 0 8px;
  font-size:11px;
  font-weight:800;
  color:#284b63;
  letter-spacing:.01em
}
.emg-chart-gap{height:14px}
'''


HELPERS = r'''
function ntRiskGroup(v){
  const txt=String(v||'').toUpperCase();
  return txt.includes('MT') ? 'MT' : 'BT';
}

function hasAssignedTeam(r){
  const team=String(r?.team||r?.teamAssigned||'---').trim();
  return Boolean(team&&team!=='---');
}

function riskColorPair(group){
  if(group==='overdue')return {light:'#f3a7b3',dark:'#b5122b'};
  if(group==='blue')return {light:'#a9d0f5',dark:'#2f80ed'};
  if(group==='yellow')return {light:'#f8e6a0',dark:'#f2c94c'};
  if(group==='orange')return {light:'#f7c59a',dark:'#f2994a'};
  return {light:'#efaaaa',dark:'#d64545'};
}

function riskBandByRemaining(start,index){
  if(index===0)return 'overdue';
  if(start<10)return 'blue';
  if(start<14)return 'yellow';
  if(start<18)return 'orange';
  return 'red';
}

function addTopTotalAnnotations(layout,groups){
  layout.annotations=(layout.annotations||[]).concat(
    groups.map(g=>({
      x:g.label,
      y:g.total,
      text:`<b>${fmtInt(g.total)}</b>`,
      showarrow:false,
      yshift:12,
      font:{size:11,color:'#243447'}
    }))
  );
  return layout;
}
'''


NEW_RENDER_BLOCK = r'''
  if(risk24Rows.length){
    const overdueRows=risk24Rows.filter(r=>r._durationHours>=24);
    const pendingRows=risk24Rows.filter(r=>r._durationHours<24);
    const maxRemaining=Math.max(...pendingRows.map(r=>r._hoursUntil24),2);
    const upper=Math.max(2,Math.ceil(maxRemaining/2)*2);
    const starts=[];
    for(let start=0;start<upper;start+=2)starts.push(start);

    const remainingGroups=[
      {
        key:'OVERDUE',
        label:'Já atingiu 24h',
        start:null,
        selected:overdueRows
      },
      ...starts.map(start=>({
        key:`${start}-${start+2}`,
        label:durationBinLabel(start,start+2),
        start,
        selected:pendingRows.filter(r=>r._hoursUntil24>start&&r._hoursUntil24<=start+2)
      }))
    ].map((g,index)=>{
      const btRows=g.selected.filter(r=>ntRiskGroup(r.ntRaw)==='BT');
      const mtRows=g.selected.filter(r=>ntRiskGroup(r.ntRaw)==='MT');
      const colors=riskColorPair(riskBandByRemaining(g.start,index));

      return {
        ...g,
        btRows,
        mtRows,
        bt:btRows.length,
        mt:mtRows.length,
        total:g.selected.length,
        colors
      };
    });

    const remainingLabels=remainingGroups.map(g=>g.label);

    const riskLayout=addTopTotalAnnotations({
      margin:{l:15,r:15,t:30,b:78},
      xaxis:{
        title:'Situação / horas restantes para atingir 24h',
        tickangle:-35,
        automargin:true,
        showgrid:false,
        zeroline:false
      },
      yaxis:{
        showticklabels:false,
        showgrid:false,
        zeroline:false,
        rangemode:'tozero'
      },
      plot_bgcolor:'#ffffff',
      paper_bgcolor:'#ffffff',
      bargap:.18,
      barmode:'stack',
      showlegend:false
    },remainingGroups);

    plot('chartRtDurationBins',[
      {
        type:'bar',
        name:'BT',
        x:remainingLabels,
        y:remainingGroups.map(g=>g.bt),
        marker:{color:remainingGroups.map(g=>g.colors.light)},
        text:remainingGroups.map(g=>g.bt>0?fmtInt(g.bt):''),
        textposition:'inside',
        textfont:{color:'#1f2937',size:11},
        customdata:remainingGroups.map(g=>({key:g.key,segment:'BT'})),
        hovertemplate:'<b>%{x}</b><br>BT: %{y}<extra></extra>'
      },
      {
        type:'bar',
        name:'MT',
        x:remainingLabels,
        y:remainingGroups.map(g=>g.mt),
        marker:{color:remainingGroups.map(g=>g.colors.dark)},
        text:remainingGroups.map(g=>g.mt>0?fmtInt(g.mt):''),
        textposition:'inside',
        textfont:{color:'#ffffff',size:11},
        customdata:remainingGroups.map(g=>({key:g.key,segment:'MT'})),
        hovertemplate:'<b>%{x}</b><br>MT: %{y}<extra></extra>'
      }
    ],riskLayout,ev=>{
      const data=ev.points[0].customdata;
      const group=remainingGroups.find(g=>g.key===data.key);
      if(!group)return;

      const selected=data.segment==='MT'?group.mtRows:group.btRows;
      const title=group.key==='OVERDUE'
        ?`Já atingiu 24h • ${data.segment}`
        :`Faltam ${group.label} para atingir 24h • ${data.segment}`;

      openDetails(title,selected);
    });

    const durationGroups=[
      {
        key:'0-8',
        label:'0–8h',
        selected:risk24Rows.filter(r=>r._durationHours>=0&&r._durationHours<8),
        band:'blue'
      },
      {
        key:'8-16',
        label:'8–16h',
        selected:risk24Rows.filter(r=>r._durationHours>=8&&r._durationHours<16),
        band:'blue'
      },
      {
        key:'16-24',
        label:'16–24h',
        selected:risk24Rows.filter(r=>r._durationHours>=16&&r._durationHours<24),
        band:'yellow'
      },
      {
        key:'24-30',
        label:'24–30h',
        selected:risk24Rows.filter(r=>r._durationHours>=24&&r._durationHours<30),
        band:'orange'
      },
      {
        key:'30-48',
        label:'30–48h',
        selected:risk24Rows.filter(r=>r._durationHours>=30&&r._durationHours<=48),
        band:'red'
      },
      {
        key:'OVER48',
        label:'Acima de 48h',
        selected:risk24Rows.filter(r=>r._durationHours>48),
        band:'overdue'
      }
    ].map(g=>{
      const withTeamRows=g.selected.filter(r=>hasAssignedTeam(r));
      const withoutTeamRows=g.selected.filter(r=>!hasAssignedTeam(r));
      const colors=riskColorPair(g.band);

      return {
        ...g,
        withTeamRows,
        withoutTeamRows,
        withTeam:withTeamRows.length,
        withoutTeam:withoutTeamRows.length,
        total:g.selected.length,
        colors
      };
    });

    const durationLabels=durationGroups.map(g=>g.label);

    const teamLayout=addTopTotalAnnotations({
      margin:{l:15,r:15,t:30,b:72},
      xaxis:{
        title:'Duração atual da incidência',
        tickangle:-25,
        automargin:true,
        showgrid:false,
        zeroline:false
      },
      yaxis:{
        showticklabels:false,
        showgrid:false,
        zeroline:false,
        rangemode:'tozero'
      },
      plot_bgcolor:'#ffffff',
      paper_bgcolor:'#ffffff',
      bargap:.24,
      barmode:'stack',
      showlegend:false
    },durationGroups);

    plot('chartRtTeamAssignmentBins',[
      {
        type:'bar',
        name:'Sem equipe atribuída',
        x:durationLabels,
        y:durationGroups.map(g=>g.withoutTeam),
        marker:{color:durationGroups.map(g=>g.colors.light)},
        text:durationGroups.map(g=>g.withoutTeam>0?fmtInt(g.withoutTeam):''),
        textposition:'inside',
        textfont:{color:'#1f2937',size:11},
        customdata:durationGroups.map(g=>({key:g.key,segment:'SEM_EQUIPE'})),
        hovertemplate:'<b>%{x}</b><br>Sem equipe atribuída: %{y}<extra></extra>'
      },
      {
        type:'bar',
        name:'Com equipe atribuída',
        x:durationLabels,
        y:durationGroups.map(g=>g.withTeam),
        marker:{color:durationGroups.map(g=>g.colors.dark)},
        text:durationGroups.map(g=>g.withTeam>0?fmtInt(g.withTeam):''),
        textposition:'inside',
        textfont:{color:'#ffffff',size:11},
        customdata:durationGroups.map(g=>({key:g.key,segment:'COM_EQUIPE'})),
        hovertemplate:'<b>%{x}</b><br>Com equipe atribuída: %{y}<extra></extra>'
      }
    ],teamLayout,ev=>{
      const data=ev.points[0].customdata;
      const group=durationGroups.find(g=>g.key===data.key);
      if(!group)return;

      const selected=data.segment==='COM_EQUIPE'
        ?group.withTeamRows
        :group.withoutTeamRows;

      const suffix=data.segment==='COM_EQUIPE'
        ?'Com equipe atribuída'
        :'Sem equipe atribuída';

      openDetails(`Duração ${group.label} • ${suffix}`,selected);
    });
  }else{
    emptyPlot(
      'chartRtDurationBins',
      'Nenhuma incidência pode atingir 24h até 08:00.'
    );
    emptyPlot(
      'chartRtTeamAssignmentBins',
      'Nenhuma incidência pode atingir 24h até 08:00.'
    );
  }
'''


def main() -> None:
    if not HTML.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {HTML}")

    text = HTML.read_text(encoding="utf-8")

    if MARCADOR in text:
        print("Este ajuste já foi aplicado.")
        return

    backup = PASTA / (
        f"Emergencia_backup_antes_graficos_empilhados_"
        f"{datetime.now():%Y%m%d_%H%M%S}.html"
    )
    shutil.copy2(HTML, backup)

    if "</style>" not in text:
        raise RuntimeError("Tag </style> não encontrada.")
    text = text.replace("</style>", CSS + "\n</style>", 1)

    old_chart = '<div id="chartRtDurationBins" class="chart tall"></div>'
    new_chart = '''<div class="emg-chart-subtitle">Risco de 24h por tempo restante • composição BT x MT</div>
            <div id="chartRtDurationBins" class="chart tall"></div>
            <div class="emg-chart-gap"></div>
            <div class="emg-chart-subtitle">Incidências por duração atual • com equipe atribuída x sem equipe</div>
            <div id="chartRtTeamAssignmentBins" class="chart tall"></div>'''

    if "chartRtTeamAssignmentBins" not in text:
        if old_chart not in text:
            raise RuntimeError("Área do gráfico atual não encontrada.")
        text = text.replace(old_chart, new_chart, 1)

    if "function ntRiskGroup(v)" not in text:
        anchor = "function renderRealtime(){"
        if anchor not in text:
            raise RuntimeError("Função renderRealtime não encontrada.")
        text = text.replace(anchor, HELPERS + "\n" + anchor, 1)

    pattern = re.compile(
        r"\n  if\(risk24Rows\.length\)\{"
        r".*?"
        r"\n  \}else\{\n"
        r"\s*emptyPlot\(\n"
        r"\s*'chartRtDurationBins',\n"
        r"\s*'Nenhuma incidência pode atingir 24h até 08:00\.'\n"
        r"\s*\);\n"
        r"\s*\}\n",
        re.S,
    )

    match = pattern.search(text)
    if not match:
        raise RuntimeError(
            "O bloco atual do gráfico de risco não foi encontrado. "
            "Nenhuma alteração foi realizada no HTML."
        )

    text = text[:match.start()] + "\n" + NEW_RENDER_BLOCK + text[match.end():]

    text = text.replace(
        "</style>",
        f"\n/* {MARCADOR} */\n</style>",
        1,
    )

    temp = PASTA / "Emergencia.__graficos_empilhados_completos_tmp__.html"
    temp.write_text(text, encoding="utf-8")
    temp.replace(HTML)

    print("=" * 78)
    print("GRÁFICOS EMPILHADOS INSTALADOS")
    print("=" * 78)
    print(f"HTML atualizado: {HTML}")
    print(f"Backup criado: {backup}")
    print("Gráfico 1:")
    print("  - barras empilhadas BT x MT")
    print("  - MT Ramal e MT Tronco consolidados em MT")
    print("  - rótulos internos e total acima da barra")
    print("Gráfico 2:")
    print("  - barras empilhadas com equipe x sem equipe")
    print("  - faixas: 0–8h, 8–16h, 16–24h, 24–30h, 30–48h e acima de 48h")


if __name__ == "__main__":
    main()
