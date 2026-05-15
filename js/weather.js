/**
 * weather.js
 * Integração com Open-Meteo API (gratuita, sem chave)
 * https://open-meteo.com/
 */

const WMO_CODES = {
  0:  { desc: "Clear sky",           icon: "☀️" },
  1:  { desc: "Mainly clear",        icon: "🌤️" },
  2:  { desc: "Partly cloudy",       icon: "⛅" },
  3:  { desc: "Overcast",            icon: "☁️" },
  45: { desc: "Foggy",               icon: "🌫️" },
  48: { desc: "Icy fog",             icon: "🌫️" },
  51: { desc: "Light drizzle",       icon: "🌦️" },
  53: { desc: "Drizzle",             icon: "🌦️" },
  55: { desc: "Heavy drizzle",       icon: "🌧️" },
  61: { desc: "Slight rain",         icon: "🌧️" },
  63: { desc: "Moderate rain",       icon: "🌧️" },
  65: { desc: "Heavy rain",          icon: "🌧️" },
  71: { desc: "Slight snow",         icon: "🌨️" },
  73: { desc: "Moderate snow",       icon: "❄️" },
  75: { desc: "Heavy snow",          icon: "❄️" },
  77: { desc: "Snow grains",         icon: "🌨️" },
  80: { desc: "Slight showers",      icon: "🌦️" },
  81: { desc: "Moderate showers",    icon: "🌧️" },
  82: { desc: "Violent showers",     icon: "⛈️" },
  85: { desc: "Slight snow showers", icon: "🌨️" },
  86: { desc: "Heavy snow showers",  icon: "❄️" },
  95: { desc: "Thunderstorm",        icon: "⛈️" },
  96: { desc: "Thunderstorm + hail", icon: "⛈️" },
  99: { desc: "Heavy thunderstorm",  icon: "⛈️" },
};

// Cache simples para evitar requisições repetidas
const weatherCache = new Map();
const CACHE_TTL = 30 * 60 * 1000; // 30 minutos

/**
 * Busca clima na Open-Meteo API
 * @param {number} lat - latitude
 * @param {number} lon - longitude
 * @returns {Promise<Object>} dados do clima
 */
async function fetchWeather(lat, lon) {
  const key = `${lat.toFixed(2)},${lon.toFixed(2)}`;
  const cached = weatherCache.get(key);
  if (cached && Date.now() - cached.ts < CACHE_TTL) {
    return cached.data;
  }

  const url = `https://api.open-meteo.com/v1/forecast?` +
    `latitude=${lat}&longitude=${lon}` +
    `&current=temperature_2m,relative_humidity_2m,apparent_temperature,` +
    `weather_code,wind_speed_10m` +
    `&wind_speed_unit=kmh` +
    `&timezone=auto` +
    `&forecast_days=1`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 8000);

  const res = await fetch(url, { signal: controller.signal });
  clearTimeout(timeoutId);
  if (!res.ok) throw new Error(`Weather API ${res.status}`);

  const json = await res.json();
  const cur = json.current;
  const wmo = WMO_CODES[cur.weather_code] || { desc: "Unknown", icon: "🌡️" };

  const data = {
    tempC:    Math.round(cur.temperature_2m),
    feelsC:   Math.round(cur.apparent_temperature),
    humidity: cur.relative_humidity_2m,
    windKmh:  Math.round(cur.wind_speed_10m),
    code:     cur.weather_code,
    desc:     wmo.desc,
    icon:     wmo.icon,
  };

  weatherCache.set(key, { ts: Date.now(), data });
  return data;
}

/**
 * Exibe o clima no card resultado
 */
async function displayWeather(lat, lon) {
  const loadingEl = document.getElementById('weather-loading');
  const dataEl    = document.getElementById('weather-data');
  const errorEl   = document.getElementById('weather-error');

  // Reset
  loadingEl.hidden = false;
  dataEl.hidden    = true;
  errorEl.hidden   = true;

  try {
    const w = await fetchWeather(lat, lon);
    window._currentWeather = w;

    document.getElementById('weather-icon').textContent  = w.icon;
    document.getElementById('weather-desc').textContent  = w.desc;
    document.getElementById('weather-humidity').textContent = `${w.humidity}%`;
    document.getElementById('weather-wind').textContent     = `${w.windKmh} km/h`;

    renderTemp(w.tempC, w.feelsC, window._useFahrenheit || false);

    loadingEl.hidden = true;
    dataEl.hidden    = false;
  } catch (err) {
    console.warn('Weather fetch failed:', err.message);
    loadingEl.hidden = true;
    errorEl.hidden   = false;
  }
}

/**
 * Renderiza temperatura em C ou F
 */
function renderTemp(tempC, feelsC, fahrenheit) {
  const el    = document.getElementById('weather-temp');
  const feels = document.getElementById('weather-feels');
  if (fahrenheit) {
    el.textContent    = `${Math.round(tempC * 9/5 + 32)}°F`;
    feels.textContent = `${Math.round(feelsC * 9/5 + 32)}°F`;
  } else {
    el.textContent    = `${tempC}°C`;
    feels.textContent = `${feelsC}°C`;
  }
}

// Toggle °C / °F
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('temp-toggle');
  if (!btn) return;
  btn.addEventListener('click', () => {
    window._useFahrenheit = !window._useFahrenheit;
    const w = window._currentWeather;
    if (w) renderTemp(w.tempC, w.feelsC, window._useFahrenheit);
  });
});
