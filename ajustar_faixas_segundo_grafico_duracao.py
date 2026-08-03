from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

PASTA = Path(
    r"C:\Users\BR0143306567\OneDrive - Enel Spa\Documentos\Michel"
    r"\Plataforma_HTML"
)
HTML = PASTA / "Emergencia.html"
MARCADOR = "FAIXAS_AMPLAS_GRAFICO_EQUIPE_DURACAO_V1"


def main() -> None:
    if not HTML.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {HTML}")

    text = HTML.read_text(encoding="utf-8")
    if MARCADOR in text:
        print("Este ajuste já foi aplicado.")
        return

    backup = PASTA / (
        f"Emergencia_backup_antes_faixas_amplas_equipe_"
        f"{datetime.now():%Y%m%d_%H%M%S}.html"
    )
    shutil.copy2(HTML, backup)

    old_start = "    const layoutAssign=addTopTotalAnnotations({"
    old_end = "    });\n  }else{\n    emptyPlot("

    start_pos = text.find(old_start)
    if start_pos < 0:
        raise RuntimeError("Início do bloco do segundo gráfico não encontrado.")

    end_pos = text.find(old_end, start_pos)
    if end_pos < 0:
        raise RuntimeError("Fim do bloco do segundo gráfico não encontrado.")

    new_block = r'''    const assignmentDurationBands=[
      {
        key:'0-8',
        label:'0–8h',
        selected:risk24Rows.filter(r=>r._durationHours>=0&&r._durationHours<8)
      },
      {
        key:'8-16',
        label:'8–16h',
        selected:risk24Rows.filter(r=>r._durationHours>=8&&r._durationHours<16)
      },
      {
        key:'16-24',
        label:'16–24h',
        selected:risk24Rows.filter(r=>r._durationHours>=16&&r._durationHours<24)
      },
      {
        key:'24-30',
        label:'24–30h',
        selected:risk24Rows.filter(r=>r._durationHours>=24&&r._durationHours<30)
      },
      {
        key:'30-48',
        label:'30–48h',
        selected:risk24Rows.filter(r=>r._durationHours>=30&&r._durationHours<=48)
      },
      {
        key:'OVER48',
        label:'Acima de 48h',
        selected:risk24Rows.filter(r=>r._durationHours>48)
      }
    ].map((g,index)=>{
      const withTeamRows=g.selected.filter(r=>hasAssignedTeam(r));
      const withoutTeamRows=g.selected.filter(r=>!hasAssignedTeam(r));
      const colors=
        index<=1?riskColorPair('blue',index):
        index===2?riskColorPair('yellow',index):
        index===3?riskColorPair('orange',index):
        riskColorPair('red',index);

      return {
        ...g,
        index,
        withTeamRows,
        withoutTeamRows,
        withTeam:withTeamRows.length,
        withoutTeam:withoutTeamRows.length,
        total:g.selected.length,
        colors
      };
    });

    const assignmentLabels=assignmentDurationBands.map(g=>g.label);

    const layoutAssign=addTopTotalAnnotations({
      margin:{l:15,r:15,t:28,b:78},
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
      legend:{orientation:'h',y:1.12,x:0},
      showlegend:false
    },assignmentDurationBands);

    plot('chartRtTeamAssignmentBins',[
      {
        type:'bar',
        name:'Sem equipe atribuída',
        x:assignmentLabels,
        y:assignmentDurationBands.map(g=>g.withoutTeam),
        marker:{color:assignmentDurationBands.map(g=>g.colors.a)},
        text:assignmentDurationBands.map(g=>g.withoutTeam>0?fmtInt(g.withoutTeam):''),
        textposition:'inside',
        textfont:{color:'#1f2937',size:11},
        customdata:assignmentDurationBands.map(g=>({key:g.key,label:g.label,segment:'SEM_EQUIPE'})),
        hovertemplate:'<b>%{x}</b><br>Sem equipe atribuída: %{y}<extra></extra>'
      },
      {
        type:'bar',
        name:'Com equipe atribuída',
        x:assignmentLabels,
        y:assignmentDurationBands.map(g=>g.withTeam),
        marker:{color:assignmentDurationBands.map(g=>g.colors.b)},
        text:assignmentDurationBands.map(g=>g.withTeam>0?fmtInt(g.withTeam):''),
        textposition:'inside',
        textfont:{color:'#ffffff',size:11},
        customdata:assignmentDurationBands.map(g=>({key:g.key,label:g.label,segment:'COM_EQUIPE'})),
        hovertemplate:'<b>%{x}</b><br>Com equipe atribuída: %{y}<extra></extra>'
      }
    ],layoutAssign,ev=>{
      const data=ev.points[0].customdata;
      const group=assignmentDurationBands.find(g=>g.key===data.key);
      if(!group)return;

      const selected=data.segment==='COM_EQUIPE'
        ?group.withTeamRows
        :group.withoutTeamRows;

      const suffix=data.segment==='COM_EQUIPE'
        ?'Com equipe atribuída'
        :'Sem equipe atribuída';

      openDetails(`Duração ${group.label} • ${suffix}`,selected);
    });'''

    text = text[:start_pos] + new_block + text[end_pos + len("    });"):]

    text = text.replace(
        "Risco de 24h por tempo restante • incidências com equipe atribuída x sem equipe",
        "Incidências por duração atual • com equipe atribuída x sem equipe",
        1,
    )

    text = text.replace(
        "</style>",
        f"\n/* {MARCADOR} */\n</style>",
        1,
    )

    temp = PASTA / "Emergencia.__faixas_amplas_equipe_tmp__.html"
    temp.write_text(text, encoding="utf-8")
    temp.replace(HTML)

    print("=" * 78)
    print("FAIXAS DO GRÁFICO DE EQUIPES ATUALIZADAS")
    print("=" * 78)
    print(f"HTML atualizado: {HTML}")
    print(f"Backup criado: {backup}")
    print("Novas faixas do segundo gráfico:")
    print("  - 0–8h")
    print("  - 8–16h")
    print("  - 16–24h")
    print("  - 24–30h")
    print("  - 30–48h")
    print("  - Acima de 48h")


if __name__ == "__main__":
    main()
