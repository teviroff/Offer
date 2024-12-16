provider_ids = new Set()
tag_ids = new Set()
geo_tag_ids = new Set()
page = 1

function resetQuery() {
    document.location.search = ""
}

function parseQuery() {
    provider_ids = new Set()
    tag_ids = new Set()
    geo_tag_ids = new Set()
    page = 1
    query_params = new URLSearchParams(document.location.search)
    query_params.forEach((value, key) => {
        if (key === "provider_ids") {
            id_int = parseInt(value)
            if (isNaN(id_int)) {
                resetQuery()
                return
            }
            provider_ids.add(id_int)
        } else if (key === "tag_ids") {
            id_int = parseInt(value)
            if (isNaN(id_int)) {
                resetQuery()
                return
            }
            tag_ids.add(id_int)
        } else if (key === "geo_tag_ids") {
            id_int = parseInt(value)
            if (isNaN(id_int)) {
                resetQuery()
                return
            }
            geo_tag_ids.add(id_int)
        } else if (key === "page") {
            page_int = parseInt(value)
            if (isNaN(page_int)) {
                resetQuery()
                return
            }
            page = page_int
        }
    })
}

function initializeFilters() {
    const filtersContainer = document.getElementById("filters-container")
    const providersJSON = JSON.parse(filtersContainer.children[0].innerText)
    const tagsJSON = JSON.parse(filtersContainer.children[1].innerText)
    const geotagsJSON = JSON.parse(filtersContainer.children[2].innerText)
    filtersContainer.innerText = ""
    filtersContainer.appendChild(createProviderFilter(providersJSON, provider_ids))
    filtersContainer.appendChild(createTagsFilter(tagsJSON, tag_ids))
    filtersContainer.appendChild(createGeoTagsFilter(geotagsJSON, geo_tag_ids))
}

function transformCardsTags() {
    const cardsContainer = document.getElementById("cards-container")
    Array.from(cardsContainer.children).forEach((card) => {
        const cardTagsContainer = card.getElementsByClassName("card-tag-container")[0]
        const cardGeoTagsContainer = card.getElementsByClassName("card-geotag-container")[0]
        const geotagsJSON = JSON.parse(cardGeoTagsContainer.children[0].innerText)
        const tagsJSON = JSON.parse(cardTagsContainer.children[0].innerText)
        cardTagsContainer.innerText = ""
        cardGeoTagsContainer.innerText = ""
        geotagsJSON.forEach((geotag) => {
            cardGeoTagsContainer.appendChild(createGeoTag(geotag["id"], geotag["name"]))
        })
        tagsJSON.forEach((tag) => {
            cardTagsContainer.appendChild(createTag(tag["id"], tag["name"]))
        })
    })
}

function fetchOpportunityCards() {
    const cardsContainer = document.getElementById("cards-container")
    fetch("/opportunities/cards", {
        method: "POST",
        body: JSON.stringify({
            provider_ids: Array.from(provider_ids),
            tag_ids: Array.from(tag_ids),
            geo_tag_ids: Array.from(geo_tag_ids),
            page: page
        }),
        headers: {
            'Content-type': 'application/json; charset=UTF-8',
        },
    })
    .then(async (response) => {
        if (response.status === 200) {
            cardsContainer.innerHTML = await response.text()
            transformCardsTags()
            return
        }
        // ...
        return
    })
}

document.addEventListener("DOMContentLoaded", () => {
    parseQuery()
    initializeFilters()
    fetchOpportunityCards()
    const applyFiltersButton = document.getElementById("apply-filters-button")
    applyFiltersButton.addEventListener("click", fetchOpportunityCards)
})
