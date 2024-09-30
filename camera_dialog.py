import wx

class CameraDialog(wx.Dialog):
    def __init__(self, parent):
        super(CameraDialog, self).__init__(parent, title="Agregar Cámara", size=(400, 300))

        panel = wx.Panel(self)

        # Controles de entrada
        self.name_text = wx.TextCtrl(panel, size=(300, -1))
        self.link_text = wx.TextCtrl(panel, size=(300, -1))

        # Botón para guardar
        self.btn_save = wx.Button(panel, label="Save")
        self.btn_save.Bind(wx.EVT_BUTTON, self.on_save)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(panel, label="Nombre de la cámara:"), flag=wx.EXPAND | wx.ALL, border=10)
        sizer.Add(self.name_text, flag=wx.EXPAND | wx.ALL, border=10)
        sizer.Add(wx.StaticText(panel, label="Link de la cámara:"), flag=wx.EXPAND | wx.ALL, border=10)
        sizer.Add(self.link_text, flag=wx.EXPAND | wx.ALL, border=10)
        sizer.Add(self.btn_save, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        panel.SetSizer(sizer)

        # Propiedades para guardar el estado
        self.saved = False
        self.camera_data = {}

    def on_save(self, event):
        name = self.name_text.GetValue()
        link = self.link_text.GetValue()

        if not name or not link:
            wx.MessageBox("All fields are required.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Guardar los datos
        self.camera_data = {'name': name, 'link': link}
        self.saved = True
        self.EndModal(wx.ID_OK)

    def get_camera_data(self):
        return self.camera_data

# Ejemplo de cómo usar el diálogo
if __name__ == "__main__":
    app = wx.App(False)
    dialog = CameraDialog(None)
    if dialog.ShowModal() == wx.ID_OK:
        camera_data = dialog.get_camera_data()
        print("Cámara guardada:", camera_data)
    dialog.Destroy()
    app.MainLoop()
