/**
 * app.js
 * Lógica principal do WorldTime.live
 * - Relógio em tempo real por timezone
 * - Busca de cidades com autocomplete
 * - Grid de relógios mundiais
 * - SEO links de cidades
 */

// ===========================
// UTILITIES
// ===========================

function getLocalTime(tz) {
  const lang = document.documentElement.lang || 'en-US';
  return new Date(new Date().toLocaleString(lang, { timeZone: tz }));
}

function formatTime(date) {
  const lang = document.documentElement.lang || 'en-US';
  return date.toLocaleTimeString(lang, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

function formatDate(date, tz) {
  const lang = document.documentElement.lang || 'en-US';
  return new Intl.DateTimeFormat(lang, {
    timeZone: tz,
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  }).format(date);
}

function getUTCOffset(tz) {
  const now = new Date();
  const utcDate = new Date(now.toLocaleString('en-US', { timeZone: 'UTC' }));
  const tzDate  = new Date(now.toLocaleString('en-US', { timeZone: tz }));
  const diff    = (tzDate - utcDate) / 3600000;
  const sign    = diff >= 0 ? '+' : '-';
  const abs     = Math.abs(diff);
  const h       = Math.floor(abs);
  const m       = Math.round((abs - h) * 60);
  return `UTC${sign}${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
}

function showToast(msg) {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();
  const t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => {
    t.classList.add('fade-out');
    setTimeout(() => t.remove(), 300);
  }, 2500);
}

// ===========================
// CITY RESULT CARD
// ===========================

let activeCity = null;
let clockInterval = null;

function showCityCard(cityData) {
  const section = document.getElementById('result-section');
  section.hidden = false;

  document.getElementById('city-name').innerHTML = `<span class="country-code">${cityData.cc}</span> ${cityData.city.toUpperCase()}`;
  document.getElementById('city-meta').textContent = `${cityData.country} · ${getUTCOffset(cityData.tz)}`;

  const btnPage = document.getElementById('btn-page');
  btnPage.href = `/horario/${cityData.slug}`;

  activeCity = cityData;
  updateCityTime(cityData);

  if (clockInterval) clearInterval(clockInterval);
  clockInterval = setInterval(() => updateCityTime(cityData), 1000);

  // Scroll ao card
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Carrega clima
  displayWeather(cityData.lat, cityData.lon);
}

function updateCityTime(cityData) {
  const now = new Date();
  const lang = document.documentElement.lang || 'en-US';
  const timeStr = new Intl.DateTimeFormat(lang, {
    timeZone: cityData.tz,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).format(now);

  const dateStr = new Intl.DateTimeFormat(lang, {
    timeZone: cityData.tz,
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  }).format(now);

  document.getElementById('time-display').textContent = timeStr;
  document.getElementById('date-display').textContent = dateStr;
  document.getElementById('tz-display').textContent   = `${cityData.tz} · ${getUTCOffset(cityData.tz)}`;
}

// Share button
document.getElementById('btn-share')?.addEventListener('click', () => {
  if (!activeCity) return;
  const url = `${location.origin}/horario/${activeCity.slug}`;
  if (navigator.share) {
    navigator.share({
      title: `Current time in ${activeCity.city}`,
      text: `Check the current time and weather in ${activeCity.city}, ${activeCity.country}`,
      url,
    });
  } else {
    navigator.clipboard.writeText(url).then(() => showToast('✅ Link copied!'));
  }
});

// ===========================
// SEARCH
// ===========================

const searchInput = document.getElementById('city-search');
const searchDropdown = document.getElementById('search-results');
const searchBtn = document.getElementById('search-btn');

let debounceTimer = null;

function renderDropdown(results) {
  searchDropdown.innerHTML = '';
  if (!results.length) {
    searchDropdown.hidden = true;
    return;
  }
  results.forEach((city, i) => {
    const li = document.createElement('li');
    li.className = 'dropdown-item';
    li.setAttribute('role', 'option');
    li.setAttribute('id', `drop-${i}`);
    li.innerHTML = `
      <span style="font-size:1.3rem">${city.flag}</span>
      <div>
        <div class="dropdown-city">${city.city}</div>
        <div class="dropdown-country">${city.country}</div>
      </div>
    `;
    li.addEventListener('click', () => selectCity(city));
    searchDropdown.appendChild(li);
  });
  searchDropdown.hidden = false;
}

function selectCity(city) {
  searchInput.value = city.city;
  searchDropdown.hidden = true;
  showCityCard(city);
}

searchInput.addEventListener('input', () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    const q = searchInput.value.trim();
    if (q.length < 1) { searchDropdown.hidden = true; return; }
    const results = searchCities(q, 8);
    renderDropdown(results);
  }, 200);
});

searchInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    const q = searchInput.value.trim();
    const results = searchCities(q, 1);
    if (results.length) selectCity(results[0]);
    searchDropdown.hidden = true;
  }
  if (e.key === 'Escape') {
    searchDropdown.hidden = true;
  }
});

searchBtn.addEventListener('click', () => {
  const q = searchInput.value.trim();
  const results = searchCities(q, 1);
  if (results.length) selectCity(results[0]);
});

// Fechar dropdown ao clicar fora
document.addEventListener('click', (e) => {
  if (!e.target.closest('.search-wrapper')) {
    searchDropdown.hidden = true;
  }
});

// ===========================
// QUICK TAGS
// ===========================

document.querySelectorAll('.quick-tag').forEach(btn => {
  btn.addEventListener('click', () => {
    const cityName = btn.dataset.city;
    const city = getCityByName(cityName);
    if (city) selectCity(city);
  });
});

// ===========================
// WORLD CLOCKS GRID
// ===========================

function buildClocksGrid() {
  const grid = document.getElementById('clocks-grid');
  if (!grid) return;

  const featured = CITIES_DB.filter(c => FEATURED_CITIES.includes(c.city));

  featured.forEach(city => {
    const card = document.createElement('div');
    card.className = 'clock-card';
    card.setAttribute('role', 'button');
    card.setAttribute('tabindex', '0');
    card.setAttribute('aria-label', `Current time in ${city.city}`);
    card.dataset.tz = city.tz;
    card.dataset.city = city.city;

    card.innerHTML = `
      <div class="clock-flag">${city.flag}</div>
      <div class="clock-city">${city.city}</div>
      <div class="clock-country">${city.country}</div>
      <div class="clock-time" data-clock-time="${city.tz}">--:--:--</div>
      <div class="clock-date" data-clock-date="${city.tz}"></div>
    `;

    card.addEventListener('click', () => selectCity(city));
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') selectCity(city);
    });

    grid.appendChild(card);
  });
}

function updateAllClocks() {
  const now = new Date();

  document.querySelectorAll('[data-clock-time]').forEach(el => {
    const tz = el.dataset.clockTime;
    const lang = document.documentElement.lang || 'en-US';
    try {
      el.textContent = new Intl.DateTimeFormat(lang, {
        timeZone: tz,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
      }).format(now);
    } catch (_) {}
  });

  document.querySelectorAll('[data-clock-date]').forEach(el => {
    const tz = el.dataset.clockDate;
    const lang = document.documentElement.lang || 'en-US';
    try {
      el.textContent = new Intl.DateTimeFormat(lang, {
        timeZone: tz,
        weekday: 'short',
        month: 'short',
        day: 'numeric',
      }).format(now);
    } catch (_) {}
  });
}

// ===========================
// SEO CITIES GRID
// ===========================

function buildSeoCitiesGrid() {
  const grid = document.getElementById('cities-seo-grid');
  if (!grid) return;

  CITIES_DB.forEach(city => {
    const a = document.createElement('a');
    a.className = 'city-seo-link';
    a.href = `/horario/${city.slug}`;
    a.innerHTML = `
      <strong>${city.flag} ${city.city}</strong>
      <small>${city.country}</small>
    `;
    grid.appendChild(a);
  });
}

// ===========================
// INIT
// ===========================

document.addEventListener('DOMContentLoaded', () => {
  buildClocksGrid();
  buildSeoCitiesGrid();
  updateAllClocks();
  setInterval(updateAllClocks, 1000);

  // Auto-detecta cidade via URL (Backend) ou Timezone do usuário
  try {
    const path = window.location.pathname;
    if (path.startsWith('/horario/')) {
      const slug = path.split('/')[2];
      const cityUrl = CITIES_DB.find(c => c.slug === slug);
      if (cityUrl) {
        selectCity(cityUrl);
        return;
      }
    }
    
    // Se estiver na HOME, tenta detectar o fuso local e abrir automaticamente
    if (path === '/' || path === '/index.html') {
      const localTz = Intl.DateTimeFormat().resolvedOptions().timeZone;
      const localCity = CITIES_DB.find(c => c.tz === localTz);
      if (localCity) {
        selectCity(localCity);
      }
    }
  } catch (err) {}
});
