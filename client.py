from pygame import *
from customtkinter import *
import menu
import time as tm
from random import *
import socket
import json
from threading import Thread

# ---ПУГАМЕ НАЛАШТУВАННЯ ---
WIDTH, HEIGHT = 1050, 650
init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")

# --- ШРИФТИ ---
font_win = font.Font(None, 72)
font_main = font.Font(None, 36)
font_score = font.Font(None, 52)
font_small = font.Font(None, 24)

# ---СЕРВЕР ---
def connect_to_server():
    try:
        with open("menu_options.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        host = data.get("host", "localhost")
        port = int(data.get("port", 8080))
        my_name = data.get("name", "Гравець")
    except:
        host = "localhost"
        port = 8080
        my_name = "Гравець"

    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, port)) # ---- Підключення до сервера
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode().strip())
            client.sendall((my_name + "\n").encode())
            return my_id, game_state, buffer, client
        except:
            pass

def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            game_state["winner"] = -1
            break

def play_sound(name, loop=False, stop=False, volume=1.0):
    if stop:
        sounds[name].stop()
        return

    if name in sounds:
        sounds[name].set_volume(volume)
        loops = -1 if loop else 0
        sounds[name].play(loops=loops)


# --- ШРИФТИ ---
font_win = font.Font(None, 72)
font_main = font.Font(None, 36)

# --- ЗОБРАЖЕННЯ ----
ball_images = []

for i in range(1, 6):
    b_image = image.load(f"Images/Ball/ball_{i}.png").convert_alpha()
    scaled_b_image = transform.smoothscale(b_image, (40,40))
    ball_images.append(scaled_b_image)

ball_animation_frame = 0
ball_animation_timer = 0
ball_animation_speed = 85

goal_image = image.load(f"Images\Goal\Goal.png")
scaled_goal_image = transform.smoothscale(goal_image, (480,180))
scaled_goal_image = transform.rotate(scaled_goal_image, (90))
n_scaled_goal_image = transform.rotate(scaled_goal_image, (0))
n_scaled_goal_image = transform.flip(n_scaled_goal_image, 1, 0)


# --- ФОН ---
particles = []

for i in range(40):
    particles.append({
        "x": randint(0, WIDTH),
        "y": randint(0, HEIGHT),
        "speed": randint(1, 3),
        "size": randint(1, 3)
    })


