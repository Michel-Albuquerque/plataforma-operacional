from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

PASTA = Path(r"C:\Users\BR0143306567\OneDrive - Enel Spa\Documentos\Michel\Plataforma_HTML")
HTML = PASTA / "Emergencia.html"
MARCADOR = "AJUSTES_CRITICOS_LAYOUT_AFETACAO_V1"

CSS_ANTIGO = ".app-shell{max-width:1900px;margin:0 auto;display:grid;grid-template-columns:245px minmax(0,1fr);min-height:calc(100vh - 126px)}\n.sidebar{background:#fff;border-right:1px solid var(--line);padding:14px 13px;position:sticky;top:126px;height:calc(100vh - 126px);overflow:auto}"
CSS_NOVO = ".app-shell{max-width:1900px;margin:0 auto;display:grid;grid-template-columns:245px minmax(0,1fr);min-height:calc(100vh - 126px);transition:grid-template-columns .22s ease}\n.sidebar{background:#fff;border-right:1px solid var(--line);padding:14px 13px;position:sticky;top:0;height:100vh;overflow:auto;transition:opacity .18s ease,transform .22s ease,padding .22s ease}\n.app-shell.filters-collapsed{grid-template-columns:0 minmax(0,1fr)}\n.app-shell.filters-collapsed .sidebar{opacity:0;transform:translateX(-100%);padding-left:0;padding-right:0;border-right:0;pointer-events:none}\n.filter-toggle{position:sticky;left:0;z-index:2;display:inline-flex;align-items:center;gap:6px;border:1px solid #bfd0dd;background:#fff;color:var(--enel-navy);border-radius:8px;padding:8px 10px;font-weight:800;white-space:nowrap;box-shadow:0 2px 6px rgba(20,61,91,.08)}\n.filter-toggle:hover{background:var(--soft-blue);border-color:var(--enel-blue-2)}\n.impact-value{font-weight:850;color:#9f1239}"
TABS_ANTIGO = ".tabs{position:sticky;top:126px;z-index:35;background:#f5f7f9;padding:10px 0 8px;display:flex;gap:7px;overflow-x:auto;border-bottom:1px solid #e5ebef}"
TABS_NOVO = ".tabs{position:sticky;top:0;z-index:80;background:#f5f7f9;padding:10px 0 8px;display:flex;gap:7px;overflow-x:auto;border-bottom:1px solid #e5ebef;box-shadow:0 3px 9px rgba(23,61,91,.08)}"
MEDIA_1450_ANTIGO = "@media(max-width:1450px){.kpi-grid{grid-template-columns:repeat(4,1fr)}.layout-main-aside{grid-template-columns:minmax(0,1fr) 330px}.topbar-inner{grid-template-columns:auto 1fr}.top-actions{grid-column:1/-1;justify-content:center}.sidebar{top:170px;height:calc(100vh - 170px)}.tabs{top:170px}}"
MEDIA_1450_NOVO = "@media(max-width:1450px){.kpi-grid{grid-template-columns:repeat(4,1fr)}.layout-main-aside{grid-template-columns:minmax(0,1fr) 360px}.topbar-inner{grid-template-columns:auto 1fr}.top-actions{grid-column:1/-1;justify-content:center}.sidebar{top:0;height:100vh}.tabs{top:0}}"
MEDIA_1050_ANTIGO = "@media(max-width:1050px){.app-shell{grid-template-columns:1fr}.sidebar{position:relative;top:auto;height:auto;border-right:none;border-bottom:1px solid var(--line);display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.sidebar h3,.filter-sep,.sidebar-note{grid-column:1/-1}.tabs{top:0}.two-col,.equal-two,.three-col,.four-col,.layout-main-aside,.import-grid{grid-template-columns:1fr}.kpi-grid{grid-template-columns:repeat(3,1fr)}.topbar{position:relative}.page-title{text-align:left}.topbar-inner{grid-template-columns:1fr}.brand{min-width:0}.top-actions{justify-content:flex-start}.statusbar{padding-bottom:8px}.clock{margin-left:0}.quality-grid{grid-template-columns:repeat(2,1fr)}}"
MEDIA_1050_NOVO = "@media(max-width:1050px){.app-shell,.app-shell.filters-collapsed{grid-template-columns:1fr}.sidebar{position:relative;top:auto;height:auto;border-right:none;border-bottom:1px solid var(--line);display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.app-shell.filters-collapsed .sidebar{display:none}.sidebar h3,.filter-sep,.sidebar-note{grid-column:1/-1}.tabs{top:0}.two-col,.equal-two,.three-col,.four-col,.layout-main-aside,.import-grid{grid-template-columns:1fr}.kpi-grid{grid-template-columns:repeat(3,1fr)}.topbar{position:relative}.page-title{text-align:left}.topbar-inner{grid-template-columns:1fr}.brand{min-width:0}.top-actions{justify-content:flex-start}.statusbar{padding-bottom:8px}.clock{margin-left:0}.quality-grid{grid-template-columns:repeat(2,1fr)}}"
NAV_ANTIGO = "    <nav class=\"tabs\" aria-label=\"Navegação principal\">\n      <button class=\"tab-btn active\" data-tab=\"executive\">Visão Executiva</button>"
NAV_NOVO = "    <nav class=\"tabs\" aria-label=\"Navegação principal\">\n      <button class=\"filter-toggle\" id=\"btnToggleSidebar\" type=\"button\" aria-expanded=\"true\" title=\"Recolher ou exibir filtros\">☰ Filtros</button>\n      <button class=\"tab-btn active\" data-tab=\"executive\">Visão Executiva</button>"
CONH_ANTIGO = "          <div class=\"panel\"><div class=\"panel-head\"><h3>TOP 5 ConH</h3><small>Valor da planilha; cálculo estimado apenas quando o campo não existir</small></div><div class=\"panel-body\"><div id=\"rtConh\"></div></div></div>\n        </div>"
CONH_NOVO = "          <div class=\"panel\"><div class=\"panel-head\"><h3>TOP 5 ConH</h3><small>Valor da planilha; cálculo estimado apenas quando o campo não existir</small></div><div class=\"panel-body\"><div id=\"rtConh\"></div></div></div>\n          <div class=\"panel\"><div class=\"panel-head blue\"><div><h3>Maiores afetações</h3><small>Incidências ordenadas por Cli Af Atual</small></div><button class=\"btn small\" id=\"btnExpandImpact\" type=\"button\" data-expanded=\"0\">Ver todas</button></div><div class=\"panel-body\"><div id=\"rtImpactTable\" class=\"table-wrap\"></div></div></div>\n        </div>"
RENDER_CONH_ANTIGO = "  const conh=sortDesc(rows,r=>realtimeConH(r,now)).slice(0,5);renderTable('rtConh',[{label:'Ranking',value:r=>conh.indexOf(r)+1},{label:'Número',value:r=>r.number},{label:'ConH',value:r=>fmtInt(realtimeConH(r,now)),class:'num'},{label:'Clientes',value:r=>fmtInt(r.clientsCurrent),class:'num'},{label:'Equipe',value:r=>r.team||'---'}],conh,{limit:5});\n  const teamStats=groupStats(withTeam,r=>r.team)"
RENDER_CONH_NOVO = "  const conh=sortDesc(rows,r=>realtimeConH(r,now)).slice(0,5);renderTable('rtConh',[{label:'Ranking',value:r=>conh.indexOf(r)+1},{label:'Número',value:r=>r.number},{label:'ConH',value:r=>fmtInt(realtimeConH(r,now)),class:'num'},{label:'Clientes',value:r=>fmtInt(r.clientsCurrent),class:'num'},{label:'Equipe',value:r=>r.team||'---'}],conh,{limit:5});\n\n  const impactAll=sortDesc(rows,r=>Number.isFinite(r.clientsCurrent)?r.clientsCurrent:0);\n  const impactExpanded=$('btnExpandImpact')?.dataset.expanded==='1';\n  const impactRows=impactExpanded?impactAll:impactAll.slice(0,10);\n  if($('btnExpandImpact')){\n    $('btnExpandImpact').textContent=impactExpanded?'Mostrar Top 10':'Ver todas';\n    $('btnExpandImpact').setAttribute('aria-expanded',impactExpanded?'true':'false');\n  }\n  renderTable('rtImpactTable',[\n    {label:'Incidência',value:r=>r.number},\n    {label:'Nível de tensão',value:r=>r.ntRaw||'---'},\n    {label:'Afetação',value:r=>fmtInt(r.clientsCurrent),class:'num impact-value'},\n    {label:'Equipe',value:r=>r.team||r.teamAssigned||'---'},\n    {label:'Alimentador',value:r=>r.feeder||'---'}\n  ],impactRows,{limit:impactExpanded?5000:10,empty:'Nenhuma incidência ativa com afetação informada'});\n\n  const teamStats=groupStats(withTeam,r=>r.team)"
BIND_ANTIGO = "function bindEvents(){\n  qsa('.tab-btn').forEach(b=>b.addEventListener('click',()=>setTab(b.dataset.tab)));"
BIND_NOVO = "function bindEvents(){\n  qsa('.tab-btn').forEach(b=>b.addEventListener('click',()=>setTab(b.dataset.tab)));\n\n  const shell=document.querySelector('.app-shell');\n  const toggleSidebar=$('btnToggleSidebar');\n  const savedCollapsed=localStorage.getItem('emergency_filters_collapsed')==='1';\n  if(shell&&savedCollapsed)shell.classList.add('filters-collapsed');\n  if(toggleSidebar){\n    const syncToggle=()=>{\n      const collapsed=shell?.classList.contains('filters-collapsed');\n      toggleSidebar.innerHTML=collapsed?'☰ Exibir filtros':'☰ Recolher filtros';\n      toggleSidebar.setAttribute('aria-expanded',collapsed?'false':'true');\n    };\n    syncToggle();\n    toggleSidebar.addEventListener('click',()=>{\n      shell?.classList.toggle('filters-collapsed');\n      localStorage.setItem('emergency_filters_collapsed',shell?.classList.contains('filters-collapsed')?'1':'0');\n      syncToggle();\n      setTimeout(()=>qsa(`#tab-${state.activeTab} .js-plotly-plot`).forEach(el=>Plotly.Plots.resize(el)),260);\n    });\n  }\n\n  if($('btnExpandImpact'))$('btnExpandImpact').addEventListener('click',()=>{\n    const button=$('btnExpandImpact');\n    button.dataset.expanded=button.dataset.expanded==='1'?'0':'1';\n    if(state.activeTab==='realtime')renderRealtime();\n  });"

