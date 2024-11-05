const countrySelect = document.getElementById('country')
const citySelect = document.getElementById('city')
const submitBtn = document.getElementById('submit_btn')

updateCitySelect = () => {
    fetch("/getcities", {
      method: "POST",
      body: JSON.stringify({
          country: countrySelect.value
      }),
      headers: {
        "Content-type": "application/json; charset=UTF-8",
      },
    })
    .then((response) => response.json())
    .then((json) => {
        console.log(json)
        citySelect.innerHTML = ''
        json.forEach(city => {
            let newOption = document.createElement('option')
            newOption.value = city
            newOption.innerText = city
            citySelect.appendChild(newOption)
        })
    });
}
updateCitySelect();

countrySelect.addEventListener('change', (e) => {
    console.log(e)
    console.log(countrySelect.value)
    updateCitySelect();
});

submitBtn.addEventListener('click', () => {
    datefield = document.getElementById('datefield').value.split('-')
    console.log(datefield)
    fetch("/updateuser", {
      method: "POST",
      body: JSON.stringify({
          name: document.getElementById('namefield').value,
          surname: document.getElementById('surnamefield').value,
          birthday: {
              day: parseInt(datefield[2]),
              month: parseInt(datefield[1]),
              year: parseInt(datefield[0])
          }
      }),
      headers: {
        "Content-type": "application/json; charset=UTF-8",
      },
    })
    .then((response) => response.json())
    .then((json) => {
        console.log(json)
    });
})