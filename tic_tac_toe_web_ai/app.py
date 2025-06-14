from flask import Flask, render_template, request, jsonify
import json, os

app = Flask(__name__)

board = [" " for _ in range(9)]
current_player = "X"
game_over = False
ai_enabled = False
player_names = {"X": "Player X", "O": "Player O"}
leaderboard_file = "leaderboard.json"

win_combos = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]

if os.path.exists(leaderboard_file):
    with open(leaderboard_file, "r") as f:
        scores = json.load(f)
else:
    scores = {}

def save_leaderboard():
    with open(leaderboard_file, "w") as f:
        json.dump(scores, f)

def check_winner(b):
    for a, b_, c in win_combos:
        if b[a] == b[b_] == b[c] != " ":
            return b[a]
    return None

def is_draw(b): return " " not in b

def minimax(b, is_max):
    winner = check_winner(b)
    if winner == "O": return 1
    elif winner == "X": return -1
    elif is_draw(b): return 0

    if is_max:
        best = -float("inf")
        for i in range(9):
            if b[i] == " ":
                b[i] = "O"
                best = max(best, minimax(b, False))
                b[i] = " "
        return best
    else:
        best = float("inf")
        for i in range(9):
            if b[i] == " ":
                b[i] = "X"
                best = min(best, minimax(b, True))
                b[i] = " "
        return best

def best_move():
    best_val = -float("inf")
    move = -1
    for i in range(9):
        if board[i] == " ":
            board[i] = "O"
            val = minimax(board, False)
            board[i] = " "
            if val > best_val:
                move = i
                best_val = val
    return move

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/move", methods=["POST"])
def move():
    global board, current_player, game_over, ai_enabled, player_names

    data = request.get_json()
    index = data["index"]
    ai_enabled = data.get("ai", False)
    player_names = data.get("names", player_names)

    if game_over or board[index] != " ":
        return jsonify({ "board": board, "scores": scores, "message": "Invalid move", "game_over": game_over })

    board[index] = current_player
    winner = check_winner(board)

    if winner:
        name = player_names.get(winner, winner)
        scores[name] = scores.get(name, 0) + 1
        game_over = True
        save_leaderboard()
        return jsonify({ "board": board, "scores": scores, "message": f"{name} wins!", "game_over": True })

    if is_draw(board):
        scores["Draws"] = scores.get("Draws", 0) + 1
        game_over = True
        save_leaderboard()
        return jsonify({ "board": board, "scores": scores, "message": "It's a draw!", "game_over": True })

    current_player = "O" if current_player == "X" else "X"

    if ai_enabled and current_player == "O":
        ai_index = best_move()
        if ai_index != -1:
            board[ai_index] = "O"
            winner = check_winner(board)
            if winner:
                name = player_names.get("O", "O")
                scores[name] = scores.get(name, 0) + 1
                game_over = True
                save_leaderboard()
                return jsonify({ "board": board, "scores": scores, "message": f"{name} wins!", "game_over": True })
            if is_draw(board):
                scores["Draws"] = scores.get("Draws", 0) + 1
                game_over = True
                save_leaderboard()
                return jsonify({ "board": board, "scores": scores, "message": "It's a draw!", "game_over": True })
            current_player = "X"

    return jsonify({ "board": board, "scores": scores, "message": "Next move", "game_over": False })

@app.route("/reset", methods=["POST"])
def reset():
    global board, current_player, game_over
    board = [" " for _ in range(9)]
    current_player = "X"
    game_over = False
    return jsonify({ "message": "Game reset", "board": board, "current": current_player, "scores": scores })

@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    return jsonify(scores)

if __name__ == "__main__":
    app.run(debug=True)
