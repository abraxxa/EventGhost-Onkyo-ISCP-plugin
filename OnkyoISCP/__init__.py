import eg
import socket

eg.RegisterPlugin(
    name = "Onkyo ISCP",
    author = "Alexander Hartmaier",
    version = "0.03",
    kind = "external",
    description = "Controls any Onkyo Receiver which supports the ISCP protocol."
)

class OnkyoISCP(eg.PluginBase):

    def __init__(self):
        self.AddAction(SendCommand)

    def __start__(self, ip, port, timeout):
        self.ip = ip
        self.port = int(port)
        self.timeout = float(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(self.timeout)
        self.socket = s
        self.Connect()

    def __stop__(self):
    	self.socket.close()

    def Connect(self):
        s = self.socket
        ip = self.ip
        port = self.port
        try:
	        s.connect((ip, port))
        except:
            print "OnkyoISCP failed to connect to " + ip + ":" + str(port)
        else:
            print "OnkyoISCP connected to " + ip + ":" + str(port)
        

    def Configure(self, ip="", port="60128", timeout="1"):
        panel = eg.ConfigPanel()
        wx_ip = wx.TextCtrl(panel, -1, ip)
        wx_port = wx.TextCtrl(panel, -1, port)
	wx_timeout = wx.TextCtrl(panel, -1, timeout)
        panel.sizer.Add(wx.StaticText(panel, -1, "IP address of Onkyo receiver"))
        panel.sizer.Add(wx_ip)
        panel.sizer.Add(wx_port)
        panel.sizer.Add(wx_timeout)
        while panel.Affirmed():
            panel.SetResult(
                wx_ip.GetValue(),
		wx_port.GetValue(),
		wx_timeout.GetValue(),
            )

class SendCommand(eg.ActionBase):

    def __call__(self, Command):
        length = len(Command) + 1
        code = chr(length)
        line = "ISCP\x00\x00\x00\x10\x00\x00\x00" + code + "\x01\x00\x00\x00!1" + Command + "\x0D"
    	s = self.plugin.socket
        try:
            s.send(line)
	    #data = s.recv(80)
        except socket.error, msg:
            # try to reopen the socket on error
            # happens if no commands are sent for a long time
            try:
		self.plugin.Connect()
                s.send(line)
            except socket.error, msg:
                print "Error " + str(msg)

    def Configure(self, Command=""):
        panel = eg.ConfigPanel()
        textControl = wx.TextCtrl(panel, -1, Command)
        panel.sizer.Add(textControl)
        while panel.Affirmed():
            panel.SetResult(textControl.GetValue())
