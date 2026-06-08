from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .sensors import SensorReadings
from .vision import VisionMetrics


class Thresholds:
    class Temp:
        MAX = 45.0
        MIN = 5.0

    class Hum:
        MAX = 90.0
        MIN = 25.0

    class Lum:
        MAX = 90.0
        MIN = 15.0

    class RoverDist:
        CRITICAL = 15.0
        ATTENTION = 25.0

    class Vision:
        MOTION_SEVERE = 0.70


class RiskLevel(str, Enum):
    NORMAL = "Normal"
    ATTENTION = "Atenção"
    CRITICAL = "Crítico"


@dataclass(slots=True)
class RiskResult:
    level: RiskLevel
    score: int
    reasons: list[str]


def evaluate_risk(vision: VisionMetrics, sensors: SensorReadings | None) -> RiskResult:
    score = 0
    reasons: list[str] = []

    if sensors is not None and sensors.distance_cm is not None:
        dist = sensors.distance_cm
        if 0 < dist <= Thresholds.RoverDist.CRITICAL:
            score += 5
            reasons.append("Impacto iminente")
        elif Thresholds.RoverDist.CRITICAL < dist <= Thresholds.RoverDist.ATTENTION:
            score += 3
            reasons.append("Alerta de colisão")

    if vision.motion_score >= Thresholds.Vision.MOTION_SEVERE:
        score += 3
        reasons.append("Instabilidade/Movimento severo")
    elif sensors is not None and sensors.pir_detected:
        score += 2
        reasons.append("Assinatura térmica móvel")

    if sensors is not None and sensors.temperature_c is not None:
        if sensors.temperature_c >= Thresholds.Temp.MAX:
            score += 3
            reasons.append(f"Risco de superaquecimento (>{Thresholds.Temp.MAX}°C)")
        elif sensors.temperature_c <= Thresholds.Temp.MIN:
            score += 2
            reasons.append(f"Risco de congelamento (<{Thresholds.Temp.MIN}°C)")

        if sensors.humidity_pct is not None:
            if sensors.humidity_pct >= Thresholds.Hum.MAX:
                score += 2
                reasons.append("Umidade crítica")
            elif sensors.humidity_pct <= Thresholds.Hum.MIN:
                score += 2
                reasons.append("Umidade baixa")

    is_dark = vision.low_light
    if sensors is not None and sensors.luminosity_pct is not None:
        if sensors.luminosity_pct <= Thresholds.Lum.MIN:
            is_dark = True
            score += 3
            reasons.append("Visibilidade crítica")
        elif sensors.luminosity_pct >= Thresholds.Lum.MAX:
            score += 1
            reasons.append("Anomalia luminosa")
    elif is_dark:
        score += 1
        reasons.append("Baixa visibilidade")

    if score >= 5:
        return RiskResult(level=RiskLevel.CRITICAL, score=score, reasons=reasons)

    if score >= 3:
        return RiskResult(level=RiskLevel.ATTENTION, score=score, reasons=reasons)

    if not reasons:
        reasons.append("Parâmetros estáveis")

    return RiskResult(level=RiskLevel.NORMAL, score=score, reasons=reasons)
