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
    price: float
    price_type: str = "una_tantum"  # una_tantum, mensile, annuale, bimestrale
    category: str = "general"
    is_active: bool = True

class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    price_type: str = "una_tantum"
    category: str = "general"
    is_active: bool = True

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    price_type: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class QuoteService(BaseModel):
    service_id: str
    service_name: str
    description: Optional[str] = None
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
        [Paragraph(f'<font color="#dbf637" size="10">Questo documento è un preventivo collettivo basato sui costi di freelancer operanti all\'interno dello studio.</font>', small_style)],
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
        [Paragraph(f'<b>LIMONE BLU STUDIO</b>', heading_style), Paragraph(f'Preventivo #{quote.get("quote_number", "")}', normal_style)],
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
    
    if quote_type == 'step' or quote_type == 'ibrido':
        elements.append(Paragraph('<b>Fasi del progetto</b>', heading_style))
        for step in quote.get('steps', []):
            elements.append(Paragraph(f"<b>Fase {step.get('step_number', '')}: {step.get('title', '')}</b>", normal_style))
            if step.get('duration'):
                elements.append(Paragraph(f"<i>Richiede {step.get('duration')}</i>", small_style))
            if step.get('description'):
                elements.append(Paragraph(step['description'], normal_style))
            if step.get('output'):
                elements.append(Paragraph(f"<b>Output:</b> {step['output']}", normal_style))
            elements.append(Spacer(1, 10))
    
    # Services table
    elements.append(Paragraph('<b>Proposta economica</b>', heading_style))
    
    service_data = [['Servizio', 'Prezzo']]
    all_services = quote.get('services', [])
    
    # Also collect services from steps for ibrido type
    if quote_type in ['step', 'ibrido']:
        for step in quote.get('steps', []):
            all_services.extend(step.get('services', []))
    
    for svc in all_services:
        if svc.get('is_selected', True):
            service_data.append([
                Paragraph(f"<b>{svc.get('service_name', '')}</b><br/><font size='8'>{svc.get('description', '') or ''}</font>", normal_style),
                Paragraph(format_price(svc.get('price', 0), svc.get('price_type', 'una_tantum')), price_style)
            ])
    
    # Total
    total = quote.get('total_amount', 0)
    total_str = f"€ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    service_data.append(['', ''])
    service_data.append([Paragraph('<b>TOTALE</b>', normal_style), Paragraph(f'<b>{total_str}</b>', price_style)])
    
    service_table = Table(service_data, colWidths=[12*cm, 4*cm])
    service_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -3), 0.5, HexColor('#dddddd')),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(service_table)
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
        {"id": str(uuid.uuid4()), "name": "Realizzazione sito web customizzato", "description": "Sito web personalizzato con design responsive, CMS, SEO di base e predisposizione GDPR", "price": 1500.00, "price_type": "una_tantum", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Realizzazione eCommerce + WooCommerce", "description": "E-commerce completo con WooCommerce, gestione prodotti, pagamenti e spedizioni", "price": 2500.00, "price_type": "una_tantum", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Manutenzione e aggiornamento annuale", "description": "Aggiornamenti, backup, monitoraggio sicurezza e supporto tecnico", "price": 250.00, "price_type": "annuale", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Landing page", "description": "Pagina di atterraggio ottimizzata per conversioni", "price": 1000.00, "price_type": "una_tantum", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Configurazione iniziale account social", "description": "Setup business manager, account pubblicitario, profili business", "price": 100.00, "price_type": "una_tantum", "category": "social", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Social media management Essential", "description": "Gestione base dei canali social con piano editoriale mensile", "price": 250.00, "price_type": "mensile", "category": "social", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Social media management Pro", "description": "Gestione completa con strategia, contenuti, community management", "price": 350.00, "price_type": "mensile", "category": "social", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Creazione contenuti foto e video", "description": "Produzione di contenuti visuali per social media", "price": 330.00, "price_type": "bimestrale", "category": "content", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Copywriting caption e testi", "description": "Scrittura professionale per social e web", "price": 150.00, "price_type": "mensile", "category": "content", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Pianificazione strategica PED + calendario editoriale", "description": "Piano editoriale trimestrale e calendario mensile", "price": 200.00, "price_type": "una_tantum", "category": "strategy", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Affiancamento marketing", "description": "Consulenza e supporto strategico continuativo", "price": 150.00, "price_type": "mensile", "category": "strategy", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Analisi e strategia", "description": "Analisi di mercato, competitor e definizione strategia", "price": 500.00, "price_type": "una_tantum", "category": "strategy", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "ADV Awareness Meta (Facebook + Instagram)", "description": "Creazione e gestione campagne awareness su Meta", "price": 70.00, "price_type": "una_tantum", "category": "advertising", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "ADV Conversione/Lead Generation", "description": "Campagne ottimizzate per conversioni e lead", "price": 300.00, "price_type": "una_tantum", "category": "advertising", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Gestione campagne Google Ads Search", "description": "Gestione campagne search su Google Ads", "price": 150.00, "price_type": "mensile", "category": "advertising", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Gestione campagne Google Ads Performance Max", "description": "Gestione campagne Performance Max", "price": 200.00, "price_type": "mensile", "category": "advertising", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Setup ecosistema Google Ads + Analytics", "description": "Configurazione account, GA4, Tag Manager, dashboard", "price": 350.00, "price_type": "una_tantum", "category": "advertising", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Revisione brand e identità visiva", "description": "Analisi e refresh dell'identità visiva esistente", "price": 150.00, "price_type": "una_tantum", "category": "branding", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Allineamento brand identity base", "description": "Definizione linee guida grafiche essenziali", "price": 500.00, "price_type": "una_tantum", "category": "branding", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Allineamento brand identity pro", "description": "Brand identity completa con brand kit", "price": 1200.00, "price_type": "una_tantum", "category": "branding", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Campagna di lancio attività", "description": "Strategia e esecuzione lancio nuovo brand/prodotto", "price": 800.00, "price_type": "una_tantum", "category": "strategy", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Consulenza marketing", "description": "Consulenza strategica e operativa", "price": 500.00, "price_type": "mensile", "category": "strategy", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "SEO di base", "description": "Ottimizzazione SEO on-page essenziale", "price": 300.00, "price_type": "una_tantum", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "SEO avanzata", "description": "Strategia SEO completa con link building", "price": 500.00, "price_type": "mensile", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Local SEO Google Business Profile", "description": "Ottimizzazione profilo Google Business", "price": 200.00, "price_type": "una_tantum", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Gestione multilingua", "description": "Configurazione e gestione sito multilingua", "price": 400.00, "price_type": "una_tantum", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Integrazione sistema di booking online", "description": "Integrazione sistema prenotazioni", "price": 350.00, "price_type": "una_tantum", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Presenza OTA", "description": "Configurazione e gestione presenza su OTA", "price": 300.00, "price_type": "una_tantum", "category": "web", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Email marketing", "description": "Setup e gestione campagne email", "price": 200.00, "price_type": "mensile", "category": "marketing", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Produzione asset creativi per campagne", "description": "Creazione grafiche e video per advertising", "price": 250.00, "price_type": "una_tantum", "category": "content", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Supporto recupero account Meta compromesso", "description": "Assistenza per recupero account social compromessi", "price": 150.00, "price_type": "una_tantum", "category": "support", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Fotografia progetto", "description": "Servizio fotografico professionale", "price": 800.00, "price_type": "una_tantum", "category": "content", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Video produzione", "description": "Produzione video professionale", "price": 1000.00, "price_type": "una_tantum", "category": "content", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Formazione marketing (6 ore)", "description": "Formazione pratica sulla gestione social e marketing", "price": 300.00, "price_type": "una_tantum", "category": "training", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Strategia di comunicazione", "description": "Definizione strategia comunicativa integrata", "price": 1200.00, "price_type": "una_tantum", "category": "strategy", "is_active": True},
        {"id": str(uuid.uuid4()), "name": "Progettazione grafica", "description": "Design materiale grafico coordinato", "price": 1900.00, "price_type": "una_tantum", "category": "branding", "is_active": True},
    ]
    await db.services.insert_many(services_data)
    
    return {"message": "Data seeded successfully", "services_count": len(services_data), "suppliers_count": len(suppliers_data)}

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
