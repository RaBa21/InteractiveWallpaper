import urllib.request
import time
from datetime import datetime
import ctypes
import os
import sys
import PIL
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pynput import mouse


class Wallpaper:
    
    def __init__(self):
        self.SCREENSIZE = (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
        self.ICONSIZE = 60
        self.ICONNUM = len(os.listdir("src/icons"))
        l = self.SCREENSIZE[0] / 2 - 350
        u = self.SCREENSIZE[0] / 2 + 350
        self.ICONPOS = lambda idx: (int([l + x * (u - l) / self.ICONNUM for x in range(self.ICONNUM)][idx] + self.ICONSIZE / 2), self.SCREENSIZE[1] - 110)
        self.ICONPOSLIST = [self.ICONPOS(i) for i in range(self.ICONNUM)]
        
        self.group = 0
        self.CACHESETTINGS = [60, 300, 120, 86400]
        self.cache = [[0,{}], [0,{}], [0,{}], [0,{}]]
    
    def get_data(self):
        DATA = {}

        get_interval = lambda currt, intervals: currt // intervals
        if get_interval(self.cache[self.group][0], self.CACHESETTINGS[self.group]) == get_interval(time.time(), self.CACHESETTINGS[self.group]):
            DATA = self.cache[self.group][1]
            return DATA

        #################
        # DATE AND TIME #
        #################
        if self.group == 0:
            month = [
                "jan", "febr", "márc", "ápr", "máj", "jún", "júl", "aug", "szept", "okt", "nov", "dec"
            ][int(time.strftime("%m")) - 1]
            DATA["date"] = time.strftime(f"%Y. {month}. %d.")
            day = [
                "hétfő", "kedd", "szerda", "csütörtök", "péntek", "szombat", "vasárnap"
            ][int(time.strftime("%w")) - 1]
            DATA["weekday"] = day.upper()
            DATA["time"] = time.strftime("%H:%M")

        ###########
        # WEATHER #
        ###########
        if self.group == 1:
            deg = "-"
            status = "-"
            wind = "-"
            try:
                url = 'https://weather.com/hu-HU/weather/today/l/e4ccdf2a797603d9e6013811f3976ac6a912e4826ee38b710aeaa79e5e54af8a'
                data = urllib.request.urlopen(url).read().decode('utf-8')

                degpattern = '<span data-testid="TemperatureValue" class="CurrentConditions--tempValue--MHmYY">'
                deg = data[data.index(degpattern) + len(degpattern):].split('<')[0]
                statuspattern = '<div data-testid="wxPhrase" class="CurrentConditions--phraseValue--mZC_p">'
                status = data[data.index(statuspattern) + len(statuspattern):].split('<')[0]
                windpattern = "</svg></span><span>"
                wind = data[data.index(windpattern) + len(windpattern):].split('<')[0]
            except: pass

            DATA["temperature"] = deg + "°"
            DATA["weatherstatus"] = status
            DATA["wind"] = wind + " km/h"

        #########
        # MONEY #
        #########
        if self.group == 2:
            try:
                url_eur = "https://www.exchangerates.org.uk/EUR-HUF-exchange-rate-history.html"
                url_usd = "https://www.exchangerates.org.uk/USD-HUF-exchange-rate-history.html"
                symbols = {"eur": "€", "usd": "$"}
                for m in ["eur", "usd"]:
                    data = urllib.request.urlopen(eval(f"url_{m}")).read().decode('utf-8')
                    pattern = f'<td>1 {m.upper()} = '

                    money = []
                    idx = 0
                    for i in range(len(data)):
                        if idx == 30:
                            break
                        if data[i:i + len(pattern)] == pattern:
                            money.append(float(data[i + len(pattern):i + len(pattern) + 6]))
                            idx += 1

                    money.reverse()
                    DATA[m] = money

                url_eur = "https://www.investing.com/currencies/eur-huf-historical-data"
                url_usd = "https://www.investing.com/currencies/usd-huf-historical-data"
                symbols = {"eur": "€", "usd": "$"}
                for m in ["eur", "usd"]:
                    req = urllib.request.Request(eval(f"url_{m}"), headers={'User-Agent': 'Mozilla/5.0'})
                    data = urllib.request.urlopen(req).read().decode('utf-8')
                    pattern = '<span class="text-2xl" data-test="instrument-price-last">'
                    DATA[f"{m}text"] = f"1 {symbols[m]} = {data[data.index(pattern) + len(pattern):].split('<')[0]} Ft"
            except:
                DATA["eur"] = []
                DATA["usd"] = []
                DATA["eurtext"] = "-"
                DATA["usdtext"] = "-"

        ###########
        # NAMEDAY #
        ###########
        if self.group == 3:
            day_of_yr = datetime.now().timetuple().tm_yday
            year = int(time.strftime("%Y"))
            if not (year%400==0 if year%100==0 else year%4==0):
                if day_of_yr >= 55:
                    day_of_yr += 1
            with open("src/namedays.txt", "r", encoding="utf-8") as file:
                name = list(file)[day_of_yr-1].strip()
            DATA["nametitle"] = "A mai névnap(ok):"
            DATA["name"] = name



        self.cache[self.group][0] = time.time()
        self.cache[self.group][1] = DATA
        return DATA

    def plot(self, stats):
        upper = int(max(stats) // 5 * 5 + 5) if int(max(stats)) % 5 != 0 else (int(max(stats)))
        lower = int(min(stats) // 5 * 5)
        scale = (190 - 10) / (upper - lower)
        chart_starts_x = 40

        img = PIL.Image.new(mode="RGB", size=(300, 200), color=(0, 0, 0))
        drawing = ImageDraw.Draw(img)

        font = ImageFont.truetype('src/Font.ttf', 15)
        drawing.text((chart_starts_x, 9), str(upper) + " -", font=font, fill=(255, 255, 255), anchor="rm")
        drawing.text((chart_starts_x, 191), str(lower) + " -", font=font, fill=(255, 255, 255), anchor="rm")

        lines = []
        for num, i in enumerate(stats):
            lines.append(chart_starts_x + 2 + num * (300 - chart_starts_x - 2) / (len(stats) - 1))
            lines.append(200 - 10 - ((i - lower) * scale))
        drawing.line(lines, fill=((150, 50, 50) if stats[-2] < stats[-1] else ((50, 150, 50))), width=1)
        drawing.line((chart_starts_x, 0, chart_starts_x, 200), fill=(150, 150, 150), width=3)

        return img

    def create_bgimage(self):
        screensize = self.SCREENSIZE
        rect = (
            screensize[0] / 2 - 500,  # x1
            screensize[1] - 600,  # y1
            screensize[0] / 2 + 500,  # x2
            screensize[1] - 120  # y2
        )

        img = PIL.Image.new(mode="RGBA", size=screensize, color=(0, 0, 0))
        drawing = ImageDraw.Draw(img)
        drawing.rectangle(rect, outline=(150, 150, 150), width=8)

        DATA = self.get_data()

        INIT = {  # offsetFromBoxMiddle, size, color, group(0=time, 1=weather)
            "time": [(0, -130), 180, (255, 255, 255), 0],
            "date": [(0, 40), 100, (210, 210, 210), 0],
            "weekday": [(0, 150), 100, (210, 210, 210), 0],
            "temperature": [(0, -130), 180, (255, 255, 255), 1],
            "weatherstatus": [(0, 50), 110, (210, 210, 210), 1],
            "wind": [(0, 160), 110, (210, 210, 210), 1],
            "eur": [(-250, -40), 1.2, 2],
            "usd": [(250, -40), 1.2, 2],
            "eurtext": [(-240, 160), 55, (210, 210, 210), 2],
            "usdtext": [(260, 160), 55, (210, 210, 210), 2],
            "nametitle": [(0, -130), 110, (255, 255, 255), 3],
            "name": [(0, 110), 70, (210, 210, 210), 3],
        }
        for k, v in INIT.items():
            if v[-1] != self.group: continue
            if type(DATA[k]) == list:
                plot = self.plot(DATA[k])
                plot = plot.resize((int(plot.size[0] * v[1]), int(plot.size[1] * v[1])))
                img.paste(plot,
                          (
                              int((rect[0] + rect[2]) / 2 + v[0][0]) - int(plot.size[0] / 2),
                              int((rect[1] + rect[3]) / 2 + v[0][1]) - int(plot.size[1] / 2)
                          )
                          )
            else:
                font = ImageFont.truetype('src/Font.ttf', v[1])
                drawing.text(
                    (
                        (rect[0] + rect[2]) / 2 + v[0][0],
                        (rect[1] + rect[3]) / 2 + v[0][1]
                    ),
                    DATA[k],
                    font=font,
                    fill=v[2],
                    anchor="mm"
                )

        icons = os.listdir("src/icons")
        idx = 0
        for i in icons:
            icon = Image.open("src/icons/" + i)
            icon = icon.resize((self.ICONSIZE, self.ICONSIZE))
            if self.group != idx:
                fil = ImageEnhance.Brightness(icon)
                icon = fil.enhance(0.1)
            img.paste(icon, self.ICONPOS(idx))
            idx += 1

        return img

    def is_desktop_focused(self):
        hWnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hWnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hWnd, buf, length + 1)
        return (buf.value in [None, "Program Manager", ""])

    def get_icon(self, mouse_infos):
        group = None
        positions = self.ICONPOSLIST
        for num,i in enumerate(positions):
            if mouse_infos[0] > i[0] and mouse_infos[0] < (i[0]+60):
                if mouse_infos[1] > i[1] and mouse_infos[1] < (i[1] + 60):
                    group = num
                    break
        return group

    def set_bg(self, group):
        self.group = group
        img = self.create_bgimage()
        img.save(fp="src/infos.png")
        path = "\\".join(__file__.split("\\")[:-1]) + "\\infos.png"
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)


wp = Wallpaper()
wp.set_bg(0)

def on_click(x, y, button, pressed):
    try:
        if pressed and button == mouse.Button.left:
            if wp.is_desktop_focused():
                gr = wp.get_icon((x,y))
                if gr is not None:
                    wp.set_bg(gr)
    except: pass

listener = mouse.Listener(on_click=on_click)
listener.start()

refresh = 0
try:
    refresh = float(sys.argv[1])
except:
    refresh = 5
while 1:
    time.sleep(refresh)
    wp.set_bg(wp.group)