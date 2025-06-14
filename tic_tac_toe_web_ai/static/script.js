let board = [];
let aiEnabled = false;
let playerNames = { X: "Player X", O: "Player O" };

function startGame() {
    playerNames.X = document.getElementById("playerX").value || "Player X";
    playerNames.O = document.getElementById("playerO").value || "Player O";
    aiEnabled = document.getElementById("aiToggle").checked;
    resetGame();
    updateScoreboard();
    updateLeaderboard();
}

function makeMove(index) {
    fetch("/move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ index: index, ai: aiEnabled, names: playerNames })
    })
    .then(res => res.json())
    .then(data => {
        board = data.board;
        updateBoard();
        document.getElementById("message").innerText = data.message;
        updateScoreboard(data.scores);
        if (data.game_over) updateLeaderboard();
    });
}

function updateBoard() {
    const boardDiv = document.getElementById("board");
    boardDiv.innerHTML = "";
    board.forEach((cell, idx) => {
        const div = document.createElement("div");
        div.className = "cell";
        if (cell !== " ") div.classList.add("played");
        div.innerText = cell;
        div.onclick = () => makeMove(idx);
        boardDiv.appendChild(div);
    });
}

function resetGame() {
    fetch("/reset", { method: "POST" })
    .then(res => res.json())
    .then(data => {
        board = data.board;
        updateBoard();
        document.getElementById("message").innerText = "Game reset!";
        updateScoreboard(data.scores);
    });
}

function updateScoreboard(scores = {}) {
    const scoreDiv = document.getElementById("scoreboard");
    let html = `
        <div>${playerNames.X}: ${scores[playerNames.X] || 0}</div>
        <div>${playerNames.O}: ${scores[playerNames.O] || 0}</div>
        <div>Draws: ${scores["Draws"] || 0}</div>
    `;
    scoreDiv.innerHTML = html;
}

function updateLeaderboard() {
    fetch("/leaderboard")
        .then(res => res.json())
        .then(scores => {
            const lb = document.getElementById("leaderboard");
            const entries = Object.entries(scores).sort((a, b) => b[1] - a[1]);
            lb.innerHTML = entries.map(([name, score]) => `<div>${name}: ${score}</div>`).join("");
        });
}

document.addEventListener("DOMContentLoaded", () => {
    startGame();
});
