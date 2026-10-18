import socket
import json
import threading
import time
import random
import math

WIDTH, HEIGHT = 1050, 650
BALL_SPEED = 3.5
BALL_ACCELERATION = 0.4
BALL_MAX_SPEED = 15
MAX_BOUNCE_ANGLE = 60
GAME_SPEED = 0
PADDLE_SPEED = 10
COUNTDOWN_START = 4

class GameServer:
    def __init__(self, host='localhost', port=8080):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2)
        print("🎮 Server started")

        self.clients = {0: None, 1: None}
        self.connected = {0: False, 1: False}

        self.player_names = {
            0: "Гравець 1",
            1: "Гравець 2"
        }

        self.lock = threading.Lock()
        self.reset_game_state()
        self.sound_event = 'Main_theme'

    def reset_game_state(self):
        self.paddles = {0: 250, 1: 250}
        self.scores = [0, 0]
        self.ball = {
            "x": WIDTH // 2,
            "y": HEIGHT // 2,
            "vx": BALL_SPEED * random.choice([-1, 1]),
            "vy": BALL_SPEED * random.choice([-1, 1])
        }
        self.countdown = COUNTDOWN_START
        self.game_over = False
        self.winner = None

    def handle_client(self, pid):
        conn = self.clients[pid]
        try:
            while True:
                data = conn.recv(64).decode()
                with self.lock:
                    if data == "UP":
                        self.paddles[pid] = max(60, self.paddles[pid] - PADDLE_SPEED)
                    elif data == "DOWN":
                        self.paddles[pid] = min(HEIGHT - 100, self.paddles[pid] + PADDLE_SPEED)
                    elif data == "K":
                        self.reset_game_state()
        except:
            with self.lock:
                self.connected[pid] = False
                self.game_over = True
                self.winner = 1 - pid
                print(f"Гравець {pid} відключився. Переміг гравець {1 - pid}.")

    def broadcast_state(self):
        state = json.dumps({
            "paddles": self.paddles,
            "ball": self.ball,
            "scores": self.scores,
            "countdown": max(self.countdown, 0),
            "winner": self.winner if self.game_over else None,
            "player_names": self.player_names,
            "sound_event": self.sound_event
        }) + "\n"
        for pid, conn in self.clients.items():
            if conn:
                try:
                    conn.sendall(state.encode())
                except:
                    self.connected[pid] = False

    def increase_ball_speed(self):
        speed = (self.ball["vx"] ** 2 + self.ball["vy"] ** 2) ** 0.5
        if speed >= BALL_MAX_SPEED:
            return
        new_speed = min(speed + BALL_ACCELERATION, BALL_MAX_SPEED)
        scale = new_speed / speed
        self.ball["vx"] *= scale
        self.ball["vy"] *= scale

    def bounce_from_paddle(self, pid):
        paddle_center = self.paddles[pid] + 50
        relative_y = (self.ball["y"] - paddle_center) / 50
        relative_y = max(-1, min(1, relative_y))
        angle = relative_y * MAX_BOUNCE_ANGLE
        angle += random.uniform(-5, 5)
        angle = max(-MAX_BOUNCE_ANGLE, min(MAX_BOUNCE_ANGLE, angle))
        angle_rad = math.radians(angle)
        speed = (self.ball["vx"] ** 2 + self.ball["vy"] ** 2) ** 0.5

        if pid == 0:
            direction = 1
        else:
            direction = -1

        self.ball["vx"] = direction * speed * math.cos(angle_rad)
        self.ball["vy"] = speed * math.sin(angle_rad)

    def ball_logic(self):
        with self.lock:
            self.sound_event = "Countdown"
            self.broadcast_state()
        time.sleep(0.1)
        with self.lock:
            self.sound_event = None

        while self.countdown > 0:
            time.sleep(1)

            with self.lock:
                self.countdown -= 1
                self.broadcast_state()

        with self.lock:
            self.sound_event = "Main_theme"
            self.broadcast_state()

        time.sleep(0.1)

        with self.lock:
            self.sound_event = None

        # --- Гра ---
        while not self.game_over:
            with self.lock:
                self.ball['x'] += self.ball['vx']
                self.ball['y'] += self.ball['vy']

                if self.ball['y'] <= 60 or self.ball['y'] >= HEIGHT:
                    self.ball['vy'] *= -1
                    self.sound_event = "wall_hit"

                if self.ball['x'] <= 40 and self.paddles[0] <= self.ball['y'] <= self.paddles[0] + 100:
                    self.bounce_from_paddle(0)
                    self.increase_ball_speed()
                    self.sound_event = 'platform_hit'

                elif self.ball['x'] >= WIDTH - 40 and self.paddles[1] <= self.ball['y'] <= self.paddles[1] + 100:
                    self.bounce_from_paddle(1)
                    self.increase_ball_speed()
                    self.sound_event = 'platform_hit'

                if self.ball['x'] < 0:
                    self.scores[1] += 1
                    self.reset_ball()

                elif self.ball['x'] > WIDTH:
                    self.scores[0] += 1
                    self.reset_ball()

                if self.scores[0] >= 10:
                    self.game_over = True
                    self.winner = 0

                elif self.scores[1] >= 10:
                    self.game_over = True
                    self.winner = 1

                self.broadcast_state()
                self.sound_event = None

            time.sleep(0.016)

    def reset_ball(self):
        self.ball = {
            "x": WIDTH // 2,
            "y": HEIGHT // 2,
            "vx": BALL_SPEED * random.choice([-1, 1]),
            "vy": BALL_SPEED * random.choice([-1, 1])
        }

    def accept_players(self):
        for pid in [0, 1]:
            print(f"Очікуємо гравця {pid}...")

            conn, _ = self.server.accept()

            self.clients[pid] = conn
            conn.sendall((str(pid) + "\n").encode())
            self.connected[pid] = True
            try:
                name_data = ""
                while "\n" not in name_data:
                    data = conn.recv(1024).decode()
                    if not data:
                        break
                    name_data += data
                name = name_data.split("\n", 1)[0].strip()
                if name:
                    self.player_names[pid] = name
                else:
                    self.player_names[pid] = f"Гравець {pid + 1}"
            except:
                self.player_names[pid] = f"Гравець {pid + 1}"
            print(f"Гравець {pid} приєднався: {self.player_names[pid]}")
            threading.Thread(
                target=self.handle_client,
                args=(pid,),
                daemon=True
            ).start()

    def run(self):
        while True:
            self.accept_players()
            self.reset_game_state()

            threading.Thread(target=self.ball_logic,daemon=True).start()

            while not self.game_over and all(self.connected.values()):
                time.sleep(0.1)
            print(f"Гравець {self.winner} переміг!")
            time.sleep(5)

            for pid in [0, 1]:
                try:
                    self.clients[pid].close()
                except:
                    pass
                self.clients[pid] = None
                self.connected[pid] = False

            self.player_names = {0: "Гравець 1",1: "Гравець 2"}

GameServer().run()