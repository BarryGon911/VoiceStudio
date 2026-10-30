"""
Genera el audio en INGLES con voz femenina (F4, Supertonic-3) para el guion
de locucion "Kernel Manufacturing Server". API key se inyecta desde el .env
local del fork - NUNCA se imprime ni se hardcodea.
"""
import re
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".voicestudio-api-key.local.txt"
OUT_DIR = Path(__file__).resolve().parent / "audio-samples"
OUT_FILE = OUT_DIR / "kernel-manufacturing-en-female-supertonic3.wav"

BASE_URL = "http://localhost:3900"

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
        print("[generate] enviando request (voz femenina F4, inglés), puede tardar varios minutos...")
        resp = client.post(
            "/generate",
            data={
                "text": SCRIPT_EN,
                "engine": "supertonic3",
                "preset_voice": "F4",
            },
        )
        print(f"[generate] status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"[generate] body: {resp.text[:1000]}")
            resp.raise_for_status()

        print(f"[generate] content-type: {resp.headers.get('content-type')}")
        OUT_FILE.write_bytes(resp.content)
        print(f"[OK] Audio guardado en: {OUT_FILE} ({len(resp.content)} bytes)")


if __name__ == "__main__":
    main()
