from __future__ import annotations

import argparse
import sys
import time

import cv2

from brightspot.risk import evaluate_risk
from brightspot.sensors import SensorReadings, SerialSensorReader
from brightspot.ui.overlay import draw_overlay
from brightspot.vision import VisionAnalyzer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="BrightSpot MVP: monitor ambiental com webcam + sensores opcionais."
    )
    parser.add_argument("--camera-index", type=int, default=0, help="Indice da webcam")
    parser.add_argument("--width", type=int, default=1280, help="Largura de captura")
    parser.add_argument("--height", type=int, default=960, help="Altura de captura")
    parser.add_argument(
        "--serial-port",
        type=str,
        default=None,
        help="Porta serial para sensores (ex.: COM3)",
    )
    parser.add_argument(
        "--baudrate", type=int, default=115200, help="Baudrate da porta serial"
    )
    parser.add_argument(
        "--no-mediapipe",
        action="store_true",
        help="Desativa deteccao de presenca com MediaPipe",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    capture = cv2.VideoCapture(args.camera_index, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    if not capture.isOpened():
        print("Erro: nao foi possivel abrir a webcam.", file=sys.stderr)
        return 1

    vision = VisionAnalyzer(enable_detection=not args.no_mediapipe)
    sensor_reader: SerialSensorReader | None = None
    latest_sensor: SensorReadings | None = None

    if args.serial_port:
        sensor_reader = SerialSensorReader(
            port=args.serial_port, baudrate=args.baudrate
        )
        try:
            sensor_reader.connect()
            print(f"Serial conectada em {args.serial_port} @ {args.baudrate}.")
        except Exception as exc:
            print(f"Aviso: falha ao abrir serial ({exc}). Continuando sem sensores.")
            sensor_reader = None

    previous_time = time.perf_counter()

    show_box = True

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                print("Erro: falha ao ler frame da webcam.", file=sys.stderr)
                return 2

            metrics = vision.process(frame)

            if sensor_reader is not None:
                try:
                    maybe_sensor = sensor_reader.read_latest()
                    if maybe_sensor is not None:
                        latest_sensor = maybe_sensor
                except Exception as exc:
                    print(f"Aviso: leitura serial invalida ({exc}).")

            risk = evaluate_risk(metrics, latest_sensor)

            now = time.perf_counter()
            dt = max(1e-6, now - previous_time)
            fps = 1.0 / dt
            previous_time = now

            draw_overlay(
                frame,
                metrics,
                risk,
                latest_sensor,
                fps,
                process_size=(640, 480),
                show_box=show_box,
            )
            cv2.imshow("BrightSpot Monitor", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("v"):
                show_box = not show_box
                estado = "LIGADA" if show_box else "DESLIGADA"
                print(f"Caixa de detecção {estado}")
    finally:
        vision.close()
        capture.release()
        if sensor_reader is not None:
            sensor_reader.close()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
