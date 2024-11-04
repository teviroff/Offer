const emailField = document.getElementById("login_form_email")
const passwordField = document.getElementById("login_form_password")
const loginBtn = document.getElementById("login_form_btn")

loginBtn.addEventListener('click', (e) => {
    fetch("/login", {
      method: "POST",
      body: JSON.stringify({
          email: emailField.value,
          password: passwordField.value
      }),
      headers: {
        "Content-type": "application/json; charset=UTF-8",
      },
    })
    .then((response) => {
        if (response.status === 200) {
            console.log(10)
            document.location.href = "/"
        } else {
            emailField.parentElement.childNodes[2].textContent = "вы инвалид))"
        }
    })
    // .then((json) => {
    //    console.log(json)
    // });
});
