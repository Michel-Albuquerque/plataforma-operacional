from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


PASTA = Path(
    r"C:\Users\BR0143306567\OneDrive - Enel Spa\Documentos\Michel"
    r"\Plataforma_HTML"
)
HTML = PASTA / "Emergencia.html"
MARCADOR = "RISCO_24H_E_DISTRIBUICAO_DURACAO_V1"


CSS = r'''
/* RISCO_24H_E_DISTRIBUICAO_DURACAO_V1 */
tr.risk24-overdue td{background:#fde2e7!important;color:#7f1026;font-weight:800}
tr.risk24-critical td{background:#ffe4e1!important;color:#8e1f18;font-weight:750}
tr.risk24-high td{background:#fff0d8!important;color:#8a4b00;font-weight:720}
tr.risk24-medium td{background:#fff8cc!important;color:#6d5a00}
tr.risk24-watch td{background:#e9f4ff!important;color:#174d75}
tr.risk24-overdue:hover td,
tr.risk24-critical:hover td,
tr.risk24-high:hover td,
tr.risk24-medium:hover td,
tr.risk24-watch:hover td{filter:brightness(.97)}
.risk24-legend{display:flex;flex-wrap:wrap;gap:7px;margin:0 0 9px}
.risk24-chip{display:inline-flex;align-items:center;gap:5px;font-size:10px;font-weight:800;border-radius:999px;padding:4px 8px;border:1px solid var(--line);background:#fff}
.risk24-chip::before{content:'';width:9px;height:9px;border-radius:3px;background:#dce8f1}
.risk24-chip.overdue::before{background:#d91e45}
.risk24-chip.critical::before{background:#f45b4f}
.risk24-chip.high::before{background:#ff9f2f}
.risk24-chip.medium::before{background:#e2c335}
.risk24-chip.watch::before{background:#4b9fe1}
.risk24-summary{font-size:11px;color:var(--muted);margin-bottom:8px}
'''


HTML_BLOCK = r'''
      <div class="grid equal-two" style="margin-top:12px">
        <div class="panel">
          <div class="panel-head red">
            <div>
              <h3>Risco de duração igual ou superior a 24h</h3>
              <small id="rt24hCutoff">Projeção até 07:00 do próximo dia</small>
            </div>
          </div>
          <div class="panel-body">
            <div class="risk24-legend">
              <span class="risk24-chip overdue">Já atingiu 24h</span>
              <span class="risk24-chip critical">Até 2h</span>
              <span class="risk24-chip high">2h a 4h</span>
              <span class="risk24-chip medium">4h a 8h</span>
              <span class="risk24-chip watch">Acima de 8h</span>
            </div>
            <div class="risk24-summary" id="rt24hSummary"></div>
            <div id="rt24hRiskTable" class="table-wrap"></div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-head blue">
            <div>
              <h3>Distribuição das incidências por duração</h3>
              <small>Faixas de duas em duas horas com base na duração atual</small>
            </div>
          </div>
          <div class="panel-body">
            <div id="chartRtDurationBins" class="chart tall"></div>
          </div>
        </div>
      </div>
'''


HELPERS = r'''
function nextOperationalCutoff7(now=new Date()){
  const cutoff=new Date(now);
  cutoff.setDate(cutoff.getDate()+1);
  cutoff.setHours(7,0,0,0);
  return cutoff;
}

function currentRealtimeDurationHours(r,now=new Date()){
  const duration=realtimeAgeHours(r,now);
  if(Number.isFinite(duration))return Math.max(0,duration);
  if(r?.startDate instanceof Date&&!Number.isNaN(r.startDate.getTime())){
    return Math.max(0,(now-r.startDate)/36e5);
  }
  return 0;
}

function hoursUntil24(r,now=new Date()){
  return Math.max(0,24-currentRealtimeDurationHours(r,now));
}

function risk24RowClass(r,now=new Date()){
  const remaining=hoursUntil24(r,now);
  if(remaining<=0)return 'risk24-overdue';
  if(remaining<=2)return 'risk24-critical';
  if(remaining<=4)return 'risk24-high';
  if(remaining<=8)return 'risk24-medium';
  return 'risk24-watch';
}

function durationBinLabel(start,end){
  return `${fmtInt(start)}–${fmtInt(end)}h`;
}
'''


