function getDescription() {
    const descriptionContainer = document.getElementById("description-container")
    fetch(`${document.location.href}/description`, {
        method: "GET"
    })
    .then(async (response) => {
        if (response.status === 200) {
            descriptionContainer.innerHTML = (new showdown.Converter()).makeHtml(await response.text())
            return
        }
        descriptionContainer.textContent = "Some error occured, refresh page to see opportunity description"
    })
}

function getForm() {
    const formContainer = document.getElementById("form-container")
    fetch(`${document.location.href}/form`, {
        method: "GET"
    })
    .then(async (response) => {
        if (response.status === 200) {
            formContainer.innerHTML = await response.text()
            // ...
            return
        }
        formContainer.textContent = "Some error occured, refresh page to see opportunity response form"
    })
}

document.addEventListener("DOMContentLoaded", () => {
    getDescription()
    getForm()
})
