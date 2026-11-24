"""
Genera 2 audios promocionales (mujer F4, hombre M1) en espanol para
"Manufacturing Server" (Kernel ERP) - version centrada en control de
produccion: ingenieria de procesos, avance de produccion, calidad e
inventarios, embarque y facturacion. API key se inyecta desde el .env local
del fork - NUNCA se imprime ni se hardcodea. Regla fija: todo audio TTS se
entrega en .mp3.
"""
import re
import subprocess
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".voicestudio-api-key.local.txt"
OUT_DIR = Path(__file__).resolve().parent / "audio-samples"

BASE_URL = "http://localhost:3900"

SCRIPT = (
    "Manufacturing Server, de Kernel E R P: experiencia sistematizada por "
    "treinta y siete años en plantas industriales. "
    "¿Necesita implantar estándares de control de producción y manufactura "
    "que generen el cumplimiento de las metas en su fábrica? "
    "Manufacturing Server administra todos los procesos de su planta: "
    "desarrollo de producto terminado, con definición de especificaciones, "
    "combinaciones, especificaciones de proceso, y especificaciones de "
    "ensamblaje. Ingeniería de procesos, con especificaciones de calidad, temperatura, "
    "tiempo de activación, ensamblaje, maquinaria, materiales y mano de "
    "obra. Control de avance de producción, con seguimiento de retrasos, "
    "avance por día, e inventarios de avance por departamento. "
    "Especificaciones y revisiones de calidad, con autorización de avance, "
    "y recepción y valuación de calidad en producto terminado. Y listas de "
    "embarque recibido, listas para facturación, talón de embarque, y "
    "fichas de embarque. "
    "Utilice la información de su planta para aumentar la productividad: "
    "conozca el avance de sus pedidos, detecte atrasos antes de que "
    "afecten la entrega, controle consumos de materiales y mano de obra, "
    "y obtenga una planeación de materiales, sub piezas y recursos por "
    "anticipado, desde la programación, para cada semana. "
    "Especialmente preparado para industrias con productos en diferentes "
    "modelos, tallas, materiales, colores y procesos. "
    "Manufacturing Server: ingeniería industrial, con treinta y siete años "
    "de experiencia sistematizada. Responda a este correo, y con gusto le "
    "atenderemos."
)

JOBS = [
    ("F4", "Manufacturing-Server-Ampliado-SP-Female-Supertonic3.wav"),
    ("M1", "Manufacturing-Server-Ampliado-SP-Male-Supertonic3.wav"),
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
        for voice, filename in JOBS:
            out_wav = OUT_DIR / filename
            out_mp3 = out_wav.with_suffix(".mp3")
            print(f"[generate] voz={voice} archivo={filename} ...")
            resp = client.post(
                "/generate",
                data={"text": SCRIPT, "engine": "supertonic3", "preset_voice": voice},
            )
            print(f"  status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"  body: {resp.text[:1000]}")
                resp.raise_for_status()
            out_wav.write_bytes(resp.content)
            print(f"  [OK] {out_wav} ({len(resp.content)} bytes)")

            subprocess.run(
                [
                    "ffmpeg", "-y", "-i", str(out_wav),
                    "-codec:a", "libmp3lame", "-qscale:a", "2",
                    str(out_mp3), "-loglevel", "error",
                ],
                check=True,
            )
            print(f"  [OK] {out_mp3}")

    print("\n[DONE] 2 audios de Manufacturing Server (control de produccion) generados.")


if __name__ == "__main__":
    main()
