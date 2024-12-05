function transformTags() {
    const tagsContainer = document.getElementById("tags-container")
    const tagsJSON = tagsContainer.children[0].innerText
    JSON.parse(tagsJSON).forEach((tag) => {
        tagsContainer.appendChild(createTag(tag["id"], tag["name"]))
    })
    tagsContainer.removeChild(tagsContainer.children[0])
}

function transformGeoTags() {
    const geotagsContainer = document.getElementById("geotags-container")
    const tagsJSON = geotagsContainer.children[0].innerText
    JSON.parse(tagsJSON).forEach((tag) => {
        geotagsContainer.appendChild(createGeoTag(tag["id"], tag["name"]))
    })
    geotagsContainer.removeChild(geotagsContainer.children[0])
}

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
            submitButton = document.getElementById("form-submit-button")
            submitButton.addEventListener('click', submitOpportunityForm)
            return
        }
        formContainer.textContent = "Some error occured, refresh page to see opportunity response form"
    })
}

function submitOpportunityForm() {
    const fieldsContainer = document.getElementById("form-fields-container")
    formData = {}
    url_parts = document.location.href.split('/')
    formData['opportunity_id'] = url_parts[url_parts.length - 1]
    formData['data'] = {}
    for (let child of fieldsContainer.children) {
        const field_data = child.getElementsByClassName("form-field-data")
        const select_data = child.getElementsByClassName("form-select-data")[0]

        const errorsField = child.getElementsByClassName("form-field-errors")
        if (errorsField.length != 1) {
            getForm()
            return
        }
        errorsField[0].innerText = ""

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
            getForm()
            return
        }
        response_json = await response.json()
        Object.keys(response_json).forEach(key => {
            response_json[key].forEach(error => {
                const form_field = fieldsContainer.querySelectorAll(`[field_name=${key}]`)
                if (form_field.length == 1) {
                    errorsField = form_field[0].getElementsByClassName("form-field-errors")
                    if (errorsField.length != 1) {
                        getForm()
                        return
                    }
                    errorsField[0].innerText += error['message']
                } else {
                    getForm()
                    return
                }
            })
        })
    })
}

document.addEventListener("DOMContentLoaded", () => {
    transformTags()
    transformGeoTags()
    getDescription()
    getForm()
})
