"""
Genera 2 audios promocionales (mujer F4, hombre M1) en espanol para el curso
"Como aplicar las Matemáticas con Regletas Cuisenaire desde preescolar"
(Kernel Corporation). API key se inyecta desde el .env local del fork - NUNCA
se imprime ni se hardcodea. Regla fija: todo audio TTS se entrega en .mp3.
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
    "Aprende a enseñar matemáticas con el método que convierte los números en "
    "algo real. Cómo aplicar las matemáticas con regletas Cuisenaire desde "
    "preescolar. Curso en línea, con acompañamiento en vivo. "
    "Al terminar el curso sabrás aplicar el método de las regletas Cuisenaire "
    "para enseñar matemáticas desde preescolar: de forma visual, manipulable, y "
    "sin depender de memorizar fórmulas. Útil tanto si eres docente y buscas "
    "actualizar tu práctica en el salón, como si eres mamá o papá, y quieres "
    "apoyar a tu hijo o hija en casa con un método probado. "
    "Si eres docente: una técnica nueva, lista para usar desde la primera "
    "clase, diploma con valor curricular para tu expediente, y más seguridad "
    "para explicar matemáticas sin depender de la memorización. "
    "Si eres papá o mamá: una forma clara de apoyar la tarea de matemáticas en "
    "casa, menos frustración para ti y para tu hijo o hija con los números, y "
    "material físico para seguir practicando después del curso. "
    "Modalidad en línea, por Google Meet. Cupo limitado a veinticinco personas "
    "por sesión. Inscríbete por WhatsApp al más cuatro, siete, siete, cuatro, "
    "nueve, cinco, cuatro, nueve, cero, cuatro. Tu próximo paso en la "
    "enseñanza de las matemáticas empieza aquí."
)

JOBS = [
    ("F4", "Regletas-Cuisenaire-SP-Female-Supertonic3.wav"),
    ("M1", "Regletas-Cuisenaire-SP-Male-Supertonic3.wav"),
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

    print("\n[DONE] 2 audios de Regletas Cuisenaire generados.")


if __name__ == "__main__":
    main()
