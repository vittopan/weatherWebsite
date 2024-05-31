// script.js
document.addEventListener('DOMContentLoaded', () => {
    const weatherContainer = document.getElementById('weatherContainer');
    if (!weatherContainer) {
        console.error('Weather container not found');
        return;
    }

    const weatherCode = weatherContainer.getAttribute('data-weather-code');
    if (!weatherCode) {
        console.error('Weather code not found');
        return;
    }

    const weatherCodeInt = parseInt(weatherCode, 10);
    console.log('Weather code:', weatherCodeInt); // Log the weather code

    let weatherClass = 'sunny'; // Default class

    switch (weatherCodeInt) {
        case 1000:
            weatherClass = 'sunny';
            break;
        case 1101:
            weatherClass = 'partlyCloudy';
            break;
        case 1001:
            weatherClass = 'cloudy';
            break;
        case 4001:
            weatherClass = 'rainy';
            break;
        case 5000:
            weatherClass = 'snow';
            break;
        case 1102:
            weatherClass = 'mostlyCloudy';
            break;
        default:
            weatherClass = 'sunny';
            break;
    }

    console.log('Weather class:', weatherClass); // Log the weather class

    document.body.className = weatherClass; // Ensure no conflicting classes
});


