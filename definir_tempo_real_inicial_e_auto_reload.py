from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


PASTA = Path(
    r"C:\Users\BR0143306567\OneDrive - Enel Spa\Documentos\Michel"
    r"\Plataforma_HTML"
)
HTML = PASTA / "Emergencia.html"
MARCADOR = "TEMPO_REAL_PADRAO_E_AUTO_RELOAD_V1"


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
        f"Emergencia_backup_antes_tempo_real_padrao_"
        f"{datetime.now():%Y%m%d_%H%M%S}.html"
    )
    shutil.copy2(HTML, backup)

    texto = substituir(
        texto,
        '<button class="tab-btn active" data-tab="executive">Visão Executiva</button>\n'
        '      <button class="tab-btn" data-tab="realtime">Tempo Real</button>',
        '<button class="tab-btn" data-tab="executive">Visão Executiva</button>\n'
        '      <button class="tab-btn active" data-tab="realtime">Tempo Real</button>',
        "botão Tempo Real como ativo",
    )

    texto = substituir(
        texto,
        '<section class="tab-panel active" id="tab-executive">',
        '<section class="tab-panel" id="tab-executive">',
        "remoção da Visão Executiva como painel inicial",
    )

    texto = substituir(
        texto,
        '<section class="tab-panel" id="tab-realtime">',
        '<section class="tab-panel active" id="tab-realtime">',
        "Tempo Real como painel inicial",
    )

    texto = substituir(
        texto,
        "activeTab:'executive'",
        "activeTab:'realtime'",
        "estado inicial da aba",
    )

    texto = substituir(
        texto,
        "async function init(){",
        "async function init(){\n  state.activeTab='realtime';",
        "forçar Tempo Real na inicialização",
    )

    auto_reload = """
// Recarregamento completo automático da plataforma a cada 5 minutos.
const AUTO_RELOAD_INTERVAL_MS=5*60*1000;
setTimeout(()=>{
  window.location.reload();
},AUTO_RELOAD_INTERVAL_MS);
"""

    if "</script>" not in texto:
        raise RuntimeError("Fechamento </script> não encontrado.")

    texto = texto.replace(
        "</script>",
        auto_reload + "\n</script>",
        1,
    )

    texto = texto.replace(
        "</style>",
        f"\n/* {MARCADOR} */\n</style>",
        1,
    )

    temporario = PASTA / "Emergencia.__tempo_real_padrao_tmp__.html"
    temporario.write_text(texto, encoding="utf-8")
    temporario.replace(HTML)

    print("=" * 78)
    print("TEMPO REAL DEFINIDO COMO ABA INICIAL")
    print("=" * 78)
    print(f"HTML atualizado: {HTML}")
    print(f"Backup criado: {backup}")
    print("Alterações:")
    print("  - Tempo Real será a primeira aba carregada")
    print("  - a página será recarregada automaticamente a cada 5 minutos")
    print("  - após o recarregamento, continuará abrindo em Tempo Real")


if __name__ == "__main__":
    main()