RENDER_BLOCK = r'''
  const cutoff24=nextOperationalCutoff7(now);
  const hoursToCutoff=Math.max(0,(cutoff24-now)/36e5);
  const risk24Rows=rows
    .map(r=>({
      ...r,
      _durationHours:currentRealtimeDurationHours(r,now),
      _hoursUntil24:hoursUntil24(r,now)
    }))
    .filter(r=>r._durationHours+hoursToCutoff>=24)
    .sort((a,b)=>a._hoursUntil24-b._hoursUntil24||b._durationHours-a._durationHours);

  if($('rt24hCutoff')){
    $('rt24hCutoff').textContent=`Projeção até ${brDate(cutoff24,true)} • janela restante: ${fmt1(hoursToCutoff)}h`;
  }
  if($('rt24hSummary')){
    const overdue=risk24Rows.filter(r=>r._hoursUntil24<=0).length;
    const approaching=risk24Rows.length-overdue;
    $('rt24hSummary').textContent=`${fmtInt(risk24Rows.length)} incidência(s) na projeção • ${fmtInt(overdue)} já atingiram 24h • ${fmtInt(approaching)} podem atingir até o corte`;
  }

  renderTable('rt24hRiskTable',[
    {label:'Incidência',value:r=>r.number},
    {label:'Equipe',value:r=>r.team||r.teamAssigned||'---'},
    {label:'Nível de tensão',value:r=>r.ntRaw||'---'},
    {label:'Alimentador',value:r=>r.feeder||'---'},
    {label:'Duração',value:r=>`${fmt1(r._durationHours)}h`,sortValue:r=>r._durationHours,class:'num'},
    {label:'Falta para 24h',value:r=>r._hoursUntil24<=0?'Já atingiu':`${fmt1(r._hoursUntil24)}h`,sortValue:r=>r._hoursUntil24,class:'num'}
  ],risk24Rows,{
    limit:500,
    sortable:true,
    rowClass:r=>risk24RowClass(r,now),
    empty:'Nenhuma incidência tem projeção de atingir 24h até o corte operacional.'
  });

  const durationValues=rows
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


def main() -> None:
    if not HTML.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {HTML}")

    text = HTML.read_text(encoding="utf-8")

    if MARCADOR in text:
        print("Os indicadores de risco de 24h já estão instalados.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = PASTA / f"Emergencia_backup_antes_risco24h_{timestamp}.html"
    shutil.copy2(HTML, backup)

    if "</style>" not in text:
        raise RuntimeError("Fechamento </style> não encontrado.")
    text = text.replace("</style>", CSS + "\n</style>", 1)

    html_anchor = '''      <div class="grid equal-two" style="margin-top:12px">
        <div class="panel"><div class="panel-head blue"><h3>Equipes com incidência ativa</h3>'''
    if html_anchor not in text:
        raise RuntimeError("Ponto de inserção dos novos painéis não encontrado.")
    text = text.replace(html_anchor, HTML_BLOCK + "\n" + html_anchor, 1)

    render_function = "function renderRealtime(){"
    if render_function not in text:
        raise RuntimeError("Função renderRealtime não encontrada.")
    text = text.replace(render_function, HELPERS + "\n" + render_function, 1)

    render_anchor = "  const teamStats=groupStats(withTeam,r=>r.team)"
    if render_anchor not in text:
        raise RuntimeError("Ponto de inserção dentro de renderRealtime não encontrado.")
    text = text.replace(render_anchor, RENDER_BLOCK + render_anchor, 1)

    if "const REALTIME_TABLE_IDS=new Set([" in text:
        text = text.replace(
            "'rtTable','rtConh','rtImpactTable','rtTeams',",
            "'rtTable','rtConh','rtImpactTable','rt24hRiskTable','rtTeams',",
            1,
        )
    if "rtImpactTable:'Maiores afetações'," in text:
        text = text.replace(
            "rtImpactTable:'Maiores afetações',",
            "rtImpactTable:'Maiores afetações',\n    rt24hRiskTable:'Risco de duração igual ou superior a 24h',",
            1,
        )

    text = text.replace(
        "</style>",
        f"\n/* {MARCADOR} */\n</style>",
        1,
    )

    temporary = PASTA / "Emergencia.__risco24h_tmp__.html"
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(HTML)

    print("=" * 78)
    print("RISCO DE 24H E DISTRIBUIÇÃO DE DURAÇÃO INSTALADOS")
    print("=" * 78)
    print(f"HTML atualizado: {HTML}")
    print(f"Backup criado: {backup}")
    print("Incluído na aba Tempo Real:")
    print("  - tabela com incidências que podem atingir 24h até 07:00 do próximo dia")
    print("  - linhas coloridas por proximidade de 24h")
    print("  - duração atual e tempo restante para 24h")
    print("  - ordenação e exportação Excel na nova tabela")
    print("  - gráfico de quantidade por faixas de duração de 2 em 2 horas")


if __name__ == "__main__":
    main()
