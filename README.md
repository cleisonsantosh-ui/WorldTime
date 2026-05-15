# WorldTime.live

Site de relógio mundial + clima em tempo real para 500+ cidades.

## 🚀 Como usar

### 1. Gerar páginas das cidades (precisa de Python 3)
```bash
python generate_city_pages.py
```
Isso gera `city/[cidade].html` + `sitemap.xml` para todas as cidades.

### 2. Deploy

**Vercel (recomendado):**
- Faça upload/conecte ao GitHub → Deploy automático

**cPanel / hospedagem tradicional:**
- Faça upload de todos os arquivos via FTP/FileZilla
- Aponte o domínio para a pasta raiz

**Netlify:**
- Arraste a pasta para o deploy em netlify.com/drop

### 3. Após o deploy
1. Vá em [Google Search Console](https://search.google.com/search-console)
2. Adicione sua propriedade (domínio)
3. Submeta `https://seudominio.com/sitemap.xml`

## 📁 Estrutura
```
index.html          — Página principal
cities.html         — Lista de todas as cidades  
city/               — Páginas individuais por cidade
css/style.css       — Design system
js/                 — Lógica e banco de dados de cidades
robots.txt          — SEO
sitemap.xml         — Gerado pelo script Python
vercel.json         — Config de deploy Vercel
```

## 🔧 APIs usadas (gratuitas)
- **Open-Meteo** — clima gratuito, sem chave de API
- **Intl API** (nativo do browser) — timezone e hora local

## ➕ Para adicionar mais cidades
Edite `js/cities-data.js` e `generate_city_pages.py` — as listas são espelho uma da outra.
