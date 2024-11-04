const emailField = document.getElementById("login_form_email")
const passwordField = document.getElementById("login_form_password")
const loginBtn = document.getElementById("login_form_btn")

loginBtn.addEventListener('click', (e) => {
    fetch("/register", {
      method: "POST",
      body: JSON.stringify({
          email: emailField.value,
          password: passwordField.value
      }),
      headers: {
        "Content-type": "application/json; charset=UTF-8",
      },
    })
    .then((response) => response.json())
    .then((json) => {
        if (Object.keys(json).length === 0) {
            window.location.href = "login"
            console.log(10)
        } else {
            Object.keys(json).forEach(key => {
                console.log(key)
                console.log(emailField.parentElement.childNodes[1])
                if (key === 'email') {
                    emailField.parentElement.childNodes[2].textContent = json[key][0]['message']
                } else if (key === 'password') {
                    passwordField.parentElement.childNodes[2].textContent = json[key][0]['message']
                }
            })
        }
        console.log(json)
    });
});
