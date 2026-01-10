import argparse
import time
from pathlib import Path

import cv2
import torch
from ultralytics import YOLO


def draw_fps(img, fps):
    txt = f"FPS: {fps:.1f}"
    cv2.rectangle(img, (10, 10), (140, 40), (0, 0, 0), -1)
    cv2.putText(img, txt, (18, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)


def main():
    parser = argparse.ArgumentParser(description="YOLOv8 Fire/Smoke Webcam Inference")
    parser.add_argument("--weights", type=str, default="weights/best.pt", help="path to your trained .pt")
    parser.add_argument("--device", type=str, default="0", help="cuda device id like '0' or 'cpu'")
    parser.add_argument("--conf", type=float, default=0.35, help="confidence threshold")
    parser.add_argument("--imgsz", type=int, default=640, help="inference image size")
    parser.add_argument("--source", type=str, default="0", help="camera index or RTSP/URL (e.g. '0' or 'rtsp://...')")
    parser.add_argument("--save", action="store_true", help="save annotated video to file")
    parser.add_argument("--out", type=str, default="runs/webcam_fire.mp4", help="output video file")
    args = parser.parse_args()

    # Resolve device
    if args.device != "cpu" and torch.cuda.is_available():
        device = int(args.device)
    else:
        device = "cpu"

    # Load model
    model = YOLO(args.weights)
    model.to(device)

    # Open capture (webcam index or URL)
    src = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open source: {args.source}")

    # Prepare writer (optional)
    writer = None
    if args.save:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        w  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1280)
        h  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 720)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 0:  # some webcams don’t report FPS
            fps = 30
        Path(Path(args.out).parent).mkdir(parents=True, exist_ok=True)
        writer = cv2.VideoWriter(args.out, fourcc, fps, (w, h))

    prev_t = time.time()
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Stream ended or failed to read frame.")
                break

            # Inference (stream=True gives generator of Results)
            results = model.predict(
                source=frame,
                imgsz=args.imgsz,
                conf=args.conf,
                verbose=False,
                device=device
            )

            # Annotate first (and only) result
            res = results[0]
            annotated = res.plot()  # draws boxes/labels

            # Draw FPS
            now = time.time()
            fps = 1.0 / max(1e-6, (now - prev_t))
            prev_t = now
            draw_fps(annotated, fps)

            # Show
            cv2.imshow("YOLOv8 Fire/Smoke - Webcam", annotated)
            if writer is not None:
                writer.write(annotated)

            # Quit with 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        if writer is not None:
            writer.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()