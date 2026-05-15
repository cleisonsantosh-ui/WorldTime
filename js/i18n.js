const i18n = {
  en: {
    hero_badge: "🕐 Live • Updated every second",
    hero_title: "What time is it<br><span class=\"gradient-text\">anywhere in the world?</span>",
    hero_subtitle: "Instant local time + live weather for <strong>500+ cities</strong>. No ads, no signup.",
    search_placeholder: "Search any city... (e.g. Tokyo, London, New York)",
    search_btn: "Search",
    popular_label: "Popular:",
    btn_share: "📤 Share",
    btn_page: "🔗 Full page",
    loading_weather: "Loading weather...",
    weather_error: "⚠️ Weather unavailable",
    temp_toggle: "°C / °F",
    humidity: "Humidity",
    wind: "Wind",
    feels_like: "Feels like",
    clocks_title: "Live World Clocks",
    clocks_sub: "All times update in real-time",
    popular_title: "Popular City Pages",
    popular_sub: "Click any city for detailed time, weather and timezone info",
    faq_title: "Frequently Asked Questions",
    footer_desc: "Real-time world clock & weather for every city on Earth.",
    nav_home: "Home",
    nav_cities: "All Cities",
    nav_timezones: "Time Zones",
    tools_converter: "Time Converter"
  },
  pt: {
    hero_badge: "🕐 Ao Vivo • Atualizado a cada segundo",
    hero_title: "Que horas são<br><span class=\"gradient-text\">em qualquer lugar do mundo?</span>",
    hero_subtitle: "Hora local instantânea + clima ao vivo para <strong>500+ cidades</strong>. Sem anúncios.",
    search_placeholder: "Pesquise qualquer cidade... (ex: Tóquio, Londres)",
    search_btn: "Pesquisar",
    popular_label: "Populares:",
    btn_share: "📤 Compartilhar",
    btn_page: "🔗 Página completa",
    loading_weather: "Carregando clima...",
    weather_error: "⚠️ Clima indisponível",
    temp_toggle: "°C / °F",
    humidity: "Umidade",
    wind: "Vento",
    feels_like: "Sensação",
    clocks_title: "Relógios Mundiais",
    clocks_sub: "Todos os horários em tempo real",
    popular_title: "Páginas Populares",
    popular_sub: "Clique em qualquer cidade para detalhes de hora e clima",
    faq_title: "Perguntas Frequentes",
    footer_desc: "Relógio mundial e clima em tempo real para todas as cidades.",
    nav_home: "Início",
    nav_cities: "Todas as Cidades",
    nav_timezones: "Fuso Horários",
    tools_converter: "Conversor de Tempo"
  },
  es: {
    hero_badge: "🕐 En Vivo • Actualizado cada segundo",
    hero_title: "¿Qué hora es<br><span class=\"gradient-text\">en cualquier lugar del mundo?</span>",
    hero_subtitle: "Hora local instantánea + clima en vivo para <strong>500+ ciudades</strong>.",
    search_placeholder: "Busca cualquier ciudad... (ej: Tokio, Londres)",
    search_btn: "Buscar",
    popular_label: "Populares:",
    btn_share: "📤 Compartir",
    btn_page: "🔗 Página completa",
    loading_weather: "Cargando clima...",
    weather_error: "⚠️ Clima no disponible",
    temp_toggle: "°C / °F",
    humidity: "Humedad",
    wind: "Viento",
    feels_like: "Sensación",
    clocks_title: "Relojes Mundiales",
    clocks_sub: "Todos los horarios en tiempo real",
    popular_title: "Páginas Populares",
    popular_sub: "Haz clic en cualquier ciudad para ver detalles",
    faq_title: "Preguntas Frecuentes",
    footer_desc: "Reloj mundial y clima en tiempo real para todas las ciudades.",
    nav_home: "Inicio",
    nav_cities: "Todas las Ciudades",
    nav_timezones: "Zonas Horarias",
    tools_converter: "Convertidor de Tiempo"
  }
};

function applyTranslations() {
  // Pega o idioma injetado pelo Backend no HTML, ou detecta no navegador
  let lang = document.documentElement.lang || navigator.language.split('-')[0];
  if (!i18n[lang]) lang = 'en';

  const dict = i18n[lang];
  
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) {
      if (el.tagName === 'INPUT' && el.hasAttribute('placeholder')) {
         el.placeholder = dict[key];
      } else {
         el.innerHTML = dict[key];
      }
    }
  });
}

document.addEventListener('DOMContentLoaded', applyTranslations);
