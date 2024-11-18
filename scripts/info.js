// const countrySelect = document.getElementById('country')
// const citySelect = document.getElementById('city')
const submitBtn = document.getElementById('submit_btn')
const uploadButton = document.getElementById('cv-upload')
const logoutButton = document.getElementById('logout')

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
    fetch("/info", {
        method: "PATCH",
        body: JSON.stringify({
            name: name,
            surname: surname,
            birthday: birthday
        }),
        headers: {
            'Content-type': 'application/json; charset=UTF-8',
        },
    })
    .then(async (response) => {
        if (response.status === 200) {
            alert('Successfully updated user info')
            return
        }
        response_json = await response.json()
        Object.keys(response_json).forEach(key => {
            if (key === 'api_key') {
                document.location.href = '/cookie'
                return
            } else if (key === 'name') {
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

const CVField = document.getElementById('cv-filefield')

uploadButton.addEventListener('click', (e) => {
    if (CVField.files.length === 0) {
        CVField.parentElement.childNodes[2].textContent = 'Select a file to upload'
        return
    }
    let formData = new FormData()
    formData.append('cv', CVField.files[0])
    fetch("/info/cv", {
        method: "POST",
        body: formData
    })
    .then(async (response) => {
        if (response.status === 200) {
            alert('Successfully uploaded CV')
            return
        }
        response_json = await response.json()
        Object.keys(response_json).forEach(key => {
            if (key === 'api_key') {
                document.location.href = '/cookie'
                return
            }
            // no errors here yet
        })
    })
})

deleteButtons = document.getElementsByClassName('cv-delete')

//Array.from(deleteButtons).forEach((e) => {
//    // ...
//})

logoutButton.addEventListener('click', (e) => {
    fetch("/logout", {
        method: "POST"
    })
    .then((response) => {
        document.location.href = '/'
        return
    })
})
