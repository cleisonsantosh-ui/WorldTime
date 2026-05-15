# 🌍 Projeto: WorldTime.live — Especificação Técnica Master

Este documento serve como contexto completo para continuidade do desenvolvimento por IA. O objetivo é um site global de fuso horário e clima com foco em SEO de alto tráfego.

## 🎯 Objetivo de Negócio
Capturar tráfego orgânico global através de buscas "long-tail" por cidades (ex: "time in New York now"). O site deve ser extremamente rápido, visualmente premium (Glassmorphism/Dark Mode) e otimizado para Core Web Vitals.

## 🛠️ Stack Tecnológica
- **Frontend:** HTML5, CSS3 (Vanilla), JavaScript (Vanilla).
- **Design:** Tema Dark, gradientes modernos, fontes Inter e JetBrains Mono.
- **Backend/Scripts:** Python para geração de páginas estáticas (SSG).
- **APIs:** Open-Meteo (Clima), Intl API (Tempo nativo).
- **Banco de Dados:** **Supabase (PostgreSQL)** para armazenamento de cidades, metadados de SEO e cache.

## 📂 Estrutura de Arquivos Atual
- `index.html`: Home com busca e relógios principais.
- `cities.html`: Hub de navegação para todas as cidades (crucial para SEO).
- `js/cities-data.js`: Atualmente um JSON estático (deve ser migrado para Supabase).
- `js/weather.js`: Lógica de consumo da Open-Meteo.
- `city/_template.html`: Molde para as milhares de páginas de cidades.
- `generate_city_pages.py`: Script que lê os dados e gera o site estático.

## 🗄️ Integração Supabase (Próximos Passos)
O projeto deve evoluir para usar o Supabase como a "Fonte da Verdade".

### Schema Sugerido (SQL):
```sql
-- Tabela de Cidades para gerar o SEO
CREATE TABLE cities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  slug TEXT UNIQUE NOT NULL, -- Ex: 'new-york'
  name TEXT NOT NULL,
  country TEXT NOT NULL,
  country_code CHAR(2),
  flag TEXT,
  latitude DECIMAL NOT NULL,
  longitude DECIMAL NOT NULL,
  timezone TEXT NOT NULL, -- IANA Format: 'America/New_York'
  is_featured BOOLEAN DEFAULT false,
  search_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela para Cache de Clima (evitar hit excessivo na API externa)
CREATE TABLE weather_cache (
  city_id UUID REFERENCES cities(id),
  data JSONB,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 🚀 Estratégia de SEO
1. **Páginas Estáticas:** Cada cidade precisa de seu próprio `.html` gerado para que o Google indexe.
2. **Schema Markup:** Uso de `WebApplication` na Home e `City` / `BreadcrumbList` nas páginas internas.
3. **Internal Linking:** A página `cities.html` deve listar todas as cidades para que o bot do Google encontre todos os links.
4. **Performance:** Carregamento em < 1s. Sem frameworks pesados.

## 🤖 Instrução para a próxima IA:
"Baseado nesta especificação, ajude-me a:
1. Criar um script Python que puxe as cidades do Supabase em vez do arquivo `.js` local.
2. Implementar uma função de busca no `index.html` que consulte o banco de dados do Supabase via REST API.
3. Gerar o `sitemap.xml` dinamicamente com base nas cidades cadastradas no banco."
