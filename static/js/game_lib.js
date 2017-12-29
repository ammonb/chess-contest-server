

function send_message(socket, action, message) {
    var m = action.toUpperCase() + " " + message + "\n";
    console.log("Sending message " + m);
    socket.send(m);
}


function observe_game(game_id, status_div, white_name_div, black_name_div) {
    manage_game("", "", game_id, status_div, white_name_div, black_name_div, false);
}

function play_games(tournament_name, player_name, join_button, status_div, white_name_div, black_name_div) {
    manage_game(tournament_name, player_name, "", status_div, white_name_div, black_name_div, true);
}

function manage_game(tournament_name, player_name, game_id, status_div, white_name_div, black_name_div, play) {
    var socket = new WebSocket("ws://" + window.location.hostname + ":8081");

    var white_to_move = false;
    var you_are_white = true;
    var your_move = false;

    var white_name = "";
    var black_name = "";

    var white_time = 0.0;
    var black_time = 0.0;

    var move_sound = new Audio('audio/move.mp3');
    var gameover_sound = new Audio('audio/gameover.mp3');

    var board = ChessBoard('board', {onDrop: piece_moved, draggable: true});

    function piece_moved(source, target, piece, newPos, oldPos, orientation) {
        if (!your_move || target==='offboard') {
            return 'snapback';
        }
        var move = source + "-" + target;
        if ((piece === "wP" || piece === "bP") && (target.charAt(1) === '1' || target.charAt(1) === '8')) {
            move += "=Q";
        }

        console.log("Source: " + source);
        console.log("Target: " + target);
        console.log("Piece: " + piece);
        console.log("Move: " + move);
        send_message(socket, "MOVE", game_id + " " + move);
    }

    var time_update_id = null;
    function _dead_reckon_time() {
        if (white_to_move) {
            white_time -= 1.0;
        } else {
            black_time -= 1.0;
        }
        update_time_labels();
        time_update_id = setTimeout(_dead_reckon_time, 1000);
    }
    function start_dead_reckon_time() {
        if (time_update_id !== null) return;
        time_update_id = setTimeout(_dead_reckon_time, 1000);
    }

    function stop_dead_reckon_time() {
        if (time_update_id === null) return;
        window.clearTimeout(time_update_id);
        time_update_id = null;
    }
    function reset_dead_reckon_time() {
        stop_dead_reckon_time();
        start_dead_reckon_time();
    }

    socket.onopen = function (event) {
        if (play) {
            send_message(socket, "JOIN", tournament_name + " " + player_name);
        } else {
            send_message(socket, "WATCH", game_id);
        }
        status_div.innerHTML = "Connected";
    }

    function update_time_labels(message_parts) {




        white_name_div.innerHTML = white_name + ": " + Math.round(white_time * 100) / 100;
        black_name_div.innerHTML = black_name + ": " + Math.round(black_time * 100) / 100;
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
        var message_parts = message.split(" ").filter(word => word.length > 0);

        function do_state_update() {
            start_index = 1;
            white_name = message_parts[0 + start_index];
            black_name = message_parts[1 + start_index];
            white_time = Number(message_parts[2 + start_index]);
            black_time = Number(message_parts[3 + start_index]);
            update_time_labels();

            var fen = message_parts.slice(4 + start_index, message_parts.length).join(" ")
            board.position(fen);
            white_to_move = (message_parts[5 + start_index] === "w" || message_parts[5 + start_index] === "W")
        }

        if (action === "INFO") {
            status_div.innerHTML = message;
        } else if (action === "GAME_STATE") {
            do_state_update();
        } else if (action === "CLOCK_UPDATE") {
            do_state_update();
            reset_dead_reckon_time();
        } else if (action === "GAME_OVER") {
            gameover_sound.play();
            your_move = false;
            stop_dead_reckon_time();
        } else if (action === "PLAYER_MOVED") {
            move_sound.play();
            var fen = message_parts.slice(7, message_parts.length).join(" ");
            white_to_move = !white_to_move;
            white_time = Number(message_parts[5])
            black_time = Number(message_parts[6])
            update_time_labels();
            board.position(fen);
            your_move = false;

            reset_dead_reckon_time();
        } else if (action === "GAME_STARTED") {
            do_state_update();
            game_id = message_parts[0];
            you_are_white = (message_parts[1] === player_name);
            send_message(socket, "ACK", game_id);
            board.orientation(you_are_white ? "white" : "black");
        } else if (action === "YOUR_MOVE") {
            do_state_update();
            your_move = true;
        } else if (action === "GAME_ACKED") {
            start_dead_reckon_time();
        }
    }
}
