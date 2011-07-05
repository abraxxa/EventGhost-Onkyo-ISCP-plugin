import eg
import socket

eg.RegisterPlugin(
    name = "Onkyo ISCP",
    author = "Alexander Hartmaier",
    version = "0.04",
    kind = "external",
    description = "Controls any Onkyo Receiver which supports the ISCP protocol."
)

class Text:
    tcpBox = "TCP/IP Settings"
    ip = "IP:"
    port = "Port:"
    timeout = "Timeout:"
    class SendCommand:
        commandBox = "Command Settings"
        command = "Code to send:"

class OnkyoISCP(eg.PluginBase):
    text = Text

    def __init__(self):
        self.AddAction(SendCommand)

    def __start__(self, ip, port, timeout):
        self.ip = ip
        self.port = int(port)
        self.timeout = float(timeout)
        self.Connect()

    def __stop__(self):
    	self.socket.close()

    def Connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(self.timeout)
        self.socket = s

        ip = self.ip
        port = self.port
        try:
            s.connect((ip, port))
        except Exception as e:
            print "Failed to connect to " + ip + ":" + str(port), e
        else:
            print "Connected to " + ip + ":" + str(port)
        

    def Configure(self, ip="", port="60128", timeout="1"):
        text = self.text
        panel = eg.ConfigPanel()
        wx_ip = panel.TextCtrl(ip)
        wx_port = panel.SpinIntCtrl(port, max=65535)
        wx_timeout = panel.TextCtrl(timeout)

        st_ip = panel.StaticText(text.ip)
        st_port = panel.StaticText(text.port)
        st_timeout = panel.StaticText(text.timeout)
        eg.EqualizeWidths((st_ip, st_port, st_timeout))

        tcpBox = panel.BoxedGroup(
            text.tcpBox,
            (st_ip, wx_ip),
            (st_port, wx_port),
            (st_timeout, wx_timeout),
        )

        panel.sizer.Add(tcpBox, 0, wx.EXPAND)

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
        try:
            self.plugin.socket.sendall(line)
            #data = s.recv(80)
        except socket.error, msg:
            print "Error sending command, retrying", msg
            # try to reopen the socket on error
            # happens if no commands are sent for a long time
            # and the tcp connection got closed because
            # e.g. the receiver was switched off and on again
            self.plugin.Connect()
            try:
                self.plugin.socket.sendall(line)
            except socket.error, msg:
                print "Error sending command", msg

    def Configure(self, Command=""):
        panel = eg.ConfigPanel()
        text = self.text
        st_command = panel.StaticText(text.command)
        wx_command = panel.TextCtrl(Command)

        commandBox = panel.BoxedGroup(
            text.commandBox,
            (st_command, wx_command)
        )

        panel.sizer.Add(commandBox, 0, wx.EXPAND)

        while panel.Affirmed():
            panel.SetResult(wx_command.GetValue())