def substituir(texto, antigo, novo, nome):
    if novo in texto:
        print(f"Já aplicado: {nome}")
        return texto
    if antigo not in texto:
        raise RuntimeError(f"Trecho não encontrado: {nome}")
    print(f"Aplicando: {nome}")
    return texto.replace(antigo, novo, 1)

def main():
    if not HTML.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {HTML}")
    texto = HTML.read_text(encoding="utf-8")
    if MARCADOR in texto:
        print("Os ajustes críticos já estão instalados.")
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = PASTA / f"Emergencia_backup_antes_layout_{timestamp}.html"
    shutil.copy2(HTML, backup)
    for antigo, novo, nome in [
        (CSS_ANTIGO, CSS_NOVO, "sidebar retrátil"),
        (TABS_ANTIGO, TABS_NOVO, "abas fixas no topo"),
        (MEDIA_1450_ANTIGO, MEDIA_1450_NOVO, "responsividade 1450px"),
        (MEDIA_1050_ANTIGO, MEDIA_1050_NOVO, "responsividade 1050px"),
        (NAV_ANTIGO, NAV_NOVO, "botão de filtros"),
        (CONH_ANTIGO, CONH_NOVO, "painel maiores afetações"),
        (RENDER_CONH_ANTIGO, RENDER_CONH_NOVO, "renderização das afetações"),
        (BIND_ANTIGO, BIND_NOVO, "eventos de expansão e filtros"),
    ]:
        texto = substituir(texto, antigo, novo, nome)
    texto = texto.replace("</style>", f"\n/* {MARCADOR} */\n</style>", 1)
    temporario = PASTA / "Emergencia.__layout_tmp__.html"
    temporario.write_text(texto, encoding="utf-8")
    temporario.replace(HTML)
    print("=" * 78)
    print("AJUSTES APLICADOS COM SUCESSO")
    print("=" * 78)
    print(f"HTML atualizado: {HTML}")
    print(f"Backup criado: {backup}")
    print("Incluído: Top 10 de maiores afetações, expansão, filtro retrátil e abas fixas.")

if __name__ == "__main__":
    main()
