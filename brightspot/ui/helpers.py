from __future__ import annotations

import cv2
import numpy as np
from .theme import Theme
from PIL import ImageDraw, ImageFont
from ..sensors import SensorReadings
from ..risk import RiskLevel, Thresholds

_FONT_CACHE: dict[tuple[bool, int], ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}

_FONT_BOLD_PATH = "./fonts/JetBrainsMono-Bold.ttf"
_FONT_REG_PATH = "./fonts/JetBrainsMono-Regular.ttf"


def _get_font(
    size: int, bold: bool = False
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    key = (bold, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    path = _FONT_BOLD_PATH if bold else _FONT_REG_PATH
    try:
        f = ImageFont.truetype(path, size)
    except IOError:
        print(
            "Aviso: falha ao carregar fonte personalizada; usando fonte padrão.",
        )
        f = ImageFont.load_default()

    _FONT_CACHE[key] = f
    return f


def _fill_rect_alpha(
    frame: np.ndarray,
    x: int,
    y: int,
    w: int,
    h: int,
    color_bgr: tuple[int, int, int],
    alpha: float,
) -> None:
    roi = frame[y : y + h, x : x + w]
    solid = np.empty_like(roi)
    solid[:] = color_bgr
    cv2.addWeighted(solid, alpha, roi, 1.0 - alpha, 0.0, roi)
    frame[y : y + h, x : x + w] = roi


def _scanlines(frame: np.ndarray, start_y: int, height: int) -> None:
    seg = frame[start_y : start_y + height]
    seg[::2] = (seg[::2] * Theme.Alphas.SCANLINE_MULT).astype(np.uint8)


def _draw_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    size: int,
    color: tuple[int, int, int],
    bold: bool = False,
) -> None:
    font = _get_font(size, bold=bold)
    draw.text(
        (x + Theme.Sizes.TEXT_SHADOW_OFFSET, y + Theme.Sizes.TEXT_SHADOW_OFFSET),
        text,
        font=font,
        fill=Theme.Colors.TEXT_SHADOW,
    )
    draw.text((x, y), text, font=font, fill=(*color, 255))


def _text_w(draw: ImageDraw.ImageDraw, text: str, size: int, bold: bool = False) -> int:
    bb = draw.textbbox((0, 0), text, font=_get_font(size, bold=bold))
    return bb[2] - bb[0]  # ty:ignore[invalid-return-type]


def _draw_badge(
    draw: ImageDraw.ImageDraw,
    label: str,
    x: int,
    y: int,
    color: tuple[int, int, int],
) -> None:
    font = _get_font(Theme.Fonts.BADGE, bold=True)
    bb = draw.textbbox((x, y), label, font=font)
    px, py = Theme.Sizes.BADGE_PAD_X, Theme.Sizes.BADGE_PAD_Y
    rect = (bb[0] - px, bb[1] - py, bb[2] + px, bb[3] + py)
    draw.rectangle(rect, fill=(*color, Theme.Alphas.BADGE_BG))
    draw.rectangle(rect, outline=(*color, Theme.Alphas.BADGE_BORDER))
    draw.text(
        (x + Theme.Sizes.TEXT_SHADOW_OFFSET, y + Theme.Sizes.TEXT_SHADOW_OFFSET),
        label,
        font=font,
        fill=Theme.Colors.BADGE_TEXT_SHADOW,
    )
    draw.text((x, y), label, font=font, fill=(*color, 255))


def _draw_inline_gauge(
    draw: ImageDraw.ImageDraw,
    label: str,
    value: float,
    x: int,
    y: int,
    bar_w: int,
    bar_h: int,
    bar_color: tuple[int, int, int],
) -> None:
    lbl_font = _get_font(Theme.Fonts.GAUGE_LBL)
    lbl_bb = draw.textbbox((0, 0), label, font=lbl_font)
    lbl_w = lbl_bb[2] - lbl_bb[0]

    draw.text((x, y), label, font=lbl_font, fill=Theme.Colors.GAUGE_LBL)

    bx = x + lbl_w + Theme.Sizes.GAUGE_LBL_PAD
    by = y + Theme.Sizes.GAUGE_Y_OFFSET

    draw.rectangle((bx, by, bx + bar_w, by + bar_h), fill=Theme.Colors.GAUGE_BG)
    fill_w = max(2, int(bar_w * min(1.0, max(0.0, value))))
    draw.rectangle(
        (bx, by, bx + fill_w, by + bar_h), fill=(*bar_color, Theme.Alphas.GAUGE_BAR)
    )

    for i in (1, 2, 3):
        tx = bx + bar_w * i // 4
        draw.line((tx, by, tx, by + bar_h), fill=Theme.Colors.GAUGE_DIV, width=1)

    pct_font = _get_font(Theme.Fonts.GAUGE_PCT)
    pct = f"{value:.0%}"
    draw.text(
        (bx + bar_w + Theme.Sizes.GAUGE_PCT_PAD_X, by - 1),
        pct,
        font=pct_font,
        fill=Theme.Colors.GAUGE_PCT,
    )


def _draw_hud_box(
    frame: np.ndarray,
    detection,
    color_rgb: tuple[int, int, int],
    process_size: tuple[int, int] = (640, 480),  #
) -> None:
    h_real, w_real = frame.shape[:2]
    w_ia, h_ia = process_size

    scale_x = w_real / w_ia
    scale_y = h_real / h_ia

    bbox = detection.bounding_box
    x = int(bbox.origin_x * scale_x)
    y = int(bbox.origin_y * scale_y)
    w = int(bbox.width * scale_x)
    h = int(bbox.height * scale_y)

    color_bgr = (color_rgb[2], color_rgb[1], color_rgb[0])

    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), color_bgr, cv2.FILLED)
    cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)

    line_len = max(15, int(w * 0.15))
    thickness = 2

    cv2.line(frame, (x, y), (x + line_len, y), color_bgr, thickness)
    cv2.line(frame, (x, y), (x, y + line_len), color_bgr, thickness)
    cv2.line(frame, (x + w, y), (x + w - line_len, y), color_bgr, thickness)
    cv2.line(frame, (x + w, y), (x + w, y + line_len), color_bgr, thickness)
    cv2.line(frame, (x, y + h), (x + line_len, y + h), color_bgr, thickness)
    cv2.line(frame, (x, y + h), (x, y + h - line_len), color_bgr, thickness)
    cv2.line(frame, (x + w, y + h), (x + w - line_len, y + h), color_bgr, thickness)
    cv2.line(frame, (x + w, y + h), (x + w, y + h - line_len), color_bgr, thickness)

    cv2.rectangle(frame, (x, y), (x + w, y + h), color_bgr, 1)


