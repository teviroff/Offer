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
    url_parts = document.location.href.split('/')
    console.log(url_parts[url_parts.length - 1])
    formData['opportunity_id'] = url_parts[url_parts.length - 1]
    formData['data'] = {}
    for (let child of formContainer.children) {
        const field_data = child.getElementsByClassName("form-field-data")
        const select_data = child.getElementsByClassName("form-select-data")[0]

//        const classAttr = child.getAttribute("class")

//        switch (classAttr) {
//            case "string-form-field":
//                if (field_data[0].length > 128) {
//                    label_data[0].innerText += "String variable must be less 128 characters"
//                    return
//                }
//                break
//            case "regex-form-field":
//                regex_string = field_data[0].getAttribute("pattern")
//                if (!new RegExp(regex_string).test(field_data[0].innerText)) {
//                    label_data[0].innerText += "String must match the regex " + regex_string
//                    return
//                }
//                break
//        }

        if (field_data.length > 0) {
            formData['data'][child.getAttribute('field_name')] = field_data[0].value;
        } else {
            formData['data'][child.getAttribute('field_name')] = select_data.options[select_data.selectedIndex].text;
        }
    }
    fetch(`/opportunity/form`, {
        method: "POST",
        body: JSON.stringify(formData),
        headers: {
            'Content-type': 'application/json; charset=UTF-8',
        },
    })
    .then(async (response) => {
        if (response.status === 200) {
            alert('Successfuly submitted for an opportunity')
            return
        }
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
    })
}

document.getElementById("submit-btn").addEventListener('click', () => {
    submitOpportunityForm()
})

document.addEventListener("DOMContentLoaded", () => {
    getDescription()
    getForm()
})
