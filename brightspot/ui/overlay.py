import datetime

import cv2
import numpy as np
from PIL import Image, ImageDraw

from .theme import Theme
from .helpers import (
    _draw_inline_gauge,
    _draw_sensor_strip,
    _risk_color_rgb,
    _text_w,
    _draw_badge,
    _draw_text,
    _fill_rect_alpha,
    _scanlines,
    _draw_hud_box,
    _get_font,
)
from ..risk import RiskResult
from ..sensors import SensorReadings
from ..vision import VisionMetrics


def draw_overlay(
    frame: np.ndarray,
    metrics: VisionMetrics,
    risk: RiskResult,
    sensors: SensorReadings | None,
    fps: float,
    process_size: tuple[int, int] = (640, 480),
    show_box: bool = True,
) -> np.ndarray:
    h, w = frame.shape[:2]
    accent_rgb = _risk_color_rgb(risk.level)
    accent_bgr = (accent_rgb[2], accent_rgb[1], accent_rgb[0])
    panel_color_bgr = Theme.Colors.PANEL

    if show_box and metrics.detections:
        for detection in metrics.detections:
            _draw_hud_box(frame, detection, accent_rgb, process_size)

    _fill_rect_alpha(
        frame, 0, 0, w, Theme.Sizes.TOP_H, panel_color_bgr, Theme.Alphas.PANEL
    )
    reason_y = h - Theme.Sizes.BOTTOM_H - Theme.Sizes.REASON_H
    _fill_rect_alpha(
        frame,
        0,
        reason_y,
        w,
        Theme.Sizes.REASON_H,
        panel_color_bgr,
        Theme.Alphas.PANEL,
    )
    _fill_rect_alpha(
        frame,
        0,
        h - Theme.Sizes.BOTTOM_H,
        w,
        Theme.Sizes.BOTTOM_H,
        panel_color_bgr,
        Theme.Alphas.PANEL,
    )

    cv2.rectangle(
        frame, (0, 0), (Theme.Sizes.ACCENT_W - 1, h - 1), accent_bgr, cv2.FILLED
    )

    div_color = Theme.Colors.DIVIDER
    cv2.line(
        frame,
        (Theme.Sizes.ACCENT_W, Theme.Sizes.TOP_H),
        (w - 1, Theme.Sizes.TOP_H),
        div_color,
        1,
    )
    cv2.line(
        frame, (Theme.Sizes.ACCENT_W, reason_y), (w - 1, reason_y), div_color, 1
    )
    cv2.line(
        frame,
        (Theme.Sizes.ACCENT_W, h - Theme.Sizes.BOTTOM_H),
        (w - 1, h - Theme.Sizes.BOTTOM_H),
        div_color,
        1,
    )

    _scanlines(frame, 0, Theme.Sizes.TOP_H)
    _scanlines(frame, reason_y, Theme.Sizes.REASON_H)
    _scanlines(frame, h - Theme.Sizes.BOTTOM_H, Theme.Sizes.BOTTOM_H)

    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil, "RGBA")

    # ---------------------------------------------------------------------------- #
    #                                    TOP BAR                                   #
    # ---------------------------------------------------------------------------- #
    pad = Theme.Sizes.ACCENT_W + Theme.Sizes.PAD_LEFT

    _draw_badge(draw, risk.level.value.upper(), pad, Theme.Sizes.BADGE_Y, accent_rgb)

    badge_font = _get_font(Theme.Fonts.BADGE, bold=True)
    badge_bb = draw.textbbox(
        (pad, Theme.Sizes.PAD_LEFT), risk.level.value.upper(), font=badge_font
    )
    gauge_x = badge_bb[2] + Theme.Sizes.GAUGE_OFFSET_X
    gauge_w = Theme.Sizes.GAUGE_W
    gauge_h = Theme.Sizes.GAUGE_H

    _draw_inline_gauge(
        draw,
        "MOVIMENTO",
        metrics.motion_score,
        gauge_x,  # ty:ignore[invalid-argument-type]
        Theme.Sizes.GAUGE_MOT_Y,
        gauge_w,
        gauge_h,
        accent_rgb if metrics.motion_detected else Theme.Colors.GAUGE_MOT_INACTIVE,
    )
    _draw_inline_gauge(
        draw,
        "BRILHO",
        metrics.brightness,
        gauge_x,  # ty:ignore[invalid-argument-type]
        Theme.Sizes.GAUGE_BRI_Y,
        gauge_w,
        gauge_h,
        Theme.Colors.GAUGE_BRI,
    )

    if metrics.low_light:
        ll = "⚠  BAIXA LUZ"
        ll_x = w // 2 - _text_w(draw, ll, Theme.Fonts.LOW_LIGHT) // 2
        _draw_text(
            draw,
            ll,
            ll_x,
            Theme.Sizes.LOW_LIGHT_Y,
            Theme.Fonts.LOW_LIGHT,
            Theme.Colors.TXT_LOW_LIGHT,
            bold=True,
        )

    fps_str = f"{fps:05.2f} FPS"
    ts_str = datetime.datetime.now().strftime("%H:%M:%S")
    fps_x = w - _text_w(draw, fps_str, Theme.Fonts.FPS) - Theme.Sizes.MARGIN_R
    ts_x = w - _text_w(draw, ts_str, Theme.Fonts.TS) - Theme.Sizes.MARGIN_R
    _draw_text(
        draw,
        fps_str,
        fps_x,
        Theme.Sizes.FPS_Y,
        Theme.Fonts.FPS,
        Theme.Colors.TXT_FPS,
        bold=True,
    )
    _draw_text(
        draw,
        ts_str,
        ts_x,
        Theme.Sizes.TS_Y,
        Theme.Fonts.TS,
        Theme.Colors.TXT_TS,
    )

    # ---------------------------------------------------------------------------- #
    #                                  REASON BAR                                  #
    # ---------------------------------------------------------------------------- #
    if risk.reasons:
        main_reason = "  ||  ".join(risk.reasons)
    else:
        main_reason = "Parâmetros ambientais estáveis. Seguro para exploração."

    reason_upper = main_reason.upper()
    ry = reason_y + (Theme.Sizes.REASON_H - Theme.Sizes.REASON_TXT_OFFSET) // 2

    _draw_text(
        draw,
        f"›› {reason_upper}",
        pad,
        ry,
        Theme.Fonts.REASON,
        accent_rgb,
        bold=True,
    )
    _draw_text(
        draw,
        f"›› {reason_upper}",
        pad,
        ry,
        Theme.Fonts.REASON,
        accent_rgb,
        bold=True,
    )
    det_count = len(metrics.detections) if metrics.detections else 0
    dot = "●" if metrics.presence_detected else "○"
    pres = f"{dot} {det_count} PESSOA{'S' if det_count != 1 else ''}"
    pres_x = w - _text_w(draw, pres, Theme.Fonts.PRESENCE) - Theme.Sizes.MARGIN_R
    _draw_text(
        draw,
        pres,
        pres_x,
        ry,
        Theme.Fonts.PRESENCE,
        accent_rgb if metrics.presence_detected else Theme.Colors.TXT_PRESENCE_NONE,
    )

    # ---------------------------------------------------------------------------- #
    #                                 BOTTOM SENSOR                                #
    # ---------------------------------------------------------------------------- #
    _draw_sensor_strip(draw, sensors, w, h)

    frame[:] = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    return frame