def _draw_sensor_strip(
    draw: ImageDraw.ImageDraw,
    sensors: SensorReadings | None,
    frame_w: int,
    frame_h: int,
) -> None:
    tiles = _sensor_tiles(sensors)
    n = len(tiles)
    strip_y = frame_h - Theme.Sizes.BOTTOM_H
    tile_w = (frame_w - Theme.Sizes.ACCENT_W) // n
    tile_x = Theme.Sizes.ACCENT_W

    # Alteramos a variável 'alert' para 'risk_level'
    for i, (label, value, unit, risk_level) in enumerate(tiles):
        cx = tile_x + tile_w // 2

        if i > 0:
            draw.line(
                (
                    tile_x,
                    strip_y + Theme.Sizes.SENSOR_DIV_PAD_Y,
                    tile_x,
                    frame_h - Theme.Sizes.SENSOR_DIV_PAD_Y,
                ),
                fill=Theme.Colors.SENSOR_DIV,
                width=1,
            )

        lbl_font = _get_font(Theme.Fonts.SENSOR_LBL)
        lbl_w = draw.textbbox((0, 0), label, font=lbl_font)[2]
        draw.text(
            (cx - lbl_w // 2, strip_y + Theme.Sizes.SENSOR_LBL_Y),
            label,
            font=lbl_font,
            fill=Theme.Colors.SENSOR_LBL,
        )

        # --- LÓGICA DE CORES DO SEMÁFORO (TRICOLOR) ---
        if risk_level == RiskLevel.CRITICAL:
            val_color = Theme.Colors.SENSOR_VAL_CRITICAL
        elif risk_level == RiskLevel.ATTENTION:
            val_color = Theme.Colors.SENSOR_VAL_ATTENTION
        else:
            val_color = Theme.Colors.SENSOR_VAL_NORMAL
        # ---------------------------------------------

        val_font = _get_font(Theme.Fonts.SENSOR_VAL, bold=True)
        val_w = draw.textbbox((0, 0), value, font=val_font)[2]
        vx = cx - val_w // 2
        vy = strip_y + Theme.Sizes.SENSOR_VAL_Y

        draw.text(
            (
                vx + Theme.Sizes.TEXT_SHADOW_OFFSET,
                vy + Theme.Sizes.TEXT_SHADOW_OFFSET,
            ),
            value,
            font=val_font,
            fill=Theme.Colors.SENSOR_VAL_SHADOW,
        )
        # O Pillow usa o val_color que foi definido no bloco if acima
        draw.text((vx, vy), value, font=val_font, fill=(*val_color, 255))

        if unit:
            u_font = _get_font(Theme.Fonts.SENSOR_UNIT)
            u_w = draw.textbbox((0, 0), unit, font=u_font)[2]
            draw.text(
                (cx - u_w // 2, strip_y + Theme.Sizes.SENSOR_UNIT_Y),
                unit,
                font=u_font,
                fill=Theme.Colors.SENSOR_UNIT,
            )

        tile_x += tile_w


def _sensor_tiles(
    sensors: SensorReadings | None,
) -> list[tuple[str, str, str, RiskLevel]]:
    def _fv(v: float | None) -> str:
        return f"{v:.1f}" if v is not None else "--"

    if sensors is None:
        return [
            ("TEMPERATURA", "--", "°C", RiskLevel.NORMAL),
            ("UMIDADE", "--", "%", RiskLevel.NORMAL),
            ("LUMINOSIDADE", "--", "%", RiskLevel.NORMAL),
            ("DISTÂNCIA", "--", "cm", RiskLevel.NORMAL),
            ("PRESENÇA", "--", "", RiskLevel.NORMAL),
        ]

    dist_risk = RiskLevel.NORMAL
    if sensors.distance_cm is not None:
        if sensors.distance_cm <= Thresholds.RoverDist.CRITICAL:
            dist_risk = RiskLevel.CRITICAL
        elif sensors.distance_cm <= Thresholds.RoverDist.ATTENTION:
            dist_risk = RiskLevel.ATTENTION

    temp_risk = RiskLevel.NORMAL
    if sensors.temperature_c is not None:
        if (
            sensors.temperature_c >= Thresholds.Temp.MAX
            or sensors.temperature_c <= Thresholds.Temp.MIN
        ):
            temp_risk = RiskLevel.CRITICAL

    hum_risk = RiskLevel.NORMAL
    if sensors.humidity_pct is not None and sensors.humidity_pct >= Thresholds.Hum.MAX:
        hum_risk = RiskLevel.ATTENTION

    lum_risk = RiskLevel.NORMAL
    if sensors.luminosity_pct is not None:
        if (
            sensors.luminosity_pct <= Thresholds.Lum.MIN
            or sensors.luminosity_pct >= Thresholds.Lum.MAX
        ):
            lum_risk = RiskLevel.ATTENTION

    pir_val = "SIM" if sensors.pir_detected else "--"
    pir_risk = RiskLevel.ATTENTION if sensors.pir_detected else RiskLevel.NORMAL

    return [
        ("TEMPERATURA", _fv(sensors.temperature_c), "°C", temp_risk),
        ("UMIDADE", _fv(sensors.humidity_pct), "%", hum_risk),
        ("LUMINOSIDADE", _fv(sensors.luminosity_pct), "%", lum_risk),
        ("DISTÂNCIA", _fv(sensors.distance_cm), "cm", dist_risk),
        ("PRESENÇA", pir_val, "", pir_risk),
    ]


def _risk_color_rgb(level: RiskLevel) -> tuple[int, int, int]:
    if level == RiskLevel.CRITICAL:
        return Theme.Colors.RISK_CRIT
    if level == RiskLevel.ATTENTION:
        return Theme.Colors.RISK_ATTN
    return Theme.Colors.RISK_NORMAL
