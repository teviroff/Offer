// const countrySelect = document.getElementById('country')
// const citySelect = document.getElementById('city')
const submitBtn = document.getElementById('submit_btn')
const uploadButton = document.getElementById('cv-upload')
const logoutButton = document.getElementById('logout')

function saveCV(saveButton) {
    id = saveButton.parentElement.getAttribute("cv_id")
    nameInput = saveButton.parentElement.getElementsByClassName("cv-name")[0]
    nameInput.parentElement.children[1].textContent = ''
    fetch("/me/cv", {
        method: "PATCH",
        body: JSON.stringify({
            cv_id: parseInt(id),
            name: nameInput.value
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8",
        },
    })
    .then(async (response) => {
        if (response.status === 200) {
            alert('Successfully updated CV, reload page to see changes')
            return
        }
        response_json = await response.json()
        Object.keys(response_json).forEach(key => {
            if (key === 'cv_id') {
                updateCVList()
                return
            } else if (key === 'name') {
                nameInput.parentElement.children[1].textContent = response_json[key][0]['message']
            }
        })
    })
}

function deleteCV(deleteButton) {
    id = deleteButton.parentElement.getAttribute("cv_id")
    fetch("/me/cv", {
        method: "DELETE",
        body: JSON.stringify({
            cv_id: parseInt(id)
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8",
        },
    })
    .then(async (response) => {
        if (response.status === 200) {
            updateCVList()
            return
        }
        response_json = await response.json()
        Object.keys(response_json).forEach(key => {
            if (key === 'cv_id') {
                updateCVList()
                return
            }
        })
    })
}

function updateCVList() {
    const cvs_container = document.getElementById('cvs-container')
    //cvs_container.textContent = ''  // delete all children
    fetch("/me/cvs", {
        method: "GET"
    })
    .then(async (response) => {
        if (response.status === 200) {
            cvs_container.innerHTML = await response.text()
            Array.from(cvs_container.children).forEach((child) => {
                saveButton = child.getElementsByClassName("cv-save")[0]
                deleteButton = child.getElementsByClassName("cv-delete")[0]
                saveButton.addEventListener("click", (e) => {
                    saveCV(saveButton)
                })
                deleteButton.addEventListener("click", (e) => {
                    deleteCV(deleteButton)
                })
            })
            return
        }
        cvs_container.textContent = 'Some error occured, refresh page to see your CVs'
    })
}

document.addEventListener('DOMContentLoaded', () => {
    updateCVList()
    const avatarUploadButton = document.getElementById("avatar-upload")
    const avatarField = document.getElementById("avatar-field")
    const avatarImg = document.getElementById("avatar-img")
    avatarUploadButton.addEventListener("click", (e) => {
        if (avatarField.files.length === 0) {
            avatarField.parentElement.children[1].textContent = 'Select a file to upload'
            return
        }
        let formData = new FormData()
        formData.append('avatar', avatarField.files[0])
        fetch("/me/avatar", {
            method: "POST",
            body: formData
        })
        .then(async (response) => {
            if (response.status === 200) {
                temp = avatarImg.src
                avatarImg.src = ''
                avatarImg.src = temp + "?" + new Date().getTime();
                return
            }
            response_json = await response.json()
            Object.keys(response_json).forEach(key => {
                // no errors here yet
            })
        })
    })
})

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
    fetch("/me", {
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

const CVField = document.getElementById('cv-filefield')

uploadButton.addEventListener('click', (e) => {
    if (CVField.files.length === 0) {
        CVField.parentElement.childNodes[2].textContent = 'Select a file to upload'
        return
    }
    let formData = new FormData()
    formData.append('cv', CVField.files[0])
    fetch("/me/cv", {
        method: "POST",
        body: formData
    })
    .then(async (response) => {
        if (response.status === 200) {
            updateCVList()
            return
        }
        response_json = await response.json()
        Object.keys(response_json).forEach(key => {
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
