(function() {

    var section = document.querySelector("#log");

    var startDate = moment();

    var isAtBottom = function() {
        var main = section.querySelector("main");
        return Math.abs((main.scrollTop + main.clientHeight) - main.scrollHeight) <= 10;
    };

    var scrollToBottom = function() {
        var main = section.querySelector("main");
        main.scrollTop = main.scrollHeight;
    };

    var log = function(message) {
        var tbody = section.querySelector("table tbody");
        var newRow = tbody.insertRow(tbody.rows.length);

        var shouldScroll = isAtBottom();

        var dateStr = moment().format("HH:mm:ss");
        newRow.insertCell(0).appendChild(document.createTextNode(dateStr));

        newRow.insertCell(1).appendChild(document.createTextNode(message));

        if (shouldScroll) {
            scrollToBottom();
        }
    };

    var randomString = function() {
        var text = "";
        // letter density is based on scrabble tile value
        var letters = "aaaaaaaaaabbbbbbbbccccccccdddddddddeeeeeeeeeefffffffggggggggghhhhhhhiiiiiiiiiijjjkkkkkkllllllllllmmmmmmmmnnnnnnnnnnoooooooooooppppppppqrrrrrrrrrrssssssssssttttttttttuuuuuuuuuuuvvvvvvvwwwwwwwwxxxyyyyyyyz                                        ";
        var length = Math.floor(15 + 150 * Math.random());

        for (var i = 0; i < length; i++) {
            text += letters.charAt(Math.floor(Math.random() * letters.length));
        }

        return text;
    };

    var logForever = function() {
        log(randomString());
        setTimeout(logForever, Math.random() * 2000);
    };

    scrollToBottom();
    logForever();

}());
