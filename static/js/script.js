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
