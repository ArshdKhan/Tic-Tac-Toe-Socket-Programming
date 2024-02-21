import socket
import ssl

server_socket = socket.socket()
host = "127.0.0.1"
port = 9999

# Create an SSL context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

# Load the server's certificate and private key
context.load_cert_chain('server.crt', 'server.key')

# Wrap the server's socket with SSL
ssl_server_socket = context.wrap_socket(server_socket, server_side=True)

matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

player_one = 1
player_two = 2

player_connections = list()
player_addresses = list()


def validate_input(x, y, conn):
    if x > 2 or y > 2:
        print("\nOut of bound! Enter again...\n")
        conn.send("Error".encode())
        return False
    elif matrix[x][y] != 0:
        print("\nAlready entered! Try again...\n")
        conn.send("Error".encode())
        return False
    return True


def get_input(current_player):
    if current_player == player_one:
        player_turn_msg = "Player One's Turn"
        conn = player_connections[0]
    else:
        player_turn_msg = "Player Two's Turn"
        conn = player_connections[1]
    print(player_turn_msg)
    send_common_msg(player_turn_msg)
    try:
        conn.send("Input".encode())
        data = conn.recv(2048 * 10)
        conn.settimeout(20)
        data_decoded = data.decode().split(",")
        x, y = int(data_decoded[0]), int(data_decoded[1])
        matrix[x][y] = current_player
        send_common_msg("Matrix")
        send_common_msg(str(matrix))
    except:
        conn.send("Error".encode())
        print("Error occurred! Try again..")


def check_rows():
    result = 0
    for i in range(3):
        if matrix[i][0] == matrix[i][1] and matrix[i][1] == matrix[i][2]:
            result = matrix[i][0]
            if result != 0:
                break
    return result


def check_columns():
    result = 0
    for i in range(3):
        if matrix[0][i] == matrix[1][i] and matrix[1][i] == matrix[2][i]:
            result = matrix[0][i]
            if result != 0:
                break
    return result


def check_diagonals():
    result = 0
    if matrix[0][0] == matrix[1][1] and matrix[1][1] == matrix[2][2]:
        result = matrix[0][0]
    elif matrix[0][2] == matrix[1][1] and matrix[1][1] == matrix[2][0]:
        result = matrix[0][2]
    return result


def check_winner():
    result = 0
    result = check_rows()
    if result == 0:
        result = check_columns()
    if result == 0:
        result = check_diagonals()
    return result


def start_server():
    try:
        ssl_server_socket.bind((host, port))
        print("Tic Tac Toe server started \nBinding to port", port)
        ssl_server_socket.listen(2)
        accept_players()
    except socket.error as e:
        print("Server binding error:", e)


def accept_players():
    try:
        for i in range(2):
            conn, addr = ssl_server_socket.accept()
            msg = "        You are player {}    ".format(i + 1)
            conn.send(msg.encode())

            player_connections.append(conn)
            player_addresses.append(addr)
            print("Player {} - [{}:{}]".format(i + 1, addr[0], str(addr[1])))

        start_game()
        ssl_server_socket.close()
    except socket.error as e:
        print("Player connection error", e)
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt")
        exit()
    except Exception as e:
        print("Error occurred:", e)


def start_game():
    result = 0
    i = 0
    while result == 0 and i < 9:
        if i % 2 == 0:
            get_input(player_one)
        else:
            get_input(player_two)
        result = check_winner()
        i += 1

    send_common_msg("Over")

    if result == 1:
        last_msg = "Player One is the winner!!"
    elif result == 2:
        last_msg = "Player Two is the winner!!"
    else:
        last_msg = "Draw game!! Try again later!"

    send_common_msg(last_msg)
    for conn in player_connections:
        conn.close()


def send_common_msg(text):
    player_connections[0].send(text.encode())
    player_connections[1].send(text.encode())


start_server()