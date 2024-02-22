import socket
import ssl
import pygame
import threading

# Create a standard socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = input("Enter the server IP:")
port = 9999

# Create an SSL context
context = ssl.create_default_context()

# Disable certificate verification
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

# Wrap the client's socket with SSL
s = context.wrap_socket(client_socket, server_side=False)

player_one = 1
player_one_color = (217, 84, 77)  # RED
player_two = 2
player_two_color = (173, 216, 230)  # BLUE
bottom_msg = ""
msg = "        Waiting...."
current_player = 0
xy = (-1, -1)
allow = 0  # Allow handling mouse events
matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

# Create worker threads
def create_thread(target):
    t = threading.Thread(target=target)  # Argument - target function
    t.daemon = True
    t.start()

# Initialize Pygame
pygame.init()

width = 600
height = 550
screen = pygame.display.set_mode((width, height))

# Set title
pygame.display.set_caption("Tic Tac Toe")

# Set icon
icon = pygame.image.load("tictactoe.png")
pygame.display.set_icon(icon)

# Fonts
big_font = pygame.font.Font('DK Lemon Yellow Sun.otf', 64)
small_font = pygame.font.Font('Crunch Chips.otf', 32)
background_color = (31, 31, 31)  # Dark background color
title_color = (255, 255, 255)  # White text color
subtitle_color = (203, 195, 227)
line_color = (255, 255, 255)

def build_screen(bottom_msg, string, player_color=subtitle_color):
    screen.fill(background_color)
    if "One" in string or "1" in string:
        player_color = player_one_color
    elif "Two" in string or "2" in string:
        player_color = player_two_color

    # Vertical lines
    pygame.draw.line(screen, line_color, (250 - 2, 150), (250 - 2, 450), 4)
    pygame.draw.line(screen, line_color, (350 - 2, 150), (350 - 2, 450), 4)
    # Horizontal lines
    pygame.draw.line(screen, line_color, (150, 250 - 2), (450, 250 - 2), 4)
    pygame.draw.line(screen, line_color, (150, 350 - 2), (450, 350 - 2), 4)

    title = big_font.render("   TIC-TAC-TOE", True, title_color)
    screen.blit(title, (110, 0))
    subtitle = small_font.render(str.upper(string), True, player_color)
    screen.blit(subtitle, (150, 70))
    center_message(bottom_msg, player_color)

def center_message(msg, color=title_color):
    pos = (100, 480)
    if "One" in msg or "1" in msg:
        color = player_one_color
    elif "Two" in msg or "2" in msg:
        color = player_two_color
    msg_rendered = small_font.render(msg, True, color)
    screen.blit(msg_rendered, pos)

def print_current(current, pos, color):
    current_rendered = big_font.render(str.upper(current), True, color)
    screen.blit(current_rendered, pos)

def print_matrix(matrix):
    for i in range(3):
        y = int((i + 1.75) * 100)
        for j in range(3):
            x = int((j + 1.75) * 100)
            current = " "
            color = title_color
            if matrix[i][j] == player_one:
                current = "X"
                color = player_one_color
            elif matrix[i][j] == player_two:
                current = "O"
                color = player_two_color
            print_current(current, (x, y), color)

def validate_input(x, y):
    if x > 2 or y > 2:
        print("\nOut of bounds! Enter again...\n")
        return False
    elif matrix[x][y] != 0:
        print("\nAlready entered! Try again...\n")
        return False
    return True

def handle_mouse_event(pos):
    x = pos[0]
    y = pos[1]
    global current_player
    global xy
    if not (150 < x < 450 and 150 < y < 450):
        xy = (-1, -1)
    else:
        col = int(x / 100 - 1.5)
        row = int(y / 100 - 1.5)
        print("({}, {})".format(row, col))
        if validate_input(row, col):
            matrix[row][col] = current_player
            xy = (row, col)

def start_player():
    global current_player
    global bottom_msg
    try:
        s.connect((host, port))
        print("Connected to:", host, ":", port)
        recv_data = s.recv(2048 * 10)
        bottom_msg = recv_data.decode()
        if "1" in bottom_msg:
            current_player = 1
        else:
            current_player = 2
        start_game()
        s.close()
    except socket.error as e:
        print("Socket connection error:", e)

def start_game():
    running = True
    global msg
    global matrix
    global bottom_msg
    create_thread(accept_msg)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if allow:
                    handle_mouse_event(pos)

        if msg == "":
            break

        build_screen(bottom_msg, msg)
        print_matrix(matrix)
        pygame.display.update()

def accept_msg():
    global matrix
    global msg
    global bottom_msg
    global allow
    global xy
    while True:
        try:
            recv_data = s.recv(2048 * 10)
            recv_data_decoded = recv_data.decode()
            build_screen(bottom_msg, recv_data_decoded)

            if recv_data_decoded == "Input":
                failed = 1
                allow = 1
                xy = (-1, -1)
                while failed:
                    try:
                        if xy != (-1, -1):
                            coordinates = str(xy[0]) + "," + str(xy[1])
                            s.send(coordinates.encode())
                            failed = 0
                            allow = 0
                    except:
                        print("Error occurred....Try again")

            elif recv_data_decoded == "Error":
                print("Error occurred! Try again..")

            elif recv_data_decoded == "Matrix":
                print(recv_data_decoded)
                matrix_recv = s.recv(2048 * 100)
                matrix_recv_decoded = matrix_recv.decode("utf-8")
                matrix = eval(matrix_recv_decoded)

            elif recv_data_decoded == "Over":
                msg_recv = s.recv(2048 * 100)
                msg_recv_decoded = msg_recv.decode("utf-8")
                bottom_msg = msg_recv_decoded
                msg = "      Game Over     "
                break
            else:
                msg = recv_data_decoded

        except KeyboardInterrupt:
            print("\nKeyboard Interrupt")
            break

        except Exception as e:
            print(f"Error occurred: {e}")
            break

start_player()