def draw_background():
    screen.fill((10, 12, 20))

    for y in range(0, HEIGHT, 40):
        draw.line(screen,(20, 25, 40),(0, y),(WIDTH, y),1)

    for x in range(0, WIDTH, 40):
        draw.line(screen,(20, 25, 40),(x, 0),(x, HEIGHT),1)

    #Центр-лінія
    for y in range(0, HEIGHT, 25):
        draw.rect(screen,(50, 55, 75),(WIDTH // 2 - 1, y, 2, 12))

    #Партикли
    for particle in particles:
        particle["y"] += particle["speed"]

        if particle["y"] > HEIGHT:
            particle["y"] = 0
            particle["x"] = randint(0, WIDTH)

        draw.circle(
            screen,
            (35, 45, 65),
            (particle["x"], particle["y"]),
            particle["size"]
        )


# --- Перемога та поразка ---
def draw_game_over(you_winner):
    screen.fill((7, 9, 17))
    for y in range(0, HEIGHT, 40):
        draw.line(screen,(15, 20, 35),(0, y),(WIDTH, y),1)
    for x in range(0, WIDTH, 40):
        draw.line(screen,(15, 20, 35),(x, 0),(x, HEIGHT),1)

    if you_winner:
        title = "ПЕРЕМОГА!"
        title_color = (80, 255, 150)
        subtitle = "Ти переміг у цьому матчі!"
    else:
        title = "ПОРАЗКА"
        title_color = (255, 70, 100)
        subtitle = "Цього разу перемога не твоя..."

    glow_surface = Surface((WIDTH, HEIGHT),SRCALPHA)
    for radius in range(280, 30, -20):
        alpha = int(3 + (280 - radius) * 0.08)
        draw.circle(glow_surface,(title_color[0],title_color[1],title_color[2],alpha),(WIDTH // 2,180),radius)
    screen.blit(glow_surface,(0, 0))

    # --- партикли
    for particle in particles:
        particle["y"] += particle["speed"] * 0.5
        if particle["y"] > HEIGHT:
            particle["y"] = 0
            particle["x"] = randint(0, WIDTH)
        if you_winner:
            particle_color = (40, 130, 90)
        else:
            particle_color = (130, 45, 70)
        draw.circle(screen,particle_color,(particle["x"],particle["y"]),particle["size"])

    # --- фон програшу та виграшу  ---
    circle_surface = Surface((170, 170),SRCALPHA)
    for radius in range(80, 20, -5):
        alpha = int(5 + (80 - radius) * 2)
        draw.circle(circle_surface,(title_color[0],title_color[1],title_color[2],alpha),(85, 85),radius)
    if you_winner:
        draw.circle(screen,title_color,(WIDTH // 2,155),45,4)
        draw.line(screen,title_color,(WIDTH // 2 - 22,155),(WIDTH // 2 - 5,172),7)
        draw.line(screen,title_color,(WIDTH // 2 - 5,172),(WIDTH // 2 + 27,135),7)
    else:
        draw.circle(screen,title_color,(WIDTH // 2,155),45,4)
        draw.line(screen,title_color,(WIDTH // 2 - 20,135),(WIDTH // 2 + 20,175),7)
        draw.line(screen,title_color,(WIDTH // 2 + 20,135),(WIDTH // 2 - 20,175),7)

    # --- мейн графа вікна програшу та виграшу ---
    win_text = font_win.render(title,True,title_color)
    text_rect = win_text.get_rect(
    center=(WIDTH // 2,270))
    screen.blit(win_text,text_rect)
    subtitle_font = font.Font(None,30)
    subtitle_text = subtitle_font.render(subtitle,True,(190, 200, 220))
    subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2,320))
    screen.blit(subtitle_text,subtitle_rect)
    result_background = Surface((300, 90),SRCALPHA)
    draw.rect(result_background,(15, 20, 35, 230),(0, 0, 300, 90),border_radius=18)
    draw.rect(result_background,(title_color[0],title_color[1],title_color[2],120),(0, 0, 300, 90),2,border_radius=18)
    screen.blit(result_background,(WIDTH // 2 - 150,365))

    # --- Рахунок ---
    if game_state:
        score_text = font_score.render(f"{game_state['scores'][0]} : {game_state['scores'][1]}",True,(240, 245, 255))
    score_rect = score_text.get_rect(center=(WIDTH // 2,410))
    screen.blit(score_text,score_rect)
    restart_font = font.Font(None,28)
    restart_text = restart_font.render("Натисни K, щоб зіграти ще раз",True,(170, 180, 200))
    restart_rect = restart_text.get_rect(center=(WIDTH // 2,500))
    screen.blit(restart_text,restart_rect)
    draw.line(screen,title_color,(WIDTH // 2 - 130,545),(WIDTH // 2 + 130,545),2)
    draw.circle(screen,title_color,(WIDTH // 2 - 140,545),4)
    draw.circle(screen,title_color,(WIDTH // 2 + 140,545),4)

# --- ЗВУКИ ---
sounds = {
          "platform_hit": mixer.Sound("C:\Python\ping-pong\Sounds\platform_hit.mp3"),
          "wall_hit": mixer.Sound("C:\Python\ping-pong\Sounds\wall_hit.mp3"),
          "Goal": mixer.Sound("C:\Python\ping-pong\Sounds\Goal.mp3"),
          "LoseGoal": mixer.Sound("C:\Python\ping-pong\Sounds\LoseGoal.mp3"),
          "Countdown": mixer.Sound("C:\Python\ping-pong\Sounds\Countdown.mp3"),
          "Main_theme": mixer.Sound("C:\Python\ping-pong\Sounds\Main_theme.mp3"),
        }


# --- ГРА ---
game_over = False
winner = None
you_winner = None
last_sound_event = None

my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive,daemon=True).start()

while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

        if e.type == KEYDOWN and e.key == K_k and game_over:
            client.close()

            game_over = False
            winner = None
            you_winner = None
            game_state = {}

            my_id, game_state, buffer, client = connect_to_server()
            Thread(target=receive,daemon=True).start()

    current_sound_event = game_state.get("sound_event")

    if current_sound_event and current_sound_event != last_sound_event:
        if current_sound_event == "Countdown":
            play_sound("Countdown",loop=False,stop=False)

        elif current_sound_event == "Main_theme":
            play_sound("Main_theme",loop=True,stop=False,volume=0.2)

        elif current_sound_event == "wall_hit":
            play_sound("wall_hit",loop=False,stop=False)

        elif current_sound_event == "platform_hit":
            play_sound("platform_hit",loop=False,stop=False)

        last_sound_event = current_sound_event

    elif current_sound_event is None:
        last_sound_event = None

    if "countdown" in game_state and game_state["countdown"] > 0:
        draw_background()
        countdown_text = font.Font(None,72).render(str(game_state["countdown"]),True,(255, 255, 255))

        screen.blit(countdown_text,(WIDTH // 2 - 20,HEIGHT // 2 - 30))
        display.update()
        continue
        
    if "winner" in game_state and game_state["winner"] is not None:
        game_over = True
        if you_winner is None:
            if game_state["winner"] == my_id:
                you_winner = True
            else:
                you_winner = False
            play_sound("Main_theme",loop=False,stop=True, volume=0.2)
            if you_winner:
                play_sound("Goal",loop=False,stop=False)
            else:
                play_sound("LoseGoal",loop=False,stop=False)

        draw_game_over(you_winner)
        display.update()
        continue

    if game_state:
        draw_background()
        screen.blit(scaled_goal_image,(-15,60))
        screen.blit(n_scaled_goal_image,(885,60))
        draw.rect(screen,(255, 0, 0),(20,game_state['paddles']['0'],20,100))
        draw.rect(screen,(0, 0, 255),(WIDTH - 40,game_state['paddles']['1'],20,100))

        ball_image = ball_images[ball_animation_frame]
        ball_rect = ball_image.get_rect(center=(game_state['ball']['x'],game_state['ball']['y']))

        screen.blit(ball_image,ball_rect)
        score_text = font_score.render(f"{game_state['scores'][0]} : {game_state['scores'][1]}",True,(240, 245, 255))
        score_rect = score_text.get_rect(center=(WIDTH // 2,42))
        score_background = Surface((170, 65),SRCALPHA)
        draw.rect(score_background,(10, 15, 28, 210),(0,0,170,65),border_radius=15)
        draw.rect(score_background,(60, 75, 105, 150),(0,0,170,65),2,border_radius=15)
        screen.blit(score_background,(WIDTH // 2 - 85,10)) #WIDTH // 2 - 85
        screen.blit(score_text,score_rect)

        if "player_names" in game_state:
            player_left_name = game_state["player_names"].get("0","Гравець 1")
            player_right_name = game_state["player_names"].get("1","Гравець 2")

            name_font = font.Font(None,28)

            left_name_text = name_font.render(
            player_left_name,True,(240, 245, 255))
            left_name_rect = left_name_text.get_rect(center=(150,42))
            left_name_background = Surface((250,65),SRCALPHA)

            draw.rect(left_name_background,(10,15,28,210),(0,0,250,65),border_radius=15)
            draw.rect(left_name_background,(255,60,70,180),(0,0,250,65),2,border_radius=15)
            screen.blit(left_name_background,(25,10))
            screen.blit(left_name_text,left_name_rect)

            right_name_text = name_font.render(player_right_name,True,(240,245,255))
            right_name_rect = right_name_text.get_rect(center=(WIDTH - 150,42))
            right_name_background = Surface((250,65),SRCALPHA)

            draw.rect(right_name_background,(10,15,28,210),(0,0,250,65),border_radius=15)
            draw.rect(right_name_background,(60,120,255,180),(0,0,250,65),2,border_radius=15)
            screen.blit(right_name_background,(WIDTH - 275,10))
            screen.blit(right_name_text,right_name_rect)

    else:
        draw_background()
        title = "Очікування гравців..."
        title_color = (102, 255, 255)
        win_text = font_win.render(title,True,title_color)
        screen.blit(win_text,(WIDTH // 2 - 255,300))

    display.update()
    clock.tick(60)

    ball_animation_timer += clock.get_time()
    if ball_animation_timer >= ball_animation_speed:
        ball_animation_timer = 0
        ball_animation_frame += 1
        if ball_animation_frame >= len(ball_images):
            ball_animation_frame = 0

    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")

    elif keys[K_s]:
        client.send(b"DOWN")