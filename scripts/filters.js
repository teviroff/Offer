function createFilter(id, name, collection) {
    let filter = document.createElement("div")
    filter.setAttribute("filter_id", id)
    filter.className = "filter"
    if (collection.has(id)) {
        filter.classList.add("selected")
    }
    filter.style = "cursor:pointer"
    filter.onclick = () => {
        if (collection.has(id)) {
            collection.delete(id)
            filter.classList.remove("selected")
        } else {
            collection.add(id)
            filter.classList.add("selected")
        }
    }
    let filter_text = document.createElement("p")
    filter_text.innerText = name
    filter.appendChild(filter_text)
    return filter
}

function createFilterSearch(placeholder) {
    let search = document.createElement("div")
    search.className = "filter-search"
    let search_input = document.createElement("input")
    search_input.type = "text"
    search_input.placeholder = placeholder
    search.appendChild(search_input)
    return search
}

function createProviderFilter(filters, collection) {
    let container = document.createElement("div")
    container.id = "provider-filters-container"
    let text = document.createElement("h3")
    text.innerText = "Provider"
    container.appendChild(text)
    container.appendChild(createFilterSearch("Provider name"))
    let filters_container = document.createElement("div")
    for (let i = 0; i < filters.length; ++i) {
        filters_container.appendChild(
            createFilter(filters[i]["id"], filters[i]["name"], collection)
        )
    }
    container.appendChild(filters_container)
    return container
}

function createTagsFilter(filters, collection) {
    let container = document.createElement("div")
    container.id = "tag-filters-container"
    let text = document.createElement("h3")
    text.innerText = "Tags"
    container.appendChild(text)
    container.appendChild(createFilterSearch("Tag name"))
    let filters_container = document.createElement("div")
    for (let i = 0; i < filters.length; ++i) {
        filters_container.appendChild(
            createFilter(filters[i]["id"], filters[i]["name"], collection)
        )
    }
    container.appendChild(filters_container)
    return container
}

function createGeoTagsFilter(filters, collection) {
    let container = document.createElement("div")
    container.id = "geotag-filters-container"
    let text = document.createElement("h3")
    text.innerText = "Geo Tags"
    container.appendChild(text)
    container.appendChild(createFilterSearch("City name"))
    let filters_container = document.createElement("div")
    for (let i = 0; i < filters.length; ++i) {
        filters_container.appendChild(
            createFilter(filters[i]["id"], filters[i]["name"], collection)
        )
    }
    container.appendChild(filters_container)
    return container
}
