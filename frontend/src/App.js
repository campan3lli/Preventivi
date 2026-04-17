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
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "./components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Badge } from "./components/ui/badge";
import { ScrollArea } from "./components/ui/scroll-area";
import { 
  FileText, Users, Package, Home, Plus, Search, Edit, Trash2, 
  Download, Mail, Eye, ChevronRight, List, Layers, Grid3X3, Shuffle,
  Building2, Phone, MapPin, Receipt, Settings, CheckCircle2
} from "lucide-react";

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
            <div className="flex justify-between items-start">
              <div>
                <p className="stats-card-title">Preventivi</p>
                <p className="stats-card-value">{stats.quotes}</p>
              </div>
              <div className="stats-card-icon bg-[#002fa7] text-white">
                <FileText size={24} />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="stats-card card-hover" data-testid="stat-clients">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="stats-card-title">Clienti</p>
                <p className="stats-card-value">{stats.clients}</p>
              </div>
              <div className="stats-card-icon bg-[#dbf637] text-[#1a281f]">
                <Users size={24} />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="stats-card card-hover" data-testid="stat-services">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="stats-card-title">Servizi</p>
                <p className="stats-card-value">{stats.services}</p>
              </div>
              <div className="stats-card-icon bg-[#1a281f] text-white">
                <Package size={24} />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="stats-card card-hover" data-testid="stat-total">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="stats-card-title">Totale Preventivi</p>
                <p className="stats-card-value text-[#002fa7]">
                  {new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(stats.total)}
                </p>
              </div>
              <div className="stats-card-icon bg-[#002fa7] text-white">
                <Receipt size={24} />
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
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-[#002fa7] text-white rounded-lg flex items-center justify-center font-bold">
                      #{quote.quote_number}
                    </div>
                    <div>
                      <p className="font-semibold text-[#1a281f]">{quote.client_name}</p>
                      <p className="text-sm text-gray-500">{quote.subject}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <StatusBadge status={quote.status} />
                    <span className="font-bold text-[#002fa7]">{formatPrice(quote.total_amount, 'una_tantum')}</span>
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
                  <div className="service-info">
                    <div className="flex items-center gap-2">
                      <span className="service-name">{service.name}</span>
                      <Badge variant="outline" className="text-xs">{service.category}</Badge>
                      {!service.is_active && <Badge variant="secondary" className="text-xs">Disattivato</Badge>}
                    </div>
                    <p className="service-desc">{service.description}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="service-price">{formatPrice(service.price, service.price_type)}</span>
                    <div className="flex gap-1">
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

// New Quote page
const NewQuotePage = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [clients, setClients] = useState([]);
  const [services, setServices] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(false);

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
        const [clientsRes, servicesRes, suppliersRes] = await Promise.all([
          axios.get(`${API}/clients`),
          axios.get(`${API}/services`),
          axios.get(`${API}/suppliers`)
        ]);
        setClients(clientsRes.data);
        setServices(servicesRes.data.filter(s => s.is_active));
        setSuppliers(suppliersRes.data);
        
        // Auto-select main supplier
        const mainSupplier = suppliersRes.data.find(s => s.is_main);
        if (mainSupplier) {
          setFormData(prev => ({ ...prev, supplier_ids: [mainSupplier.id] }));
        }
      } catch (err) { console.error(err); }
    };
    fetchData();
  }, []);

  const quoteTypes = [
    { value: 'standard', label: 'Standard', desc: 'Lista servizi singoli', icon: List },
    { value: 'step', label: 'A Step', desc: 'Fasi progressive', icon: Layers },
    { value: 'moduli', label: 'Moduli', desc: 'Servizi selezionabili', icon: Grid3X3 },
    { value: 'ibrido', label: 'Ibrido', desc: 'Moduli + Step', icon: Shuffle }
  ];

  const toggleService = (service) => {
    const existing = formData.services.find(s => s.service_id === service.id);
    if (existing) {
      setFormData(prev => ({
        ...prev,
        services: prev.services.filter(s => s.service_id !== service.id)
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        services: [...prev.services, {
          service_id: service.id,
          service_name: service.name,
          description: service.description,
          price: service.price,
          price_type: service.price_type,
          quantity: 1,
          is_selected: true
        }]
      }));
    }
  };

  const calculateTotal = () => {
    return formData.services.reduce((sum, s) => s.is_selected ? sum + (s.price * s.quantity) : sum, 0);
  };

  const handleSubmit = async () => {
    if (!formData.client_id) {
      toast.error('Seleziona un cliente');
      return;
    }
    if (!formData.subject) {
      toast.error('Inserisci l\'oggetto del preventivo');
      return;
    }
    if (formData.services.length === 0) {
      toast.error('Seleziona almeno un servizio');
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post(`${API}/quotes`, formData);
      toast.success('Preventivo creato!');
      navigate(`/preventivi/${res.data.id}`);
    } catch (err) {
      toast.error('Errore nella creazione');
    }
    setLoading(false);
  };

  return (
    <div className="animate-fadeIn" data-testid="new-quote-page">
      <div className="page-header">
        <h1 className="page-title">Nuovo Preventivo</h1>
        <p className="page-subtitle">Step {step} di 3</p>
      </div>

      {/* Progress bar */}
      <div className="flex gap-2 mb-8">
        {[1, 2, 3].map(s => (
          <div key={s} className={`h-2 flex-1 rounded-full transition-colors ${s <= step ? 'bg-[#002fa7]' : 'bg-gray-200'}`} />
        ))}
      </div>

      {step === 1 && (
        <Card className="animate-slideIn">
          <CardHeader>
            <CardTitle>Informazioni Base</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <label className="form-label">Cliente *</label>
              <Select value={formData.client_id} onValueChange={(v) => setFormData({...formData, client_id: v})}>
                <SelectTrigger data-testid="select-client">
                  <SelectValue placeholder="Seleziona cliente" />
                </SelectTrigger>
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
                    onClick={() => setFormData({...formData, quote_type: type.value})} data-testid={`quote-type-${type.value}`}>
                    <div className="quote-type-icon"><type.icon size={24} /></div>
                    <p className="quote-type-name">{type.label}</p>
                    <p className="quote-type-desc">{type.desc}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex justify-end">
              <Button onClick={() => setStep(2)} className="btn-primary gap-2" data-testid="next-step-1">
                Avanti <ChevronRight size={18} />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {step === 2 && (
        <Card className="animate-slideIn">
          <CardHeader>
            <CardTitle>Seleziona Servizi</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <ScrollArea className="h-[500px] pr-4">
                  <div className="service-list">
                    {services.map(service => {
                      const isSelected = formData.services.some(s => s.service_id === service.id);
                      return (
                        <div key={service.id} className={`service-item ${isSelected ? 'selected' : ''}`}
                          onClick={() => toggleService(service)} data-testid={`select-service-${service.id}`}>
                          <div className="flex items-center gap-3">
                            <Checkbox checked={isSelected} className="pointer-events-none" />
                            <div className="service-info">
                              <p className="service-name">{service.name}</p>
                              <p className="service-desc">{service.description}</p>
                            </div>
                          </div>
                          <span className="service-price">{formatPrice(service.price, service.price_type)}</span>
                        </div>
                      );
                    })}
                  </div>
                </ScrollArea>
              </div>
              <div>
                <Card className="bg-gray-50 sticky top-4">
                  <CardHeader>
                    <CardTitle className="text-lg">Riepilogo</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 mb-4">
                      {formData.services.map(s => (
                        <div key={s.service_id} className="flex justify-between text-sm">
                          <span className="text-gray-600 truncate flex-1 mr-2">{s.service_name}</span>
                          <span className="font-semibold whitespace-nowrap">{formatPrice(s.price, s.price_type)}</span>
                        </div>
                      ))}
                    </div>
                    {formData.services.length > 0 && (
                      <div className="pt-4 border-t">
                        <div className="flex justify-between items-center">
                          <span className="font-semibold">Totale</span>
                          <span className="text-xl font-bold text-[#002fa7]">{formatPrice(calculateTotal(), 'una_tantum')}</span>
                        </div>
                      </div>
                    )}
                    {formData.services.length === 0 && (
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

      {step === 3 && (
        <Card className="animate-slideIn">
          <CardHeader>
            <CardTitle>Dettagli Aggiuntivi</CardTitle>
          </CardHeader>
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
                <Input type="number" value={formData.validity_days} onChange={(e) => setFormData({...formData, validity_days: parseInt(e.target.value)})} />
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

            <Card className="bg-[#002fa7] text-white">
              <CardContent className="p-6">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-sm opacity-80">Totale Preventivo</p>
                    <p className="text-3xl font-bold">{formatPrice(calculateTotal(), 'una_tantum')}</p>
                  </div>
                  <CheckCircle2 size={48} className="opacity-50" />
                </div>
              </CardContent>
            </Card>

            <div className="flex justify-between">
              <Button variant="outline" onClick={() => setStep(2)}>Indietro</Button>
              <Button onClick={handleSubmit} className="btn-secondary gap-2" disabled={loading} data-testid="create-quote-btn">
                {loading ? 'Creazione...' : 'Crea Preventivo'}
              </Button>
            </div>
          </CardContent>
        </Card>
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

  if (!quote) return <div className="p-8">Caricamento...</div>;

  return (
    <div className="animate-fadeIn" data-testid="quote-detail-page">
      <div className="page-header flex justify-between items-center">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Button variant="ghost" onClick={() => navigate('/preventivi')} className="p-2">
              <ChevronRight size={20} className="rotate-180" />
            </Button>
            <h1 className="page-title">Preventivo #{quote.quote_number}</h1>
            <StatusBadge status={quote.status} />
          </div>
          <p className="page-subtitle">{quote.subject}</p>
        </div>
        <div className="flex gap-2">
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
          <Button variant="outline" onClick={handleDownload} className="gap-2" data-testid="download-pdf-btn">
            <Download size={18} /> Scarica PDF
          </Button>
          <Button onClick={() => setIsEmailModalOpen(true)} className="btn-primary gap-2" data-testid="send-email-btn">
            <Mail size={18} /> Invia Email
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Servizi</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {quote.services.map((service, idx) => (
                  <div key={idx} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-semibold">{service.service_name}</p>
                      {service.description && <p className="text-sm text-gray-500">{service.description}</p>}
                    </div>
                    <span className="font-bold text-[#002fa7]">{formatPrice(service.price, service.price_type)}</span>
                  </div>
                ))}
              </div>
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
          <Route path="/preventivi/:id" element={<QuoteDetailPage />} />
          <Route path="/clienti" element={<ClientsPage />} />
          <Route path="/servizi" element={<ServicesPage />} />
          <Route path="/fornitori" element={<SuppliersPage />} />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  );
}

export default App;
