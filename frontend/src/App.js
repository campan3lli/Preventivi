import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, NavLink, useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Textarea } from "./components/ui/textarea";
import { Checkbox } from "./components/ui/checkbox";
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "./components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Badge } from "./components/ui/badge";
import { ScrollArea } from "./components/ui/scroll-area";
import { 
  FileText, Users, Package, Home, Plus, Search, Edit, Trash2, 
  Download, Mail, Eye, ChevronRight, List, Layers, Grid3X3, Shuffle,
  Building2, Phone, MapPin, Receipt, Settings, CheckCircle2, Copy,
  BookTemplate, Bookmark, GripVertical
} from "lucide-react";
import { DndContext, closestCenter, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy, useSortable, arrayMove } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Logo component
const Logo = ({ variant = "white", size = 40 }) => (
  <img 
    src={variant === "blue" 
      ? "https://customer-assets.emergentagent.com/job_quote-builder-217/artifacts/9u4ii33h_1.png"
      : variant === "lime"
      ? "https://customer-assets.emergentagent.com/job_quote-builder-217/artifacts/9puk5jut_2.png"
      : "https://customer-assets.emergentagent.com/job_quote-builder-217/artifacts/sliapkzx_3.png"
    }
    alt="Limone Blu Studio"
    style={{ width: size, height: 'auto' }}
  />
);

// Sidebar component
const Sidebar = () => (
  <aside className="sidebar" data-testid="sidebar">
    <div className="sidebar-logo">
      <Logo variant="lime" size={60} />
    </div>
    <nav className="sidebar-nav">
      <NavLink to="/" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} data-testid="nav-dashboard">
        <Home size={20} />
        Dashboard
      </NavLink>
      <NavLink to="/preventivi" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} data-testid="nav-quotes">
        <FileText size={20} />
        Preventivi
      </NavLink>
      <NavLink to="/clienti" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} data-testid="nav-clients">
        <Users size={20} />
        Clienti
      </NavLink>
      <NavLink to="/servizi" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} data-testid="nav-services">
        <Package size={20} />
        Servizi
      </NavLink>
      <NavLink to="/fornitori" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} data-testid="nav-suppliers">
        <Building2 size={20} />
        Fornitori
      </NavLink>
      <NavLink to="/template" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} data-testid="nav-templates">
        <Bookmark size={20} />
        Template
      </NavLink>
    </nav>
  </aside>
);

// Format price helper
const formatPrice = (price, priceType) => {
  const formatted = new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(price);
  const suffixes = { mensile: '/mese', annuale: '/anno', bimestrale: '/bimestre', una_tantum: '' };
  return formatted + (suffixes[priceType] || '');
};

// Status badge component
const StatusBadge = ({ status }) => {
  const styles = {
    draft: 'bg-gray-100 text-gray-700',
    sent: 'bg-blue-100 text-blue-700',
    accepted: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700'
  };
  const labels = { draft: 'Bozza', sent: 'Inviato', accepted: 'Accettato', rejected: 'Rifiutato' };
  return <Badge className={styles[status] || styles.draft}>{labels[status] || status}</Badge>;
};

