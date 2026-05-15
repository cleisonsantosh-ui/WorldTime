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
    SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    
    supabase_client = None
    if SUPABASE_URL and SUPABASE_KEY:
        supabase_client = httpx.AsyncClient(
            base_url=SUPABASE_URL,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            timeout=10.0
        )

    # Configurações de Pastas e Templates
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    # Na Vercel, o index.html pode estar no root ou junto ao index.py
    if os.path.exists(os.path.join(CURRENT_DIR, "index.html")):
        templates_dir = CURRENT_DIR
    else:
        templates_dir = os.path.dirname(CURRENT_DIR)
        
    if not os.path.exists(os.path.join(templates_dir, "index.html")):
        # Se não achar o arquivo, não explode agora para permitir que a rota /debug funcione
        templates = None
    else:
        from fastapi.templating import Jinja2Templates
        templates = Jinja2Templates(directory=templates_dir)

except Exception as e:
    error_trace = traceback.format_exc()

@app.get("/debug")
async def debug():
    return {
        "status": "ready" if not error_trace else "error",
        "error_trace": error_trace,
        "supabase_client": "initialized" if supabase_client else "missing",
        "templates_dir": templates_dir if 'templates_dir' in locals() else "not defined"
    }
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
@app.get("/api/horario/{slug}")
async def show_location(request: Request, slug: str):
    if error_trace:
        return JSONResponse(status_code=500, content={"error": "Global init failed", "traceback": error_trace})

    if not supabase_client:
        raise HTTPException(status_code=500, detail="Supabase não configurado no arquivo .env")
        
    if not templates:
        raise HTTPException(status_code=500, detail="Configuração de templates falhou. Verifique se o index.html existe.")

    location = None
    suggestions = []
    
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
@app.get("/api/index")
async def index(request: Request):
    if error_trace:
        return JSONResponse(status_code=500, content={"error": "Global init failed", "traceback": error_trace})

    if not supabase_client:
        raise HTTPException(status_code=500, detail="Supabase não configurado no arquivo .env")

    if not templates:
        raise HTTPException(status_code=500, detail="Configuração de templates falhou. Verifique se o index.html existe.")

    location = None
    suggestions = []
    
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
        "suggestions": suggestions,
        "seo_title": seo_title,
        "seo_description": seo_desc,
        "lang": lang
    })

@app.api_route("/{path_name:path}", methods=["GET"])
async def catch_all(request: Request, path_name: str):
    return {
        "message": "Rota nao encontrada no FastAPI",
        "caminho_recebido": path_name,
        "url_completa": str(request.url),
        "status": "app_running"
    }
