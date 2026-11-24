"""
Prueba de validacion aislada (fuera de VoiceStudio/Docker) de Chatterbox
Multilingual (Resemble AI, MIT) para comparar contra Supertonic-3:
- Ingles: modelo base ChatterboxTTS (acento nativo US/Canada del modelo)
- Espanol: checkpoint fine-tuned "es-mx-latam" (acento mexicano explicito)

No requiere API key (corre 100% local, pesos se descargan de HuggingFace la
primera vez). Guarda WAV en tests/audio-samples/ y luego se convierte a MP3
(regla fija: todo audio TTS se entrega en .mp3).
"""
from pathlib import Path

import torchaudio as ta

OUT_DIR = Path(__file__).resolve().parent / "audio-samples"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SCRIPT_EN = (
    "Is your production plant facing delays, uncontrolled waste, or cost "
    "variations? It's time to take the next step in engineering your processes. "
    "Discover Kernel Manufacturing Server, the specialized module from Kernel "
    "Corporation designed to standardize every variable in your operation."
)

SCRIPT_ES_MX = (
    "¿Tu planta de producción enfrenta retrasos, mermas descontroladas o "
    "variaciones en los costos? Es hora de dar el siguiente paso en la "
    "ingeniería de tus procesos. Descubre Kernel Manufacturing Server, el "
    "módulo especializado de Kernel Corporation diseñado para estandarizar "
    "cada variable de tu operación."
)


def generate_english() -> None:
    from chatterbox.tts import ChatterboxTTS

    print("[EN] cargando modelo base ChatterboxTTS (device=cpu)...")
    model = ChatterboxTTS.from_pretrained(device="cpu")
    print("[EN] generando audio...")
    wav = model.generate(SCRIPT_EN)
    out_file = OUT_DIR / "kernel-validacion-chatterbox-en.wav"
    ta.save(str(out_file), wav, model.sr)
    print(f"[EN] [OK] {out_file}")


def generate_spanish_mx() -> None:
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

    print("[ES-MX] cargando checkpoint es-mx-latam (device=cpu)...")
    model = ChatterboxMultilingualTTS.from_pretrained(
        device="cpu",
        repo_id="ResembleAI/Chatterbox-Multilingual-es-mx-latam",
    )
    print("[ES-MX] generando audio...")
    wav = model.generate(SCRIPT_ES_MX, language_id="es")
    out_file = OUT_DIR / "kernel-validacion-chatterbox-es-mx.wav"
    ta.save(str(out_file), wav, model.sr)
    print(f"[ES-MX] [OK] {out_file}")


def main() -> None:
    generate_english()
    generate_spanish_mx()
    print("\n[DONE] ambas pruebas generadas.")


if __name__ == "__main__":
    main()
