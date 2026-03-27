"""Tiny Wi-Fi AP + HTTP remote controller for ESP32 MicroPython."""

import socket
import network


class WifiRemoteController:
    def __init__(self, motor_driver, line_follower, wifi_cfg):
        self.motor = motor_driver
        self.line_follower = line_follower
        self.wifi_cfg = wifi_cfg

        self.mode = "auto"
        self.server = None

    def start(self):
        self._start_ap()
        self._start_server()

    def _start_ap(self):
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(
            essid=self.wifi_cfg["ssid"],
            password=self.wifi_cfg["password"],
            authmode=self.wifi_cfg.get("authmode", 3),
            channel=self.wifi_cfg.get("channel", 6),
        )

        while not ap.active():
            pass

        ip = ap.ifconfig()[0]
        print("[WIFI] AP started")
        print("[WIFI] SSID:", self.wifi_cfg["ssid"])
        print("[WIFI] IP:", ip)

    def _start_server(self):
        addr = socket.getaddrinfo("0.0.0.0", self.wifi_cfg.get("port", 80))[0][-1]
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(addr)
        self.server.listen(2)
        self.server.setblocking(False)
        print("[WIFI] HTTP server listening on port", self.wifi_cfg.get("port", 80))

    def tick(self):
        if not self.server:
            return
        try:
            client, _ = self.server.accept()
        except OSError:
            return

        try:
            request = client.recv(1024)
            if not request:
                return

            request_line = request.decode("utf-8", "ignore").split("\r\n")[0]
            path = "/"
            parts = request_line.split(" ")
            if len(parts) >= 2:
                path = parts[1]

            if path.startswith("/action?"):
                self._handle_action(path)
                self._send_json(client, '{"ok": true, "mode": "%s"}' % self.mode)
            else:
                html = self._load_page()
                self._send_html(client, html)
        except Exception as exc:
            self._send_json(client, '{"ok": false, "error": "%s"}' % str(exc))
        finally:
            client.close()

    def _handle_action(self, path):
        cmd = ""
        if "cmd=" in path:
            cmd = path.split("cmd=", 1)[1].split("&", 1)[0]

        if cmd == "mode_auto":
            self.mode = "auto"
            self.motor.stop()
            return

        if cmd == "mode_manual":
            self.mode = "manual"
            self.motor.stop()
            return

        if self.mode != "manual":
            # Safety lock: movement commands only accepted in manual mode.
            return

        speed = self.line_follower.tuning["base_speed"]
        if cmd == "forward":
            self.motor.forward(speed)
        elif cmd == "backward":
            self.motor.backward(speed)
        elif cmd == "left":
            self.motor.turn_left(speed, pivot=True)
        elif cmd == "right":
            self.motor.turn_right(speed, pivot=True)
        else:
            self.motor.stop()

    def _load_page(self):
        try:
            with open("web/index.html", "r") as file_obj:
                return file_obj.read()
        except OSError:
            return "<html><body><h1>Missing web/index.html</h1></body></html>"

    def _send_html(self, client, content):
        client.send("HTTP/1.1 200 OK\r\n")
        client.send("Content-Type: text/html\r\n")
        client.send("Connection: close\r\n\r\n")
        client.send(content)

    def _send_json(self, client, content):
        client.send("HTTP/1.1 200 OK\r\n")
        client.send("Content-Type: application/json\r\n")
        client.send("Connection: close\r\n\r\n")
        client.send(content)
