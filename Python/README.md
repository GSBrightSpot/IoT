# BrightSpot MVP (GS 2026.1)

Monitor ambiental com visão computacional em tempo real (webcam) e integração opcional de sensores via serial.

## Requisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

## Setup com uv

No diretório do projeto:

```powershell
uv venv
.\.venv\Scripts\activate
uv sync
```

## Execução

### Somente webcam

```powershell
uv run python -m main
```

### Webcam + sensores serial

> Substitua `COM3` pela porta serial correta do seu dispositivo.

```powershell
uv run python -m main --serial-port COM3
```

### Ajuda e opções

```powershell
uv run python -m main --help
```

## Formato serial esperado (Arduino)

```text
{"temp":28.4,"hum":62.1,"ldr":180,"distance_cm":72}
```

## Estrutura

```text
src/
  main.py
  vision.py
  sensors.py
  risk.py
  ui.py
```
