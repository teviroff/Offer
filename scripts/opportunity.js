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

function submitOpportunityForm() {
    const formContainer = document.getElementById("form-container")
    formData = {}
    for (let child of formContainer.children) {
        const field_data = child.getElementsByClassName("form-field-data")
        const label_data = child.getElementsByClassName("form-label-data")[0]
        const select_data = child.getElementsByClassName("form-select-data")[0]

        const classAttr = child.getAttribute("class")

        switch (classAttr) {
            case "string-form-field":
                if (field_data[0].length > 128) {
                    label_data[0].innerText += "String variable must be less 128 characters"
                    return
                }
                break
            case "regex-form-field":
                regex_string = field_data[0].getAttribute("pattern")
                if (!new RegExp(regex_string).test(field_data[0].innerText)) {
                    label_data[0].innerText += "String must match the regex " + regex_string
                    return
                }
                break
        }

        if (field_data.length > 0) {
            formData[label_data.innerText] = field_data[0].value;
        } else {
            formData[label_data.innerText] = select_data.options[select_data.selectedIndex].text;
        }
    }
    console.log(JSON.stringify(formData));
    fetch(`...`, {
        method: "POST",
        body: JSON.stringify(formData),
        headers: {
            'Content-type': 'application/json; charset=UTF-8',
        },
    })
    .then(async (response) => {
        if (response.status === 200) {
            response_json = JSON.parse(await response.json());
            Object.keys(response_json).forEach(key => {
                response_json[key].forEach(error => {
                    const form_field = formContainer.querySelectorAll('[field_name=key]')
                    if (form_field) {
                        form_field.innerText += error;
                    } else {
                        getForm()
                    }
                })
            })
        }
    })
}

document.getElementById("submit-btn").addEventListener('click', () => {
    submitOpportunityForm()
})

document.addEventListener("DOMContentLoaded", () => {
    getDescription()
    getForm()
})
