let defaultTabId = 0
let activeTabId = 0

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

function createErrorBlock(error_string) {
    const p_block = document.createElement("p");
    p_block.innerText = error_string;
    return p_block;
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
        const classAttr = child.getAttribute("class")
        console.log(classAttr)

        if (classAttr === "string-form-field") {
            const string_field = child.getElementsByClassName("form-field-data")[0]

            is_required = string_field.getAttribute("is_required")
            if (is_required && !string_field.checkValidity() || string_field.value === "") {
                const string_label = child.getElementsByClassName("form-label-data")[0]
                const string_errors = child.getElementsByClassName("form-field-errors")[0]
                if (is_required && string_field.value === "") {
                    string_errors.appendChild(createErrorBlock(string_label.innerText + " field is required"))
                }
                return;
            }
        }  else if (classAttr === "regex-form-field") {
            const regex_field = child.getElementsByClassName("form-field-data")[0]
            is_required = regex_field.getAttribute("is_required")
            if (is_required && !regex_field.checkValidity() || regex_field.value === "") {
                const regex_errors = child.getElementsByClassName("form-field-errors")[0]
                const regex_label = child.getElementsByClassName("form-label-data")[0]
                if (is_required && regex_field.value === "") {
                    regex_errors.appendChild(createErrorBlock(regex_label.innerText + " field is required"));
                } else if (!regex_field.checkValidity()) {
                    regex_errors.appendChild(createErrorBlock(regex_label.innerText + " not validated"));
                }
                return;
            }
        }

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

function activateTab(button, tabId) {
    let tab = document.getElementsByClassName("tab-content")[tabId]
    tab.style.display = "block";
    button.classList.add("active")
    activeTabId = tabId;
}

function deactivateTab(tabId) {
    let tab = document.getElementsByClassName("tab-content")[tabId]
    tab.style.display = "none";
    document.getElementsByClassName("tab-links")[tabId].classList.remove("active")
}

function changeTab(event, tabId) {
    deactivateTab(activeTabId)
    activateTab(event.currentTarget, tabId)
    activeTabId = tabId;
}

function setDefaultTab() {
    const defaultButton = document.getElementsByClassName("tab-links")[defaultTabId]
    activateTab(defaultButton, defaultTabId)
    activeTabId = defaultTabId;
}

document.addEventListener("DOMContentLoaded", () => {
    transformTags()
    transformGeoTags()
    getDescription()
    getForm()
    setDefaultTab()
})
