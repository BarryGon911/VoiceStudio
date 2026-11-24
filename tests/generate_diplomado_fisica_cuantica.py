"""
Genera 2 audios promocionales (mujer F4, hombre M1) en espanol para el
"Diplomado Física Cuántica para la Transformación Personal 1.0" (Ser-Hacer-Tener).
API key se inyecta desde el .env local del fork - NUNCA se imprime ni se
hardcodea. Regla fija: todo audio TTS se entrega en .mp3.
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
    "Descubre cómo los principios de la física cuántica pueden inspirarte a "
    "transformar tu mentalidad, tus emociones y tus acciones, para alcanzar "
    "mayores niveles de excelencia, éxito y resultados. "
    "Te presentamos el Diplomado Física Cuántica para la Transformación "
    "Personal uno punto cero: ser, hacer, tener. Conecta la ciencia, la "
    "conciencia y la acción, para crear una vida extraordinaria. "
    "Un enfoque único que integra cuatro pilares. "
    "Ciencia: los principios de la física cuántica, explicados de forma "
    "práctica y aplicable. "
    "Ontología: comprende quién eres, y cómo interpretas tu realidad. "
    "Coaching: herramientas para pasar de la comprensión, a la acción. "
    "Y superación personal: desarrolla tu potencial, y alcanza tus metas más "
    "importantes. "
    "Transforma tu vida en tres dimensiones. "
    "Ser: fortalece tu mentalidad, tus emociones y tu identidad. "
    "Hacer: desarrolla hábitos, habilidades y acciones conscientes. "
    "Y tener: logra resultados tangibles, en tu vida personal, profesional y "
    "financiera. "
    "Expande tu conciencia, clarifica tus objetivos, eleva tu bienestar, "
    "potencia tu productividad, y crea una vida con mayor propósito. "
    "Mayor claridad, nuevas oportunidades, relaciones más plenas, bienestar "
    "integral, crecimiento financiero, y una vida con mayor propósito. "
    "Modalidad en línea, con acompañamiento en vivo. Reserva tu lugar: tu "
    "próximo nivel comienza hoy."
)

JOBS = [
    ("F4", "Diplomado-Fisica-Cuantica-SP-Female-Supertonic3.wav"),
    ("M1", "Diplomado-Fisica-Cuantica-SP-Male-Supertonic3.wav"),
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

    print("\n[DONE] 2 audios del diplomado generados.")


if __name__ == "__main__":
    main()
