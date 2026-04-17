from fastapi import FastAPI, APIRouter, HTTPException, Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import io
import base64

# PDF Generation
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Email
import resend

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Resend API
resend.api_key = os.environ.get('RESEND_API_KEY', '')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Colors
BLUE = HexColor('#002fa7')
LIME = HexColor('#dbf637')
WHITE = HexColor('#ffffff')
DARK_GREEN = HexColor('#1a281f')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

class Supplier(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    legal_name: str
    address: str
    vat_number: str
    phone: Optional[str] = None
    email: Optional[str] = None
    is_main: bool = False

class SupplierCreate(BaseModel):
    name: str
    legal_name: str
    address: str
    vat_number: str
    phone: Optional[str] = None
    email: Optional[str] = None
    is_main: bool = False

class Client(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_name: str
    vat_number: str
    address: str
    email: str
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClientCreate(BaseModel):
    company_name: str
    vat_number: str
    address: str
    email: str
    phone: Optional[str] = None

class Service(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    sub_items: List[str] = []
    price: float
    price_type: str = "una_tantum"  # una_tantum, mensile, annuale, bimestrale
    category: str = "general"
    is_active: bool = True

class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sub_items: List[str] = []
    price: float
    price_type: str = "una_tantum"
    category: str = "general"
    is_active: bool = True

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sub_items: Optional[List[str]] = None
    price: Optional[float] = None
    price_type: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class QuoteService(BaseModel):
    service_id: str
    service_name: str
    description: Optional[str] = None
    sub_items: List[str] = []
    price: float
    price_type: str
    quantity: int = 1
    is_selected: bool = True
    step_number: Optional[int] = None  # For step-based quotes

class QuoteStep(BaseModel):
    step_number: int
    title: str
    description: Optional[str] = None
    duration: Optional[str] = None
    output: Optional[str] = None
    services: List[QuoteService] = []

class Quote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quote_number: int
    client_id: str
    client_name: str
    supplier_ids: List[str] = []
    subject: str
    quote_type: str = "standard"  # standard, step, moduli, ibrido
    services: List[QuoteService] = []
    steps: List[QuoteStep] = []
    premise: Optional[str] = None
    methodology: Optional[str] = None
    validity_days: int = 30
    payment_terms: str = "30% all'accettazione, 70% alla consegna"
    delivery_time: Optional[str] = None
    extra_notes: Optional[str] = None
    total_amount: float = 0
    status: str = "draft"  # draft, sent, accepted, rejected
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class QuoteCreate(BaseModel):
    client_id: str
    supplier_ids: List[str] = []
    subject: str
    quote_type: str = "standard"
    services: List[QuoteService] = []
    steps: List[QuoteStep] = []
    premise: Optional[str] = None
    methodology: Optional[str] = None
    validity_days: int = 30
    payment_terms: str = "30% all'accettazione, 70% alla consegna"
    delivery_time: Optional[str] = None
    extra_notes: Optional[str] = None

class EmailRequest(BaseModel):
    quote_id: str
    recipient_email: EmailStr
    subject: str
    message: str

# ==================== SUPPLIERS API ====================

@api_router.get("/suppliers", response_model=List[Supplier])
async def get_suppliers():
    suppliers = await db.suppliers.find({}, {"_id": 0}).to_list(100)
    return suppliers

@api_router.post("/suppliers", response_model=Supplier)
async def create_supplier(supplier: SupplierCreate):
    supplier_obj = Supplier(**supplier.model_dump())
    doc = supplier_obj.model_dump()
    doc['created_at'] = datetime.now(timezone.utc).isoformat()
    await db.suppliers.insert_one(doc)
    return supplier_obj

@api_router.put("/suppliers/{supplier_id}", response_model=Supplier)
async def update_supplier(supplier_id: str, supplier: SupplierCreate):
    result = await db.suppliers.find_one({"id": supplier_id}, {"_id": 0})
    if not result:
        raise HTTPException(status_code=404, detail="Supplier not found")
    update_data = supplier.model_dump()
    await db.suppliers.update_one({"id": supplier_id}, {"$set": update_data})
    updated = await db.suppliers.find_one({"id": supplier_id}, {"_id": 0})
    return updated

@api_router.delete("/suppliers/{supplier_id}")
async def delete_supplier(supplier_id: str):
    result = await db.suppliers.delete_one({"id": supplier_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {"message": "Supplier deleted"}

# ==================== CLIENTS API ====================

@api_router.get("/clients", response_model=List[Client])
async def get_clients():
    clients = await db.clients.find({}, {"_id": 0}).to_list(1000)
    for c in clients:
        if isinstance(c.get('created_at'), str):
            c['created_at'] = datetime.fromisoformat(c['created_at'])
    return clients

@api_router.get("/clients/{client_id}", response_model=Client)
async def get_client(client_id: str):
    client = await db.clients.find_one({"id": client_id}, {"_id": 0})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if isinstance(client.get('created_at'), str):
        client['created_at'] = datetime.fromisoformat(client['created_at'])
    return client

@api_router.post("/clients", response_model=Client)
async def create_client(client: ClientCreate):
    client_obj = Client(**client.model_dump())
    doc = client_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.clients.insert_one(doc)
    return client_obj

@api_router.put("/clients/{client_id}", response_model=Client)
async def update_client(client_id: str, client: ClientCreate):
    result = await db.clients.find_one({"id": client_id}, {"_id": 0})
    if not result:
        raise HTTPException(status_code=404, detail="Client not found")
    update_data = client.model_dump()
    await db.clients.update_one({"id": client_id}, {"$set": update_data})
    updated = await db.clients.find_one({"id": client_id}, {"_id": 0})
    if isinstance(updated.get('created_at'), str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    return updated

@api_router.delete("/clients/{client_id}")
async def delete_client(client_id: str):
    result = await db.clients.delete_one({"id": client_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deleted"}

# ==================== SERVICES API ====================

@api_router.get("/services", response_model=List[Service])
async def get_services():
    services = await db.services.find({}, {"_id": 0}).to_list(1000)
    return services

@api_router.get("/services/{service_id}", response_model=Service)
async def get_service(service_id: str):
    service = await db.services.find_one({"id": service_id}, {"_id": 0})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@api_router.post("/services", response_model=Service)
async def create_service(service: ServiceCreate):
    service_obj = Service(**service.model_dump())
    doc = service_obj.model_dump()
    await db.services.insert_one(doc)
    return service_obj

@api_router.put("/services/{service_id}", response_model=Service)
async def update_service(service_id: str, service: ServiceUpdate):
    result = await db.services.find_one({"id": service_id}, {"_id": 0})
    if not result:
        raise HTTPException(status_code=404, detail="Service not found")
    update_data = {k: v for k, v in service.model_dump().items() if v is not None}
    if update_data:
        await db.services.update_one({"id": service_id}, {"$set": update_data})
    updated = await db.services.find_one({"id": service_id}, {"_id": 0})
    return updated

@api_router.delete("/services/{service_id}")
async def delete_service(service_id: str):
    result = await db.services.delete_one({"id": service_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted"}

# ==================== QUOTES API ====================

async def get_next_quote_number():
    last_quote = await db.quotes.find_one(sort=[("quote_number", -1)], projection={"_id": 0, "quote_number": 1})
    return (last_quote.get("quote_number", 0) if last_quote else 0) + 1

@api_router.get("/quotes", response_model=List[Quote])
async def get_quotes():
    quotes = await db.quotes.find({}, {"_id": 0}).to_list(1000)
    for q in quotes:
        if isinstance(q.get('created_at'), str):
            q['created_at'] = datetime.fromisoformat(q['created_at'])
    return quotes

@api_router.get("/quotes/{quote_id}", response_model=Quote)
async def get_quote(quote_id: str):
    quote = await db.quotes.find_one({"id": quote_id}, {"_id": 0})
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    if isinstance(quote.get('created_at'), str):
        quote['created_at'] = datetime.fromisoformat(quote['created_at'])
    return quote

@api_router.post("/quotes", response_model=Quote)
async def create_quote(quote: QuoteCreate):
    # Get client name
    client = await db.clients.find_one({"id": quote.client_id}, {"_id": 0})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    quote_number = await get_next_quote_number()
    
    # Calculate total
    total = 0
    for service in quote.services:
        if service.is_selected:
            total += service.price * service.quantity
    for step in quote.steps:
        for service in step.services:
            if service.is_selected:
                total += service.price * service.quantity
    
    quote_obj = Quote(
        **quote.model_dump(),
        quote_number=quote_number,
        client_name=client['company_name'],
        total_amount=total
    )
    
    doc = quote_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.quotes.insert_one(doc)
    return quote_obj

@api_router.put("/quotes/{quote_id}", response_model=Quote)
async def update_quote(quote_id: str, quote: QuoteCreate):
    existing = await db.quotes.find_one({"id": quote_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Get client name
    client = await db.clients.find_one({"id": quote.client_id}, {"_id": 0})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Calculate total
    total = 0
    for service in quote.services:
        if service.is_selected:
            total += service.price * service.quantity
    for step in quote.steps:
        for service in step.services:
            if service.is_selected:
                total += service.price * service.quantity
    
    update_data = quote.model_dump()
    update_data['client_name'] = client['company_name']
    update_data['total_amount'] = total
    
    await db.quotes.update_one({"id": quote_id}, {"$set": update_data})
    updated = await db.quotes.find_one({"id": quote_id}, {"_id": 0})
    if isinstance(updated.get('created_at'), str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    return updated

@api_router.put("/quotes/{quote_id}/status")
async def update_quote_status(quote_id: str, status: str):
    result = await db.quotes.find_one({"id": quote_id}, {"_id": 0})
    if not result:
        raise HTTPException(status_code=404, detail="Quote not found")
    await db.quotes.update_one({"id": quote_id}, {"$set": {"status": status}})
    return {"message": "Status updated"}

@api_router.delete("/quotes/{quote_id}")
async def delete_quote(quote_id: str):
    result = await db.quotes.delete_one({"id": quote_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Quote not found")
    return {"message": "Quote deleted"}

@api_router.post("/quotes/{quote_id}/duplicate", response_model=Quote)
async def duplicate_quote(quote_id: str):
    original = await db.quotes.find_one({"id": quote_id}, {"_id": 0})
    if not original:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    new_number = await get_next_quote_number()
    new_id = str(uuid.uuid4())
    
    new_quote = {**original}
    new_quote['id'] = new_id
    new_quote['quote_number'] = new_number
    new_quote['status'] = 'draft'
    new_quote['created_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.quotes.insert_one(new_quote)
    new_quote.pop('_id', None)
    if isinstance(new_quote.get('created_at'), str):
        new_quote['created_at'] = datetime.fromisoformat(new_quote['created_at'])
    return new_quote

# ==================== TEMPLATES API ====================

class Template(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    quote_type: str = "standard"
    services: List[QuoteService] = []
    steps: List[QuoteStep] = []
    premise: Optional[str] = None
    methodology: Optional[str] = None
    payment_terms: str = "30% all'accettazione, 70% alla consegna"
    delivery_time: Optional[str] = None

class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    quote_type: str = "standard"
    services: List[QuoteService] = []
    steps: List[QuoteStep] = []
    premise: Optional[str] = None
    methodology: Optional[str] = None
    payment_terms: str = "30% all'accettazione, 70% alla consegna"
    delivery_time: Optional[str] = None

@api_router.get("/templates", response_model=List[Template])
async def get_templates():
    templates = await db.templates.find({}, {"_id": 0}).to_list(100)
    return templates

@api_router.post("/templates", response_model=Template)
async def create_template(template: TemplateCreate):
    template_obj = Template(**template.model_dump())
    doc = template_obj.model_dump()
    await db.templates.insert_one(doc)
    return template_obj

@api_router.delete("/templates/{template_id}")
async def delete_template(template_id: str):
    result = await db.templates.delete_one({"id": template_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted"}

@api_router.post("/templates/from-quote/{quote_id}", response_model=Template)
async def create_template_from_quote(quote_id: str, name: str, description: str = ""):
    quote = await db.quotes.find_one({"id": quote_id}, {"_id": 0})
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    template_obj = Template(
        name=name,
        description=description,
        quote_type=quote.get('quote_type', 'standard'),
        services=quote.get('services', []),
        steps=quote.get('steps', []),
        premise=quote.get('premise', ''),
        methodology=quote.get('methodology', ''),
        payment_terms=quote.get('payment_terms', ''),
        delivery_time=quote.get('delivery_time', '')
    )
    doc = template_obj.model_dump()
    await db.templates.insert_one(doc)
    return template_obj

# ==================== PDF GENERATION ====================

def format_price(price: float, price_type: str) -> str:
    price_str = f"€ {price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    suffixes = {
        "mensile": "/mese",
        "annuale": "/anno",
        "bimestrale": "/bimestre",
        "una_tantum": ""
    }
    return price_str + suffixes.get(price_type, "")

@api_router.get("/quotes/{quote_id}/pdf")
async def generate_quote_pdf(quote_id: str):
    quote = await db.quotes.find_one({"id": quote_id}, {"_id": 0})
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    client = await db.clients.find_one({"id": quote['client_id']}, {"_id": 0})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get suppliers
    suppliers = []
    for sid in quote.get('supplier_ids', []):
        supplier = await db.suppliers.find_one({"id": sid}, {"_id": 0})
        if supplier:
            suppliers.append(supplier)
    
    # If no suppliers, get main supplier
    if not suppliers:
        main_supplier = await db.suppliers.find_one({"is_main": True}, {"_id": 0})
        if main_supplier:
            suppliers.append(main_supplier)
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=32, textColor=white, alignment=TA_LEFT, spaceAfter=20, fontName='Helvetica-Bold')
    heading_style = ParagraphStyle('Heading', parent=styles['Heading1'], fontSize=14, textColor=BLUE, spaceAfter=10, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10, spaceAfter=6, fontName='Helvetica')
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=8, textColor=HexColor('#666666'), fontName='Helvetica')
    price_style = ParagraphStyle('Price', parent=styles['Normal'], fontSize=12, textColor=BLUE, fontName='Helvetica-Bold', alignment=TA_RIGHT)
    
    elements = []
    
    # Cover page
    cover_data = [
        [Paragraph('<font color="white" size="12">LIMONE BLU STUDIO</font>', normal_style)],
        [Spacer(1, 100)],
        [Paragraph('<font color="white" size="28"><b>PREVENTIVO</b></font>', title_style)],
        [Spacer(1, 20)],
        [Paragraph(f'<font color="white" size="12">{quote.get("quote_number", "")}/2026</font>', normal_style)],
        [Spacer(1, 30)],
        [Paragraph('<font color="#dbf637" size="10">Questo documento è un preventivo collettivo basato sui costi di freelancer operanti all\'interno dello studio.</font>', small_style)],
    ]
    
    cover_table = Table(cover_data, colWidths=[16*cm])
    cover_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BLUE),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 30),
        ('RIGHTPADDING', (0, 0), (-1, -1), 30),
        ('TOPPADDING', (0, 0), (-1, -1), 50),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 50),
    ]))
    elements.append(cover_table)
    elements.append(PageBreak())
    
    # Header
    created_at = quote.get('created_at', datetime.now(timezone.utc))
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)
    date_str = created_at.strftime("%d.%m.%y")
    
    header_data = [
        [Paragraph('<b>LIMONE BLU STUDIO</b>', heading_style), Paragraph(f'Preventivo #{quote.get("quote_number", "")}', normal_style)],
        [Paragraph(f'Data: {date_str}', small_style), Paragraph(f'Og. {quote.get("subject", "")}', normal_style)],
    ]
    header_table = Table(header_data, colWidths=[8*cm, 8*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))
    
    # Supplier & Client info
    supplier_text = ""
    for s in suppliers:
        supplier_text += f"<b>{s.get('name', '')}</b><br/>"
        supplier_text += f"{s.get('legal_name', '')}<br/>"
        supplier_text += f"{s.get('address', '')}<br/>"
        supplier_text += f"P.IVA {s.get('vat_number', '')}<br/>"
        if s.get('phone'):
            supplier_text += f"{s.get('phone')}<br/>"
        if s.get('email'):
            supplier_text += f"{s.get('email')}<br/>"
        supplier_text += "<br/>"
    
    client_text = f"<b>{client.get('company_name', '')}</b><br/>"
    client_text += f"{client.get('address', '')}<br/>"
    client_text += f"P.IVA {client.get('vat_number', '')}<br/>"
    if client.get('phone'):
        client_text += f"{client.get('phone')}<br/>"
    client_text += f"{client.get('email', '')}"
    
    info_data = [
        [Paragraph('<b>Fornitore</b>', heading_style), Paragraph('<b>Cliente</b>', heading_style)],
        [Paragraph(supplier_text, small_style), Paragraph(client_text, small_style)],
    ]
    info_table = Table(info_data, colWidths=[8*cm, 8*cm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Premise
    if quote.get('premise'):
        elements.append(Paragraph('<b>Premessa</b>', heading_style))
        elements.append(Paragraph(quote['premise'], normal_style))
        elements.append(Spacer(1, 15))
    
    # Methodology
    if quote.get('methodology'):
        elements.append(Paragraph('<b>Metodologia e approccio</b>', heading_style))
        elements.append(Paragraph(quote['methodology'], normal_style))
        elements.append(Spacer(1, 15))
    
    # Services section based on quote type
    quote_type = quote.get('quote_type', 'standard')
    
    if quote_type in ('step', 'ibrido'):
        elements.append(Paragraph('<b>Fasi del progetto</b>', heading_style))
        for step_data in quote.get('steps', []):
            step_title_style = ParagraphStyle('StepTitle', parent=styles['Normal'], fontSize=12, textColor=BLUE, fontName='Helvetica-Bold', spaceAfter=4)
            elements.append(Paragraph(f"Fase {step_data.get('step_number', '')}: {step_data.get('title', '')}", step_title_style))
            if step_data.get('duration'):
                elements.append(Paragraph(f"<i>Richiede {step_data.get('duration')}</i>", small_style))
            if step_data.get('description'):
                elements.append(Paragraph(step_data['description'], normal_style))
            if step_data.get('output'):
                elements.append(Paragraph(f"<b>Output:</b> {step_data['output']}", normal_style))
            # Show services within this step
            for svc in step_data.get('services', []):
                if svc.get('is_selected', True):
                    elements.append(Spacer(1, 4))
                    elements.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>{svc.get('service_name', '')}</b> — {format_price(svc.get('price', 0), svc.get('price_type', 'una_tantum'))}", normal_style))
                    for sub in svc.get('sub_items', []):
                        elements.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• {sub}", small_style))
            elements.append(Spacer(1, 12))
    
    # Services table - Proposta economica
    elements.append(Paragraph('<b>Proposta economica</b>', heading_style))
    
    all_services = list(quote.get('services', []))
    
    # Also collect services from steps
    if quote_type in ('step', 'ibrido'):
        for step_data in quote.get('steps', []):
            all_services.extend(step_data.get('services', []))
    
    for svc in all_services:
        if svc.get('is_selected', True):
            svc_name = svc.get('service_name', '')
            svc_desc = svc.get('description', '') or ''
            sub_items = svc.get('sub_items', [])
            sub_text = ""
            for sub in sub_items:
                sub_text += f"<br/>&nbsp;&nbsp;&nbsp;&nbsp;• {sub}"
            
            svc_block = f"<b>{svc_name}</b>"
            if svc_desc:
                svc_block += f"<br/><font size='8' color='#666666'>{svc_desc}</font>"
            if sub_text:
                svc_block += f"<font size='7' color='#444444'>{sub_text}</font>"
            
            elements.append(Spacer(1, 6))
            svc_table_data = [[
                Paragraph(svc_block, normal_style),
                Paragraph(format_price(svc.get('price', 0), svc.get('price_type', 'una_tantum')), price_style)
            ]]
            svc_table = Table(svc_table_data, colWidths=[12*cm, 4*cm])
            svc_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, HexColor('#dddddd')),
            ]))
            elements.append(svc_table)
    
    # Total
    total = quote.get('total_amount', 0)
    total_str = f"\u20ac {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    elements.append(Spacer(1, 10))
    total_data = [[Paragraph('<b>TOTALE</b>', normal_style), Paragraph(f'<b>{total_str}</b>', price_style)]]
    total_table = Table(total_data, colWidths=[12*cm, 4*cm])
    total_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LINEABOVE', (0, 0), (-1, 0), 1.5, BLUE),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 20))
    
    # Additional info
    elements.append(Paragraph('<b>Info aggiuntive</b>', heading_style))
    elements.append(Paragraph(f"<b>Validità:</b> {quote.get('validity_days', 30)} giorni dalla data di emissione.", normal_style))
    elements.append(Paragraph("<b>Riservatezza:</b> Il presente documento è riservato e non può essere diffuso a terzi.", normal_style))
    
    if quote.get('delivery_time'):
        elements.append(Paragraph(f"<b>Tempi di consegna:</b> {quote.get('delivery_time')}", normal_style))
    
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Modalità di pagamento:</b> {quote.get('payment_terms', '')}", normal_style))
    elements.append(Paragraph("<b>Modalità di accettazione:</b> Inviare il presente documento firmato e timbrato a info@limoneblu.it", normal_style))
    
    if quote.get('extra_notes'):
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"<b>Note:</b> {quote.get('extra_notes')}", normal_style))
    
    # Signature
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("_________________________________", normal_style))
    elements.append(Paragraph("Firma del Rappresentante legale", small_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Preventivo_{quote.get('quote_number', '')}.pdf"}
    )

# ==================== EMAIL API ====================

@api_router.post("/quotes/{quote_id}/send-email")
async def send_quote_email(quote_id: str, email_request: EmailRequest):
    if not resend.api_key:
        raise HTTPException(status_code=500, detail="Email service not configured")
    
    quote = await db.quotes.find_one({"id": quote_id}, {"_id": 0})
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Generate PDF
    pdf_response = await generate_quote_pdf(quote_id)
    pdf_content = pdf_response.body
    pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
    
    params = {
        "from": SENDER_EMAIL,
        "to": [email_request.recipient_email],
        "subject": email_request.subject,
        "html": f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #1a281f;">
            <h2 style="color: #002fa7;">Limone Blu Studio</h2>
            <p>{email_request.message.replace(chr(10), '<br/>')}</p>
            <p>In allegato troverai il preventivo #{quote.get('quote_number', '')}.</p>
            <br/>
            <p style="color: #666;">Limone Blu Studio - enjoy the juice.</p>
        </body>
        </html>
        """,
        "attachments": [
            {
                "filename": f"Preventivo_{quote.get('quote_number', '')}.pdf",
                "content": pdf_base64
            }
        ]
    }
    
    try:
        email = await asyncio.to_thread(resend.Emails.send, params)
        # Update quote status
        await db.quotes.update_one({"id": quote_id}, {"$set": {"status": "sent"}})
        return {"status": "success", "message": f"Email sent to {email_request.recipient_email}", "email_id": email.get("id")}
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# ==================== SEED DATA ====================

@api_router.post("/seed")
async def seed_data():
    # Check if already seeded
    existing = await db.services.count_documents({})
    if existing > 0:
        return {"message": "Data already seeded"}
    
    # Seed suppliers
    suppliers_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Limone Blu Studio",
            "legal_name": "Limone Blu Studio",
            "address": "Via Marconi 99, 60035 Jesi (AN)",
            "vat_number": "",
            "phone": "",
            "email": "info@limoneblu.it",
            "is_main": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Esseppi Multimedia",
            "legal_name": "Esseppi Multimedia di Pianesi Simone",
            "address": "Via Marconi 99, 60035 Jesi (AN)",
            "vat_number": "01975820430",
            "phone": "+39 338 4533261",
            "email": "esseppimultimedia@gmail.com",
            "is_main": False
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Key Soluzioni Informatiche",
            "legal_name": "Key Soluzioni Informatiche di Michele Cappannari",
            "address": "Jesi (AN)",
            "vat_number": "",
            "phone": "",
            "email": "",
            "is_main": False
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Luca Campanelli",
            "legal_name": "Luca Campanelli",
            "address": "Via del Lavoro n.1, 60035 Jesi (AN)",
            "vat_number": "02912470420",
            "phone": "+39 334 8992998",
            "email": "campanelli.luca@icloud.com",
            "is_main": False
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Troiano Marika",
            "legal_name": "Troiano Marika",
            "address": "Via Croce Benedetto 10, 60030 Maiolati Spontini (AN)",
            "vat_number": "03021830421",
            "phone": "",
            "email": "",
            "is_main": False
        }
    ]
    await db.suppliers.insert_many(suppliers_data)
    
    # Seed services
    services_data = [
        {"id": str(uuid.uuid4()), "name": "Realizzazione sito web customizzato", "description": "Sito web personalizzato con design responsive, CMS, SEO di base e predisposizione GDPR", "sub_items": ["Progettazione grafica e personalizzazione secondo le esigenze del cliente", "Design responsive per desktop, tablet e mobile", "Inserimento di elementi dinamici per differenziazioni e valore visivo", "Possibilità di inserire e modificare contenuti testuali ed immagini in autonomia", "Progettazione secondo standard di usabilità e accessibilità", "SEO di base e revisione dei testi", "Configurazione Google Analytics", "Predisposizione GDPR: Cookie Policy, Privacy Policy, Termini e condizioni e banner Cookies"], "price": 1500.00, "price_type": "una_tantum", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Realizzazione eCommerce + WooCommerce", "description": "E-commerce completo con WooCommerce, gestione prodotti, pagamenti e spedizioni", "sub_items": ["Installazione e configurazione WooCommerce", "Design e personalizzazione del tema", "Configurazione metodi di pagamento (Stripe, PayPal)", "Configurazione spedizioni e calcolo tariffe", "Gestione catalogo prodotti con varianti", "Pagine carrello, checkout e account cliente", "Predisposizione GDPR e Cookie Policy", "SEO di base per prodotti e categorie"], "price": 2500.00, "price_type": "una_tantum", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Manutenzione e aggiornamento annuale", "description": "Aggiornamenti, backup, monitoraggio sicurezza e supporto tecnico", "sub_items": ["Aggiornamenti plugin e tema", "Rinnovo dominio, hosting e caselle email con backup", "Supporto tecnico e assistenza fino a 5h/anno", "Rinnovo licenze e applicazioni"], "price": 250.00, "price_type": "annuale", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Landing page", "description": "Pagina di atterraggio ottimizzata per conversioni", "sub_items": ["Analisi e studio piattaforma", "Studio del layout e ideazione grafica", "Settaggio e aggiustamenti responsive", "Predisposizione GDPR", "Configurazione GA4", "Consulenza per modifiche future in autonomia"], "price": 1000.00, "price_type": "una_tantum", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Configurazione iniziale account social", "description": "Setup business manager, account pubblicitario, profili business", "sub_items": ["Ottimizzazione profili social Facebook e Instagram", "Settaggio business manager", "Settaggio corretto account pubblicitario intestato all'attività del cliente"], "price": 100.00, "price_type": "una_tantum", "category": "social", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Social media management Essential", "description": "Gestione base dei canali social con piano editoriale mensile", "sub_items": ["Creazione calendario mensile per attività di promozione", "Definizione e mantenimento dell'identità visiva", "Creazione e gestione di 2 storie dove necessario", "Ideazione e pubblicazione di 2 post settimanali (statici, caroselli e Reels)", "Attività di copywriting per caption social", "Monitoraggio base delle performance (engagement, reach, salvataggi)"], "price": 250.00, "price_type": "mensile", "category": "social", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Social media management Pro", "description": "Gestione completa con strategia, contenuti, community management", "sub_items": ["Analisi e strategia", "Adeguamento della strategia di comunicazione", "Call mensile o riunione in presenza 45min", "PED mensile e calendario editoriale", "Creazione e condivisione di layout per format post e stories", "Graphic Design per creazione di grafiche", "Aggregatore di link per ottimizzazione", "Attività di copywriting", "Pubblicazione da 6 a 8 post al mese", "Micro-shooting lite bimestrale: 75-90 min con output foto + Reels"], "price": 350.00, "price_type": "mensile", "category": "social", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Creazione contenuti foto e video", "description": "Produzione di contenuti visuali per social media", "sub_items": ["Foto e video che raccontino l'atmosfera dell'attività", "Foto e video di preparazione prodotti/servizi", "Video parlati e rubriche per campagne e promozione", "Scrittura script video"], "price": 330.00, "price_type": "bimestrale", "category": "content", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Copywriting caption e testi", "description": "Scrittura professionale per social e web", "sub_items": ["Scrittura caption social per post e stories", "Scrittura testi per blog e sito web", "Storytelling e narrazione del brand", "Revisione e ottimizzazione testi esistenti"], "price": 150.00, "price_type": "mensile", "category": "content", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Pianificazione strategica PED + calendario editoriale", "description": "Piano editoriale trimestrale e calendario mensile", "sub_items": ["PED trimestrale basato su obiettivi strategici", "Calendario editoriale mensile condiviso con il cliente", "Definizione dei pillar comunicativi", "Pianificazione rubriche e format ricorrenti"], "price": 200.00, "price_type": "una_tantum", "category": "strategy", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Affiancamento marketing", "description": "Consulenza e supporto strategico continuativo", "sub_items": ["Incontri periodici di confronto e consulenza strategica", "Monitoraggio andamento attività e analisi risultati", "Valutazione KPI e individuazione nuove opportunità", "Analisi dei dati e dei trend mensile", "Adeguamento del Piano Editoriale mensile", "Definizione dei pillar comunicativi mensili"], "price": 150.00, "price_type": "mensile", "category": "strategy", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Analisi e strategia", "description": "Analisi di mercato, competitor e definizione strategia", "sub_items": ["Analisi dei competitor e posizionamento", "Analisi del target e contesti di acquisto", "Definizione posizionamento differenziante", "Touchpoint audit sui canali esistenti", "Documento con opportunità, rischi e direzioni consigliate"], "price": 500.00, "price_type": "una_tantum", "category": "strategy", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "ADV Awareness Meta (Facebook + Instagram)", "description": "Creazione e gestione campagne awareness su Meta", "sub_items": ["Creazione e gestione campagna pubblicitaria per Facebook e Instagram", "Ricerca e ideazione di un pubblico target per l'ADV", "Studio e ideazione contenuti multimediali per la campagna", "Ideazione del copy per l'ADV", "Attività di monitoraggio", "Budget a discrezione del cliente da versare direttamente a Meta (non compreso)"], "price": 70.00, "price_type": "una_tantum", "category": "advertising", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "ADV Conversione/Lead Generation", "description": "Campagne ottimizzate per conversioni e lead", "sub_items": ["Creazione campagne lead generation su Facebook e Instagram", "Configurazione moduli di contatto e landing", "Ottimizzazione audience e targeting", "A/B testing creatività e copy", "Monitoraggio e ottimizzazione continua", "Budget ads non compreso"], "price": 300.00, "price_type": "una_tantum", "category": "advertising", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Gestione campagne Google Ads Search", "description": "Gestione campagne search su Google Ads", "sub_items": ["Gestione attiva e ottimizzazione continua", "Verifica della qualità delle query", "Aggiornamento annunci", "Manutenzione della dashboard", "Comunicazione periodica risultati"], "price": 150.00, "price_type": "mensile", "category": "advertising", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Gestione campagne Google Ads Performance Max", "description": "Gestione campagne Performance Max", "sub_items": ["Setup e gestione campagne Performance Max", "Ottimizzazione feed prodotti e asset creativi", "Monitoraggio conversioni e ROAS", "Report periodici con Looker Studio"], "price": 200.00, "price_type": "mensile", "category": "advertising", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Setup ecosistema Google Ads + Analytics", "description": "Configurazione account, GA4, Tag Manager, dashboard", "sub_items": ["Configurazione metodo di pagamento", "Collegamenti Ads + GA4 + Tag Manager", "Implementazione tracciamenti", "Analisi keyword iniziale e impianto campagne", "Creazione dashboard Looker Studio", "Prima ottimizzazione"], "price": 350.00, "price_type": "una_tantum", "category": "advertising", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Revisione brand e identità visiva", "description": "Analisi e refresh dell'identità visiva esistente", "sub_items": ["Analisi brand attuale", "Ottimizzazione logo, aggiornamento palette colori e font", "Allineamento grafico ai canali social"], "price": 150.00, "price_type": "una_tantum", "category": "branding", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Allineamento brand identity base", "description": "Definizione linee guida grafiche essenziali", "sub_items": ["Brand Discovery Questionnaire", "Definizione purpose, promessa, valori", "Logo design (proposte e revisioni)", "Palette colori e tipografia", "Linee guida grafiche essenziali"], "price": 500.00, "price_type": "una_tantum", "category": "branding", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Allineamento brand identity pro", "description": "Brand identity completa con brand kit", "sub_items": ["Brand Discovery Questionnaire e raccolta materiali", "Analisi competitor e posizionamento", "Brand Strategy Deck (purpose, promessa, personalità, tone of voice)", "Logo system (primario, secondario, monogramma)", "Palette colori, tipografia, pattern, elementi grafici", "Art direction (stile fotografico, texture, materiali)", "Brand Guidelines PDF con regole d'uso", "Template base per social, banner, schede prodotto", "Handover strutturato con file organizzati"], "price": 1200.00, "price_type": "una_tantum", "category": "branding", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Campagna di lancio attività", "description": "Strategia e esecuzione lancio nuovo brand/prodotto", "sub_items": ["Definizione strategia di lancio", "Piano editoriale dedicato al lancio", "Creazione contenuti grafici e testuali", "Campagne ADV di awareness e conversione", "Coordinamento canali online e offline"], "price": 800.00, "price_type": "una_tantum", "category": "strategy", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Consulenza marketing", "description": "Consulenza strategica e operativa", "sub_items": ["Analisi del contesto e posizionamento", "Adeguamento continuo della strategia di comunicazione", "Call mensile o riunione in presenza 45min", "PED trimestrale e calendario mensile", "Supporto alle attività grafiche secondo necessità", "Consulenza nel copywriting"], "price": 500.00, "price_type": "mensile", "category": "strategy", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "SEO di base", "description": "Ottimizzazione SEO on-page essenziale", "sub_items": ["Analisi keyword e struttura sito", "Ottimizzazione meta tag (title, description)", "Ottimizzazione contenuti testuali", "Configurazione sitemap e robots.txt", "Registrazione su Google Search Console"], "price": 300.00, "price_type": "una_tantum", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "SEO avanzata", "description": "Strategia SEO completa con link building", "sub_items": ["Audit SEO completo del sito", "Strategia keyword e contenuti", "Ottimizzazione tecnica (velocità, struttura URL, schema markup)", "Link building e digital PR", "Report mensile con analisi posizionamenti", "Ottimizzazione continua basata sui dati"], "price": 500.00, "price_type": "mensile", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Local SEO Google Business Profile", "description": "Ottimizzazione profilo Google Business", "sub_items": ["Creazione o ottimizzazione scheda Google Business", "Inserimento informazioni, foto, orari", "Strategia recensioni e risposte", "Monitoraggio posizionamento locale"], "price": 200.00, "price_type": "una_tantum", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Gestione multilingua", "description": "Configurazione e gestione sito multilingua", "sub_items": ["Setup plugin multilingua (WPML/Polylang)", "Configurazione struttura URL per lingue", "Coordinamento traduzioni", "Ottimizzazione SEO per ogni lingua"], "price": 400.00, "price_type": "una_tantum", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Integrazione sistema di booking online", "description": "Integrazione sistema prenotazioni", "sub_items": ["Analisi esigenze di prenotazione", "Installazione e configurazione plugin booking", "Personalizzazione calendario e disponibilità", "Configurazione notifiche email", "Test e ottimizzazione flusso di prenotazione"], "price": 350.00, "price_type": "una_tantum", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Presenza OTA", "description": "Configurazione e gestione presenza su OTA", "sub_items": ["Setup profili su piattaforme OTA", "Ottimizzazione descrizioni e foto", "Gestione tariffe e disponibilità", "Monitoraggio recensioni"], "price": 300.00, "price_type": "una_tantum", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Email marketing", "description": "Setup e gestione campagne email", "sub_items": ["Setup piattaforma email marketing", "Design template email responsive", "Segmentazione lista contatti", "Creazione e invio newsletter periodiche", "Automazioni email (welcome, follow-up)", "Report performance (open rate, click rate)"], "price": 200.00, "price_type": "mensile", "category": "marketing", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Produzione asset creativi per campagne", "description": "Creazione grafiche e video per advertising", "sub_items": ["Ideazione visual concept per campagne", "Creazione grafiche statiche per social ads", "Creazione video brevi per advertising", "Adattamento formati per diversi posizionamenti", "Revisioni e ottimizzazioni"], "price": 250.00, "price_type": "una_tantum", "category": "content", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Supporto recupero account Meta compromesso", "description": "Assistenza per recupero account social compromessi", "sub_items": ["Analisi situazione e livello di compromissione", "Procedura di recupero tramite canali ufficiali Meta", "Messa in sicurezza account recuperato", "Consulenza su best practice di sicurezza"], "price": 150.00, "price_type": "una_tantum", "category": "support", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Fotografia progetto", "description": "Servizio fotografico professionale", "sub_items": ["Pianificazione e briefing creativo", "Sessione fotografica on-location", "Post-produzione e ritocco immagini", "Consegna file alta risoluzione", "Cessione diritti d'uso per comunicazione"], "price": 800.00, "price_type": "una_tantum", "category": "content", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Video produzione", "description": "Produzione video professionale", "sub_items": ["Scrittura script e storyboard", "Riprese video professionali", "Montaggio e post-produzione", "Color grading e grafiche animate", "Consegna in formati ottimizzati per web e social"], "price": 1000.00, "price_type": "una_tantum", "category": "content", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Formazione marketing (6 ore)", "description": "Formazione pratica sulla gestione social e marketing", "sub_items": ["Formazione di 6 ore totali divise in 3 sessioni da 2h", "Panoramica dei canali Facebook e Instagram", "Differenze tra account personali, pagine e profili business", "Preparazione base nell'utilizzo della Meta Business Suite", "Studio degli strumenti di monitoraggio e programmazione", "Principi di visual design per social (post, storie, carosello, video)", "Scrittura base per caption e storytelling"], "price": 300.00, "price_type": "una_tantum", "category": "training", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Strategia di comunicazione", "description": "Definizione strategia comunicativa integrata", "sub_items": ["Analisi del contesto di mercato e competitor", "Definizione obiettivi di comunicazione", "Identificazione target audience e personas", "Definizione canali e touchpoint", "Piano strategico integrato online/offline", "KPI e metriche di misurazione"], "price": 1200.00, "price_type": "una_tantum", "category": "strategy", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Progettazione grafica", "description": "Design materiale grafico coordinato", "sub_items": ["Materiale cartaceo informativo per territorio ed eventi", "Immagine coordinata di campagna e linee guida grafiche", "Template grafici per canali digitali", "Adattamento formati per stampa e web"], "price": 1900.00, "price_type": "una_tantum", "category": "branding", "is_active": True},
    ]
    await db.services.insert_many(services_data)
    
    # Seed predefined templates
    # We need service IDs to reference them in templates. Use the ones we just created
    svc_map = {}
    for s in services_data:
        svc_map[s['name']] = s

    def make_svc(name):
        s = svc_map.get(name, {})
        return {"service_id": s.get("id", ""), "service_name": s.get("name", name), "description": s.get("description", ""), "sub_items": s.get("sub_items", []), "price": s.get("price", 0), "price_type": s.get("price_type", "una_tantum"), "quantity": 1, "is_selected": True}

    templates_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Pacchetto Sito Web",
            "description": "Template per preventivi di realizzazione sito web con manutenzione",
            "quote_type": "standard",
            "services": [make_svc("Realizzazione sito web customizzato"), make_svc("Manutenzione e aggiornamento annuale"), make_svc("SEO di base"), make_svc("Local SEO Google Business Profile")],
            "steps": [],
            "premise": "La presente proposta riguarda la progettazione e lo sviluppo di un sito web professionale, pensato per comunicare in modo chiaro e coinvolgente i valori e i servizi della vostra attività.",
            "methodology": "Il nostro approccio si basa sulla creazione di un ecosistema digitale moderno e funzionale, ottimizzato per la visibilità sui motori di ricerca e per un'esperienza utente efficace su tutti i dispositivi.",
            "payment_terms": "30% all'accettazione, 70% alla consegna",
            "delivery_time": "4-6 settimane"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Pacchetto Social Media",
            "description": "Template per gestione social media con contenuti e ADV",
            "quote_type": "moduli",
            "services": [make_svc("Configurazione iniziale account social"), make_svc("Social media management Pro"), make_svc("Creazione contenuti foto e video"), make_svc("ADV Awareness Meta (Facebook + Instagram)"), make_svc("Affiancamento marketing")],
            "steps": [],
            "premise": "La presente proposta ha l'obiettivo di costruire una presenza digitale solida e riconoscibile, attraverso una gestione professionale dei canali social e la creazione di contenuti di qualità.",
            "methodology": "Adottiamo un approccio strategico e data-driven, combinando creatività e analisi per massimizzare l'engagement e la crescita della community online.",
            "payment_terms": "Fatturazione mensile",
            "delivery_time": "Avvio entro 1 settimana dalla conferma"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Pacchetto E-Commerce",
            "description": "Template per realizzazione e-commerce completo",
            "quote_type": "standard",
            "services": [make_svc("Realizzazione eCommerce + WooCommerce"), make_svc("Manutenzione e aggiornamento annuale"), make_svc("SEO di base"), make_svc("Email marketing"), make_svc("Gestione campagne Google Ads Search")],
            "steps": [],
            "premise": "La presente proposta riguarda la realizzazione di un e-commerce professionale, progettato per offrire un'esperienza di acquisto intuitiva e sicura ai vostri clienti.",
            "methodology": "Sviluppiamo soluzioni e-commerce personalizzate con WooCommerce, integrando strategie di marketing digitale per massimizzare le vendite online.",
            "payment_terms": "30% all'accettazione, 40% a metà lavoro, 30% alla consegna",
            "delivery_time": "6-8 settimane"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Pacchetto Brand Identity",
            "description": "Template per percorso di branding completo a step",
            "quote_type": "step",
            "services": [],
            "steps": [
                {"step_number": 1, "title": "Onboarding e set-up", "description": "Raccolta informazioni strutturate su storia del brand, obiettivi, percezione attuale e direzione desiderata.", "duration": "3 giorni", "output": "Brief approvato, calendario scadenze, lista asset necessari", "services": [make_svc("Analisi e strategia")]},
                {"step_number": 2, "title": "Analisi e insight", "description": "Analisi competitor, definizione posizionamento, analisi target e touchpoint audit.", "duration": "5 giorni", "output": "Documento con opportunità, rischi e direzioni consigliate", "services": [make_svc("Analisi e strategia")]},
                {"step_number": 3, "title": "Brand Strategy", "description": "Definizione purpose, promessa, valori, personalità, tone of voice e value proposition.", "duration": "10 giorni", "output": "Brand Strategy Deck", "services": [make_svc("Allineamento brand identity pro")]},
                {"step_number": 4, "title": "Brand Identity", "description": "Proposte logo, direzione creativa completa: logo system, palette colori, tipografia, pattern.", "duration": "12 giorni", "output": "Brand Identity approvata", "services": [make_svc("Progettazione grafica")]},
                {"step_number": 5, "title": "Brand Kit e lancio", "description": "Creazione brand guidelines, template base e handover strutturato.", "duration": "5 giorni", "output": "Brand Kit completo, Kit di lancio", "services": [make_svc("Revisione brand e identità visiva")]}
            ],
            "premise": "Il percorso proposto mira a costruire un'identità di brand solida, coerente e riconoscibile, partendo da un'analisi approfondita fino alla creazione di tutti gli strumenti necessari per comunicare efficacemente.",
            "methodology": "Adottiamo un approccio strategico e progressivo: ogni fase si basa sui risultati della precedente, garantendo coerenza e qualità in ogni passaggio del processo creativo.",
            "payment_terms": "30% all'accettazione, 30% a metà percorso, 40% alla consegna",
            "delivery_time": "35 giorni lavorativi"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Pacchetto Google Ads",
            "description": "Template per gestione campagne Google Ads",
            "quote_type": "standard",
            "services": [make_svc("Setup ecosistema Google Ads + Analytics"), make_svc("Gestione campagne Google Ads Search"), make_svc("Gestione campagne Google Ads Performance Max")],
            "steps": [],
            "premise": "La presente proposta riguarda la configurazione e gestione professionale di campagne pubblicitarie su Google Ads, con l'obiettivo di aumentare la visibilità online e generare contatti qualificati.",
            "methodology": "Il nostro approccio si basa su un'analisi approfondita delle keyword strategiche e sull'ottimizzazione continua delle campagne, supportata da dashboard di monitoraggio in tempo reale.",
            "payment_terms": "Setup una tantum + fatturazione mensile per gestione",
            "delivery_time": "Setup in 1 settimana, gestione continuativa"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Pacchetto Lancio Attività",
            "description": "Template completo per lancio nuova attività (ibrido)",
            "quote_type": "ibrido",
            "services": [make_svc("Configurazione iniziale account social"), make_svc("Campagna di lancio attività")],
            "steps": [
                {"step_number": 1, "title": "Strategia e brand", "description": "Definizione strategia comunicativa e allineamento identità visiva per il lancio.", "duration": "2 settimane", "output": "Strategia di lancio, Brand kit", "services": [make_svc("Strategia di comunicazione"), make_svc("Revisione brand e identità visiva")]},
                {"step_number": 2, "title": "Sito web e presenza digitale", "description": "Realizzazione sito web e ottimizzazione SEO per il lancio.", "duration": "4 settimane", "output": "Sito web online, Google Business configurato", "services": [make_svc("Realizzazione sito web customizzato"), make_svc("SEO di base"), make_svc("Local SEO Google Business Profile")]},
                {"step_number": 3, "title": "Social e ADV", "description": "Avvio gestione social e campagne pubblicitarie di lancio.", "duration": "Continuativa", "output": "Canali social attivi, Campagne ADV in corso", "services": [make_svc("Social media management Pro"), make_svc("ADV Awareness Meta (Facebook + Instagram)")]}
            ],
            "premise": "Questo percorso è pensato per accompagnare il lancio della vostra attività con una strategia di comunicazione integrata, dalla definizione del brand alla presenza online e alla promozione attiva.",
            "methodology": "Un approccio a fasi progressive che garantisce una base solida prima di procedere con la promozione, massimizzando l'impatto del lancio.",
            "payment_terms": "Piano personalizzato in base alle fasi",
            "delivery_time": "8-10 settimane per il setup, poi gestione continuativa"
        }
    ]
    await db.templates.insert_many(templates_data)
    
    return {"message": "Data seeded successfully", "services_count": len(services_data), "suppliers_count": len(suppliers_data), "templates_count": len(templates_data)}

# ==================== ROOT ====================

@api_router.get("/")
async def root():
    return {"message": "Limone Blu Studio - Quote Generator API"}

# Include router and middleware
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
