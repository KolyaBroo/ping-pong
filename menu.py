from pygame import *
import subprocess
import sys
from customtkinter import *
from PIL import Image, ImageTk
import json
from random import randint, uniform, choice
import math

init()
sounds = {
          "Menu_theme": mixer.Sound("C:\Python\ping-pong\Sounds\Menu_theme.mp3"),
          "Button": mixer.Sound("C:\Python\ping-pong\Sounds\Button.mp3"),
        }

def play_sound(name, loop=False, stop=False, volume=1.0):
    if stop:
        sounds[name].stop()
        return

    if name in sounds:
        sounds[name].set_volume(volume)
        loops = -1 if loop else 0
        sounds[name].play(loops=loops)

class GameMenu(CTk):
    def __init__(self, fg_color=None, **kwargs):
        super().__init__(fg_color, **kwargs)

        self.geometry("1100x650")
        self.title("pingPong")
        #self.configure(fg_color="transparent")
        self._set_appearance_mode("transperent")
        self.resizable(False, False)

        # -----BACKGROUND-------  #

        self.background_canvas = CTkCanvas(self,width=1400,height=900,bg="#0A0C14",highlightthickness=0)
        self.background_canvas.place(x=0,y=0)
        self.background_ball_images = []
        for i in range(1, 6):
            try:
                b_image = Image.open(f"Images/Ball/ball_{i}.png").convert("RGBA")
                b_image = b_image.resize((34, 34),Image.Resampling.LANCZOS)
                b_image = ImageTk.PhotoImage(b_image)
                self.background_ball_images.append(b_image)
            except Exception:
                pass

        if len(self.background_ball_images) == 0:
            self.background_ball_images = [None]

        #animation
        self.background_ball_frame = 0
        self.background_ball_timer = 0
        self.background_balls = []

        for i in range(7):
            ball = {

                "x": uniform(50, 1050),
                "y": uniform(70, 580),

                "vx": choice([
                    uniform(-2.0, -0.7),
                    uniform(0.7, 2.0)
                ]),

                "vy": choice([
                    uniform(-1.5, -0.5),
                    uniform(0.5, 1.5)
                ]),

                "size": randint(16, 24),

                "trail": [],

                "image": None,

                "image_id": None
            }

            self.background_balls.append(ball)

        self.background_particles = []
        for i in range(80):
            particle = {

                "x": uniform(
                    0,
                    1380
                ),

                "y": uniform(
                    0,
                    850
                ),

                "speed": uniform(
                    0.15,
                    0.6
                ),

                "size": randint(
                    1,
                    2
                ),

                "alpha": randint(
                    30,
                    100
                )
            }
            self.background_particles.append(particle)

        self.background_effects = []
        self.draw_animated_background()
        self.animate_background()

        #   ------ЗАВАНТАЖЕННЯ ДАНИХ-------  #

        self.data = {
            "name": "",
            "host": "localhost",
            "port": 8080
        }

        try:
            with open(
                "menu_options.json",
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if data.get("name"):
                self.data["name"] = data["name"]

            if data.get("host"):
                self.data["host"] = data["host"]

            if data.get("port"):
                self.data["port"] = data["port"]

        except:
            pass

        #   ------MAIN_MENU-------  #

        self.Main_Menu()

    #   ------АНІМАЦІЯ-------  #

    def animate_background(self):
        for particle in self.background_particles:
            particle["y"] += particle["speed"]
            if particle["y"] > 850:
                particle["y"] = -5
                particle["x"] = uniform(0,1380)

        for ball in self.background_balls:
            ball["x"] += ball["vx"]
            ball["y"] += ball["vy"]
            ball["trail"].append((ball["x"],ball["y"]))

            if len(ball["trail"]) > 12:
                ball["trail"].pop(0)

            # Colisions (Стіни)
            #ліва
            if ball["x"] <= 20:
                ball["x"] = 20
                ball["vx"] *= -1
                self.create_ball_effect(ball["x"],ball["y"])

            #права
            if ball["x"] >= 1360:
                ball["x"] = 1360
                ball["vx"] *= -1
                self.create_ball_effect(ball["x"],ball["y"])

            #верхня
            if ball["y"] <= 15:
                ball["y"] = 15
                ball["vy"] *= -1
                self.create_ball_effect(ball["x"],ball["y"])

            #нижня
            if ball["y"] >= 800:
                ball["y"] = 800
                ball["vy"] *= -1
                self.create_ball_effect(ball["x"],ball["y"])

        for effect in self.background_effects[:]:
            effect["x"] += effect["vx"]
            effect["y"] += effect["vy"]
            effect["life"] -= 1
            effect["size"] *= 0.94
            if effect["life"] <= 0:
                self.background_effects.remove(effect)
        self.after(16,self.animate_background)

    def create_ball_effect(self,x,y):
        for i in range(10):
            angle = uniform(0,math.pi * 2)
            speed = uniform(0.8,2.8)
            self.background_effects.append({
                "x": x,
                "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "size": uniform(1.5,3.5),
                "life": randint(15,30)
            })

    #   ------BACKGROUND-------  #

    def draw_animated_background(self):
        self.background_canvas.delete("all")
        self.background_canvas.create_rectangle(
            0,
            0,
            1360,
            850,
            fill="#0A0C14",
            outline=""
        )

        for y in range(
            0,
            850,
            40
        ):

            self.background_canvas.create_line(
                0,
                y,
                1380,
                y,
                fill="#141927",
                width=1
            )

        for x in range(
            0,
            1380,
            40
        ):

            self.background_canvas.create_line(
                x,
                0,
                x,
                850,
                fill="#141927",
                width=1
            )

        for y in range(
            0,
            850,
            25
        ):

            self.background_canvas.create_rectangle(
                680,
                y,
                682,
                y + 12,
                fill="#32394C",
                outline=""
            )

        for particle in self.background_particles:

            size = particle["size"]

            self.background_canvas.create_oval(
                particle["x"] - size,
                particle["y"] - size,
                particle["x"] + size,
                particle["y"] + size,
                fill="#28334A",
                outline=""
            )

        for effect in self.background_effects:

            size = max(
                1,
                int(effect["size"])
            )

            self.background_canvas.create_oval(
                effect["x"] - size,
                effect["y"] - size,
                effect["x"] + size,
                effect["y"] + size,
                fill="#DDEEFF",
                outline=""
            )

        for ball in self.background_balls:
            trail = ball["trail"]
            for index, position in enumerate(
                trail
            ):

                progress = (
                    index + 1
                ) / len(trail)

                size = max(
                    1,
                    int(
                        ball["size"] *
                        progress *
                        0.45
                    )
                )

                self.background_canvas.create_oval(
                    position[0] - size,
                    position[1] - size,
                    position[0] + size,
                    position[1] + size,
                    fill="#596A82",
                    outline=""
                )

            glow_size = ball["size"] + 9
            self.background_canvas.create_oval(
                ball["x"] - glow_size,
                ball["y"] - glow_size,
                ball["x"] + glow_size,
                ball["y"] + glow_size,
                fill="#182233",
                outline=""
            )

            if self.background_ball_images[0] is not None:
                image_index = (
                    self.background_ball_frame %
                    len(
                        self.background_ball_images
                    )
                )

                ball_image = (
                    self.background_ball_images[
                        image_index
                    ]
                )

                self.background_canvas.create_image(
                    ball["x"],
                    ball["y"],
                    image=ball_image
                )

            else:
                self.background_canvas.create_oval(
                    ball["x"] - ball["size"],
                    ball["y"] - ball["size"],
                    ball["x"] + ball["size"],
                    ball["y"] + ball["size"],
                    fill="#E8EEF5",
                    outline="#FFFFFF"
                )

        self.background_ball_frame += 1
        self.after(16,self.draw_animated_background)

    #   ------MAIN_MENU-------  #

    def Main_Menu(self):
        for widget in self.winfo_children():
            if widget != self.background_canvas:
                widget.destroy()
        try:
            self.gamelogo = CTkImage(
                dark_image=Image.open(r"C:\Python\ping-pong\Images\Main\Main_logo (2).png"),
                light_image=Image.open(r"C:\Python\ping-pong\Images\Main\Main_logo (2).png"),size=(500, 250))
            self.logo = CTkLabel(self,image=self.gamelogo,text="",fg_color="transparent")
            self.logo.place(relx=0.5,rely=0.25,anchor="center")

        except Exception:
            self.logo = CTkLabel(
                self,
                text="PING PONG",
                text_color="#3FD5FF",
                font=(
                    "Arial",
                    55,
                    "bold"
                )
            )

            self.logo.place(relx=0.5,rely=0.25,anchor="center")

        self.btn_game = CTkButton(
            self,
            width=280,
            height=55,
            text="🎮  ГРАТИ",
            corner_radius=12,
            text_color="#FFFFFF",
            fg_color="#0087B5",
            hover_color="#00A9E0",
            font=(
                "Arial",
                20,
                "bold"
            ),
            command=self.Game_Window
        )

        self.btn_game.place(relx=0.5,rely=0.55,anchor="center")

        self.btn_settings = CTkButton(
            self,
            width=280,
            height=50,
            text="⚙  НАЛАШТУВАННЯ",
            corner_radius=12,
            text_color="#FFFFFF",
            fg_color="#005477",
            hover_color="#00739F",
            font=(
                "Arial",
                17,
                "bold"
            ),
            command=self.Settings_Window
        )

        self.btn_settings.place(relx=0.5,rely=0.65,anchor="center")

        self.version = CTkLabel(
            self,
            text="PingPong v0.1",
            text_color="#FFFFFF",
            fg_color="#001029",
            font=(
                "Arial",
                12
            )
        )

        self.version.place(relx=0.5,rely=0.94,anchor="center")

    #   ------GAME_WINDOW-------  #

    def Game_Window(self):
        play_sound("Button", loop=False, stop=False)
        for widget in self.winfo_children():
            if widget != self.background_canvas:
                widget.destroy()

        self.txt = CTkLabel(
            self,
            text="ВХІД У ГРУ",
            text_color="#3FD5FF",
            font=(
                "Arial",
                32,
                "bold"
            )
        )

        self.txt.place(relx=0.5,rely=0.25,anchor="center")

        self.inp_name = CTkEntry(
            self,
            width=300,
            height=45,
            placeholder_text="👤  Ваш нікнейм",
            fg_color="#3FD5FF",
            placeholder_text_color="Black",
            text_color="Black",
            corner_radius=10,
            font=(
                "Arial",
                15
            )
        )

        self.inp_name.place(relx=0.5,rely=0.42,anchor="center")

        if self.data.get("name"):
            self.inp_name.insert(0,self.data["name"])

        self.btn_log = CTkButton(
            self,
            width=300,
            height=50,
            text="🎮  ГРАТИ!",
            corner_radius=10,
            text_color="#FFFFFF",
            fg_color="#0087B5",
            hover_color="#00A9E0",
            font=(
                "Arial",
                18,
                "bold"
            ),
            command=self.go_to_app
        )

        self.btn_log.place(relx=0.5,rely=0.55,anchor="center")

        self.btn_back = CTkButton(
            self,
            width=150,
            height=40,
            text="← НАЗАД",
            corner_radius=10,
            fg_color="#16344A",
            hover_color="#214E68",
            command=self.Main_Menu
        )

        self.btn_back.place(relx=0.5,rely=0.67,anchor="center")

    #   ------SETTINGS_WINDOW-------  #

    def Settings_Window(self):
        play_sound("Button", loop=False, stop=False, volume=0.2)
        for widget in self.winfo_children():

            if widget != self.background_canvas:
                widget.destroy()

        self.settings_title = CTkLabel(
            self,
            text="НАЛАШТУВАННЯ",
            text_color="#3FD5FF",
            font=(
                "Arial",
                32,
                "bold"
            )
        )

        self.settings_title.place(relx=0.5,rely=0.20,anchor="center")

        self.host_pass = CTkEntry(
            self,
            width=300,
            height=45,
            placeholder_text="💬  Хост серверу",
            fg_color="#00BFFF",
            placeholder_text_color="Black",
            text_color="Black",
            corner_radius=10,
            font=(
                "Arial",
                15
            )
        )

        self.host_pass.place(relx=0.5,rely=0.38,anchor="center")

        self.port_pass = CTkEntry(
            self,
            width=300,
            height=45,
            placeholder_text="🔒  Порт серверу",
            fg_color="#00BFFF",
            show="*",
            placeholder_text_color="Black",
            text_color="Black",
            corner_radius=10,
            font=(
                "Arial",
                15
            )
        )

        self.port_pass.place(relx=0.5,rely=0.48,anchor="center")

        if self.data.get("host"):
            self.host_pass.insert(0,self.data["host"])

        if self.data.get("port"):
            self.port_pass.insert(0,str(self.data["port"]))

        self.show_btn = CTkButton(
            self,
            text="👁",
            width=45,
            height=45,
            command=self.toggle_password,
            fg_color="#00BFFF",
            hover_color="#009DD1",
            text_color="Black",
            corner_radius=10)

        self.show_btn.place(relx=0.5,rely=0.48,x=175,anchor="center")

        self.save_btn = CTkButton(
            self,
            width=300,
            height=50,
            text="💾  ЗБЕРЕГТИ",
            corner_radius=10,
            text_color="#FFFFFF",
            fg_color="#0087B5",
            hover_color="#00A9E0",
            font=(
                "Arial",
                17,
                "bold"
            ),
            command=self.save_settings
        )

        self.save_btn.place(relx=0.5,rely=0.60,anchor="center")

        self.btn_back = CTkButton(
            self,
            width=150,
            height=40,
            text="← НАЗАД",
            corner_radius=10,
            fg_color="#16344A",
            hover_color="#214E68",
            command=self.Main_Menu    
        )

        self.btn_back.place(relx=0.5,rely=0.70,anchor="center")

    #   ------SHOW/HIDE PASSWORD-------  #

    def toggle_password(self):
        play_sound("Button", loop=False, stop=False)

        if self.port_pass.cget("show") == "":
            self.port_pass.configure(show="*")
        else:
            self.port_pass.configure(show="")

    #   ------SAVE SETTINGS-------  #

    def save_settings(self):
        play_sound("Button", loop=False, stop=False,volume=0.2)
        try:
            self.data["host"] = (self.host_pass.get())
            self.data["port"] = int(self.port_pass.get())

            with open("menu_options.json","w",encoding="utf-8") as file:
                json.dump(self.data,file,ensure_ascii=False,indent=4)
            self.Main_Menu()

        except ValueError:
            self.port_pass.delete(0,"end")
            self.port_pass.insert(0,"8080")

    #   ------GO__TO__APP-------  #

    def go_to_app(self):
        play_sound("Button", loop=False, stop=False)
        name = self.inp_name.get()

        if name == "":
            self.inp_name.configure(border_color="#FF3333")
            return
        self.data["name"] = name

        if "host" not in self.data:
            self.data["host"] = "localhost"

        if "port" not in self.data:
            self.data["port"] = 8080
        self.env = {"name": self.data["name"],"host": self.data["host"],"port": self.data["port"]}

        #DATA
        with open("menu_options.json","w",encoding="utf-8") as file:
            json.dump(self.env,file,ensure_ascii=False,indent=4)
        try:
            self.after_cancel(self.background_animation_id)
        except:
            pass
        subprocess.Popen([sys.executable, "client.py"])
        self.destroy()

if __name__ == "__main__":
    menu = GameMenu()
    play_sound("Menu_theme", loop=True, stop=False, volume=0.2)
    menu.mainloop()

    env = getattr(menu,"env",None)
    if env:
        print("Нік:",env["name"])
        print("Хост:",env["host"])
        print("Порт:",env["port"])