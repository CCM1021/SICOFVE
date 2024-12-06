import cv2
import sys
from pyapriltags import Detector
import tkinter as tk
from tkinter import messagebox

# Función para mostrar un mensaje emergente con las coordenadas
def show_message(tag_coordinates):
    """
    Muestra un mensaje emergente con las coordenadas de los tags detectados.
    :param tag_coordinates: Lista de coordenadas de los tags.
    """
    message = "Se detectaron dos AprilTags:\n"
    for i, coords in enumerate(tag_coordinates):
        message += f"Tag {i+1} - ID: {coords['id']}, Coordenadas (X, Y): {coords['x']}, {coords['y']}\n"
    
    # Crear una ventana emergente usando tkinter
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal de tkinter
    messagebox.showinfo("Detección de AprilTags", message)
    root.destroy()


def calibration(selected_camera_index):
    # Configuración del detector
    at_detector = Detector(
        families="tag25h9",  # Familia de tags
        nthreads=4,          # Número de hilos
        quad_decimate=1.0,   # Resolución
        quad_sigma=0.0,      # Desenfoque de detección
        refine_edges=True,   # Mejorar detección de bordes
        decode_sharpening=0.25,
    )

    # Captura de video
    # Selección de fuente de video
    if selected_camera_index.isdigit():
        # Si camera_source es un número, tratamos como índice de cámara
        camera_index = int(selected_camera_index)
        cap = cv2.VideoCapture(camera_index)
    else:
        # Si camera_source es una URL, tratamos como enlace de video
        cap = cv2.VideoCapture(selected_camera_index)

    if not cap.isOpened():
        print(f"Error: Cannot open camera or video source with index {selected_camera_index}")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("No se pudo capturar el frame.")
            break

        # Convertir a escala de grises (requisito del detector)
        frame = cv2.resize(frame, (1080,540))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectar AprilTags
        tags = at_detector.detect(gray)

        # Lista para almacenar datos de los tags detectados
        detected_tags = []

        # Dibujar los resultados
        for tag in tags:
            # Coordenadas de los vértices del tag
            corners = tag.corners
            for i in range(4):
                start_point = tuple(map(int, corners[i]))
                end_point = tuple(map(int, corners[(i + 1) % 4]))
                cv2.line(frame, start_point, end_point, (0, 255, 0), 2)

            # Centro del tag
            center = tuple(map(int, tag.center))
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

            # ID del tag
            cv2.putText(
                frame, f"ID: {tag.tag_id}", (center[0] - 10, center[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2
            )

            # Guardar datos del tag detectado
            detected_tags.append({
                "id": tag.tag_id,
                "x": center[0],  # Coordenada X
                "y": center[1]   # Coordenada Y
            })

        # Revisar si se detectaron exactamente dos tags
        if len(detected_tags) == 2:
            # Mostrar mensaje y detener el análisis
            cap.release()
            cv2.destroyAllWindows()
            show_message(detected_tags)
            break

        # Mostrar frame con detecciones
        cv2.imshow("AprilTags Detection", frame)

        # Salir con la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar recursos si se rompe el loop
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Verifica que se pase al menos un argumento
    if len(sys.argv)> 1 :
        
           
        selected_camera_index = sys.argv[1]
      
        calibration(selected_camera_index)
    else:
        print("Error: No camera source provided")