// Dashboard page
const Dashboard = () => {
  const [stats, setStats] = useState({ quotes: 0, clients: 0, services: 0, total: 0 });
  const [recentQuotes, setRecentQuotes] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [quotesRes, clientsRes, servicesRes] = await Promise.all([
          axios.get(`${API}/quotes`),
          axios.get(`${API}/clients`),
          axios.get(`${API}/services`)
        ]);
        const quotes = quotesRes.data;
        const total = quotes.reduce((sum, q) => sum + (q.total_amount || 0), 0);
        setStats({
          quotes: quotes.length,
          clients: clientsRes.data.length,
          services: servicesRes.data.length,
          total
        });
        setRecentQuotes(quotes.slice(-5).reverse());
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="animate-fadeIn" data-testid="dashboard-page">
      <div className="page-header flex justify-between items-center">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Panoramica della tua attività</p>
        </div>
        <Button onClick={() => navigate('/preventivi/nuovo')} className="btn-primary gap-2" data-testid="new-quote-btn">
          <Plus size={18} /> Nuovo Preventivo
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="stats-card card-hover" data-testid="stat-quotes">
          <CardContent className="p-6">
            <div className="flex justify-between items-center">
              <div>
                <p className="stats-card-title">Preventivi</p>
                <p className="stats-card-value">{stats.quotes}</p>
              </div>
              <div className="w-12 h-12 min-w-[3rem] rounded-xl bg-[#002fa7] text-white flex items-center justify-center">
                <FileText size={22} />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="stats-card card-hover" data-testid="stat-clients">
          <CardContent className="p-6">
            <div className="flex justify-between items-center">
              <div>
                <p className="stats-card-title">Clienti</p>
                <p className="stats-card-value">{stats.clients}</p>
              </div>
              <div className="w-12 h-12 min-w-[3rem] rounded-xl bg-[#dbf637] text-[#1a281f] flex items-center justify-center">
                <Users size={22} />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="stats-card card-hover" data-testid="stat-services">
          <CardContent className="p-6">
            <div className="flex justify-between items-center">
              <div>
                <p className="stats-card-title">Servizi</p>
                <p className="stats-card-value">{stats.services}</p>
              </div>
              <div className="w-12 h-12 min-w-[3rem] rounded-xl bg-[#1a281f] text-white flex items-center justify-center">
                <Package size={22} />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="stats-card card-hover" data-testid="stat-total">
          <CardContent className="p-6">
            <div className="flex justify-between items-center">
              <div className="min-w-0">
                <p className="stats-card-title">Totale Preventivi</p>
                <p className="stats-card-value text-[#002fa7] truncate text-2xl">
                  {new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(stats.total)}
                </p>
              </div>
              <div className="w-12 h-12 min-w-[3rem] rounded-xl bg-[#002fa7] text-white flex items-center justify-center">
                <Receipt size={22} />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card data-testid="recent-quotes">
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Preventivi Recenti</CardTitle>
        </CardHeader>
        <CardContent>
          {recentQuotes.length > 0 ? (
            <div className="space-y-3">
              {recentQuotes.map((quote) => (
                <div key={quote.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
                  onClick={() => navigate(`/preventivi/${quote.id}`)} data-testid={`quote-item-${quote.id}`}>
                  <div className="flex items-center gap-4 min-w-0">
                    <div className="w-10 h-10 min-w-[2.5rem] bg-[#002fa7] text-white rounded-lg flex items-center justify-center font-bold text-sm shrink-0">
                      #{quote.quote_number}
                    </div>
                    <div className="min-w-0">
                      <p className="font-semibold text-[#1a281f] truncate">{quote.client_name}</p>
                      <p className="text-sm text-gray-500 truncate">{quote.subject}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0 ml-4">
                    <StatusBadge status={quote.status} />
                    <span className="font-bold text-[#002fa7] whitespace-nowrap">{formatPrice(quote.total_amount, 'una_tantum')}</span>
                    <ChevronRight size={20} className="text-gray-400" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon"><FileText size={32} /></div>
              <p className="empty-state-title">Nessun preventivo</p>
              <p className="empty-state-desc">Crea il tuo primo preventivo per iniziare</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Clients page
const ClientsPage = () => {
  const [clients, setClients] = useState([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingClient, setEditingClient] = useState(null);
  const [formData, setFormData] = useState({ company_name: '', vat_number: '', address: '', email: '', phone: '' });

  const fetchClients = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/clients`);
      setClients(res.data);
    } catch (err) { console.error(err); }
  }, []);

  useEffect(() => { fetchClients(); }, [fetchClients]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingClient) {
        await axios.put(`${API}/clients/${editingClient.id}`, formData);
        toast.success('Cliente aggiornato');
      } else {
        await axios.post(`${API}/clients`, formData);
        toast.success('Cliente creato');
      }
      setIsModalOpen(false);
      setEditingClient(null);
      setFormData({ company_name: '', vat_number: '', address: '', email: '', phone: '' });
      fetchClients();
    } catch (err) {
      toast.error('Errore nel salvataggio');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Eliminare questo cliente?')) {
      try {
        await axios.delete(`${API}/clients/${id}`);
        toast.success('Cliente eliminato');
        fetchClients();
      } catch (err) { toast.error('Errore'); }
    }
  };

  const openEdit = (client) => {
    setEditingClient(client);
    setFormData(client);
    setIsModalOpen(true);
  };

  const filteredClients = clients.filter(c => 
    c.company_name.toLowerCase().includes(search.toLowerCase()) ||
    c.email.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="animate-fadeIn" data-testid="clients-page">
      <div className="page-header flex justify-between items-center">
        <div>
          <h1 className="page-title">Clienti</h1>
          <p className="page-subtitle">Gestisci la tua anagrafica clienti</p>
        </div>
        <Button onClick={() => { setEditingClient(null); setFormData({ company_name: '', vat_number: '', address: '', email: '', phone: '' }); setIsModalOpen(true); }} 
          className="btn-primary gap-2" data-testid="add-client-btn">
          <Plus size={18} /> Nuovo Cliente
        </Button>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="flex gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <Input placeholder="Cerca cliente..." value={search} onChange={(e) => setSearch(e.target.value)} 
                className="pl-10" data-testid="search-clients" />
            </div>
          </div>

          {filteredClients.length > 0 ? (
            <table className="data-table" data-testid="clients-table">
              <thead>
                <tr>
                  <th>Azienda</th>
                  <th>P.IVA</th>
                  <th>Email</th>
                  <th>Telefono</th>
                  <th>Azioni</th>
                </tr>
              </thead>
              <tbody>
                {filteredClients.map((client) => (
                  <tr key={client.id} data-testid={`client-row-${client.id}`}>
                    <td className="font-semibold">{client.company_name}</td>
                    <td>{client.vat_number}</td>
                    <td>{client.email}</td>
                    <td>{client.phone || '-'}</td>
                    <td>
                      <div className="flex gap-2">
                        <Button variant="ghost" size="sm" onClick={() => openEdit(client)} data-testid={`edit-client-${client.id}`}>
                          <Edit size={16} />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(client.id)} className="text-red-600" data-testid={`delete-client-${client.id}`}>
                          <Trash2 size={16} />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon"><Users size={32} /></div>
              <p className="empty-state-title">Nessun cliente</p>
              <p className="empty-state-desc">Aggiungi il tuo primo cliente</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent data-testid="client-modal">
          <DialogHeader>
            <DialogTitle>{editingClient ? 'Modifica Cliente' : 'Nuovo Cliente'}</DialogTitle>
            <DialogDescription>Inserisci i dati del cliente per l'anagrafica</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div>
                <label className="form-label">Nome Azienda *</label>
                <Input value={formData.company_name} onChange={(e) => setFormData({...formData, company_name: e.target.value})} 
                  required data-testid="client-name-input" />
              </div>
              <div>
                <label className="form-label">P.IVA *</label>
                <Input value={formData.vat_number} onChange={(e) => setFormData({...formData, vat_number: e.target.value})} 
                  required data-testid="client-vat-input" />
              </div>
              <div>
                <label className="form-label">Indirizzo *</label>
                <Input value={formData.address} onChange={(e) => setFormData({...formData, address: e.target.value})} 
                  required data-testid="client-address-input" />
              </div>
              <div>
                <label className="form-label">Email *</label>
                <Input type="email" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} 
                  required data-testid="client-email-input" />
              </div>
              <div>
                <label className="form-label">Telefono</label>
                <Input value={formData.phone} onChange={(e) => setFormData({...formData, phone: e.target.value})} 
                  data-testid="client-phone-input" />
              </div>
            </div>
            <DialogFooter className="mt-6">
              <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Annulla</Button>
              <Button type="submit" className="btn-primary" data-testid="save-client-btn">Salva</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Services page
const ServicesPage = () => {
  const [services, setServices] = useState([]);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingService, setEditingService] = useState(null);
  const [formData, setFormData] = useState({ name: '', description: '', price: '', price_type: 'una_tantum', category: 'general', is_active: true });

  const categories = ['web', 'social', 'content', 'strategy', 'advertising', 'branding', 'marketing', 'training', 'support', 'general'];
  const priceTypes = [
    { value: 'una_tantum', label: 'Una tantum' },
    { value: 'mensile', label: 'Mensile' },
    { value: 'annuale', label: 'Annuale' },
    { value: 'bimestrale', label: 'Bimestrale' }
  ];

  const fetchServices = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/services`);
      setServices(res.data);
    } catch (err) { console.error(err); }
  }, []);

  useEffect(() => { fetchServices(); }, [fetchServices]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = { ...formData, price: parseFloat(formData.price) };
      if (editingService) {
        await axios.put(`${API}/services/${editingService.id}`, data);
        toast.success('Servizio aggiornato');
      } else {
        await axios.post(`${API}/services`, data);
        toast.success('Servizio creato');
      }
      setIsModalOpen(false);
      setEditingService(null);
      fetchServices();
    } catch (err) { toast.error('Errore'); }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Eliminare questo servizio?')) {
      try {
        await axios.delete(`${API}/services/${id}`);
        toast.success('Servizio eliminato');
        fetchServices();
      } catch (err) { toast.error('Errore'); }
    }
  };

  const openEdit = (service) => {
    setEditingService(service);
    setFormData({ ...service, price: service.price.toString() });
    setIsModalOpen(true);
  };

  const filteredServices = services.filter(s => 
    (s.name.toLowerCase().includes(search.toLowerCase()) || (s.description || '').toLowerCase().includes(search.toLowerCase())) &&
    (categoryFilter === 'all' || s.category === categoryFilter)
  );

  return (
    <div className="animate-fadeIn" data-testid="services-page">
      <div className="page-header flex justify-between items-center">
        <div>
          <h1 className="page-title">Servizi</h1>
          <p className="page-subtitle">Gestisci il listino prezzi</p>
        </div>
        <Button onClick={() => { setEditingService(null); setFormData({ name: '', description: '', price: '', price_type: 'una_tantum', category: 'general', is_active: true }); setIsModalOpen(true); }} 
          className="btn-primary gap-2" data-testid="add-service-btn">
          <Plus size={18} /> Nuovo Servizio
        </Button>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="flex gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <Input placeholder="Cerca servizio..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" data-testid="search-services" />
            </div>
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-48" data-testid="category-filter">
                <SelectValue placeholder="Categoria" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tutte le categorie</SelectItem>
                {categories.map(cat => <SelectItem key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>

          {filteredServices.length > 0 ? (
            <div className="service-list">
              {filteredServices.map((service) => (
                <div key={service.id} className="service-item" data-testid={`service-item-${service.id}`}>
                  <div className="service-info min-w-0 flex-1 mr-4">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="service-name">{service.name}</span>
                      <Badge variant="outline" className="text-xs shrink-0">{service.category}</Badge>
                      {!service.is_active && <Badge variant="secondary" className="text-xs shrink-0">Disattivato</Badge>}
                    </div>
                    <p className="service-desc truncate">{service.description}</p>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <span className="service-price whitespace-nowrap">{formatPrice(service.price, service.price_type)}</span>
                    <div className="flex gap-0.5">
                      <Button variant="ghost" size="sm" onClick={() => openEdit(service)} data-testid={`edit-service-${service.id}`}>
                        <Edit size={16} />
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(service.id)} className="text-red-600" data-testid={`delete-service-${service.id}`}>
                        <Trash2 size={16} />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon"><Package size={32} /></div>
              <p className="empty-state-title">Nessun servizio</p>
              <p className="empty-state-desc">Aggiungi i tuoi servizi al listino</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent data-testid="service-modal">
          <DialogHeader>
            <DialogTitle>{editingService ? 'Modifica Servizio' : 'Nuovo Servizio'}</DialogTitle>
            <DialogDescription>Gestisci i dettagli e il prezzo del servizio</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div>
                <label className="form-label">Nome Servizio *</label>
                <Input value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} required data-testid="service-name-input" />
              </div>
              <div>
                <label className="form-label">Descrizione</label>
                <Textarea value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} data-testid="service-desc-input" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="form-label">Prezzo *</label>
                  <Input type="number" step="0.01" value={formData.price} onChange={(e) => setFormData({...formData, price: e.target.value})} required data-testid="service-price-input" />
                </div>
                <div>
                  <label className="form-label">Tipo Prezzo</label>
                  <Select value={formData.price_type} onValueChange={(v) => setFormData({...formData, price_type: v})}>
                    <SelectTrigger data-testid="service-pricetype-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {priceTypes.map(pt => <SelectItem key={pt.value} value={pt.value}>{pt.label}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <label className="form-label">Categoria</label>
                <Select value={formData.category} onValueChange={(v) => setFormData({...formData, category: v})}>
                  <SelectTrigger data-testid="service-category-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map(cat => <SelectItem key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox checked={formData.is_active} onCheckedChange={(c) => setFormData({...formData, is_active: c})} data-testid="service-active-checkbox" />
                <label className="text-sm">Servizio attivo</label>
              </div>
            </div>
            <DialogFooter className="mt-6">
              <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Annulla</Button>
              <Button type="submit" className="btn-primary" data-testid="save-service-btn">Salva</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Suppliers page
const SuppliersPage = () => {
  const [suppliers, setSuppliers] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState(null);
  const [formData, setFormData] = useState({ name: '', legal_name: '', address: '', vat_number: '', phone: '', email: '', is_main: false });

  const fetchSuppliers = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/suppliers`);
      setSuppliers(res.data);
    } catch (err) { console.error(err); }
  }, []);

  useEffect(() => { fetchSuppliers(); }, [fetchSuppliers]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingSupplier) {
        await axios.put(`${API}/suppliers/${editingSupplier.id}`, formData);
        toast.success('Fornitore aggiornato');
      } else {
        await axios.post(`${API}/suppliers`, formData);
        toast.success('Fornitore creato');
      }
      setIsModalOpen(false);
      setEditingSupplier(null);
      fetchSuppliers();
    } catch (err) { toast.error('Errore'); }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Eliminare questo fornitore?')) {
      try {
        await axios.delete(`${API}/suppliers/${id}`);
        toast.success('Fornitore eliminato');
        fetchSuppliers();
      } catch (err) { toast.error('Errore'); }
    }
  };

  return (
    <div className="animate-fadeIn" data-testid="suppliers-page">
      <div className="page-header flex justify-between items-center">
        <div>
          <h1 className="page-title">Fornitori</h1>
          <p className="page-subtitle">Gestisci i collaboratori dello studio</p>
        </div>
        <Button onClick={() => { setEditingSupplier(null); setFormData({ name: '', legal_name: '', address: '', vat_number: '', phone: '', email: '', is_main: false }); setIsModalOpen(true); }} 
          className="btn-primary gap-2" data-testid="add-supplier-btn">
          <Plus size={18} /> Nuovo Fornitore
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {suppliers.map((supplier) => (
          <Card key={supplier.id} className="card-hover" data-testid={`supplier-card-${supplier.id}`}>
            <CardContent className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="font-semibold text-lg text-[#1a281f]">{supplier.name}</h3>
                  {supplier.is_main && <Badge className="bg-[#dbf637] text-[#1a281f] mt-1">Principale</Badge>}
                </div>
                <div className="flex gap-1">
                  <Button variant="ghost" size="sm" onClick={() => { setEditingSupplier(supplier); setFormData(supplier); setIsModalOpen(true); }}>
                    <Edit size={16} />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => handleDelete(supplier.id)} className="text-red-600">
                    <Trash2 size={16} />
                  </Button>
                </div>
              </div>
              <p className="text-sm text-gray-600 mb-2">{supplier.legal_name}</p>
              <div className="space-y-1 text-sm text-gray-500">
                {supplier.address && <p className="flex items-center gap-2"><MapPin size={14} /> {supplier.address}</p>}
                {supplier.vat_number && <p>P.IVA: {supplier.vat_number}</p>}
                {supplier.phone && <p className="flex items-center gap-2"><Phone size={14} /> {supplier.phone}</p>}
                {supplier.email && <p>{supplier.email}</p>}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent data-testid="supplier-modal">
          <DialogHeader>
            <DialogTitle>{editingSupplier ? 'Modifica Fornitore' : 'Nuovo Fornitore'}</DialogTitle>
            <DialogDescription>Gestisci i dati del collaboratore</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div>
                <label className="form-label">Nome *</label>
                <Input value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} required />
              </div>
              <div>
                <label className="form-label">Ragione Sociale</label>
                <Input value={formData.legal_name} onChange={(e) => setFormData({...formData, legal_name: e.target.value})} />
              </div>
              <div>
                <label className="form-label">Indirizzo</label>
                <Input value={formData.address} onChange={(e) => setFormData({...formData, address: e.target.value})} />
              </div>
              <div>
                <label className="form-label">P.IVA</label>
                <Input value={formData.vat_number} onChange={(e) => setFormData({...formData, vat_number: e.target.value})} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="form-label">Telefono</label>
                  <Input value={formData.phone} onChange={(e) => setFormData({...formData, phone: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">Email</label>
                  <Input type="email" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox checked={formData.is_main} onCheckedChange={(c) => setFormData({...formData, is_main: c})} />
                <label className="text-sm">Fornitore principale</label>
              </div>
            </div>
            <DialogFooter className="mt-6">
              <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Annulla</Button>
              <Button type="submit" className="btn-primary">Salva</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Quotes list page
const QuotesPage = () => {
  const [quotes, setQuotes] = useState([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchQuotes = async () => {
      try {
        const res = await axios.get(`${API}/quotes`);
        setQuotes(res.data.reverse());
      } catch (err) { console.error(err); }
    };
    fetchQuotes();
  }, []);

  const handleDelete = async (id) => {
    if (window.confirm('Eliminare questo preventivo?')) {
      try {
        await axios.delete(`${API}/quotes/${id}`);
        toast.success('Preventivo eliminato');
        setQuotes(quotes.filter(q => q.id !== id));
      } catch (err) { toast.error('Errore'); }
    }
  };

  const handleDownload = async (quote) => {
    try {
      const res = await axios.get(`${API}/quotes/${quote.id}/pdf`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Preventivo_${quote.quote_number}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('PDF scaricato');
    } catch (err) { toast.error('Errore download PDF'); }
  };

  const handleDuplicate = async (quote) => {
    try {
      const res = await axios.post(`${API}/quotes/${quote.id}/duplicate`);
      toast.success(`Preventivo #${res.data.quote_number} duplicato!`);
      const quotesRes = await axios.get(`${API}/quotes`);
      setQuotes(quotesRes.data.reverse());
    } catch (err) { toast.error('Errore nella duplicazione'); }
  };

  const filteredQuotes = quotes.filter(q => 
    (q.client_name.toLowerCase().includes(search.toLowerCase()) || q.subject.toLowerCase().includes(search.toLowerCase())) &&
    (statusFilter === 'all' || q.status === statusFilter)
  );

  return (
    <div className="animate-fadeIn" data-testid="quotes-page">
      <div className="page-header flex justify-between items-center">
        <div>
          <h1 className="page-title">Preventivi</h1>
          <p className="page-subtitle">Gestisci i tuoi preventivi</p>
        </div>
        <Button onClick={() => navigate('/preventivi/nuovo')} className="btn-primary gap-2" data-testid="new-quote-btn">
          <Plus size={18} /> Nuovo Preventivo
        </Button>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="flex gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <Input placeholder="Cerca preventivo..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" data-testid="search-quotes" />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48" data-testid="status-filter">
                <SelectValue placeholder="Stato" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tutti gli stati</SelectItem>
                <SelectItem value="draft">Bozza</SelectItem>
                <SelectItem value="sent">Inviato</SelectItem>
                <SelectItem value="accepted">Accettato</SelectItem>
                <SelectItem value="rejected">Rifiutato</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {filteredQuotes.length > 0 ? (
            <table className="data-table" data-testid="quotes-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Cliente</th>
                  <th>Oggetto</th>
                  <th>Tipo</th>
                  <th>Totale</th>
                  <th>Stato</th>
                  <th>Azioni</th>
                </tr>
              </thead>
              <tbody>
                {filteredQuotes.map((quote) => (
                  <tr key={quote.id} data-testid={`quote-row-${quote.id}`}>
                    <td className="font-bold text-[#002fa7]">#{quote.quote_number}</td>
                    <td className="font-semibold">{quote.client_name}</td>
                    <td>{quote.subject}</td>
                    <td><Badge variant="outline">{quote.quote_type}</Badge></td>
                    <td className="font-semibold">{formatPrice(quote.total_amount, 'una_tantum')}</td>
                    <td><StatusBadge status={quote.status} /></td>
                    <td>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="sm" onClick={() => navigate(`/preventivi/${quote.id}`)} data-testid={`view-quote-${quote.id}`}>
                          <Eye size={16} />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => navigate(`/preventivi/${quote.id}/modifica`)} data-testid={`edit-quote-${quote.id}`}>
                          <Edit size={16} />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDuplicate(quote)} data-testid={`duplicate-quote-${quote.id}`} title="Duplica">
                          <Copy size={16} />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDownload(quote)} data-testid={`download-quote-${quote.id}`}>
                          <Download size={16} />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(quote.id)} className="text-red-600" data-testid={`delete-quote-${quote.id}`}>
                          <Trash2 size={16} />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon"><FileText size={32} /></div>
              <p className="empty-state-title">Nessun preventivo</p>
              <p className="empty-state-desc">Crea il tuo primo preventivo</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Service selector - defined outside NewQuotePage to avoid re-mount on state changes
const ServiceSelector = ({ services, selectedServices, onToggle, compact = false }) => (
  <div className={`${compact ? "max-h-[300px]" : "max-h-[500px]"} overflow-y-auto pr-2`}>
    <div className="service-list">
      {services.map(service => {
        const isSelected = selectedServices.some(s => s.service_id === service.id);
        return (
          <div key={service.id} className={`service-item ${isSelected ? 'selected' : ''}`}
            onClick={() => onToggle(service)} data-testid={`select-service-${service.id}`}>
            <div className="flex items-center gap-3">
              <Checkbox checked={isSelected} className="pointer-events-none" />
              <div className="service-info">
                <p className="service-name">{service.name}</p>
                <p className="service-desc">{service.description}</p>
                {service.sub_items && service.sub_items.length > 0 && (
                  <div className="mt-1 space-y-0.5">
                    {service.sub_items.slice(0, 3).map((item, i) => (
                      <p key={i} className="text-xs text-gray-400 pl-2">- {item}</p>
                    ))}
                    {service.sub_items.length > 3 && (
                      <p className="text-xs text-gray-400 pl-2 italic">...e altri {service.sub_items.length - 3}</p>
                    )}
                  </div>
                )}
              </div>
            </div>
            <span className="service-price">{formatPrice(service.price, service.price_type)}</span>
          </div>
        );
      })}
    </div>
  </div>
);

// Sortable step card - defined outside NewQuotePage to avoid re-mount on drag
const SortableStepCard = ({ id, idx, phaseStep, services, updateStep, removeStep, toggleStepService }) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id });
  const style = { transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.5 : 1, zIndex: isDragging ? 50 : 'auto' };
  return (
    <div ref={setNodeRef} style={style} data-testid={`step-card-${idx}`}>
      <Card className={`border-2 ${isDragging ? 'border-[#002fa7] shadow-lg' : 'border-gray-200'}`}>
        <CardContent className="p-5">
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center gap-3">
              <div {...attributes} {...listeners} className="cursor-grab active:cursor-grabbing p-1 rounded hover:bg-gray-100 touch-none" data-testid={`drag-handle-${idx}`}>
                <GripVertical size={20} className="text-gray-400" />
              </div>
              <div className="w-10 h-10 min-w-[2.5rem] bg-[#002fa7] text-white rounded-lg flex items-center justify-center font-bold text-lg shrink-0">
                {phaseStep.step_number}
              </div>
              <Input value={phaseStep.title} onChange={(e) => updateStep(idx, 'title', e.target.value)}
                placeholder="Titolo fase (es. Onboarding e set-up)" className="font-semibold text-lg border-0 focus:ring-0 p-0 h-auto"
                data-testid={`step-title-${idx}`} />
            </div>
            <Button variant="ghost" size="sm" onClick={() => removeStep(idx)} className="text-red-600 shrink-0" data-testid={`remove-step-${idx}`}>
              <Trash2 size={16} />
            </Button>
          </div>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="form-label">Durata</label>
              <Input value={phaseStep.duration} onChange={(e) => updateStep(idx, 'duration', e.target.value)}
                placeholder="Es. 5 giorni" data-testid={`step-duration-${idx}`} />
            </div>
            <div>
              <label className="form-label">Output</label>
              <Input value={phaseStep.output} onChange={(e) => updateStep(idx, 'output', e.target.value)}
                placeholder="Es. Brief approvato, Calendario" data-testid={`step-output-${idx}`} />
            </div>
          </div>
          <div>
            <label className="form-label">Descrizione</label>
            <Textarea value={phaseStep.description} onChange={(e) => updateStep(idx, 'description', e.target.value)}
              placeholder="Descrizione della fase..." rows={2} data-testid={`step-desc-${idx}`} />
          </div>
          <div className="mt-4">
            <label className="form-label">Servizi associati a questa fase</label>
            <ServiceSelector services={services} selectedServices={phaseStep.services} onToggle={(svc) => toggleStepService(idx, svc)} compact />
          </div>
          {phaseStep.services.length > 0 && (
            <div className="mt-3 pt-3 border-t">
              <div className="flex justify-between text-sm font-semibold">
                <span>Subtotale fase</span>
                <span className="text-[#002fa7]">
                  {formatPrice(phaseStep.services.reduce((sum, s) => sum + s.price * s.quantity, 0), 'una_tantum')}
                </span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Quote PDF-style preview component
const QuotePreview = ({ formData, clients, suppliers, calculateTotal }) => {
  const client = clients.find(c => c.id === formData.client_id);
  const selectedSuppliers = suppliers.filter(s => formData.supplier_ids?.includes(s.id) || s.is_main);
  const isStepBased = formData.quote_type === 'step' || formData.quote_type === 'ibrido';
  const dateStr = new Date().toLocaleDateString('it-IT', { day: '2-digit', month: '2-digit', year: '2-digit' });
  const year = new Date().getFullYear();

  const allServices = [...(formData.services || [])];
  (formData.steps || []).forEach(st => { allServices.push(...(st.services || [])); });
  const total = calculateTotal();

  // Page wrapper
  const Page = ({ children, className = '' }) => (
    <div className={`bg-white shadow-md rounded-lg mb-4 ${className}`} style={{ padding: '32px 36px', position: 'relative' }}>
      {children}
    </div>
  );

  return (
    <div data-testid="quote-preview" className="space-y-4">

      {/* PAGE 1: COVER */}
      <div className="bg-[#002fa7] shadow-lg rounded-lg flex flex-col justify-between" style={{ padding: '40px', minHeight: '400px' }}>
        <div>
          <img src="https://customer-assets.emergentagent.com/job_quote-builder-217/artifacts/sliapkzx_3.png" alt="Logo" className="h-14 mb-8" />
          <p className="text-white/50 text-xs tracking-[0.3em] uppercase mt-4">Limone Blu Studio</p>
        </div>
        <div>
          <h1 className="text-white text-5xl font-extrabold tracking-tight mb-4">PREVENTIVO</h1>
          <p className="text-white/80 text-xl mb-8">---/{year}</p>
        </div>
        <p className="text-[#dbf637] text-xs leading-relaxed max-w-sm">
          Questo documento è un preventivo collettivo basato sui costi di freelancer operanti all'interno dello studio.
        </p>
      </div>

      {/* PAGE 2: HEADER + SUPPLIER/CLIENT + PREMISE + METHODOLOGY */}
      <Page>
        {/* Header bar */}
        <div className="flex justify-between items-start mb-6 pb-4 border-b-2 border-[#002fa7]">
          <div>
            <p className="text-[#002fa7] font-extrabold text-base tracking-wide">LIMONE BLU STUDIO</p>
            <p className="text-gray-400 text-[10px] mt-0.5">Preventivo | Data: {dateStr}</p>
          </div>
          <div className="text-right">
            <p className="text-gray-600 text-xs">Og. <span className="font-semibold">{formData.subject || '—'}</span></p>
          </div>
        </div>

        {/* Fornitore / Cliente */}
        <div className="grid grid-cols-2 gap-10 mb-8">
          <div>
            <p className="text-[#002fa7] font-bold text-xs uppercase tracking-wider mb-3">Fornitore</p>
            {selectedSuppliers.map((s, i) => (
              <div key={i} className="mb-3">
                <p className="font-semibold text-xs text-gray-800">{s.legal_name || s.name}</p>
                {s.address && <p className="text-[10px] text-gray-500">{s.address}</p>}
                {s.vat_number && <p className="text-[10px] text-gray-500">P.IVA {s.vat_number}</p>}
                {s.phone && <p className="text-[10px] text-gray-500">{s.phone}</p>}
                {s.email && <p className="text-[10px] text-gray-500">{s.email}</p>}
              </div>
            ))}
          </div>
          <div>
            <p className="text-[#002fa7] font-bold text-xs uppercase tracking-wider mb-3">Cliente</p>
            {client ? (
              <div>
                <p className="font-semibold text-xs text-gray-800">{client.company_name}</p>
                <p className="text-[10px] text-gray-500">{client.address}</p>
                <p className="text-[10px] text-gray-500">P.IVA {client.vat_number}</p>
                {client.phone && <p className="text-[10px] text-gray-500">{client.phone}</p>}
                <p className="text-[10px] text-gray-500">{client.email}</p>
              </div>
            ) : <p className="text-[10px] text-gray-400 italic">Seleziona un cliente</p>}
          </div>
        </div>

        {/* Premessa */}
        {formData.premise && (
          <div className="mb-6">
            <p className="text-[#002fa7] font-bold text-xs uppercase tracking-wider mb-2">Premessa</p>
            <p className="text-xs text-gray-600 leading-relaxed whitespace-pre-line">{formData.premise}</p>
          </div>
        )}

        {/* Metodologia */}
        {formData.methodology && (
          <div className="mb-6">
            <p className="text-[#002fa7] font-bold text-xs uppercase tracking-wider mb-2">Metodologia e approccio al lavoro</p>
            <p className="text-xs text-gray-600 leading-relaxed whitespace-pre-line">{formData.methodology}</p>
          </div>
        )}

        {/* Steps/Phases (if step-based) */}
        {isStepBased && formData.steps.length > 0 && (
          <div className="mb-4">
            <p className="text-[#002fa7] font-bold text-xs uppercase tracking-wider mb-3">Il progetto / Roadmap</p>
            <div className="space-y-4">
              {formData.steps.map((phaseStep, idx) => (
                <div key={idx} className="pl-3" style={{ borderLeft: '3px solid #002fa7' }}>
                  <p className="font-bold text-xs text-[#002fa7]">Fase {phaseStep.step_number}: {phaseStep.title || 'Senza titolo'}</p>
                  {phaseStep.duration && <p className="text-[10px] text-gray-400 italic">Richiede {phaseStep.duration}</p>}
                  {phaseStep.description && <p className="text-[10px] text-gray-600 mt-1 leading-relaxed">{phaseStep.description}</p>}
                  {phaseStep.output && <p className="text-[10px] text-gray-700 mt-1"><span className="font-semibold">Output:</span> {phaseStep.output}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-6 pt-3 border-t border-gray-100 flex justify-between items-end">
          <p className="text-[10px] text-gray-300">1/{allServices.length > 6 ? '4' : '3'}</p>
          <p className="text-[10px] text-gray-300 italic">enjoy the juice.</p>
        </div>
      </Page>

      {/* PAGE 3: PROPOSTA ECONOMICA */}
      <Page>
        <div className="flex justify-between items-start mb-6 pb-4 border-b-2 border-[#002fa7]">
          <p className="text-[#002fa7] font-extrabold text-base tracking-wide">LIMONE BLU STUDIO</p>
          <p className="text-gray-400 text-[10px]">Preventivo | {dateStr}</p>
        </div>

        <p className="text-[#002fa7] font-bold text-xs uppercase tracking-wider mb-4">Proposta economica</p>

        <div className="space-y-0">
          {allServices.filter(s => s.is_selected).map((svc, idx) => (
            <div key={idx} className="py-3 border-b border-gray-100">
              <div className="flex justify-between items-start">
                <div className="flex-1 mr-4">
                  <p className="font-bold text-xs text-gray-800">{svc.service_name}</p>
                  {svc.description && <p className="text-[10px] text-gray-400 mt-0.5">{svc.description}</p>}
                  {svc.sub_items && svc.sub_items.length > 0 && (
                    <div className="mt-1.5 space-y-0.5 pl-2">
                      {svc.sub_items.map((item, i) => (
                        <p key={i} className="text-[10px] text-gray-500">- {item}</p>
                      ))}
                    </div>
                  )}
                </div>
                <span className="font-bold text-xs text-[#002fa7] whitespace-nowrap">{formatPrice(svc.price, svc.price_type)}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Total */}
        <div className="mt-4 pt-3 border-t-2 border-[#002fa7] flex justify-between items-center">
          <span className="font-extrabold text-sm text-gray-800">TOTALE</span>
          <span className="font-extrabold text-lg text-[#002fa7]">{formatPrice(total, 'una_tantum')}</span>
        </div>

        <div className="mt-6 pt-3 border-t border-gray-100 flex justify-between items-end">
          <p className="text-[10px] text-gray-300">2/{allServices.length > 6 ? '4' : '3'}</p>
          <p className="text-[10px] text-gray-300 italic">enjoy the juice.</p>
        </div>
      </Page>

      {/* PAGE 4: INFO AGGIUNTIVE */}
      <Page>
        <div className="flex justify-between items-start mb-6 pb-4 border-b-2 border-[#002fa7]">
          <p className="text-[#002fa7] font-extrabold text-base tracking-wide">LIMONE BLU STUDIO</p>
          <p className="text-gray-400 text-[10px]">Preventivo | {dateStr}</p>
        </div>

        <p className="text-[#002fa7] font-bold text-xs uppercase tracking-wider mb-4">Info aggiuntive</p>

        <div className="space-y-5 text-[11px] text-gray-600 leading-relaxed">
          <div>
            <p className="font-bold text-xs text-gray-800 mb-1">Validità, riservatezza e limiti del preventivo</p>
            <p>Il presente preventivo ha validità n.{formData.validity_days || 30} giorni. Le informazioni contenute nel presente documento sono riservate e non potranno essere cedute o divulgate a terzi senza il consenso scritto dell'altra parte. Qualsiasi servizio non espressamente incluso sarà oggetto di valutazione separata, comprese le spese di trasferta ed eventuali costi aggiuntivi.</p>
            <p className="mt-1">Le attività ed i costi riportati nel preventivo potrebbero subire variazioni di anno in anno secondo linee guida del mercato.</p>
          </div>

          {formData.delivery_time && (
            <div>
              <p className="font-bold text-xs text-gray-800 mb-1">Tempi di consegna</p>
              <p>Il progetto avrà inizio entro 7 giorni lavorativi dalla ricezione dell'acconto. La durata stimata del progetto è di circa {formData.delivery_time}, salvo imprevisti o modifiche in corso d'opera.</p>
              <p className="mt-1">Il rispetto delle tempistiche è subordinato alla puntualità nella consegna dei materiali da parte del cliente (testi, immagini, loghi, ecc.).</p>
            </div>
          )}

          <div>
            <p className="font-bold text-xs text-gray-800 mb-1">Contenuti e attività extra-preventivo</p>
            <p>Sono da considerarsi extra-preventivo tutte le attività non espressamente incluse nel presente documento e che saranno preventivate separatamente. In particolare:</p>
            <ul className="mt-1 space-y-0.5 pl-3">
              <li>- produzione di contenuti fotografici e video</li>
              <li>- copywriting integrale di testi non forniti dal cliente</li>
              <li>- traduzioni o gestione multilingua</li>
              <li>- modifiche strutturali richieste dopo l'approvazione del layout</li>
              <li>- inserimento di funzionalità aggiuntive non previste</li>
              <li>- campagne advertising, attività SEO avanzata, gestione social o altri servizi di comunicazione non inclusi</li>
              <li>- eventuali verifiche legali o consulenze specialistiche relative alla documentazione GDPR</li>
            </ul>
          </div>

          <div>
            <p className="font-bold text-xs text-gray-800 mb-1">Modalità di accettazione</p>
            <p>Inviare il seguente preventivo firmato e timbrato alla casella e-mail: <span className="font-semibold">info@limoneblu.it</span></p>
          </div>

          <div>
            <p className="font-bold text-xs text-gray-800 mb-1">Modalità di pagamento</p>
            <p>{formData.payment_terms || "30% all'accettazione, 70% alla consegna"}</p>
            <p className="mt-1">I pagamenti dovranno avvenire a mezzo bonifico bancario entro 15 giorni dalla data di emissione della fattura elettronica.</p>
          </div>

          {formData.extra_notes && (
            <div>
              <p className="font-bold text-xs text-gray-800 mb-1">Note</p>
              <p>{formData.extra_notes}</p>
            </div>
          )}
        </div>

        {/* Firma */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-[10px] text-gray-400 mb-1">Firma del Rappresentante legale</p>
          {client && (
            <div className="text-[10px] text-gray-500 mt-2">
              <p className="font-semibold text-gray-700">{client.company_name}</p>
              <p>{client.address}</p>
              <p>P.IVA: {client.vat_number}</p>
            </div>
          )}
          <div className="w-48 border-b border-gray-300 mt-6 mb-2" />
        </div>

        <div className="mt-6 pt-3 border-t border-gray-100 flex justify-between items-end">
          <p className="text-[10px] text-gray-300">{allServices.length > 6 ? '4/4' : '3/3'}</p>
          <p className="text-[10px] text-gray-300 italic">enjoy the juice.</p>
        </div>
      </Page>
    </div>
  );
};

// New/Edit Quote page
const NewQuotePage = () => {
  const navigate = useNavigate();
  const { id: editId } = useParams();
  const isEditing = !!editId;
  const [step, setStep] = useState(1);
  const [clients, setClients] = useState([]);
  const [services, setServices] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);

  const [formData, setFormData] = useState({
    client_id: '',
    supplier_ids: [],
    subject: '',
    quote_type: 'standard',
    services: [],
    steps: [],
    premise: '',
    methodology: '',
    validity_days: 30,
    payment_terms: '30% all\'accettazione, 70% alla consegna',
    delivery_time: '',
    extra_notes: ''
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [clientsRes, servicesRes, suppliersRes, templatesRes] = await Promise.all([
          axios.get(`${API}/clients`),
          axios.get(`${API}/services`),
          axios.get(`${API}/suppliers`),
          axios.get(`${API}/templates`)
        ]);
        setClients(clientsRes.data);
        setServices(servicesRes.data.filter(s => s.is_active));
        setSuppliers(suppliersRes.data);
        setTemplates(templatesRes.data);
        
        if (isEditing) {
          // Load existing quote data
          const quoteRes = await axios.get(`${API}/quotes/${editId}`);
          const q = quoteRes.data;
          setFormData({
            client_id: q.client_id, supplier_ids: q.supplier_ids || [],
            subject: q.subject, quote_type: q.quote_type,
            services: q.services || [], steps: q.steps || [],
            premise: q.premise || '', methodology: q.methodology || '',
            validity_days: q.validity_days || 30, payment_terms: q.payment_terms || '',
            delivery_time: q.delivery_time || '', extra_notes: q.extra_notes || ''
          });
        } else {
          // Auto-select main supplier
          const mainSupplier = suppliersRes.data.find(s => s.is_main);
          if (mainSupplier) {
            setFormData(prev => ({ ...prev, supplier_ids: [mainSupplier.id] }));
          }
        }
      } catch (err) { console.error(err); }
    };
    fetchData();
  }, [editId, isEditing]);

  const loadTemplate = (template) => {
    setFormData(prev => ({
      ...prev,
      quote_type: template.quote_type,
      services: template.services || [],
      steps: template.steps || [],
      premise: template.premise || '',
      methodology: template.methodology || '',
      payment_terms: template.payment_terms || '',
      delivery_time: template.delivery_time || ''
    }));
    setShowTemplates(false);
    toast.success(`Template "${template.name}" caricato`);
  };

  const quoteTypes = [
    { value: 'standard', label: 'Standard', desc: 'Lista servizi singoli', icon: List },
    { value: 'step', label: 'A Step', desc: 'Fasi progressive', icon: Layers },
    { value: 'moduli', label: 'Moduli', desc: 'Servizi selezionabili', icon: Grid3X3 },
    { value: 'ibrido', label: 'Ibrido', desc: 'Moduli + Step', icon: Shuffle }
  ];

  const isStepBased = formData.quote_type === 'step' || formData.quote_type === 'ibrido';
  const totalSteps = 4;
  const lastStep = 4;

  const toggleService = (service) => {
    const existing = formData.services.find(s => s.service_id === service.id);
    if (existing) {
      setFormData(prev => ({ ...prev, services: prev.services.filter(s => s.service_id !== service.id) }));
    } else {
      setFormData(prev => ({
        ...prev,
        services: [...prev.services, {
          service_id: service.id, service_name: service.name, description: service.description,
          sub_items: service.sub_items || [], price: service.price, price_type: service.price_type,
          quantity: 1, is_selected: true
        }]
      }));
    }
  };

  const addStep = () => {
    const newStep = {
      step_number: formData.steps.length + 1,
      title: '', description: '', duration: '', output: '', services: []
    };
    setFormData(prev => ({ ...prev, steps: [...prev.steps, newStep] }));
  };

  const updateStep = (idx, field, value) => {
    setFormData(prev => {
      const newSteps = [...prev.steps];
      newSteps[idx] = { ...newSteps[idx], [field]: value };
      return { ...prev, steps: newSteps };
    });
  };

  const removeStep = (idx) => {
    setFormData(prev => {
      const newSteps = prev.steps.filter((_, i) => i !== idx).map((s, i) => ({ ...s, step_number: i + 1 }));
      return { ...prev, steps: newSteps };
    });
  };

  const toggleStepService = (stepIdx, service) => {
    setFormData(prev => {
      const newSteps = [...prev.steps];
      const stepServices = newSteps[stepIdx].services;
      const existing = stepServices.find(s => s.service_id === service.id);
      if (existing) {
        newSteps[stepIdx] = { ...newSteps[stepIdx], services: stepServices.filter(s => s.service_id !== service.id) };
      } else {
        newSteps[stepIdx] = {
          ...newSteps[stepIdx],
          services: [...stepServices, {
            service_id: service.id, service_name: service.name, description: service.description,
            sub_items: service.sub_items || [], price: service.price, price_type: service.price_type,
            quantity: 1, is_selected: true
          }]
        };
      }
      return { ...prev, steps: newSteps };
    });
  };

  const calculateTotal = () => {
    let total = formData.services.reduce((sum, s) => s.is_selected ? sum + (s.price * s.quantity) : sum, 0);
    formData.steps.forEach(st => {
      st.services.forEach(s => { if (s.is_selected) total += s.price * s.quantity; });
    });
    return total;
  };

  const handleSubmit = async () => {
    if (!formData.client_id) { toast.error('Seleziona un cliente'); return; }
    if (!formData.subject) { toast.error('Inserisci l\'oggetto del preventivo'); return; }
    const hasServices = formData.services.length > 0 || formData.steps.some(s => s.services.length > 0);
    if (!hasServices) { toast.error('Seleziona almeno un servizio'); return; }
    setLoading(true);
    try {
      if (isEditing) {
        await axios.put(`${API}/quotes/${editId}`, formData);
        toast.success('Preventivo aggiornato!');
        navigate(`/preventivi/${editId}`);
      } else {
        const res = await axios.post(`${API}/quotes`, formData);
        toast.success('Preventivo creato!');
        navigate(`/preventivi/${res.data.id}`);
      }
    } catch (err) { toast.error('Errore nel salvataggio'); }
    setLoading(false);
  };

  // Drag and drop for steps
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } })
  );

  const handleDragEnd = (event) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const oldIndex = parseInt(active.id.split('-')[1]);
    const newIndex = parseInt(over.id.split('-')[1]);
    setFormData(prev => {
      const reordered = arrayMove(prev.steps, oldIndex, newIndex).map((s, i) => ({ ...s, step_number: i + 1 }));
      return { ...prev, steps: reordered };
    });
  };

  return (
    <div className="animate-fadeIn" data-testid="new-quote-page">
      <div className="page-header">
        <h1 className="page-title">{isEditing ? 'Modifica Preventivo' : 'Nuovo Preventivo'}</h1>
        <p className="page-subtitle">Step {step} di {totalSteps}</p>
      </div>

      {/* Progress bar */}
      <div className="flex gap-2 mb-8">
        {Array.from({ length: totalSteps }, (_, i) => i + 1).map(s => (
          <div key={s} className={`h-2 flex-1 rounded-full transition-colors ${s <= step ? 'bg-[#002fa7]' : 'bg-gray-200'}`} />
        ))}
      </div>

      {/* Step 1: Base Info */}
      {step === 1 && (
        <Card className="animate-slideIn">
          <CardHeader><CardTitle>Informazioni Base</CardTitle></CardHeader>
          <CardContent className="space-y-6">
            <div>
              <label className="form-label">Cliente *</label>
              <Select value={formData.client_id} onValueChange={(v) => setFormData({...formData, client_id: v})}>
                <SelectTrigger data-testid="select-client"><SelectValue placeholder="Seleziona cliente" /></SelectTrigger>
                <SelectContent>
                  {clients.map(c => <SelectItem key={c.id} value={c.id}>{c.company_name}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="form-label">Oggetto Preventivo *</label>
              <Input value={formData.subject} onChange={(e) => setFormData({...formData, subject: e.target.value})} 
                placeholder="Es. Realizzazione sito web" data-testid="quote-subject" />
            </div>
            <div>
              <label className="form-label">Tipologia Preventivo</label>
              <div className="quote-type-grid mt-2">
                {quoteTypes.map(type => (
                  <div key={type.value} className={`quote-type-item ${formData.quote_type === type.value ? 'selected' : ''}`}
                    onClick={() => setFormData({...formData, quote_type: type.value, steps: [], services: []})} data-testid={`quote-type-${type.value}`}>
                    <div className="quote-type-icon"><type.icon size={24} /></div>
                    <p className="quote-type-name">{type.label}</p>
                    <p className="quote-type-desc">{type.desc}</p>
                  </div>
                ))}
              </div>
            </div>

            {!isEditing && templates.length > 0 && (
              <div>
                <div className="flex items-center justify-between">
                  <label className="form-label">Carica da Template</label>
                  <Button variant="ghost" size="sm" onClick={() => setShowTemplates(!showTemplates)} data-testid="toggle-templates-btn">
                    {showTemplates ? 'Nascondi' : 'Mostra template'}
                  </Button>
                </div>
                {showTemplates && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mt-2">
                    {templates.map(t => (
                      <div key={t.id} className="border rounded-lg p-4 hover:border-[#002fa7] cursor-pointer transition-colors"
                        onClick={() => loadTemplate(t)} data-testid={`template-${t.id}`}>
                        <div className="flex items-center gap-2 mb-1">
                          <Bookmark size={16} className="text-[#002fa7]" />
                          <p className="font-semibold text-sm">{t.name}</p>
                        </div>
                        <p className="text-xs text-gray-500">{t.description}</p>
                        <Badge variant="outline" className="mt-2 text-xs">{t.quote_type}</Badge>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            <div className="flex justify-end">
              <Button onClick={() => setStep(2)} className="btn-primary gap-2" data-testid="next-step-1">
                Avanti <ChevronRight size={18} />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: For step/ibrido - Define phases */}
      {step === 2 && isStepBased && (
        <Card className="animate-slideIn">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Definisci le Fasi del Progetto</CardTitle>
              <Button onClick={addStep} className="btn-primary gap-2" data-testid="add-step-btn">
                <Plus size={18} /> Aggiungi Fase
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {formData.steps.length === 0 && (
              <div className="empty-state py-10">
                <div className="empty-state-icon"><Layers size={32} /></div>
                <p className="empty-state-title">Nessuna fase definita</p>
                <p className="empty-state-desc">Aggiungi le fasi del progetto con i relativi servizi</p>
              </div>
            )}
            <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
              <SortableContext items={formData.steps.map((_, i) => `step-${i}`)} strategy={verticalListSortingStrategy}>
                <div className="space-y-6">
                  {formData.steps.map((phaseStep, idx) => (
                    <SortableStepCard key={`step-${idx}`} id={`step-${idx}`} idx={idx} phaseStep={phaseStep}
                      services={services} updateStep={updateStep} removeStep={removeStep} toggleStepService={toggleStepService} />
                  ))}
                </div>
              </SortableContext>
            </DndContext>

            {/* For ibrido: also show standalone services */}
            {formData.quote_type === 'ibrido' && (
              <div className="mt-8">
                <h3 className="text-lg font-semibold mb-4">Servizi Standalone (fuori dalle fasi)</h3>
                <ServiceSelector services={services} selectedServices={formData.services} onToggle={toggleService} compact />
              </div>
            )}

            <div className="flex justify-between mt-6">
              <Button variant="outline" onClick={() => setStep(1)}>Indietro</Button>
              <Button onClick={() => setStep(3)} className="btn-primary gap-2" data-testid="next-step-2">
                Avanti <ChevronRight size={18} />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: For standard/moduli - Select services */}
      {step === 2 && !isStepBased && (
        <Card className="animate-slideIn">
          <CardHeader><CardTitle>Seleziona Servizi</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <ServiceSelector services={services} selectedServices={formData.services} onToggle={toggleService} />
              </div>
              <div>
                <Card className="bg-gray-50 sticky top-4">
                  <CardHeader><CardTitle className="text-lg">Riepilogo</CardTitle></CardHeader>
                  <CardContent>
                    <div className="space-y-2 mb-4">
                      {formData.services.map(s => (
                        <div key={s.service_id} className="flex justify-between text-sm">
                          <span className="text-gray-600 truncate flex-1 mr-2">{s.service_name}</span>
                          <span className="font-semibold whitespace-nowrap">{formatPrice(s.price, s.price_type)}</span>
                        </div>
                      ))}
                    </div>
                    {formData.services.length > 0 ? (
                      <div className="pt-4 border-t">
                        <div className="flex justify-between items-center">
                          <span className="font-semibold">Totale</span>
                          <span className="text-xl font-bold text-[#002fa7]">{formatPrice(calculateTotal(), 'una_tantum')}</span>
                        </div>
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 text-center py-4">Nessun servizio selezionato</p>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
            <div className="flex justify-between mt-6">
              <Button variant="outline" onClick={() => setStep(1)}>Indietro</Button>
              <Button onClick={() => setStep(3)} className="btn-primary gap-2" data-testid="next-step-2">
                Avanti <ChevronRight size={18} />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Details */}
      {step === 3 && (
        <Card className="animate-slideIn">
          <CardHeader><CardTitle>Dettagli Aggiuntivi</CardTitle></CardHeader>
          <CardContent className="space-y-6">
            <div>
              <label className="form-label">Premessa</label>
              <Textarea value={formData.premise} onChange={(e) => setFormData({...formData, premise: e.target.value})}
                placeholder="Descrizione introduttiva del progetto..." rows={3} data-testid="quote-premise" />
            </div>
            <div>
              <label className="form-label">Metodologia</label>
              <Textarea value={formData.methodology} onChange={(e) => setFormData({...formData, methodology: e.target.value})}
                placeholder="Approccio e metodologia di lavoro..." rows={3} data-testid="quote-methodology" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="form-label">Validità (giorni)</label>
                <Input type="number" value={formData.validity_days} onChange={(e) => setFormData({...formData, validity_days: parseInt(e.target.value) || 30})} />
              </div>
              <div>
                <label className="form-label">Tempi di consegna</label>
                <Input value={formData.delivery_time} onChange={(e) => setFormData({...formData, delivery_time: e.target.value})} 
                  placeholder="Es. 4-6 settimane" />
              </div>
            </div>
            <div>
              <label className="form-label">Termini di pagamento</label>
              <Input value={formData.payment_terms} onChange={(e) => setFormData({...formData, payment_terms: e.target.value})} />
            </div>
            <div>
              <label className="form-label">Note aggiuntive</label>
              <Textarea value={formData.extra_notes} onChange={(e) => setFormData({...formData, extra_notes: e.target.value})} rows={2} />
            </div>

            {/* Summary card */}
            <Card className="bg-[#002fa7] text-white">
              <CardContent className="p-6">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-sm opacity-80">Totale Preventivo</p>
                    <p className="text-3xl font-bold">{formatPrice(calculateTotal(), 'una_tantum')}</p>
                    {isStepBased && formData.steps.length > 0 && (
                      <div className="mt-2 space-y-1">
                        {formData.steps.map((s, i) => (
                          <p key={i} className="text-sm opacity-70">Fase {s.step_number}: {s.title || 'Senza titolo'} — {formatPrice(s.services.reduce((sum, sv) => sum + sv.price * sv.quantity, 0), 'una_tantum')}</p>
                        ))}
                        {formData.services.length > 0 && (
                          <p className="text-sm opacity-70">Servizi standalone — {formatPrice(formData.services.reduce((sum, s) => sum + s.price * s.quantity, 0), 'una_tantum')}</p>
                        )}
                      </div>
                    )}
                  </div>
                  <CheckCircle2 size={48} className="opacity-50" />
                </div>
              </CardContent>
            </Card>

            <div className="flex justify-between">
              <Button variant="outline" onClick={() => setStep(2)}>Indietro</Button>
              <Button onClick={() => setStep(lastStep)} className="btn-primary gap-2" data-testid="next-step-3">
                Anteprima <ChevronRight size={18} />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Last Step: Preview */}
      {step === lastStep && (
        <div className="animate-slideIn space-y-6">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Anteprima Preventivo</CardTitle>
                <Badge className="bg-[#dbf637] text-[#1a281f]">Anteprima</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <QuotePreview formData={formData} clients={clients} suppliers={suppliers} calculateTotal={calculateTotal} />
            </CardContent>
          </Card>

          <div className="flex justify-between pb-16">
            <Button variant="outline" onClick={() => setStep(lastStep - 1)}>Indietro</Button>
            <Button onClick={handleSubmit} className="btn-secondary gap-2" disabled={loading} data-testid="create-quote-btn">
              {loading ? 'Salvataggio...' : isEditing ? 'Aggiorna Preventivo' : 'Crea Preventivo'}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

// Quote detail page
const QuoteDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [quote, setQuote] = useState(null);
  const [client, setClient] = useState(null);
  const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);
  const [emailData, setEmailData] = useState({ subject: '', message: '', recipient_email: '' });
  const [sending, setSending] = useState(false);

  useEffect(() => {
    const fetchQuote = async () => {
      try {
        const res = await axios.get(`${API}/quotes/${id}`);
        setQuote(res.data);
        const clientRes = await axios.get(`${API}/clients/${res.data.client_id}`);
        setClient(clientRes.data);
        setEmailData(prev => ({
          ...prev,
          recipient_email: clientRes.data.email,
          subject: `Preventivo #${res.data.quote_number} - ${res.data.subject}`,
          message: `Gentile ${clientRes.data.company_name},\n\nin allegato il preventivo richiesto.\n\nRimaniamo a disposizione per qualsiasi chiarimento.\n\nCordiali saluti,\nLimone Blu Studio`
        }));
      } catch (err) {
        console.error(err);
        toast.error('Errore nel caricamento');
      }
    };
    fetchQuote();
  }, [id]);

  const handleDownload = async () => {
    try {
      const res = await axios.get(`${API}/quotes/${id}/pdf`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Preventivo_${quote.quote_number}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('PDF scaricato');
    } catch (err) { toast.error('Errore download PDF'); }
  };

  const handleSendEmail = async (e) => {
    e.preventDefault();
    setSending(true);
    try {
      await axios.post(`${API}/quotes/${id}/send-email`, {
        quote_id: id,
        ...emailData
      });
      toast.success('Email inviata con successo!');
      setIsEmailModalOpen(false);
      // Refresh quote to update status
      const res = await axios.get(`${API}/quotes/${id}`);
      setQuote(res.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Errore nell\'invio');
    }
    setSending(false);
  };

  const updateStatus = async (status) => {
    try {
      await axios.put(`${API}/quotes/${id}/status?status=${status}`);
      setQuote(prev => ({ ...prev, status }));
      toast.success('Stato aggiornato');
    } catch (err) { toast.error('Errore'); }
  };

  const handleDuplicate = async () => {
    try {
      const res = await axios.post(`${API}/quotes/${id}/duplicate`);
      toast.success(`Preventivo #${res.data.quote_number} duplicato!`);
      navigate(`/preventivi/${res.data.id}`);
    } catch (err) { toast.error('Errore nella duplicazione'); }
  };

  const handleSaveAsTemplate = async () => {
    const name = prompt('Nome del template:');
    if (!name) return;
    try {
      await axios.post(`${API}/templates/from-quote/${id}?name=${encodeURIComponent(name)}`);
      toast.success('Template salvato!');
    } catch (err) { toast.error('Errore nel salvataggio template'); }
  };

  if (!quote) return <div className="p-8">Caricamento...</div>;

  return (
    <div className="animate-fadeIn" data-testid="quote-detail-page">
      <div className="page-header">
        <div className="flex items-center gap-3 mb-2">
          <Button variant="ghost" onClick={() => navigate('/preventivi')} className="p-2 shrink-0">
            <ChevronRight size={20} className="rotate-180" />
          </Button>
          <h1 className="page-title">Preventivo #{quote.quote_number}</h1>
          <StatusBadge status={quote.status} />
        </div>
        <p className="page-subtitle ml-11">{quote.subject}</p>
        <div className="flex flex-wrap items-center gap-2 mt-4">
          <Select value={quote.status} onValueChange={updateStatus}>
            <SelectTrigger className="w-36" data-testid="status-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="draft">Bozza</SelectItem>
              <SelectItem value="sent">Inviato</SelectItem>
              <SelectItem value="accepted">Accettato</SelectItem>
              <SelectItem value="rejected">Rifiutato</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm" onClick={handleDownload} className="gap-1.5" data-testid="download-pdf-btn">
            <Download size={16} /> Scarica PDF
          </Button>
          <Button variant="outline" size="sm" onClick={() => navigate(`/preventivi/${id}/modifica`)} className="gap-1.5" data-testid="edit-quote-btn">
            <Edit size={16} /> Modifica
          </Button>
          <Button variant="outline" size="sm" onClick={handleDuplicate} className="gap-1.5" data-testid="duplicate-quote-btn">
            <Copy size={16} /> Duplica
          </Button>
          <Button variant="outline" size="sm" onClick={handleSaveAsTemplate} className="gap-1.5" data-testid="save-template-btn">
            <Bookmark size={16} /> Salva Template
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{(quote.quote_type === 'step' || quote.quote_type === 'ibrido') && quote.steps?.length > 0 ? 'Fasi e Servizi' : 'Servizi'}</CardTitle>
            </CardHeader>
            <CardContent>
              {/* Show steps if present */}
              {(quote.quote_type === 'step' || quote.quote_type === 'ibrido') && quote.steps?.length > 0 && (
                <div className="space-y-6 mb-6">
                  {quote.steps.map((phaseStep, idx) => (
                    <div key={idx} className="border-l-4 border-[#002fa7] pl-4">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="inline-flex items-center justify-center w-8 h-8 min-w-[2rem] bg-[#002fa7] text-white rounded-full text-sm font-bold shrink-0">{phaseStep.step_number}</span>
                        <h4 className="font-bold text-lg text-[#1a281f]">{phaseStep.title}</h4>
                      </div>
                      {phaseStep.duration && <p className="text-sm text-gray-500 italic mb-1">Richiede {phaseStep.duration}</p>}
                      {phaseStep.description && <p className="text-gray-600 mb-2">{phaseStep.description}</p>}
                      {phaseStep.output && <p className="text-sm mb-3"><span className="font-semibold">Output:</span> {phaseStep.output}</p>}
                      <div className="space-y-2">
                        {phaseStep.services?.map((service, sIdx) => (
                          <div key={sIdx} className="flex justify-between items-start p-3 bg-gray-50 rounded-lg">
                            <div className="flex-1">
                              <p className="font-semibold">{service.service_name}</p>
                              {service.sub_items && service.sub_items.length > 0 && (
                                <div className="mt-1 space-y-0.5">
                                  {service.sub_items.map((item, i) => (
                                    <p key={i} className="text-xs text-gray-500 pl-2">- {item}</p>
                                  ))}
                                </div>
                              )}
                            </div>
                            <span className="font-bold text-[#002fa7] ml-4 whitespace-nowrap">{formatPrice(service.price, service.price_type)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {/* Show standalone services */}
              {quote.services?.length > 0 && (
                <div className="space-y-3">
                  {(quote.quote_type === 'ibrido' && quote.steps?.length > 0) && (
                    <h4 className="font-semibold text-gray-500 text-sm uppercase tracking-wide mb-2">Servizi Standalone</h4>
                  )}
                  {quote.services.map((service, idx) => (
                    <div key={idx} className="flex justify-between items-start p-4 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <p className="font-semibold">{service.service_name}</p>
                        {service.description && <p className="text-sm text-gray-500">{service.description}</p>}
                        {service.sub_items && service.sub_items.length > 0 && (
                          <div className="mt-1 space-y-0.5">
                            {service.sub_items.map((item, i) => (
                              <p key={i} className="text-xs text-gray-500 pl-2">- {item}</p>
                            ))}
                          </div>
                        )}
                      </div>
                      <span className="font-bold text-[#002fa7] ml-4 whitespace-nowrap">{formatPrice(service.price, service.price_type)}</span>
                    </div>
                  ))}
                </div>
              )}
              <div className="mt-6 pt-4 border-t flex justify-between items-center">
                <span className="text-lg font-semibold">Totale</span>
                <span className="text-2xl font-bold text-[#002fa7]">{formatPrice(quote.total_amount, 'una_tantum')}</span>
              </div>
            </CardContent>
          </Card>

          {(quote.premise || quote.methodology) && (
            <Card>
              <CardHeader>
                <CardTitle>Dettagli Progetto</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {quote.premise && (
                  <div>
                    <h4 className="font-semibold mb-2">Premessa</h4>
                    <p className="text-gray-600">{quote.premise}</p>
                  </div>
                )}
                {quote.methodology && (
                  <div>
                    <h4 className="font-semibold mb-2">Metodologia</h4>
                    <p className="text-gray-600">{quote.methodology}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Cliente</CardTitle>
            </CardHeader>
            <CardContent>
              {client && (
                <div className="space-y-2">
                  <p className="font-semibold text-lg">{client.company_name}</p>
                  <p className="text-sm text-gray-500">{client.address}</p>
                  <p className="text-sm">P.IVA: {client.vat_number}</p>
                  <p className="text-sm">{client.email}</p>
                  {client.phone && <p className="text-sm">{client.phone}</p>}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Informazioni</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-500">Tipologia</span>
                <Badge variant="outline">{quote.quote_type}</Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Validità</span>
                <span>{quote.validity_days} giorni</span>
              </div>
              {quote.delivery_time && (
                <div className="flex justify-between">
                  <span className="text-gray-500">Consegna</span>
                  <span>{quote.delivery_time}</span>
                </div>
              )}
              <div className="pt-2 border-t">
                <p className="text-sm text-gray-500 mb-1">Pagamento</p>
                <p className="text-sm">{quote.payment_terms}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Dialog open={isEmailModalOpen} onOpenChange={setIsEmailModalOpen}>
        <DialogContent className="max-w-lg" data-testid="email-modal">
          <DialogHeader>
            <DialogTitle>Invia Preventivo via Email</DialogTitle>
            <DialogDescription>Il PDF verrà allegato automaticamente all'email</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSendEmail}>
            <div className="space-y-4">
              <div>
                <label className="form-label">Destinatario *</label>
                <Input type="email" value={emailData.recipient_email} onChange={(e) => setEmailData({...emailData, recipient_email: e.target.value})} 
                  required data-testid="email-recipient" />
              </div>
              <div>
                <label className="form-label">Oggetto *</label>
                <Input value={emailData.subject} onChange={(e) => setEmailData({...emailData, subject: e.target.value})} 
                  required data-testid="email-subject" />
              </div>
              <div>
                <label className="form-label">Messaggio</label>
                <Textarea value={emailData.message} onChange={(e) => setEmailData({...emailData, message: e.target.value})} 
                  rows={6} data-testid="email-message" />
              </div>
            </div>
            <DialogFooter className="mt-6">
              <Button type="button" variant="outline" onClick={() => setIsEmailModalOpen(false)}>Annulla</Button>
              <Button type="submit" className="btn-primary gap-2" disabled={sending} data-testid="send-email-submit">
                {sending ? 'Invio...' : <><Mail size={16} /> Invia</>}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Templates page
const TemplatesPage = () => {
  const [templates, setTemplates] = useState([]);
  const navigate = useNavigate();

  const fetchTemplates = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/templates`);
      setTemplates(res.data);
    } catch (err) { console.error(err); }
  }, []);

  useEffect(() => { fetchTemplates(); }, [fetchTemplates]);

  const handleDelete = async (id) => {
    if (window.confirm('Eliminare questo template?')) {
      try {
        await axios.delete(`${API}/templates/${id}`);
        toast.success('Template eliminato');
        fetchTemplates();
      } catch (err) { toast.error('Errore'); }
    }
  };

  const typeLabels = { standard: 'Standard', step: 'A Step', moduli: 'Moduli', ibrido: 'Ibrido' };

  const countServices = (t) => {
    let count = (t.services || []).length;
    (t.steps || []).forEach(s => { count += (s.services || []).length; });
    return count;
  };

  return (
    <div className="animate-fadeIn" data-testid="templates-page">
      <div className="page-header">
        <h1 className="page-title">Template Predefiniti</h1>
        <p className="page-subtitle">Usa i template per creare preventivi più velocemente</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((template) => (
          <Card key={template.id} className="card-hover" data-testid={`template-card-${template.id}`}>
            <CardContent className="p-6">
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-[#002fa7] text-white rounded-lg flex items-center justify-center">
                    <Bookmark size={20} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-[#1a281f]">{template.name}</h3>
                    <Badge variant="outline" className="text-xs mt-1">{typeLabels[template.quote_type] || template.quote_type}</Badge>
                  </div>
                </div>
                <Button variant="ghost" size="sm" onClick={() => handleDelete(template.id)} className="text-red-600">
                  <Trash2 size={16} />
                </Button>
              </div>
              <p className="text-sm text-gray-500 mb-4">{template.description}</p>
              <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                <span>{countServices(template)} servizi</span>
                {template.steps?.length > 0 && <span>{template.steps.length} fasi</span>}
              </div>
              <Button className="w-full btn-primary gap-2" onClick={() => navigate('/preventivi/nuovo')} data-testid={`use-template-${template.id}`}>
                <Plus size={16} /> Usa Template
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {templates.length === 0 && (
        <Card>
          <CardContent className="p-6">
            <div className="empty-state">
              <div className="empty-state-icon"><Bookmark size={32} /></div>
              <p className="empty-state-title">Nessun template</p>
              <p className="empty-state-desc">I template verranno creati automaticamente. Puoi anche salvare un preventivo come template dalla sua pagina di dettaglio.</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// App layout
const AppLayout = ({ children }) => (
  <div className="App">
    <Sidebar />
    <main className="main-content">
      {children}
    </main>
    <Toaster position="top-right" richColors />
  </div>
);

// Main App
function App() {
  useEffect(() => {
    // Seed data on first load
    axios.post(`${API}/seed`).catch(() => {});
  }, []);

  return (
    <BrowserRouter>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/preventivi" element={<QuotesPage />} />
          <Route path="/preventivi/nuovo" element={<NewQuotePage />} />
          <Route path="/preventivi/:id/modifica" element={<NewQuotePage />} />
          <Route path="/preventivi/:id" element={<QuoteDetailPage />} />
          <Route path="/clienti" element={<ClientsPage />} />
          <Route path="/servizi" element={<ServicesPage />} />
          <Route path="/fornitori" element={<SuppliersPage />} />
          <Route path="/template" element={<TemplatesPage />} />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  );
}

export default App;
