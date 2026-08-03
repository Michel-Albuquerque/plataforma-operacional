from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


PASTA = Path(
    r"C:\Users\BR0143306567\OneDrive - Enel Spa\Documentos\Michel"
    r"\Plataforma_HTML"
)
HTML = PASTA / "Emergencia.html"
MARCADOR = "AJUSTE_RISCO_24H_CORTE_08H_GRAFICO_V2"


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
        f"Emergencia_backup_antes_ajuste_risco24h_"
        f"{datetime.now():%Y%m%d_%H%M%S}.html"
    )
    shutil.copy2(HTML, backup)

    texto = substituir(
        texto,
        "cutoff.setHours(7,0,0,0);",
        "cutoff.setHours(8,0,0,0);",
        "corte operacional de 07:00 para 08:00",
    )

    texto = substituir(
        texto,
        '<small id="rt24hCutoff">Projeção até 07:00 do próximo dia</small>',
        '<small id="rt24hCutoff">Projeção até 08:00 do próximo dia</small>',
        "texto do corte operacional",
    )

    texto = substituir(
        texto,
        "<h3>Distribuição das incidências por duração</h3>\n              <small>Faixas de duas em duas horas com base na duração atual</small>",
        "<h3>Risco de 24h por tempo restante</h3>\n              <small>Quantidade de incidências que podem atingir 24h até 08:00, agrupadas pelo tempo restante</small>",
        "título e descrição do gráfico",
    )

    bloco_antigo = r'''  const durationValues=rows
    .map(r=>currentRealtimeDurationHours(r,now))
    .filter(value=>Number.isFinite(value)&&value>=0);

  if(durationValues.length){
    const maxDuration=Math.max(...durationValues);
    const upper=Math.max(2,Math.ceil(maxDuration/2)*2);
    const starts=[];
    for(let start=0;start<upper;start+=2)starts.push(start);
    const labels=starts.map(start=>durationBinLabel(start,start+2));
    const counts=starts.map(start=>durationValues.filter(value=>value>=start&&value<(start+2)).length);

    plot('chartRtDurationBins',[{
      type:'bar',
      x:labels,
      y:counts,
      marker:{color:starts.map(start=>start>=24?COLORS.red:start>=16?COLORS.orange:start>=8?COLORS.mt:COLORS.blue2)},
      text:counts.map(fmtInt),
      textposition:'outside',
      cliponaxis:false,
      customdata:starts
    }],{
      margin:{l:45,r:15,t:15,b:75},
      xaxis:{title:'Faixa de duração',tickangle:-45,automargin:true},
      yaxis:{title:'Quantidade de incidências',rangemode:'tozero',dtick:1},
      bargap:.18
    },ev=>{
      const start=Number(ev.points[0].customdata);
      const selected=rows.filter(r=>{
        const duration=currentRealtimeDurationHours(r,now);
        return duration>=start&&duration<(start+2);
      });
      openDetails(`Duração entre ${fmtInt(start)}h e ${fmtInt(start+2)}h`,selected);
    });
  }else{
    emptyPlot('chartRtDurationBins','Sem duração disponível para as incidências ativas.');
  }
'''

    bloco_novo = r'''  if(risk24Rows.length){
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

    texto = substituir(
        texto,
        bloco_antigo,
        bloco_novo,
        "gráfico baseado nas incidências da tabela de risco",
    )

    texto = texto.replace(
        "</style>",
        f"\n/* {MARCADOR} */\n</style>",
        1,
    )

    temporario = PASTA / "Emergencia.__ajuste_risco24h_08h_tmp__.html"
    temporario.write_text(texto, encoding="utf-8")
    temporario.replace(HTML)

    print("=" * 78)
    print("AJUSTE DO RISCO DE 24H CONCLUÍDO")
    print("=" * 78)
    print(f"HTML atualizado: {HTML}")
    print(f"Backup criado: {backup}")
    print("Alterações:")
    print("  - corte operacional alterado para 08:00")
    print("  - gráfico usa somente as incidências da tabela de risco")
    print("  - eixo X mostra faixas de horas restantes para atingir 24h")
    print("  - rótulos mostram a quantidade por intervalo")
    print("  - hover mostra as equipes do intervalo")
    print("  - rótulos e grade do eixo Y removidos")
    print("  - fundo do gráfico mantido branco")


if __name__ == "__main__":
    main()
