import sys
import os
import json
import wx
import subprocess
import cv2
import threading
from camera_dialog import CameraDialog

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(400, 600))
        # Obtén la ruta absoluta de la carpeta actual
        icon_path = os.path.abspath('./logo.ico')

        # Asigna el ícono a la ventana
        icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        panel = wx.Panel(self)

        # Lista desplegable para seleccionar la cámara
        self.camera_choice = wx.Choice(panel)
        self.refresh_camera_list()

        # Cuadros de texto para las coordenadas y distancia
        self.txt_distance = wx.TextCtrl(panel)
        self.txt_x1 = wx.TextCtrl(panel)
        self.txt_y1 = wx.TextCtrl(panel)
        self.txt_x2 = wx.TextCtrl(panel)
        self.txt_y2 = wx.TextCtrl(panel)

        # Botón para iniciar el script
        self.btn_start = wx.Button(panel, label="Iniciar Análisis")
        self.btn_start.Bind(wx.EVT_BUTTON, self.on_start_analysis)

        # Botón para agregar una cámara
        self.btn_add_camera = wx.Button(panel, label="Agregar Cámara")
        self.btn_add_camera.Bind(wx.EVT_BUTTON, self.on_add_camera)

        # Botón para eliminar una cámara
        self.btn_delete_camera = wx.Button(panel, label="Eliminar Cámara")
        self.btn_delete_camera.Bind(wx.EVT_BUTTON, self.on_delete_camera)

        # Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        grid_sizer = wx.GridSizer(rows=6, cols=2, hgap=10, vgap=10)

        # Agregar los campos al grid
        grid_sizer.Add(wx.StaticText(panel, label="Seleccione Cámara:"), flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.camera_choice, flag=wx.EXPAND)

        grid_sizer.Add(wx.StaticText(panel, label="Distancia entre lineas (m):"), flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_distance, flag=wx.EXPAND)

        grid_sizer.Add(wx.StaticText(panel, label="Coordenada X1:"), flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_x1, flag=wx.EXPAND)

        grid_sizer.Add(wx.StaticText(panel, label="Coordenada Y1:"), flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_y1, flag=wx.EXPAND)

        grid_sizer.Add(wx.StaticText(panel, label="Coordenada X2:"), flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_x2, flag=wx.EXPAND)

        grid_sizer.Add(wx.StaticText(panel, label="Coordenada Y2:"), flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_y2, flag=wx.EXPAND)

        main_sizer.Add(grid_sizer, flag=wx.EXPAND | wx.ALL, border=15)
        main_sizer.Add(self.btn_start, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        main_sizer.Add(self.btn_add_camera, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        main_sizer.Add(self.btn_delete_camera, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        panel.SetSizer(main_sizer)
        self.Center()
        self.Show()

    def resource_path(self, relative_path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def refresh_camera_list(self):
        cameras = self.get_available_cameras()
        self.camera_choice.SetItems(cameras)
        if cameras:
            self.camera_choice.SetSelection(0)

    def get_available_cameras(self):
        index = 0
        available_cameras = []
        try:
            with open(self.resource_path('cameras.json'), 'r') as f:
                cameras = json.load(f)
                for cam in cameras:
                    available_cameras.append(cam['name'])
        except FileNotFoundError:
            pass
        
        while True:
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                cam_name = f"Camera {index}"
                if cam_name not in available_cameras:
                    available_cameras.append(cam_name)
                cap.release()
                index += 1
            else:
                break

        return available_cameras

    def on_start_analysis(self, event):
        selected_camera = self.camera_choice.GetStringSelection()
        if not selected_camera:
            wx.MessageBox("Please select a camera.", "Error", wx.OK | wx.ICON_ERROR)
            return

        camera_data = self.get_camera_data(selected_camera)
        if camera_data is None:
            wx.MessageBox("Selected camera data not found.", "Error", wx.OK | wx.ICON_ERROR)
            return

        try:
            distance = int(self.txt_distance.GetValue())
            x1 = int(self.txt_x1.GetValue())
            y1 = int(self.txt_y1.GetValue())
            x2 = int(self.txt_x2.GetValue())
            y2 = int(self.txt_y2.GetValue())
            name = self.camera_choice.GetStringSelection()
        except ValueError:
            wx.MessageBox("Please enter valid integers for coordinates and distance.", "Error", wx.OK | wx.ICON_ERROR)
            return

        command_args = (camera_data['link'], distance, x1, y1, x2, y2, name)

        analysis_thread = threading.Thread(target=self.run_analysis_script, args=command_args)
        analysis_thread.start()

    def run_analysis_script(self, camera_link, distance, x1, y1, x2, y2, name):

    # Comando para ejecutar main.py dentro del entorno virtual de poetry
        command_to_run = f'poetry run python main.py {camera_link} {distance} {x1} {y1} {x2} {y2} {name}'

        if sys.platform.startswith('win'):
            # En Windows, abrir una consola de cmd y ejecutar poetry run seguido del script
            subprocess.Popen(['start', 'cmd', '/k', command_to_run], shell=True)

        elif sys.platform.startswith('linux'):
            # En Linux, abrir una nueva terminal y ejecutar poetry run seguido del script
            subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', command_to_run])

        elif sys.platform == 'darwin':
            # En macOS, abrir una nueva terminal de Terminal.app y ejecutar poetry run seguido del script
            subprocess.Popen(['open', '-a', 'Terminal.app', 'bash', '-c', command_to_run])

        else:
            wx.CallAfter(wx.MessageBox, "Operating system not supported for separate terminal execution.", "Error", wx.OK | wx.ICON_ERROR)

    def get_camera_data(self, camera_name):
        if camera_name.startswith("Camera "):
            return {'link': camera_name.split(' ')[-1]}

        try:
            with open(self.resource_path('cameras.json'), 'r') as f:
                cameras = json.load(f)
                for cam in cameras:
                    if cam['name'] == camera_name:
                        return cam
        except FileNotFoundError:
            pass
        return None

    def on_add_camera(self, event):
        dialog = CameraDialog(self)
        if dialog.ShowModal() == wx.ID_OK:
            camera_data = dialog.get_camera_data()
            self.save_camera(camera_data)
            self.refresh_camera_list()
        dialog.Destroy()

    def save_camera(self, camera_data):
        try:
            with open(self.resource_path('cameras.json'), 'r') as f:
                cameras = json.load(f)
        except FileNotFoundError:
            cameras = []
        
        cameras.append(camera_data)

        with open(self.resource_path('cameras.json'), 'w') as f:
            json.dump(cameras, f, indent=4)

    def on_delete_camera(self, event):
        selected_camera = self.camera_choice.GetStringSelection()
        if not selected_camera:
            wx.MessageBox("Please select a camera to delete.", "Error", wx.OK | wx.ICON_ERROR)
            return

        try:
            with open(self.resource_path('cameras.json'), 'r') as f:
                cameras = json.load(f)
        except FileNotFoundError:
            cameras = []

        cameras = [cam for cam in cameras if cam['name'] != selected_camera]

        with open(self.resource_path('cameras.json'), 'w') as f:
            json.dump(cameras, f, indent=4)

        self.refresh_camera_list()

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame(None, "SICOFVE")
    app.MainLoop()
