import wx
import wx.adv
import psycopg2
import csv

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(1080, 1000))

        panel = wx.Panel(self)

        # Lista de valores para las listas desplegables
        values_to_select = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat']
        values_to_select2 = ['going up', 'going down']

        # Crear las listas desplegables para que el usuario seleccione los valores
        self.choice1 = wx.Choice(panel, choices=values_to_select)
        self.choice2 = wx.Choice(panel, choices=values_to_select2)
        self.choice3 = wx.Choice(panel)

        # Llenar la lista de cámaras desde la base de datos
        self.load_cameras()

        # Agregar controles de fecha
        self.calendar_start = wx.adv.CalendarCtrl(panel)
        self.calendar_end = wx.adv.CalendarCtrl(panel)

        self.btn_query = wx.Button(panel, label="Consultar")
        self.btn_query.Bind(wx.EVT_BUTTON, self.on_query)

        # Botón para generar CSV
        self.btn_csv = wx.Button(panel, label="Exportar a CSV")
        self.btn_csv.Bind(wx.EVT_BUTTON, self.on_export_csv)
        self.btn_csv.Disable()  # Deshabilitar el botón inicialmente

        self.text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE)

        # Crear un layout con sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(panel, label="Seleccione la clasificación a consultar:"), flag=wx.EXPAND | wx.ALL, border=10)
        sizer.Add(self.choice1, flag=wx.EXPAND | wx.ALL, border=10)
        sizer.Add(wx.StaticText(panel, label="Seleccione la direccion a consultar:"), flag=wx.EXPAND | wx.ALL,
                  border=10)
        sizer.Add(self.choice2, flag=wx.EXPAND | wx.ALL, border=10)
        sizer.Add(wx.StaticText(panel, label="Seleccione la cámara a consultar:"), flag=wx.EXPAND | wx.ALL, border=10)
        sizer.Add(self.choice3, flag=wx.EXPAND | wx.ALL, border=10)
        sizer.Add(wx.StaticText(panel, label="Seleccione las fechas de inicio y fin:"), flag=wx.EXPAND | wx.ALL, border=10)
        sizer.Add(self.calendar_start, flag=wx.EXPAND | wx.ALL, border=10)
        sizer.Add(self.calendar_end, flag=wx.EXPAND | wx.ALL, border=10)
        sizer.Add(self.btn_query, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        sizer.Add(self.btn_csv, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        sizer.Add(self.text_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        panel.SetSizer(sizer)

        self.results = []  # Lista para almacenar los resultados de la consulta

        self.Center()
        self.Show()

    def load_cameras(self):
        """Load available cameras from the database and populate the choice control."""
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="1606", port="5432")
        cur = conn.cursor()

        cur.execute("SELECT DISTINCT camara FROM camera;")
        cameras = cur.fetchall()

        # Clear existing items and add new camera options
        self.choice3.Clear()
        self.choice3.Append("All Cameras")  # Default option

        for cam in cameras:
            self.choice3.Append(cam[0])

        cur.close()
        conn.close()

    def on_query(self, event):
        # Obtener los valores seleccionados por el usuario
        value1 = self.choice1.GetString(self.choice1.GetSelection())
        value2 = self.choice2.GetString(self.choice2.GetSelection())
        value3 = self.choice3.GetString(self.choice3.GetSelection())

        # Verificar si no se ha seleccionado ningún valor en los cuadros de lista desplegable
        if value1 and value2 and value3 == 'All Cameras':
            # Consulta SQL para mostrar todos los datos
            query = "SELECT * FROM camera;"
        else:
            # Obtener las fechas seleccionadas por el usuario
            start_date = self.calendar_start.GetDate()
            end_date = self.calendar_end.GetDate()

            # Convertir las fechas a formato de cadena YYYY-MM-DD
            start_date_str = start_date.Format("%Y-%m-%d") + " 00:00:00"
            end_date_str = end_date.Format("%Y-%m-%d") + " 23:59:59"

            # Construir la consulta SQL con los valores y fechas seleccionados
            query = f"SELECT * FROM camera WHERE clase = '{value1}' and way = '{value2}' AND fecha BETWEEN '{start_date_str}' AND '{end_date_str}' AND camara = '{value3}';"

        # Realizar la conexión a la base de datos y ejecutar la consulta
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="1606", port="5432")
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        self.results = rows  # Guardar los resultados para exportación

        # Calcular la suma de los resultados
        suma = len(rows)

        # Extraer la velocidad de cada tupla y convertirla a tipo float
        velocidades = [float(dato[2]) for dato in rows]
        if velocidades == []:
            suma_velocidades = 0
            maximo_velocidades = 0
            minimo_velocidades = 0
            promedio_velocidades = 0
        else:
            suma_velocidades = sum(velocidades)
            maximo_velocidades = max(velocidades)
            minimo_velocidades = min(velocidades)
            promedio_velocidades = suma_velocidades / len(velocidades)

        # Mostrar los resultados y la suma en el TextCtrl
        self.text_ctrl.SetValue("")
        for row in rows:
            for value in row:
                self.text_ctrl.AppendText(str(value) + " ")
            self.text_ctrl.AppendText("\n")
        self.text_ctrl.AppendText(f"\nSuma total: {suma}")
        self.text_ctrl.AppendText(f"\nVelocidad máxima: {maximo_velocidades} km/h")
        self.text_ctrl.AppendText(f"\nVelocidad mínima: {minimo_velocidades} km/h")
        self.text_ctrl.AppendText(f"\nVelocidad promedio: {promedio_velocidades} km/h")

        # Habilitar el botón para exportar a CSV si hay resultados
        if self.results:
            self.btn_csv.Enable()

        cur.close()
        conn.close()

    def on_export_csv(self, event):
        """Export the current query results to a CSV file."""
        if not self.results:
            return  # Si no hay resultados, no hacer nada

        # Abrir un diálogo de guardado para elegir el nombre del archivo CSV
        with wx.FileDialog(self, "Guardar archivo CSV", wildcard="CSV files (*.csv)|*.csv",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # El usuario canceló el guardado

            # Obtener la ruta completa del archivo
            path = fileDialog.GetPath()

            # Crear el archivo CSV y escribir los resultados
            with open(path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Escribir encabezados de las columnas (ajustar según tus columnas)
                writer.writerow(['ID', 'clase', 'velocidad', 'way', 'fecha','Camara'])

                # Escribir los datos
                for row in self.results:
                    writer.writerow(row)

        wx.MessageBox(f"Archivo CSV guardado correctamente en {path}", "Exportación exitosa", wx.OK | wx.ICON_INFORMATION)

if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame(None, title="Sistema de Visualización de Datos de Tránsito (SiViT)")
    app.MainLoop()
