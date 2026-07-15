from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
