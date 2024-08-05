import cv2
import numpy as np
import time
import torch
import psycopg2
import datetime
import queue

from ultralytics import YOLO
from supervision import BoxAnnotator, Detections, ColorPalette
from tracker import Tracker

# Configuración de la base de datos
conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="1606", port="5432")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS camera (
    id SERIAL PRIMARY KEY,
    clase varchar(255),
    speed varchar(255),
    way varchar (255),
    fecha varchar(255),
    camara varchar(255)
);
""")
consulta = """INSERT INTO camera (clase, speed, way, fecha, camara) VALUES (%s, %s, %s, %s, %s);"""

# Configuración del buffer de frames
BUFFER_SIZE = 30  # Número de frames a acumular en el buffer
frame_buffer = queue.Queue(maxsize=BUFFER_SIZE)

def main():
    video_url = "http://192.168.1.129:8080//"
    cap = cv2.VideoCapture(video_url)

    if not cap.isOpened():
        print("Failed to open the video stream.")
        exit()

    model = YOLO("yolov8x.pt")
    if torch.cuda.is_available():
        model.to("cuda")

    CLASS_NAMES_DICT = model.model.names
    CLASS_ID = [0, 1, 2, 3, 4, 5, 7]
    box_annotator = BoxAnnotator(color=ColorPalette.default(), thickness=2, text_thickness=2, text_scale=1)
    tracker = Tracker()

    cy1 = 250
    cy2 = 325
    offset = 6

    vh_down = {}
    counter_down = []
    vh_up = {}
    counter_up = []
    id2speed = {}
    camara_dir = "Camara Base"

    while True:
        fecha_actual = datetime.datetime.now()
        ret, frame = cap.read()

        if not ret:
            print("Failed to capture frame")
            break

        frame = cv2.resize(frame, (1020, 500))

        # Acumula frames en el buffer
        if frame_buffer.full():
            frame_buffer.get()  # Elimina el frame más antiguo
        frame_buffer.put(frame)

        # Procesa frames desde el buffer
        while not frame_buffer.empty():
            frame = frame_buffer.get()
            results = model(frame)

            mask = np.array([class_id in CLASS_ID for class_id in results[0].boxes.cls.cpu().numpy().astype(int)], dtype=bool)
            detections = Detections(
                xyxy=results[0].boxes.xyxy.cpu().numpy()[mask],
                confidence=results[0].boxes.conf.cpu().numpy()[mask],
                class_id=results[0].boxes.cls.cpu().numpy().astype(int)[mask]
            )

            bbox_id = tracker.update(detections.xyxy)
            for bbox in bbox_id:
                x3, y3, x4, y4, id = bbox
                x3, y3, x4, y4 = int(x3), int(y3), int(x4), int(y4)
                cx = int(x3 + x4) // 2
                cy = int(y3 + y4) // 2
                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

                if cy1 < (cy + offset) and cy1 > (cy - offset):
                    vh_down[id] = time.time()
                if id in vh_down:
                    if cy2 < (cy + offset) and cy2 > (cy - offset):
                        elapsed_time = time.time() - vh_down[id]
                        if id not in counter_down:
                            nombre = ""
                            counter_down.append(id)
                            distance = 8.60  # meters
                            a_speed_ms = distance / elapsed_time
                            a_speed_kh = a_speed_ms * 3.6
                            id2speed[id] = a_speed_kh
                            for i in CLASS_NAMES_DICT:
                                if i != " ":
                                    nombre += i
                                else:
                                    break
                            datos = [(nombre, a_speed_kh, 'going down', fecha_actual, camara_dir)]
                            cur.executemany(consulta, datos)
                            conn.commit()

                if cy2 < (cy + offset) and cy2 > (cy - offset):
                    vh_up[id] = time.time()

                if id in vh_up:
                    if cy1 < (cy + offset) and cy1 > (cy - offset):
                        elapsed1_time = time.time() - vh_up[id]
                        if id not in counter_up:
                            nombre = ""
                            counter_up.append(id)
                            distance1 = 8.60  # meters
                            a_speed_ms1 = distance1 / elapsed1_time
                            a_speed_kh1 = a_speed_ms1 * 3.6
                            id2speed[id] = a_speed_kh1
                            for i in CLASS_NAMES_DICT:
                                if i != " ":
                                    nombre += i
                                else:
                                    break
                            datos = [(nombre, a_speed_kh1, 'going up', fecha_actual, camara_dir)]
                            cur.executemany(consulta, datos)
                            conn.commit()

                if id in id2speed:
                    cv2.putText(frame, str(int(id2speed[id])) + 'Km/h', (x4, y4), cv2.FONT_HERSHEY_COMPLEX, 0.8, (16, 255, 170), 2)

            labels = [
                f"{CLASS_NAMES_DICT[class_id]} {confidence:0.2f}"
                for _, _, confidence, class_id, tracker_id in detections
            ]

            frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)
            cv2.line(frame, (100, cy1), (1300, cy1), (255, 255, 255), 1)
            cv2.line(frame, (100, cy2), (1300, cy2), (255, 255, 255), 1)

            d = len(counter_down)
            u = len(counter_up)

            cv2.putText(frame, f'going down: {d}', (160, 150), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(frame, f'going up: {u}', (160, 190), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

            cv2.imshow("yolov8", frame)

        if cv2.waitKey(30) == 27:  # press Esc to exit
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
