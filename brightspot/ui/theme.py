class Theme:
    class Colors:
        RISK_NORMAL = (30, 220, 120)
        RISK_ATTN = (255, 180, 0)
        RISK_CRIT = (255, 60, 60)

        PANEL = (8, 8, 8)
        DIVIDER = (60, 60, 60)

        GAUGE_MOT_INACTIVE = (70, 170, 255)
        GAUGE_BRI = (220, 220, 90)
        GAUGE_BG = (20, 20, 25, 220)
        GAUGE_DIV = (80, 80, 90, 200)
        GAUGE_LBL = (190, 190, 210, 255)
        GAUGE_PCT = (210, 210, 230, 255)

        TXT_LOW_LIGHT = (255, 210, 60)
        TXT_FPS = (255, 255, 255)
        TXT_TS = (160, 165, 180)
        TXT_PRESENCE_NONE = (130, 130, 150)
        TEXT_SHADOW = (0, 0, 0, 220)
        BADGE_TEXT_SHADOW = (0, 0, 0, 150)

        SENSOR_DIV = (70, 70, 85, 255)
        SENSOR_LBL = (140, 140, 170, 255)
        SENSOR_VAL_NORMAL = (245, 245, 255)
        SENSOR_VAL_ATTENTION = (255, 193, 7)
        SENSOR_VAL_CRITICAL = (255, 50, 50)
        SENSOR_VAL_SHADOW = (0, 0, 0, 220)
        SENSOR_UNIT = (120, 130, 150, 255)

    class Sizes:
        TOP_H = 68
        REASON_H = 34
        BOTTOM_H = 76
        ACCENT_W = 5

        PAD_LEFT = 14
        MARGIN_R = 14
        TEXT_SHADOW_OFFSET = 1
        REASON_TXT_OFFSET = 16

        BADGE_Y = 18
        BADGE_PAD_X = 10
        BADGE_PAD_Y = 5

        GAUGE_W = 135
        GAUGE_H = 8
        GAUGE_OFFSET_X = 22
        GAUGE_LBL_PAD = 7
        GAUGE_PCT_PAD_X = 5
        GAUGE_Y_OFFSET = 2
        GAUGE_MOT_Y = 16
        GAUGE_BRI_Y = 38

        LOW_LIGHT_Y = 25
        FPS_Y = 14
        TS_Y = 36

        SENSOR_DIV_PAD_Y = 10
        SENSOR_LBL_Y = 6
        SENSOR_VAL_Y = 27
        SENSOR_UNIT_Y = 54

    class Alphas:
        PANEL = 0.80
        SCANLINE_MULT = 0.75
        BADGE_BG = 40
        BADGE_BORDER = 220
        GAUGE_BAR = 230

    class Fonts:
        BADGE = 21
        GAUGE_LBL = 11
        GAUGE_PCT = 10
        LOW_LIGHT = 14
        FPS = 15
        TS = 12
        REASON = 14
        PRESENCE = 13
        SENSOR_LBL = 14
        SENSOR_VAL = 20
        SENSOR_UNIT = 12
