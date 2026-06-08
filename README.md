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
uv run python -m src.main
```

### Webcam + sensores serial
```powershell
uv run python -m src.main --serial-port COM3 --baudrate 115200
```

### Opções úteis
```powershell
uv run python -m src.main --help
```

## Formato serial esperado (Arduino)
Pode enviar JSON:
```text
{"temp":28.4,"hum":62.1,"lux":180,"pir":1,"distance_cm":72}
```

Ou pares `chave=valor`:
```text
temp=28.4,hum=62.1,lux=180,pir=1,distance_cm=72
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