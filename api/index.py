import os
import traceback
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="Global Horas Backend")

error_trace = None

try:
    from fastapi.templating import Jinja2Templates
    from dotenv import load_dotenv

    load_dotenv()

    # Conecta ao Supabase usando httpx no lugar do supabase_py
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    supabase_client = None
    if SUPABASE_URL and SUPABASE_KEY:
        supabase_client = httpx.AsyncClient(
            base_url=SUPABASE_URL.rstrip("/"),
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
        )

    # Configurações de Pastas e Templates
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Garante que na Vercel o BASE_DIR existe ou levanta um erro claro
    templates_dir = str(BASE_DIR)
    if not os.path.exists(templates_dir):
        raise RuntimeError(f"BASE_DIR '{templates_dir}' não existe no ambiente da Vercel!")
        
    templates = Jinja2Templates(directory=templates_dir)

except Exception as e:
    error_trace = traceback.format_exc()


# StaticFiles removido: Na Vercel, o CSS, JS e Midia são servidos automaticamente
# pela própria Vercel (Edge Network) apenas existindo na raiz do projeto.
# Tentar montar essas pastas aqui dentro causa "FUNCTION_INVOCATION_FAILED"
# caso a Vercel não copie a pasta de mídia pesada para dentro da função lambda.

def get_language(request: Request):
    lang_header = request.headers.get("accept-language", "en")
    if "pt" in lang_header: return "pt"
    if "es" in lang_header: return "es"
    return "en"

@app.get("/horario/{slug}")
async def show_location(request: Request, slug: str):
    if error_trace:
        return JSONResponse(status_code=500, content={"error": "Global init failed", "traceback": error_trace})

    if not supabase_client:
        raise HTTPException(status_code=500, detail="Supabase não configurado no arquivo .env")
        
    try:
        # 1. Busca os dados na tabela 'locations'
        resp_loc = await supabase_client.get(f"/rest/v1/locations?slug=eq.{slug}&select=*")
        resp_loc.raise_for_status()
        loc_data = resp_loc.json()
        
        if not loc_data:
            raise HTTPException(status_code=404, detail="Página não encontrada")
        
        location = loc_data[0]
        
        # 2. Busca sugestões via RPC
        sugg_response = await supabase_client.post("/rest/v1/rpc/get_random_locations", json={"limit_num": 5})
        sugg_data = sugg_response.json() if sugg_response.status_code == 200 else []
        suggestions = [s for s in sugg_data if s.get("slug") != slug][:4]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 3. Monta as variáveis de SEO dinamicamente com base no Idioma do Navegador
    lang = get_language(request)
    
    if lang == "pt":
        seo_title = f"Horário agora em {location['city']} ({location['country']}) - Hora exata"
        seo_desc = f"Descubra a hora exata, clima e fuso horário de {location['country']}. Acompanhe ao vivo com precisão de segundos."
    elif lang == "es":
        seo_title = f"Hora actual en {location['city']} ({location['country']}) - Hora exacta"
        seo_desc = f"Descubre la hora exacta, clima y zona horaria de {location['country']}. Sigue en vivo con precisión de segundos."
    else:
        seo_title = f"Current time in {location['city']} ({location['country']}) - Exact time"
        seo_desc = f"Discover the exact time, weather, and time zone of {location['country']}. Track live with second accuracy."

    # 4. Injeta as variáveis no seu index.html
    return templates.TemplateResponse("index.html", {
        "request": request,
        "location": location,
        "suggestions": suggestions,
        "seo_title": seo_title,
        "seo_description": seo_desc,
        "lang": lang
    })

@app.get("/")
async def index(request: Request):
    if error_trace:
        return JSONResponse(status_code=500, content={"error": "Global init failed", "traceback": error_trace})

    if not supabase_client:
        raise HTTPException(status_code=500, detail="Supabase não configurado no arquivo .env")

    # Detecta o IP do usuário (aqui simulamos o fallback para são paulo)
    fallback_slug = "sao-paulo" 
    
    try:
        resp_loc = await supabase_client.get(f"/rest/v1/locations?slug=eq.{fallback_slug}&select=*")
        resp_loc.raise_for_status()
        loc_data = resp_loc.json()
        location = loc_data[0] if loc_data else None
        
        sugg_response = await supabase_client.post("/rest/v1/rpc/get_random_locations", json={"limit_num": 4})
        suggestions = sugg_response.json() if sugg_response.status_code == 200 else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    lang = get_language(request)
    if lang == "pt":
        seo_title = "World Time & Weather — A hora exata na sua cidade"
        seo_desc = "Detectamos seu local automaticamente. Veja a hora global."
    elif lang == "es":
        seo_title = "World Time & Weather — La hora exacta en tu ciudad"
        seo_desc = "Detectamos tu ubicación automáticamente. Mira la hora global."
    else:
        seo_title = "World Time & Weather — The exact time in your city"
        seo_desc = "We automatically detect your location. Check global time."
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "location": location,
        "suggestions": sugg_response.data,
        "seo_title": seo_title,
        "seo_description": seo_desc,
        "lang": lang
    })
