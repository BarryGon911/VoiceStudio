"""
Genera audios promocionales (mujer F4, hombre M1, espanol e ingles) para los
2 servidores HPE ProLiant ML30 G9 de Kernel Corporation (8GB con Windows
Server 2022 Datacenter, y 4GB sin sistema operativo). Datos verificados en
https://kernelcorporation.com/tienda/index.html - NUNCA inventar precios ni
especificaciones. API key se inyecta desde el .env local del fork - NUNCA se
imprime ni se hardcodea. Regla fija: todo audio TTS se entrega en .mp3.
"""
import re
import subprocess
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".voicestudio-api-key.local.txt"
OUT_DIR = Path(__file__).resolve().parent / "audio-samples"

BASE_URL = "http://localhost:3900"

SCRIPT_8GB_SP = (
    "Servidor completamente nuevo, H P E ProLiant M L treinta G nueve. "
    "Procesador Intel Xeon E tres mil doscientos veinte, v cinco: cuatro "
    "núcleos, tres gigahertz base, hasta tres punto cinco gigahertz en "
    "modo turbo. Ocho gigabytes de memoria RAM, DDR cuatro, con E C C. "
    "Un terabyte de disco duro, con controlador H P E Dynamic Smart Array "
    "B ciento cuarenta i. Fuente de poder de trescientos cincuenta watts "
    "fija, con opción redundante de cuatrocientos sesenta watts. Cuatro "
    "ranuras de expansión P C I e, versión tres punto cero. Administración "
    "remota, con H P E i L O. "
    "Este equipo llega completamente configurado con Windows Server dos "
    "mil veintidós, Datacenter: incluye instalación del sistema operativo, "
    "configuración de red, configuración básica de usuarios, y "
    "configuración de respaldo. Listo para operar. "
    "Precio: treinta y siete mil, seiscientos veinticinco pesos mexicanos, "
    "más I V A. "
    "Kernel Corporation: responda a este correo, y con gusto le "
    "atenderemos."
)

SCRIPT_8GB_EN = (
    "Brand new server: HPE ProLiant ML thirty G nine. "
    "Intel Xeon E three, twelve twenty, v five processor: four cores, "
    "three gigahertz base clock, up to three point five gigahertz turbo. "
    "Eight gigabytes of DDR four RAM, with E C C. "
    "One terabyte hard drive, with HPE Dynamic Smart Array B one forty i "
    "controller. Three hundred fifty watt fixed power supply, with an "
    "optional four hundred sixty watt redundant configuration. Four P C "
    "I express three point zero expansion slots. Remote management, with "
    "HPE i L O. "
    "This system ships fully configured with Windows Server twenty "
    "twenty two, Datacenter: including operating system installation, "
    "network setup, basic user configuration, and backup setup. Ready to "
    "operate. "
    "Price: thirty seven thousand, six hundred twenty five Mexican pesos, "
    "plus tax. "
    "Kernel Corporation: reply to this email, and we will be glad to "
    "assist you."
)

SCRIPT_4GB_SP = (
    "Servidor completamente nuevo, H P E ProLiant M L treinta G nueve. "
    "Procesador Intel Xeon E tres mil doscientos veinte, v cinco: cuatro "
    "núcleos, tres gigahertz base, hasta tres punto cinco gigahertz en "
    "modo turbo. Cuatro gigabytes de memoria RAM, DDR cuatro, con E C C. "
    "Un terabyte de disco duro, con controlador H P E Dynamic Smart Array "
    "B ciento cuarenta i. Fuente de poder de trescientos cincuenta watts "
    "fija, con opción redundante de cuatrocientos sesenta watts. Cuatro "
    "ranuras de expansión P C I e, versión tres punto cero. Administración "
    "remota, con H P E i L O. "
    "Este equipo se entrega sin sistema operativo, permitiéndole una "
    "implementación totalmente personalizada. "
    "Precio: veintisiete mil, doscientos cincuenta pesos mexicanos, más "
    "I V A. "
    "Kernel Corporation: responda a este correo, y con gusto le "
    "atenderemos."
)

SCRIPT_4GB_EN = (
    "Brand new server: HPE ProLiant ML thirty G nine. "
    "Intel Xeon E three, twelve twenty, v five processor: four cores, "
    "three gigahertz base clock, up to three point five gigahertz turbo. "
    "Four gigabytes of DDR four RAM, with E C C. "
    "One terabyte hard drive, with HPE Dynamic Smart Array B one forty i "
    "controller. Three hundred fifty watt fixed power supply, with an "
    "optional four hundred sixty watt redundant configuration. Four P C "
    "I express three point zero expansion slots. Remote management, with "
    "HPE i L O. "
    "This system is delivered without an operating system, allowing for a "
    "fully customized deployment. "
    "Price: twenty seven thousand, two hundred fifty Mexican pesos, plus "
    "tax. "
    "Kernel Corporation: reply to this email, and we will be glad to "
    "assist you."
)

JOBS = [
    ("F4", SCRIPT_8GB_SP, "HP-ProLiant-ML30-8GB-SP-Female-Supertonic3.wav"),
    ("M1", SCRIPT_8GB_SP, "HP-ProLiant-ML30-8GB-SP-Male-Supertonic3.wav"),
    ("F4", SCRIPT_8GB_EN, "HP-ProLiant-ML30-8GB-EN-Female-Supertonic3.wav"),
    ("M1", SCRIPT_8GB_EN, "HP-ProLiant-ML30-8GB-EN-Male-Supertonic3.wav"),
    ("F4", SCRIPT_4GB_SP, "HP-ProLiant-ML30-4GB-SP-Female-Supertonic3.wav"),
    ("M1", SCRIPT_4GB_SP, "HP-ProLiant-ML30-4GB-SP-Male-Supertonic3.wav"),
    ("F4", SCRIPT_4GB_EN, "HP-ProLiant-ML30-4GB-EN-Female-Supertonic3.wav"),
    ("M1", SCRIPT_4GB_EN, "HP-ProLiant-ML30-4GB-EN-Male-Supertonic3.wav"),
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
            out_wav = OUT_DIR / filename
            out_mp3 = out_wav.with_suffix(".mp3")
            print(f"[generate] voz={voice} archivo={filename} ...")
            resp = client.post(
                "/generate",
                data={"text": text, "engine": "supertonic3", "preset_voice": voice},
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

    print("\n[DONE] 8 audios de servidores HPE ProLiant ML30 G9 generados.")


if __name__ == "__main__":
    main()
