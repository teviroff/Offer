function createTag(id, name) {
    let tag_container = document.createElement("div")
    tag_container.className += "tag-container"
    tag_container.setAttribute("tag_id", id)
    tag_container.style = "cursor:pointer"
    tag_container.onclick =
        () => document.location.href = `/opportunities?tag_ids=${id}`
    let tag_text = document.createElement("p")
    tag_text.innerText = name
    tag_container.appendChild(tag_text)
    return tag_container
}

function createGeoTag(id, name) {
    let tag_container = document.createElement("div")
    tag_container.className += "geotag-container"
    tag_container.setAttribute("geo_tag_id", id)
    tag_container.style = "cursor:pointer"
    tag_container.onclick =
        () => document.location.href = `/opportunities?geo_tag_ids=${id}`
    let tag_text = document.createElement("p")
    tag_text.innerText = name
    tag_container.appendChild(tag_text)
    return tag_container
}
