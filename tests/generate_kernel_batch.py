"""
Genera 3 audios del guion "Kernel Manufacturing Server":
1. F4 (femenina) en Espanol
2. M1 (masculina, grave/formal) en Espanol
3. M1 (masculina, grave/formal) en Ingles
API key se inyecta desde el .env local del fork - NUNCA se imprime ni se hardcodea.
"""
import re
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".voicestudio-api-key.local.txt"
OUT_DIR = Path(__file__).resolve().parent / "audio-samples"

BASE_URL = "http://localhost:3900"

SCRIPT_ES = (
    "¿Tu planta de producción enfrenta retrasos, mermas descontroladas o "
    "variaciones en los costos? Es hora de dar el siguiente paso en la "
    "ingeniería de tus procesos. "
    "Descubre Kernel Manufacturing Server, el módulo especializado de Kernel "
    "Corporation diseñado para estandarizar cada variable de tu operación. "
    "Desde el desarrollo preciso de producto terminado y especificaciones de "
    "construcción, hasta la gestión avanzada de tu Bill of Materials. "
    "Calcula consumos exactos, mermas y costeo estándar unitario utilizando "
    "algoritmos de ingeniería como Russ y Small y el escalado de consumos "
    "Kernel Scaling. Elimina el margen de error y garantiza el cumplimiento "
    "de calidad en cada departamento. "
    "Estandariza tu fábrica, optimiza tu rentabilidad y toma el control total "
    "de tu producción. "
    "Visítanos en kernelcorporation punto com o contáctanos por WhatsApp. "
    "Kernel Corporation: tecnología que transforma la manufactura."
)

SCRIPT_EN = (
    "Is your production plant facing delays, uncontrolled waste, or cost "
    "variations? It's time to take the next step in engineering your processes. "
    "Discover Kernel Manufacturing Server, the specialized module from Kernel "
    "Corporation designed to standardize every variable in your operation. "
    "From precise finished product development and construction specifications, "
    "to advanced management of your Bill of Materials. "
    "Calculate exact consumption, waste, and standard unit costing using "
    "engineering algorithms like Russ and Small, and Kernel Scaling consumption "
    "scaling. Eliminate margin of error and guarantee quality compliance across "
    "every department. "
    "Standardize your factory, optimize your profitability, and take full "
    "control of your production. "
    "Visit us at kernelcorporation dot com, or contact us on WhatsApp. "
    "Kernel Corporation: technology that transforms manufacturing."
)

JOBS = [
    ("F4", SCRIPT_ES, "kernel-manufacturing-es-female-supertonic3.wav"),
    ("M1", SCRIPT_ES, "kernel-manufacturing-es-male-supertonic3.wav"),
    ("M1", SCRIPT_EN, "kernel-manufacturing-en-male-supertonic3.wav"),
]


def load_api_key() -> str:
    text = ENV_FILE.read_text(encoding="utf-8")
    match = re.search(r"OMNIVOICE_API_KEY=(\S+)", text)
    if not match:
        raise RuntimeError("OMNIVOICE_API_KEY not found in local env file")
    return match.group(1)


def main() -> None:
    api_key = load_api_key()
    headers = {"Authorization": f"Bearer {api_key}"}
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with httpx.Client(base_url=BASE_URL, headers=headers, timeout=480.0) as client:
        for voice, text, filename in JOBS:
            out_file = OUT_DIR / filename
            print(f"[generate] voz={voice} archivo={filename} ...")
            resp = client.post(
                "/generate",
                data={"text": text, "engine": "supertonic3", "preset_voice": voice},
            )
            print(f"  status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"  body: {resp.text[:1000]}")
                resp.raise_for_status()
            out_file.write_bytes(resp.content)
            print(f"  [OK] {out_file} ({len(resp.content)} bytes)")

    print("\n[DONE] 3 audios generados.")


if __name__ == "__main__":
    main()
