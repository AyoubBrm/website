const chatSocket = new WebSocket(`ws://${window.location.host}/ws/chat/`);

chatSocket.onopen = function(e) {
    console.log('WebSocket connection established!');
}

chatSocket.onmessage = function(event) {
    const message = event.data;
    console.log('Received message:', message);
    // Display the message in the chat UI
};

function sendMessage(message) {
    chatSocket.send(message);
}