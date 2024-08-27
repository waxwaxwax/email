document.getElementById('alertForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value || '';
    const city = document.getElementById('city').value;
    const email = document.getElementById('email').value;

    fetch('https://email0824001.azurewebsites.net/api/http_trigger', { // バックエンドのAzure Functionのエンドポイントを指定
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ firstName: firstName, lastName: lastName, city: city, email: email })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('cityName').value = city;
        document.getElementById('weatherDescription').value = data.weather.description;
        document.getElementById('temperature').value = `${data.temperature}°C`;
        document.getElementById('alertMessage').textContent = `Alert mail sent to ${email}`;
    })
    .catch(error => {
        document.getElementById('alertMessage').textContent = 'Request failed.';
        console.error('Error:', error);
    });
});
