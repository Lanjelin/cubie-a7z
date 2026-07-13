#!/usr/bin/env python3

import argparse
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path
from time import sleep

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('EPD_PLATFORM', 'cubie')

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13_V4

# started by /lib/systemd/system/time.service
# keep this script together with the bundled waveshare_epd/ directory

# Local policy/config that is likely to vary between machines.
HIDDEN_PORTS = {
    port for port
    in os.environ.get('SCREEN_TIME_HIDDEN_PORTS', '111,5355').replace(',', ' ').split()
    if port
}
TUNNEL_REMOTE = os.environ.get('SCREEN_TIME_TUNNEL_REMOTE', '').strip()


class Screen:
    @staticmethod
    def _text_bbox(font, text):
        return font.getbbox(text)

    @classmethod
    def _text_size(cls, font, text):
        left, top, right, bottom = cls._text_bbox(font, text)
        return right - left, bottom - top

    @staticmethod
    def _run(command):
        return subprocess.getoutput(command).strip()

    def __init__(self):
        self.saved_time = '00:00'
        self.saved_ssid = 'Connecting...'
        self.saved_signal = '--%'
        self.saved_ip = ''
        self.saved_face = '(ᵔ◡◡ᵔ)'
        self.saved_temp = '--°C'
        self.saved_fan = '--%'
        self.saved_uptime = '--'
        self.saved_disk = '--'
        self.saved_ram = '--'
        self.ports = ''
        self.push_update = True
        self.partial_ready = False
        self.partial_updates = 0
        self.full_refresh_every = 25

        self.name = self._run('hostname') or 'cubie'

        self.epd = epd2in13_V4.EPD()
        self.canvas_width = self.epd.height
        self.canvas_height = self.epd.width
        self.margin_x = 2
        self.margin_y = 2

        self.font_small_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        self.font_face_path = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
        try:
            self.font_small = ImageFont.truetype(self.font_small_path, 10)
            self.font_face = ImageFont.truetype(self.font_face_path, 40)
        except OSError:
            self.font_small = ImageFont.load_default()
            self.font_face = ImageFont.load_default()

        self.faces = [
            '( ⚆_⚆)', '(☉_☉ )', '( ◕‿◕)', '(◕‿◕ )', '(⇀‿‿↼)', '(≖‿‿≖)',
            '(◕‿‿◕)', '(-__-)', '(°▃▃°)', '(⌐■_■)', '(•‿‿•)', '(^‿‿^)',
            '(ᵔ◡◡ᵔ)', '(☼‿‿☼)', '(≖__≖)', '(✜‿‿✜)', '(ب__ب)', '(╥☁╥ )',
            "(-_-')", '(♥‿‿♥)', '(☓‿‿☓)', '(#__#)', '(1__0)', '(1__1)', '(0__1)'
        ]

        self.loc_top_left = (0, 0)
        self.loc_top_left_sub = (0, 0)
        self.loc_top_center = (0, 0)
        self.loc_top_right = (0, 0)
        self.loc_top_right_sub = (0, 0)
        self.loc_top_right_sub2 = (0, 0)
        self.loc_center = (0, 0)
        self.loc_bot_left = (0, 0)
        self.loc_bot_left_sub = (0, 0)
        self.loc_bot_right = (0, 0)
        self.loc_bot_right_sub = (0, 0)

    def _fit_text(self, text, font, max_width):
        if self._text_size(font, text)[0] <= max_width:
            return text
        if max_width <= self._text_size(font, '...')[0]:
            return ''
        trimmed = text
        while trimmed:
            candidate = trimmed + '...'
            if self._text_size(font, candidate)[0] <= max_width:
                return candidate
            trimmed = trimmed[:-1]
        return ''

    def init_display(self):
        self.epd.init()
        self.epd.Clear(0xFF)

    def close(self):
        self.epd.sleep()

    def updateTime(self):
        current = self._run('date +%H:%M')
        if current != self.saved_time:
            self.push_update = True
        self.saved_time = current

    def updateThermals(self):
        cpu_temps = []
        for zone in Path('/sys/class/thermal').glob('thermal_zone*'):
            try:
                zone_type = (zone / 'type').read_text().strip()
                if zone_type not in {'cpub_thermal_zone', 'cpul_thermal_zone'}:
                    continue
                temp_c = int((zone / 'temp').read_text().strip()) / 1000
                cpu_temps.append(temp_c)
            except Exception:
                pass

        if cpu_temps:
            temp_text = f'{max(cpu_temps):.0f}°C'
        else:
            temp_text = '--°C'

        pwm_percent = None
        for pwm_path in sorted(Path('/sys/class/hwmon').glob('hwmon*/pwm1')):
            try:
                pwm_value = int(pwm_path.read_text().strip())
                pwm_percent = round((pwm_value / 255) * 100)
                break
            except Exception:
                pass

        fan_text = f'{pwm_percent}%'
        if pwm_percent is None:
            fan_text = '--%'

        if temp_text != self.saved_temp or fan_text != self.saved_fan:
            self.push_update = True
        self.saved_temp = temp_text
        self.saved_fan = fan_text

    def updateSSID(self):
        ssid = self._run("""nmcli -t -f ACTIVE,SSID dev wifi | awk -F: '$1==\"yes\" {print $2; exit}'""")
        if not ssid:
            ssid = self._run("""nmcli -t -f GENERAL.CONNECTION device show wlan0 | awk -F': ' '$1==\"GENERAL.CONNECTION\" {print $2; exit}'""")
        if not ssid or ssid == '--':
            ssid = 'Connecting...'
        if ssid != self.saved_ssid:
            self.push_update = True
        self.saved_ssid = ssid

    def updateWiFiSignal(self):
        signal = self._run("""nmcli -t -f ACTIVE,SIGNAL dev wifi | awk -F: '$1==\"yes\" {print $2; exit}'""")
        signal_text = '--%'
        if signal:
            try:
                signal_value = int(signal)
                signal_value = max(0, min(100, int(round(signal_value / 5) * 5)))
                signal_text = f'{signal_value}%'
            except ValueError:
                pass
        if signal_text != self.saved_signal:
            self.push_update = True
        self.saved_signal = signal_text

    def updateIP(self):
        ip = self._run("nmcli -t -f IP4.ADDRESS device show wlan0 | cut -d: -f2- | head -n 1")
        if ip:
            ip = ip.split('/')[0]
        if not ip:
            ip = self._run("ip -4 -o addr show dev wlan0 | awk '{print $4}' | cut -d/ -f1 | head -n 1")
        tunnel_arrow = ''
        if TUNNEL_REMOTE:
            tunnel = self._run(f"ss -tn state established '( dst {TUNNEL_REMOTE} )' | tail -n +2")
            tunnel_arrow = '▲' if tunnel else '▼'
        display_ip = f'{tunnel_arrow} {ip}'.strip()
        if display_ip != self.saved_ip:
            self.push_update = True
        self.saved_ip = display_ip

    def getListenPorts(self):
        ports = self._run("ss -lntH | awk '$4 ~ /^0\\.0\\.0\\.0:/ {print $4}' | sed 's/.*://' | sort -n | uniq").splitlines()
        ports = [port for port in ports if port and port not in HIDDEN_PORTS]
        ports_string = ','.join(ports)
        if ports_string != self.ports:
            self.push_update = True
        self.ports = ports_string

    def updateSystemStats(self):
        uptime_text = '--'
        try:
            uptime_seconds = int(float(Path('/proc/uptime').read_text().split()[0]))
            days, rem = divmod(uptime_seconds, 86400)
            hours, rem = divmod(rem, 3600)
            minutes, _ = divmod(rem, 60)
            if days:
                uptime_text = f'{days}d {hours}h'
            elif hours:
                uptime_text = f'{hours}h {minutes}m'
            else:
                uptime_text = f'{minutes}m'
        except Exception:
            pass

        disk_text = '--'
        try:
            free_bytes = shutil.disk_usage('/').free
            free_gib = free_bytes / (1024 ** 3)
            if free_gib >= 10:
                disk_text = f'{free_gib:.0f}G'
            else:
                disk_text = f'{free_gib:.1f}G'
        except Exception:
            pass

        ram_text = '--'
        try:
            meminfo = {}
            for line in Path('/proc/meminfo').read_text().splitlines():
                key, value = line.split(':', 1)
                meminfo[key] = int(value.strip().split()[0])
            total_kib = meminfo.get('MemTotal', 0)
            available_kib = meminfo.get('MemAvailable', 0)
            used_kib = max(0, total_kib - available_kib)
            if total_kib > 0:
                ram_text = f'{(used_kib / total_kib) * 100:.0f}%'
        except Exception:
            pass

        if uptime_text != self.saved_uptime or disk_text != self.saved_disk or ram_text != self.saved_ram:
            self.push_update = True
        self.saved_uptime = uptime_text
        self.saved_disk = disk_text
        self.saved_ram = ram_text

    def updatePositions(self):
        face_left, face_top, face_right, face_bottom = self._text_bbox(self.font_face, self.saved_face)
        face_w = face_right - face_left
        face_h = face_bottom - face_top
        self.loc_center = (
            int((self.canvas_width - face_w) / 2) - face_left,
            int((self.canvas_height - face_h) / 2) - face_top - 2,
        )

        _, time_top, time_right, time_bottom = self._text_bbox(self.font_small, self.saved_time)
        _, stats_top, stats_right, stats_bottom = self._text_bbox(self.font_small, f'{self.saved_temp} {self.saved_fan}')
        _, uptime_top, _, uptime_bottom = self._text_bbox(self.font_small, self.saved_uptime)
        _, disk_top, disk_right, disk_bottom = self._text_bbox(self.font_small, self.saved_disk)
        _, ram_top, ram_right, ram_bottom = self._text_bbox(self.font_small, self.saved_ram)
        _, signal_top, _, signal_bottom = self._text_bbox(self.font_small, self.saved_signal)
        _, ports_top, ports_right, ports_bottom = self._text_bbox(self.font_small, self.ports)
        _, _, ip_right, ip_bottom = self._text_bbox(self.font_small, self.saved_ip)
        _, _, _, ssid_bottom = self._text_bbox(self.font_small, self.saved_ssid)

        top_gap = 7
        bottom_y = self.canvas_height - max(ip_bottom, ssid_bottom) - self.margin_y
        bottom_left_second_y = bottom_y - (signal_bottom - signal_top) - 2
        bottom_right_second_y = bottom_y - (ports_bottom - ports_top) - 2
        top_y = self.margin_y - time_top
        top_second_y = top_y + (time_bottom - time_top) + top_gap

        self.loc_top_left = (self.margin_x, top_y)
        self.loc_top_left_sub = (self.margin_x, top_second_y - uptime_top)
        self.loc_top_center = (int((self.canvas_width - time_right) / 2), top_y)
        self.loc_top_right = (self.canvas_width - stats_right - self.margin_x, top_y)
        self.loc_top_right_sub = (self.canvas_width - disk_right - self.margin_x, top_second_y - disk_top)
        self.loc_top_right_sub2 = (self.canvas_width - ram_right - self.margin_x, top_second_y + (disk_bottom - disk_top) + 3 - ram_top)
        self.loc_bot_left = (self.margin_x, bottom_y)
        self.loc_bot_left_sub = (self.margin_x, bottom_left_second_y - signal_top)
        self.loc_bot_right = (self.canvas_width - ip_right - self.margin_x, bottom_y)
        self.loc_bot_right_sub = (self.canvas_width - ports_right - self.margin_x, bottom_right_second_y - ports_top)

    def makeFace(self):
        self.saved_face = random.choice(self.faces)

    def build_image(self):
        image = Image.new('1', (self.canvas_width, self.canvas_height), 255)
        draw = ImageDraw.Draw(image)

        top_center_x = self.loc_top_center[0]
        bot_right_x = self.loc_bot_right[0]
        top_left_text = self._fit_text(self.name, self.font_small, max(0, top_center_x - self.margin_x * 2))
        top_left_sub_text = self._fit_text(self.saved_uptime, self.font_small, max(0, top_center_x - self.margin_x * 2))
        bot_left_signal = self._fit_text(self.saved_signal, self.font_small, max(0, bot_right_x - self.margin_x * 2))
        bot_left_text = self._fit_text(self.saved_ssid, self.font_small, max(0, bot_right_x - self.margin_x * 2))
        bot_right_ports = self._fit_text(self.ports, self.font_small, max(0, self.canvas_width - self.margin_x * 2))

        draw.text(self.loc_top_left, top_left_text, fill=0, font=self.font_small)
        draw.text(self.loc_top_left_sub, top_left_sub_text, fill=0, font=self.font_small)
        draw.text(self.loc_center, self.saved_face, fill=0, font=self.font_face)
        draw.text(self.loc_top_center, self.saved_time, fill=0, font=self.font_small)
        draw.text(self.loc_top_right, f'{self.saved_temp} {self.saved_fan}', fill=0, font=self.font_small)
        draw.text(self.loc_top_right_sub, self.saved_disk, fill=0, font=self.font_small)
        draw.text(self.loc_top_right_sub2, self.saved_ram, fill=0, font=self.font_small)
        draw.text(self.loc_bot_left_sub, bot_left_signal, fill=0, font=self.font_small)
        draw.text(self.loc_bot_left, bot_left_text, fill=0, font=self.font_small)
        draw.text(self.loc_bot_right_sub, bot_right_ports, fill=0, font=self.font_small)
        draw.text(self.loc_bot_right, self.saved_ip, fill=0, font=self.font_small)
        return image

    def write(self):
        image = self.build_image()
        buffer = self.epd.getbuffer(image)

        if not self.partial_ready:
            self.epd.displayPartBaseImage(buffer)
            self.partial_ready = True
            self.partial_updates = 0
            return

        if self.partial_updates >= self.full_refresh_every:
            self.epd.display(buffer)
            self.epd.displayPartBaseImage(buffer)
            self.partial_updates = 0
            return

        self.epd.displayPartial(buffer)
        self.partial_updates += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=10)
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()

    screen = Screen()
    screen.init_display()

    try:
        while True:
            screen.updateTime()
            screen.updateSSID()
            screen.updateWiFiSignal()
            screen.updateIP()
            screen.updateThermals()
            screen.updateSystemStats()
            screen.getListenPorts()

            if screen.push_update:
                screen.makeFace()
                screen.updatePositions()
                screen.write()
                screen.push_update = False

            if args.once:
                break
            sleep(args.interval)
    finally:
        screen.close()


if __name__ == '__main__':
    main()
