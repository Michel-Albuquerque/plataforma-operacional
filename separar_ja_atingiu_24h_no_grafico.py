from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


PASTA = Path(
    r"C:\Users\BR0143306567\OneDrive - Enel Spa\Documentos\Michel"
    r"\Plataforma_HTML"
)
HTML = PASTA / "Emergencia.html"
MARCADOR = "SEPARAR_JA_ATINGIU_24H_NO_GRAFICO_V1"


def substituir(texto: str, antigo: str, novo: str, nome: str) -> str:
    if novo in texto:
        print(f"Já aplicado: {nome}")
        return texto
    if antigo not in texto:
        raise RuntimeError(f"Trecho não encontrado: {nome}")
    print(f"Aplicando: {nome}")
    return texto.replace(antigo, novo, 1)


def main() -> None:
    if not HTML.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {HTML}")

    texto = HTML.read_text(encoding="utf-8")

    if MARCADOR in texto:
        print("Este ajuste já foi aplicado.")
        return

    backup = PASTA / (
        f"Emergencia_backup_antes_separar_24h_"
        f"{datetime.now():%Y%m%d_%H%M%S}.html"
    )
    shutil.copy2(HTML, backup)

    antigo = r'''  if(risk24Rows.length){
    const maxRemaining=Math.max(...risk24Rows.map(r=>r._hoursUntil24),2);
    const upper=Math.max(2,Math.ceil(maxRemaining/2)*2);
    const starts=[];
    for(let start=0;start<upper;start+=2)starts.push(start);

    const labels=starts.map(start=>start===0?'0–2h':durationBinLabel(start,start+2));
    const grouped=starts.map(start=>{
      const selected=risk24Rows.filter(r=>{
        if(start===0)return r._hoursUntil24>=0&&r._hoursUntil24<2;
        return r._hoursUntil24>=start&&r._hoursUntil24<(start+2);
      });
      return {
        start,
        selected,
        count:selected.length,
        teams:unique(selected.map(r=>r.team||r.teamAssigned||'SEM EQUIPE')).sort((a,b)=>String(a).localeCompare(String(b),'pt-BR'))
      };
    });

    plot('chartRtDurationBins',[{
      type:'bar',
      x:labels,
      y:grouped.map(g=>g.count),
      marker:{
        color:starts.map(start=>start<2?COLORS.red:start<4?COLORS.orange:start<8?COLORS.mt:COLORS.blue2)
      },
      text:grouped.map(g=>fmtInt(g.count)),
      textposition:'outside',
      cliponaxis:false,
      customdata:grouped.map(g=>({
        start:g.start,
        teams:g.teams,
        count:g.count
      })),
      hovertemplate:'<b>%{x} restantes</b><br>Incidências: %{y}<br>Equipes: %{customdata.teams}<extra></extra>'
    }],{
      margin:{l:15,r:15,t:20,b:65},
      xaxis:{
        title:'Horas restantes para atingir 24h',
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
      showlegend:false
    },ev=>{
      const start=Number(ev.points[0].customdata.start);
      const selected=risk24Rows.filter(r=>{
        if(start===0)return r._hoursUntil24>=0&&r._hoursUntil24<2;
        return r._hoursUntil24>=start&&r._hoursUntil24<(start+2);
      });
      openDetails(
        `Faltam entre ${fmtInt(start)}h e ${fmtInt(start+2)}h para atingir 24h`,
        selected
      );
    });
  }else{
    emptyPlot(
      'chartRtDurationBins',
      'Nenhuma incidência pode atingir 24h até 08:00.'
    );
  }
'''

    novo = r'''  if(risk24Rows.length){
    const overdueRows=risk24Rows.filter(r=>r._durationHours>=24);
    const pendingRows=risk24Rows.filter(r=>r._durationHours<24);
    const maxRemaining=Math.max(...pendingRows.map(r=>r._hoursUntil24),2);
    const upper=Math.max(2,Math.ceil(maxRemaining/2)*2);
    const starts=[];
    for(let start=0;start<upper;start+=2)starts.push(start);

    const grouped=[
      {
        key:'OVERDUE',
        label:'Já atingiu 24h',
        selected:overdueRows,
        count:overdueRows.length,
        teams:unique(overdueRows.map(r=>r.team||r.teamAssigned||'SEM EQUIPE')).sort((a,b)=>String(a).localeCompare(String(b),'pt-BR'))
      },
      ...starts.map(start=>{
        const selected=pendingRows.filter(r=>r._hoursUntil24>start&&r._hoursUntil24<=start+2);
        return {
          key:`${start}-${start+2}`,
          label:durationBinLabel(start,start+2),
          start,
          selected,
          count:selected.length,
          teams:unique(selected.map(r=>r.team||r.teamAssigned||'SEM EQUIPE')).sort((a,b)=>String(a).localeCompare(String(b),'pt-BR'))
        };
      })
    ];

    plot('chartRtDurationBins',[{
      type:'bar',
      x:grouped.map(g=>g.label),
      y:grouped.map(g=>g.count),
      marker:{
        color:grouped.map((g,index)=>index===0?COLORS.red:g.start<2?COLORS.orange:g.start<4?COLORS.mt:COLORS.blue2),
        line:{
          color:grouped.map((g,index)=>index===0?'#7f1026':'rgba(0,0,0,0)'),
          width:grouped.map((g,index)=>index===0?2:0)
        }
      },
      text:grouped.map(g=>fmtInt(g.count)),
      textposition:'outside',
      cliponaxis:false,
      customdata:grouped.map(g=>({
        key:g.key,
        start:g.start,
        teams:g.teams,
        count:g.count
      })),
      hovertemplate:'<b>%{x}</b><br>Incidências: %{y}<br>Equipes: %{customdata.teams}<extra></extra>'
    }],{
      margin:{l:15,r:15,t:20,b:75},
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
      showlegend:false
    },ev=>{
      const data=ev.points[0].customdata;
      let selected;
      let title;

      if(data.key==='OVERDUE'){
        selected=overdueRows;
        title='Incidências que já atingiram 24h';
      }else{
        const start=Number(data.start);
        selected=pendingRows.filter(r=>r._hoursUntil24>start&&r._hoursUntil24<=start+2);
        title=`Faltam mais de ${fmtInt(start)}h e até ${fmtInt(start+2)}h para atingir 24h`;
      }

      openDetails(title,selected);
    });
  }else{
    emptyPlot(
      'chartRtDurationBins',
      'Nenhuma incidência pode atingir 24h até 08:00.'
    );
  }
'''

    texto = substituir(
        texto,
        antigo,
        novo,
        "separação de incidências que já atingiram 24h",
    )

    texto = texto.replace(
        "</style>",
        f"\n/* {MARCADOR} */\n</style>",
        1,
    )

    temporario = PASTA / "Emergencia.__separar_24h_tmp__.html"
    temporario.write_text(texto, encoding="utf-8")
    temporario.replace(HTML)

    print("=" * 78)
    print("GRÁFICO DE RISCO DE 24H AJUSTADO")
    print("=" * 78)
    print(f"HTML atualizado: {HTML}")
    print(f"Backup criado: {backup}")
    print("Agora o gráfico possui:")
    print("  - barra exclusiva 'Já atingiu 24h'")
    print("  - barra separada para 0–2h restantes")
    print("  - demais faixas de 2 em 2 horas")
    print("  - destaque visual reforçado na primeira barra")
    print("  - clique individual para abrir os registros de cada grupo")


if __name__ == "__main__":
    main()
