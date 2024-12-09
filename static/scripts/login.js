const emailField = document.getElementById('login_form_email')
const passwordField = document.getElementById('login_form_password')
const loginBtn = document.getElementById('login_form_btn')

loginBtn.addEventListener('click', (e) => {
    emailField.parentElement.childNodes[2].textContent = ''
    passwordField.parentElement.childNodes[2].textContent = ''
    fetch('/login', {
      method: 'POST',
      body: JSON.stringify({
          email: emailField.value,
          password: passwordField.value
      }),
      headers: {
        'Content-type': 'application/json; charset=UTF-8',
      },
    })
    .then(async (response) => {
        if (response.status === 200) {
            document.location.href = '/'
            return
        }
        if (response.status === 401) {
            passwordField.parentElement.childNodes[2].textContent = 'Wrong combination of email and password'
            return
        }
        if (response.status === 422) {
            response_json = await response.json()
            Object.keys(response_json).forEach(key => {
                if (key === 'email') {
                    emailField.parentElement.childNodes[2].textContent = response_json[key][0]['message']
                } else if (key === 'password') {
                    passwordField.parentElement.childNodes[2].textContent = response_json[key][0]['message']
                }
            })
            return
        }
    })
});
