

function send_message(socket, action, message) {
    var m = action.toUpperCase() + " " + message + "\n";
    console.log("Sending message " + m);
    socket.send(m);
}


function observe_game(board, game_id, status_div, white_name_div, black_name_div, pgn_div) {
    var socket = new WebSocket("ws://127.0.0.1:8081");
    var white_to_move = false;

    var white_name = "";
    var black_name = "";

    var white_time = 0.0;
    var black_time = 0.0;

    var move_sound = new Audio('audio/move.mp3');
    var gameover_sound = new Audio('audio/gameover.mp3');

    socket.onopen = function (event) {
        send_message(socket, "WATCH", game_id);
    }

    function update_time_labels(message_parts) {
        white_name_div.innerHTML = white_name + ": " + white_time;
        black_name_div.innerHTML = black_name + ": " + black_time;
        if (white_to_move) {
            white_name_div.innerHTML = "<b>" + white_name_div.innerHTML + "</b>"
        } else {
            black_name_div.innerHTML = "<b>" + black_name_div.innerHTML + "</b>"
        }
    }

    socket.onmessage = function (event) {
        console.log("Got message: " + event.data);
        var parts = event.data.split(" ");
        var action = parts.shift();
        var message = parts.join(" ").trim();
        var message_parts = message.split(" ").filter(word => word.length > 0)

        if (action === "INFO") {
            status_div.innerHTML = message;
        } else if (action === "GAME_STATE") {
            var fen = message_parts.slice(5, message_parts.length).join(" ");
            board.position(fen);
            white_to_move = (message_parts[6] === "w" || message_parts[6] === "W")
            white_name = message_parts[1];
            black_name = message_parts[2];
            white_time = Number(message_parts[3]);
            black_time = Number(message_parts[4]);
            update_time_labels();
        } else if (action === "CLOCK_UPDATE") {
            white_time = Number(message_parts[3]);
            black_time = Number(message_parts[4]);
            update_time_labels();

        } else if (action === "GAME_OVER") {
            gameover_sound.play();
            status_div.innerHTML = "Game over: " + message_parts.slice(1, message_parts.length).join(" ")
        } else if (action === "PLAYER_MOVED") {
            move_sound.play();
            var fen = message_parts.slice(7, message_parts.length).join(" ");
            console.log("fen: " + fen);
            white_to_move = !white_to_move;
            white_time = Number(message_parts[5])
            black_time = Number(message_parts[6])
            update_time_labels();
            board.position(fen);
        }
        //PLAYER_MOVED ea209b9eeb2a11e7a4ef48d705daa9ad a d2-d4 a b 278.94 300.00 rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1
    }
}
//setTimeout(function() { your_func(); }, 5000);


//GAME_STATE cce43542ea9e11e7b5ef48d705daa9ad b a 289.200165987 300.0 rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

// function connect_to_server() {
//     var user_name = document.getElementById("user_name").value;
//     var tournament = document.getElementById("tournament").value;
//     var button = document.getElementById("connect_button")
//     var status_div =  document.getElementById("connection_status")
//     var info_div =  document.getElementById("server_info")

//     var socket = new WebSocket("ws://127.0.0.1:8081");
//     var game_id;

//     var board = ChessBoard('board', {orientation:'white'});

//     function send_message(action, message) {
//         var m = action.toUpperCase() + " " + message + "\n";
//         console.log("Sending message " + m);
//         socket.send(m);
//     }

//     socket.onopen = function (event) {
//         button.disabled = true;
//         status_div.innerHTML = "Connected";
//         send_message("JOIN", tournament + " " + user_name);
//     }

//     socket.onmessage = function (event) {
//         console.log("Got message: " + event.data);
//         var parts = event.data.split(" ");
//         var action = parts.shift();
//         var message = parts.join(" ").trim();
//         var message_parts = message.split(" ").filter(word => word.length > 0)

//         if (action === "INFO") {
//             info_div.innerHTML = message;
//         } else if (action === "GAME_STARTED") {
//             game_id = message_parts[0];
//             send_message("ACK", game_id);
//             if (message_parts[1] == user_name) {
//                 board = ChessBoard('board', {orientation:'white'});
//             } else {
//                 board = ChessBoard('board', {orientation:'black'});
//             }
//         }
//     }

//     socket.onclose = function (event) {
//         status_div.innerHTML = "Not connected";
//         button.disabled = false;
//     }
//     console.log();
// }


