import json
import time
from dataclasses import dataclass
from typing import Any

try:
    import serial as _serial

    serial = _serial
except ImportError:
    serial = None


@dataclass(slots=True)
class SensorReadings:
    temperature_c: float | None = None
    humidity_pct: float | None = None
    luminosity_pct: float | None = None
    pir_detected: bool | None = None
    distance_cm: float | None = None
    timestamp: float = 0.0
    raw: str = ""


class SerialSensorReader:
    def __init__(
        self, port: str, baudrate: int = 115200, timeout: float = 0.05
    ) -> None:
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._serial_connection: Any

    def connect(self) -> None:
        if serial is None:
            raise RuntimeError("pyserial não está instalado.")
        self._serial_connection = serial.Serial(
            self._port, self._baudrate, timeout=self._timeout
        )

    def close(self) -> None:
        if self._serial_connection is not None and self._serial_connection.is_open:
            self._serial_connection.close()

    def read_latest(self) -> SensorReadings | None:
        if self._serial_connection is None:
            return None

        if not self._serial_connection.in_waiting:
            return None

        raw_line = (
            self._serial_connection.readline().decode("utf-8", errors="replace").strip()
        )
        if not raw_line:
            return None

        return _parse_sensor_line(raw_line)


def _parse_sensor_line(line: str) -> SensorReadings:
    line = line.strip()
    if not line:
        raise ValueError("Linha serial vazia.")

    if line.startswith("{"):
        return _from_json(line)

    raise ValueError(f"Formato de linha inesperado (não é JSON): {line}")


def _ldr_to_pct(raw_value: float | None) -> float | None:
    """Converte a leitura analógica bruta (0-1023) em porcentagem de luminosidade (0-100%)."""
    if raw_value is None or raw_value <= 0:
        return 0.0

    if raw_value >= 1023:
        return 100.0

    luminosidade_pct = (raw_value / 1023.0) * 100.0

    return round(luminosidade_pct, 1)


def _from_json(line: str) -> SensorReadings:
    payload = json.loads(line)
    if not isinstance(payload, dict):
        raise ValueError("JSON de sensor inválido.")

    raw_ldr = _to_float(payload.get("ldr"))

    return SensorReadings(
        temperature_c=_to_float(payload.get("temp") or payload.get("temperature")),
        humidity_pct=_to_float(payload.get("hum") or payload.get("humidity")),
        luminosity_pct=_ldr_to_pct(raw_ldr),
        pir_detected=_to_bool(payload.get("pir")),
        distance_cm=_to_float(payload.get("distance") or payload.get("distance_cm")),
        timestamp=time.time(),
        raw=line,
    )


def _to_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)  # ty:ignore[invalid-argument-type]
    except (TypeError, ValueError):
        return None


def _to_bool(value: object) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "on", "yes", "detected"}:
        return True
    if normalized in {"0", "false", "off", "no"}:
        return False
    return None
