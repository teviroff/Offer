function getCookie(name) {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}

// const countrySelect = document.getElementById('country')
// const citySelect = document.getElementById('city')
const submitBtn = document.getElementById('submit_btn')

// updateCitySelect = () => {
//     fetch("/getcities", {
//       method: "POST",
//       body: JSON.stringify({
//           country: countrySelect.value
//       }),
//       headers: {
//         "Content-type": "application/json; charset=UTF-8",
//       },
//     })
//     .then((response) => response.json())
//     .then((json) => {
//         console.log(json)
//         citySelect.innerHTML = ''
//         json.forEach(city => {
//             let newOption = document.createElement('option')
//             newOption.value = city
//             newOption.innerText = city
//             citySelect.appendChild(newOption)
//         })
//     });
// }
// updateCitySelect();

// countrySelect.addEventListener('change', (e) => {
//     console.log(e)
//     console.log(countrySelect.value)
//     updateCitySelect();
// });

const nameField = document.getElementById('namefield')
const surnameField = document.getElementById('surnamefield')
const birthdayField = document.getElementById('datefield')

submitBtn.addEventListener('click', (e) => {
    let user_id = getCookie('user_id')
    if (user_id === undefined) {
        document.location.href = '/login'
        return
    } else {
        user_id = parseInt(user_id)
    }
    let name = null
    if (nameField.value.length > 0)
        name = nameField.value
    let surname = null
    if (surnameField.value.length > 0)
        surname = surnameField.value
    let birthday = null
    if (birthdayField.value.length > 0) {
        let [year, month, day] = birthdayField.value.split('-')
        birthday = {
            day: parseInt(day),
            month: parseInt(month),
            year: parseInt(year)
        }
    }
    fetch("/api/user/info", {
        method: "PATCH",
        body: JSON.stringify({
            user_id: user_id,
            name: name,
            surname: surname,
            birthday: birthday
        }),
        headers: {
            'Content-type': 'application/json; charset=UTF-8',
        },
    })
    .then(async (response) => {
        if (response.status === 200)
            return
        response_json = await response.json()
        Object.keys(response_json).forEach(key => {
            if (key === 'name') {
                nameField.parentElement.childNodes[2].textContent = response_json[key][0]['message']
            } else if (key === 'surname') {
                surnameField.parentElement.childNodes[2].textContent = response_json[key][0]['message']
            } else if (key === 'birthday') {
                // you are doing something wrong, if you are here
                // birthdayField.parentElement.childNodes[2].textContent = response_json[key]['message']
            }
        })
    })
})