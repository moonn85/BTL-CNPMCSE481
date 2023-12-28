document.addEventListener("DOMContentLoaded", function() {
    // Xác thực dữ liệu của form
    function validateForm(form) {
        var email = form["email"].value;
        var password = form["password"].value;
        var confirmPassword = form["confirmPassword"] ? form["confirmPassword"].value : null;

        if (!email || !password || (confirmPassword && password !== confirmPassword)) {
            alert("Vui lòng điền đầy đủ thông tin vào các trường.");
            return false;
        }
        return true;
    }

    // Yêu cầu AJAX cho việc đăng ký
    function registerUser() {
        var registerForm = document.getElementById('registerForm');
        if (registerForm && validateForm(registerForm)) {
            var formData = new FormData(registerForm);
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/register', true);
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        window.location.href = '/dn';
                    } else {
                        alert('Đăng ký thất bại');
                    }
                }
            };
            xhr.send(formData);
        }
    }

    // Yêu cầu AJAX cho việc đăng nhập
    function loginUser() {
        var loginForm = document.getElementById('loginForm');
        if (loginForm && validateForm(loginForm)) {
            var formData = new FormData(loginForm);
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/dn', true);
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        window.location.href = '/';
                    } else {
                        alert('Đăng nhập thất bại');
                    }
                }
            };
            xhr.send(formData);
        }
    }

    // Bắt sự kiện khi form được gửi đi
    var registerFormElement = document.getElementById('registerForm');
    var loginFormElement = document.getElementById('loginForm');

    if (registerFormElement) {
        registerFormElement.addEventListener('submit', function(event) {
            event.preventDefault();
            registerUser();
        });
    }

    if (loginFormElement) {
        loginFormElement.addEventListener('submit', function(event) {
            event.preventDefault();
            loginUser();
        });
    }
});

$(document).ready(function() {
    var socket = io.connect('http://127.0.0.1:5000');
    var $messages = $('#messages');
    var $inputMessage = $('#myMessage');

    $('#chat-icon').click(function(event) {
        event.preventDefault();
        $('#chatbox').toggle(); // Chuyển đổi trạng thái hiển thị của chat box
    });
    
    socket.on('receive_message', function(msg) {
        var messageType = msg.sender_id === "{{ sender_id }}" ? 'admin' : 'user'; // Xác định loại tin nhắn dựa trên sender_id
        var messageElement = $('<li class="message ' + messageType + '"><div class="message-content">' + msg.text + '</div></li>');
        $messages.append(messageElement);
        scrollToBottom();
    });

    // Giả sử bạn đã lưu trữ ID người dùng hiện tại trong localStorage
    var sender_id = localStorage.getItem('user_id');

    $('#messageForm').submit(function(e) {
        e.preventDefault();
        var messageText = $inputMessage.val().trim();
        if (messageText) {
            socket.emit('send_message', {
                sender_id: sender_id, // Sử dụng ID người dùng hiện tại
                receiver_id: 1, // Gửi trả lời đến ID người gửi
                text: messageText
            });
            // Thêm tin nhắn đã gửi vào giao diện người dùng
            var messageElement = $('<li class="message user"><div class="message-content">' + messageText + '</div></li>');
            $messages.append(messageElement);
            scrollToBottom();

            $inputMessage.val('');
        }
    });

    function scrollToBottom() {
        $messages.scrollTop($messages[0].scrollHeight);
    }
});