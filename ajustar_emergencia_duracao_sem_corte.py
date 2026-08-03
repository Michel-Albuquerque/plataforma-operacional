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
MARCADOR = "DURACAO_ATIVA_SEM_CORTE_V1"


def main() -> None:
    if not HTML.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {HTML}")

    texto = HTML.read_text(encoding="utf-8")

    if MARCADOR in texto:
        print("Este ajuste já foi aplicado.")
        return

    backup = PASTA / (
        f"Emergencia_backup_antes_duracao_sem_corte_"
        f"{datetime.now():%Y%m%d_%H%M%S}.html"
    )
    shutil.copy2(HTML, backup)

    substituicoes = {
        "Risco de duração igual ou superior a 24h": "Incidências ativas ordenadas por duração",
        "Projeção até 08:00 do próximo dia": "Todas as incidências ativas, da maior para a menor duração",
        "Já atingiu 24h": "Acima de 48h",
        "Até 2h": "30h a 48h",
        "2h a 4h": "24h a 30h",
        "4h a 8h": "12h a 24h",
        "Acima de 8h": "Até 12h",
        "Risco de 24h por tempo restante": "Distribuição das incidências por duração",
        "Quantidade de incidências que podem atingir 24h até 08:00, agrupadas pelo tempo restante":
            "Quantidade de incidências abertas em faixas de duração",
    }
    for antigo, novo in substituicoes.items():
        texto = texto.replace(antigo, novo)

    texto = re.sub(
        r"\nfunction nextOperationalCutoff7\(now=new Date\(\)\)\{.*?\n\}\n",
        "\n",
        texto,
        count=1,
        flags=re.DOTALL,
    )

    texto = re.sub(
        r"function risk24RowClass\(r,now=new Date\(\)\)\{.*?\n\}",
        """function risk24RowClass(r,now=new Date()){
  const duration=currentRealtimeDurationHours(r,now);
  if(duration>=48)return 'risk24-overdue';
  if(duration>=30)return 'risk24-critical';
  if(duration>=24)return 'risk24-high';
  if(duration>=12)return 'risk24-medium';
  return 'risk24-watch';
}""",
        texto,
        count=1,
        flags=re.DOTALL,
    )

    inicio = texto.find("  const cutoff24=nextOperationalCutoff7(now);")
    fim = texto.find("  const teamStats=groupStats(withTeam,r=>r.team)", inicio)

    if inicio == -1 or fim == -1:
        raise RuntimeError(
            "Não foi possível localizar o bloco atual da tabela e do gráfico de duração."
        )

    novo_bloco = r'''  const durationRows=rows
    .map(r=>({
      ...r,
      _durationHours:currentRealtimeDurationHours(r,now)
    }))
    .sort((a,b)=>b._durationHours-a._durationHours);

  if($('rt24hCutoff')){
    $('rt24hCutoff').textContent='Todas as incidências ativas, da maior para a menor duração';
  }
  if($('rt24hSummary')){
    const over48=durationRows.filter(r=>r._durationHours>=48).length;
    const over30=durationRows.filter(r=>r._durationHours>=30&&r._durationHours<48).length;
    const over24=durationRows.filter(r=>r._durationHours>=24&&r._durationHours<30).length;
    $('rt24hSummary').textContent=`${fmtInt(durationRows.length)} incidência(s) ativa(s) • ${fmtInt(over48)} acima de 48h • ${fmtInt(over30)} entre 30h e 48h • ${fmtInt(over24)} entre 24h e 30h`;
  }

  renderTable('rt24hRiskTable',[
    {label:'Incidência',value:r=>r.number},
    {label:'Equipe',value:r=>r.team||r.teamAssigned||'---'},
    {label:'Nível de tensão',value:r=>r.ntRaw||'---'},
    {label:'Alimentador',value:r=>r.feeder||'---'},
    {label:'Duração',value:r=>`${fmt1(r._durationHours)}h`,sortValue:r=>r._durationHours,class:'num'}
  ],durationRows,{
    limit:500,
    sortable:true,
    rowClass:r=>risk24RowClass(r,now),
    empty:'Nenhuma incidência ativa com duração disponível.'
  });

  if(durationRows.length){
    const buckets=[
      {
        key:'GT48',
        label:'Acima de 48h',
        selected:durationRows.filter(r=>r._durationHours>=48)
      },
      {
        key:'30_48',
        label:'30h–48h',
        selected:durationRows.filter(r=>r._durationHours>=30&&r._durationHours<48)
      },
      {
        key:'24_30',
        label:'24h–30h',
        selected:durationRows.filter(r=>r._durationHours>=24&&r._durationHours<30)
      }
    ];

    for(let start=22;start>=0;start-=2){
      buckets.push({
        key:`${start}_${start+2}`,
        label:`${start}h–${start+2}h`,
        selected:durationRows.filter(r=>r._durationHours>=start&&r._durationHours<start+2)
      });
    }

    const chartBuckets=buckets.map((bucket,index)=>({
      ...bucket,
      count:bucket.selected.length,
      teams:unique(bucket.selected.map(r=>r.team||r.teamAssigned||'SEM EQUIPE'))
        .sort((a,b)=>String(a).localeCompare(String(b),'pt-BR')),
      color:index===0?COLORS.red:index===1?COLORS.orange:index===2?COLORS.mt:COLORS.blue2
    }));

    plot('chartRtDurationBins',[{
      type:'bar',
      x:chartBuckets.map(b=>b.label),
      y:chartBuckets.map(b=>b.count),
      marker:{
        color:chartBuckets.map(b=>b.color),
        line:{
          color:chartBuckets.map((b,index)=>index===0?'#7f1026':'rgba(0,0,0,0)'),
          width:chartBuckets.map((b,index)=>index===0?2:0)
        }
      },
      text:chartBuckets.map(b=>fmtInt(b.count)),
      textposition:'outside',
      cliponaxis:false,
      customdata:chartBuckets.map(b=>({
        key:b.key,
        teams:b.teams,
        count:b.count
      })),
      hovertemplate:'<b>%{x}</b><br>Incidências: %{y}<br>Equipes: %{customdata.teams}<extra></extra>'
    }],{
      margin:{l:15,r:15,t:20,b:80},
      xaxis:{
        title:'Faixa de duração das incidências abertas',
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
      const key=ev.points[0].customdata.key;
      const bucket=chartBuckets.find(b=>b.key===key);
      if(bucket)openDetails(`Duração: ${bucket.label}`,bucket.selected);
    });
  }else{
    emptyPlot(
      'chartRtDurationBins',
      'Nenhuma incidência ativa com duração disponível.'
    );
  }

'''

    texto = texto[:inicio] + novo_bloco + texto[fim:]

    texto = texto.replace(
        "rt24hRiskTable:'Risco de duração igual ou superior a 24h'",
        "rt24hRiskTable:'Incidências ativas por duração'"
    )

    texto = texto.replace(
        "</style>",
        f"\n/* {MARCADOR} */\n</style>",
        1,
    )

    temporario = PASTA / "Emergencia.__duracao_sem_corte_tmp__.html"
    temporario.write_text(texto, encoding="utf-8")
    temporario.replace(HTML)

    print("=" * 78)
    print("VISÃO DE DURAÇÃO ATUALIZADA")
    print("=" * 78)
    print(f"HTML atualizado: {HTML}")
    print(f"Backup criado: {backup}")
    print("Alterações:")
    print("  - removido o corte de 08:00")
    print("  - tabela mostra todas as incidências ativas")
    print("  - ordenação padrão pela duração, da maior para a menor")
    print("  - removida a coluna 'Falta para 24h'")
    print("  - gráfico por faixas não sobrepostas:")
    print("      Acima de 48h")
    print("      30h–48h")
    print("      24h–30h")
    print("      22h–24h, 20h–22h ... 0h–2h")
    print("  - fundo branco e sem grade mantidos")
    print("  - clique nas barras abre os registros da faixa")


if __name__ == "__main__":
    main()
