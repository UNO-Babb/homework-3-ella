#Example Flask App for a hexaganal tile game
#Logic is in this python file

from flask import Flask, render_template_string, request, jsonify
import random

app = Flask(__name__)

# Game Setup
class Game:
    def __init__(self):
        self.players = {
            "Player 1": {"position": 0, "medallions": [], "color": "red"},
            "Player 2": {"position": 6, "medallions": [], "color": "blue"},
            "Player 3": {"position": 12, "medallions": [], "color": "green"},
            "Player 4": {"position": 18, "medallions": [], "color": "yellow"},
        }
        self.turn = "Player 1"
        self.board_size = 24
        self.questions = [
            {"question": "What is the capital of France?", "answer": "Paris"},
            {"question": "What is 5 + 7?", "answer": "12"},
            {"question": "What color are emeralds?", "answer": "Green"}
        ]

    def roll_dice(self, value, direction):
        player = self.players[self.turn]
        if direction == "clockwise":
            player["position"] = (player["position"] + value) % self.board_size
        else:
            player["position"] = (player["position"] - value) % self.board_size
        return True

    def ask_question(self):
        return random.choice(self.questions)

    def answer_question(self, user_answer):
        question = self.ask_question()
        correct_answer = question["answer"]

        if user_answer.lower() == correct_answer.lower():
            return True
        else:
            self.next_turn()
            return False

    def next_turn(self):
        player_order = list(self.players.keys())
        current_index = player_order.index(self.turn)
        self.turn = player_order[(current_index + 1) % len(player_order)]

    def get_state(self):
        return {"turn": self.turn, "players": self.players}

game = Game()

@app.route('/')
def index():
    question = game.ask_question()  # Get a question for the initial display
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Trippy Trivia</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; }
            .board { display: grid; grid-template-columns: repeat(5, 80px); width: 400px; margin: auto; }
            .cell { width: 80px; height: 80px; border: 1px solid black; display: flex; justify-content: center; align-items: center; position: relative; }
            .player { width: 20px; height: 20px; border-radius: 50%; position: absolute; }
            .red { background-color: red; }
            .blue { background-color: blue; }
            .green { background-color: green; }
            .yellow { background-color: yellow; }
        </style>
        <script>
            function rollDice(direction) {
                fetch('/roll_dice', {
                    method: 'POST',
                    body: JSON.stringify({ "direction": direction }),
                    headers: { 'Content-Type': 'application/json' }
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('gameState').innerText = JSON.stringify(data.game_state, null, 2);
                    alert("You rolled a " + data.dice);
                    updateBoard(data.game_state.players);
                    document.getElementById('question').innerText = data.question.question;  // Show the trivia question
                    document.getElementById('answerInput').value = '';  // Clear the input
                });
            }

            function submitAnswer() {
                let answer = document.getElementById("answerInput").value;
                fetch('/answer_question', {
                    method: 'POST',
                    body: JSON.stringify({ "answer": answer }),
                    headers: { 'Content-Type': 'application/json' }
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('gameState').innerText = JSON.stringify(data.game_state, null, 2);
                    alert(data.correct ? "Correct!" : "Wrong answer.");
                    if (!data.correct) {
                        document.getElementById('question').innerText = "";  // Clear question if answer is wrong
                    }
                });
            }

            function updateBoard(players) {
                document.querySelectorAll(".player").forEach(e => e.remove());
                for (let player in players) {
                    let pos = players[player].position;
                    let color = players[player].color;
                    let cell = document.getElementById(`cell-${pos}`);
                    let piece = document.createElement("div");
                    piece.className = "player " + color;
                    cell.appendChild(piece);
                }
            }
        </script>
    </head>
    <body>
        <h1>Trippy Trivia</h1>
        <p>Choose a direction and roll the dice:</p>
        <button onclick="rollDice('clockwise')">Roll Clockwise</button>
        <button onclick="rollDice('counterclockwise')">Roll Counterclockwise</button>
        
        <h2>Answer Trivia</h2>
        <p id="question">{{ question["question"] }}</p>
        <input type="text" id="answerInput" placeholder="Type your answer">
        <button onclick="submitAnswer()">Submit Answer</button>

        <h3>Game Board</h3>
        <div class="board">
            {% for i in range(24) %}
                <div id="cell-{{ i }}" class="cell"></div>
            {% endfor %}
        </div>

        <h3>Game State</h3>
        <pre id="gameState"></pre>
    </body>
    </html>
    """, question=question, game_state=game.get_state())

@app.route('/roll_dice', methods=['POST'])
def roll_dice():
    dice_value = random.randint(1, 6)
    direction = request.json.get("direction")
    game.roll_dice(dice_value, direction)
    question = game.ask_question()  # Get a new question after the dice roll
    return jsonify({"dice": dice_value, "game_state": game.get_state(), "question": question})

@app.route('/answer_question', methods=['POST'])
def answer_question():
    user_answer = request.json.get("answer")
    correct = game.answer_question(user_answer)
    return jsonify({"correct": correct, "game_state": game.get_state()})

if __name__ == '__main__':
    app.run(debug=True)
