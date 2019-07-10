var socket = io.connect('http://localhost:5000');

socket.on('user login/logout', function(data) {
    console.log(data.data)
    updateUserCount(data.data)
});

function updateUserCount(count) {
    document.getElementById('userCount').textContent = count;
}
