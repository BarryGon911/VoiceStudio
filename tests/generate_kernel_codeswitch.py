"""
Genera 2 audios del guion "Kernel Manufacturing Server" en ESPAÑOL con
code-switching: los términos de marca en inglés ("Kernel Corporation", el
dominio "kernelcorporation.com") se generan en una pasada separada con
language="en" y se concatenan con el resto del texto en español
(language="es"), usando la misma voz en ambas pasadas para mantener timbre
consistente. Supertonic-3 no soporta code-switching nativo ni SSML de
idioma (confirmado por investigación de código) — esta es la única ruta
viable sin modificar el motor.

API key se inyecta desde el .env local del fork - NUNCA se imprime ni se
hardcodea. Concatenación de WAV vía ffmpeg CLI (ya disponible en el host).
"""
import re
import subprocess
import tempfile
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".voicestudio-api-key.local.txt"
OUT_DIR = Path(__file__).resolve().parent / "audio-samples"

BASE_URL = "http://localhost:3900"

# Cada guion se parte en segmentos (texto, idioma). Los segmentos en "en"
# son los términos de marca/dominio que deben sonar con fonética inglesa.
SEGMENTS_ES = [
    (
        "¿Tu planta de producción enfrenta retrasos, mermas descontroladas o "
        "variaciones en los costos? Es hora de dar el siguiente paso en la "
        "ingeniería de tus procesos.",
        "es",
    ),
    ("Discover Kernel Manufacturing Server,", "en"),
    (
        "el módulo especializado de",
        "es",
    ),
    ("Kernel Corporation", "en"),
    (
        "diseñado para estandarizar cada variable de tu operación. Desde el "
        "desarrollo preciso de producto terminado y especificaciones de "
        "construcción, hasta la gestión avanzada de tu",
        "es",
    ),
    ("Bill of Materials.", "en"),
    (
        "Calcula consumos exactos, mermas y costeo estándar unitario "
        "utilizando algoritmos de ingeniería como Russ y Small y el escalado "
        "de consumos",
        "es",
    ),
    ("Kernel Scaling.", "en"),
    (
        "Elimina el margen de error y garantiza el cumplimiento de calidad en "
        "cada departamento. Estandariza tu fábrica, optimiza tu rentabilidad y "
        "toma el control total de tu producción. Visítanos en",
        "es",
    ),
    ("kernelcorporation dot com,", "en"),
    ("o contáctanos por WhatsApp.", "es"),
    ("Kernel Corporation:", "en"),
    ("tecnología que transforma la manufactura.", "es"),
]

JOBS = [
    ("F4", SEGMENTS_ES, "kernel-manufacturing-es-female-supertonic3-codeswitch.wav"),
    ("M1", SEGMENTS_ES, "kernel-manufacturing-es-male-supertonic3-codeswitch.wav"),
]


def load_api_key() -> str:
    text = ENV_FILE.read_text(encoding="utf-8")
    match = re.search(r"OMNIVOICE_API_KEY=(\S+)", text)
    if not match:
        raise RuntimeError("OMNIVOICE_API_KEY not found in local env file")
    return match.group(1)


def concat_wavs(wav_paths: list[Path], out_path: Path) -> None:
    """Concatena WAVs en orden usando el demuxer concat de ffmpeg (sin recodificar)."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as list_file:
        for wav_path in wav_paths:
            escaped = str(wav_path).replace("\\", "/").replace("'", "'\\''")
            list_file.write(f"file '{escaped}'\n")
        list_file_path = list_file.name

    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", list_file_path, "-c", "copy", str(out_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        print(exc.stdout)
        print(exc.stderr)
        raise
    finally:
        Path(list_file_path).unlink(missing_ok=True)


def main() -> None:
    api_key = load_api_key()
    headers = {"Authorization": f"Bearer {api_key}"}
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with httpx.Client(base_url=BASE_URL, headers=headers, timeout=480.0) as client:
        for voice, segments, filename in JOBS:
            out_file = OUT_DIR / filename
            print(f"[codeswitch] voz={voice} archivo={filename} ({len(segments)} segmentos)")

            with tempfile.TemporaryDirectory() as tmp_dir:
                segment_paths: list[Path] = []
                for i, (text, lang) in enumerate(segments):
                    print(f"  segmento {i+1}/{len(segments)} lang={lang}: {text[:50]!r}...")
                    resp = client.post(
                        "/generate",
                        data={
                            "text": text,
                            "engine": "supertonic3",
                            "preset_voice": voice,
                            "language": lang,
                        },
                    )
                    if resp.status_code != 200:
                        print(f"    status: {resp.status_code} body: {resp.text[:500]}")
                        resp.raise_for_status()
                    seg_path = Path(tmp_dir) / f"seg_{i:02d}.wav"
                    seg_path.write_bytes(resp.content)
                    segment_paths.append(seg_path)

                print(f"  concatenando {len(segment_paths)} segmentos con ffmpeg...")
                concat_wavs(segment_paths, out_file)

            print(f"  [OK] {out_file} ({out_file.stat().st_size} bytes)")

    print("\n[DONE] audios con code-switching generados.")


if __name__ == "__main__":
    main()
