import cv2
import numpy as np
import time
import torch

from ultralytics import YOLO
from supervision import BoxAnnotator, Detections, ColorPalette

from tracker import Tracker


def main():

    video_url = "https://sochi.camera/vse-kamery/dorogi/"

    cap = cv2.VideoCapture("Video 1.mp4")

    if not cap.isOpened():
        print("Failed to open the video stream.")
        exit()
    model = YOLO("yolov8x.pt")
    if torch.cuda.is_available():
        print("Switching device to CUDA")
        model.to("cuda")
        print("Switched device to CUDA")

    # dict maping class_id to class_name
    CLASS_NAMES_DICT = model.model.names
    print(CLASS_NAMES_DICT)

    # class_ids of interest - car, motorcycle, bus and truck
    CLASS_ID = [0, 1, 2, 3, 4, 5, 7]

    box_annotator = BoxAnnotator(color=ColorPalette.default(), thickness=2, text_thickness=2, text_scale=1)
    tracker = Tracker()


    cx1 = 1000
    cx2 = 1500

    cy1 = 100
    cy2 = 750

    offset = 6

    frame_cnt = 0

    vh_down = {}
    counter_down = []

    vh_up = {}
    counter_up = []
    id2speed = {}

    while True:
        ret, frame = cap.read()
        # for playback speed
        if frame_cnt > 0:
            if frame_cnt == 1:
                frame_cnt = -1
            frame_cnt += 1
            print("skipped")
            continue
        frame_cnt += 1

        results = model(frame)

        # filter only vehicles detections
        mask = np.array([class_id in CLASS_ID for class_id in results[0].boxes.cls.cpu().numpy().astype(int)], dtype=bool)
        detections = Detections(
            xyxy=results[0].boxes.xyxy.cpu().numpy()[mask.astype(bool)],
            confidence=results[0].boxes.conf.cpu().numpy()[mask.astype(bool)],
            class_id=results[0].boxes.cls.cpu().numpy().astype(int)[mask.astype(bool)]
        )

        bbox_id = tracker.update(detections.xyxy)
        for bbox in bbox_id:
            x3, y3, x4, y4, id = bbox
            x3, y3, x4, y4 = int(x3), int(y3), int(x4), int(y4)
            cx = int(x3 + x4) // 2
            cy = int(y3 + y4) // 2
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
            if cx1 < (cx + offset) and cx1 > (cx - offset):
                vh_down[id] = time.time()
            if id in vh_down:

                if cx2 < (cx + offset) and cx2 > (cx - offset):
                    elapsed_time = time.time() - vh_down[id]
                    if counter_down.count(id) == 0:
                        counter_down.append(id)
                        distance = 10  # meters
                        a_speed_ms = distance / elapsed_time
                        a_speed_kh = a_speed_ms * 3.6
                        id2speed[id] = a_speed_kh



            # going UP
            if cx2 < (cx + offset) and cx2 > (cx - offset):
                vh_up[id] = time.time()
            if id in vh_up:

                if cx1 < (cx + offset) and cx1 > (cx - offset):
                    elapsed1_time = time.time() - vh_up[id]

                    if counter_up.count(id) == 0:
                        counter_up.append(id)
                        distance1 = 10  # meters
                        a_speed_ms1 = distance1 / elapsed1_time

                        a_speed_kh1 = a_speed_ms1 * 3.6
                        print(a_speed_kh1)
                        id2speed[id] = a_speed_kh1


            if id in id2speed:
                cv2.putText(frame, str(int(id2speed[id])) + 'Km/h', (x4, y4), cv2.FONT_HERSHEY_COMPLEX, 0.8, (16, 255, 170), 2)

        labels = [
            f"{CLASS_NAMES_DICT[class_id]} {confidence:0.2f}"
            for _, _, confidence, class_id, tracker_id
            in detections
        ]

        frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)
        cv2.line(frame, (cx1, cy1), (cx1, cy2), (255, 255, 255), 1)

        cv2.line(frame, (cx2, cy1), (cx2, cy2), (255, 255, 255), 1)

        d = (len(counter_down))
        u = (len(counter_up))

        cv2.putText(frame, ('goingdown:-') + str(d), (160, 150), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

        cv2.putText(frame, ('goingup:-') + str(u), (160, 190), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("yolov8", frame)
        print(counter_up)

        if cv2.waitKey(30) == 27:  # press Esc to exit
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
