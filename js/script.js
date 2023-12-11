document.addEventListener("DOMContentLoaded", function() {
    // Validate form data
    function validateForm(form) {
        var email = form["email"].value;
        var password = form["password"].value;
        var confirmPassword = form["confirmPassword"] ? form["confirmPassword"].value : null;

        if (!email || !password || (confirmPassword && password !== confirmPassword)) {
            alert("Please fill out all fields correctly.");
            return false;
        }
        return true;
    }

    // AJAX Request for Registration
    function registerUser() {
        var registerForm = document.getElementById('registerForm');
        if (registerForm && validateForm(registerForm)) {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/register', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        window.location.href = '/dn';
                    } else {
                        alert('Registration failed');
                    }
                }
            };
            var data = JSON.stringify({
                email: registerForm['email'].value,
                phone: registerForm['phone'].value,
                password: registerForm['password'].value,
                confirm_password: registerForm['confirm_password'].value
            });
            xhr.send(data);
        }
    }

    // AJAX Request for Login
    function loginUser() {
        var loginForm = document.getElementById('loginForm');
        if (loginForm && validateForm(loginForm)) {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/dn', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        window.location.href = '/';
                    } else {
                        alert('Login failed');
                    }
                }
            };
            var data = JSON.stringify({
                email: loginForm['email'].value,
                password: loginForm['password'].value
            });
            xhr.send(data);
        }
    }

    // Event listener for form submissions
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
