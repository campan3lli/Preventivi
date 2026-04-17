"""
Test suite for Step/Phase-based quotes (A Step and Ibrido types)
Tests the new feature: gestione Step/Fasi per preventivi 'A Step' e 'Ibrido'
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://quote-builder-217.preview.emergentagent.com').rstrip('/')

class TestServicesSubItems:
    """Test that services have sub_items (bullet points)"""
    
    def test_services_have_sub_items(self):
        """Verify services contain sub_items field"""
        response = requests.get(f"{BASE_URL}/api/services", timeout=10)
        assert response.status_code == 200
        
        services = response.json()
        assert len(services) > 0, "No services found"
        
        # Check that services have sub_items
        services_with_sub_items = [s for s in services if s.get('sub_items') and len(s['sub_items']) > 0]
        assert len(services_with_sub_items) > 0, "No services have sub_items"
        
        # Verify sub_items structure
        first_service = services_with_sub_items[0]
        assert isinstance(first_service['sub_items'], list)
        assert all(isinstance(item, str) for item in first_service['sub_items'])
        print(f"Found {len(services_with_sub_items)} services with sub_items")
        print(f"Sample sub_items: {first_service['sub_items'][:2]}")


class TestClientCreation:
    """Test client creation for quote testing"""
    
    @pytest.fixture
    def test_client_data(self):
        return {
            "company_name": f"TEST_Client_{uuid.uuid4().hex[:8]}",
            "vat_number": "IT12345678901",
            "address": "Via Test 123, 60035 Jesi (AN)",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.it",
            "phone": "+39 123 456 7890"
        }
    
    def test_create_client(self, test_client_data):
        """Create a test client"""
        response = requests.post(f"{BASE_URL}/api/clients", json=test_client_data, timeout=10)
        assert response.status_code in [200, 201]
        
        client = response.json()
        assert client['company_name'] == test_client_data['company_name']
        assert 'id' in client
        print(f"Created client: {client['company_name']} with ID: {client['id']}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/clients/{client['id']}", timeout=10)


class TestStandardQuote:
    """Test STANDARD type quote creation with sub_items"""
    
    @pytest.fixture
    def setup_client(self):
        """Create a test client and return its ID"""
        client_data = {
            "company_name": f"TEST_StandardQuote_{uuid.uuid4().hex[:8]}",
            "vat_number": "IT12345678901",
            "address": "Via Test 123, 60035 Jesi (AN)",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.it"
        }
        response = requests.post(f"{BASE_URL}/api/clients", json=client_data, timeout=10)
        client = response.json()
        yield client['id']
        # Cleanup
        requests.delete(f"{BASE_URL}/api/clients/{client['id']}", timeout=10)
    
    def test_create_standard_quote_with_sub_items(self, setup_client):
        """Create a STANDARD quote and verify sub_items are preserved"""
        client_id = setup_client
        
        # Get services with sub_items
        services_response = requests.get(f"{BASE_URL}/api/services", timeout=10)
        services = services_response.json()
        services_with_sub_items = [s for s in services if s.get('sub_items') and len(s['sub_items']) > 0][:2]
        
        assert len(services_with_sub_items) >= 1, "Need at least 1 service with sub_items"
        
        quote_data = {
            "client_id": client_id,
            "subject": "TEST Standard Quote with Sub Items",
            "quote_type": "standard",
            "services": [
                {
                    "service_id": svc['id'],
                    "service_name": svc['name'],
                    "description": svc.get('description', ''),
                    "sub_items": svc.get('sub_items', []),
                    "price": svc['price'],
                    "price_type": svc['price_type'],
                    "quantity": 1,
                    "is_selected": True
                } for svc in services_with_sub_items
            ],
            "premise": "Test premise",
            "validity_days": 30,
            "payment_terms": "30% all'accettazione, 70% alla consegna"
        }
        
        response = requests.post(f"{BASE_URL}/api/quotes", json=quote_data, timeout=10)
        assert response.status_code in [200, 201], f"Failed to create quote: {response.text}"
        
        quote = response.json()
        assert quote['quote_type'] == 'standard'
        assert len(quote['services']) == len(services_with_sub_items)
        
        # Verify sub_items are preserved
        for svc in quote['services']:
            assert 'sub_items' in svc
            if svc['sub_items']:
                assert isinstance(svc['sub_items'], list)
                print(f"Service '{svc['service_name']}' has {len(svc['sub_items'])} sub_items")
        
        # Verify via GET
        get_response = requests.get(f"{BASE_URL}/api/quotes/{quote['id']}", timeout=10)
        assert get_response.status_code == 200
        fetched_quote = get_response.json()
        assert fetched_quote['services'][0].get('sub_items') is not None
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/quotes/{quote['id']}", timeout=10)


class TestStepQuote:
    """Test A STEP type quote creation with phases"""
    
    @pytest.fixture
    def setup_client(self):
        """Create a test client and return its ID"""
        client_data = {
            "company_name": f"TEST_StepQuote_{uuid.uuid4().hex[:8]}",
            "vat_number": "IT12345678901",
            "address": "Via Test 123, 60035 Jesi (AN)",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.it"
        }
        response = requests.post(f"{BASE_URL}/api/clients", json=client_data, timeout=10)
        client = response.json()
        yield client['id']
        requests.delete(f"{BASE_URL}/api/clients/{client['id']}", timeout=10)
    
    def test_create_step_quote_with_phases(self, setup_client):
        """Create an A STEP quote with phases, duration, output, description"""
        client_id = setup_client
        
        # Get services
        services_response = requests.get(f"{BASE_URL}/api/services", timeout=10)
        services = services_response.json()[:4]
        
        quote_data = {
            "client_id": client_id,
            "subject": "TEST A Step Quote with Phases",
            "quote_type": "step",
            "services": [],  # No standalone services for step type
            "steps": [
                {
                    "step_number": 1,
                    "title": "Fase 1: Onboarding e Set-up",
                    "description": "Raccolta informazioni e setup iniziale del progetto",
                    "duration": "5 giorni",
                    "output": "Brief approvato, Calendario condiviso",
                    "services": [
                        {
                            "service_id": services[0]['id'],
                            "service_name": services[0]['name'],
                            "description": services[0].get('description', ''),
                            "sub_items": services[0].get('sub_items', []),
                            "price": services[0]['price'],
                            "price_type": services[0]['price_type'],
                            "quantity": 1,
                            "is_selected": True
                        }
                    ]
                },
                {
                    "step_number": 2,
                    "title": "Fase 2: Sviluppo",
                    "description": "Sviluppo del progetto secondo le specifiche",
                    "duration": "15 giorni",
                    "output": "Prima versione del deliverable",
                    "services": [
                        {
                            "service_id": services[1]['id'],
                            "service_name": services[1]['name'],
                            "description": services[1].get('description', ''),
                            "sub_items": services[1].get('sub_items', []),
                            "price": services[1]['price'],
                            "price_type": services[1]['price_type'],
                            "quantity": 1,
                            "is_selected": True
                        },
                        {
                            "service_id": services[2]['id'],
                            "service_name": services[2]['name'],
                            "description": services[2].get('description', ''),
                            "sub_items": services[2].get('sub_items', []),
                            "price": services[2]['price'],
                            "price_type": services[2]['price_type'],
                            "quantity": 1,
                            "is_selected": True
                        }
                    ]
                }
            ],
            "premise": "Test premise for step quote",
            "validity_days": 30,
            "payment_terms": "30% all'accettazione, 70% alla consegna"
        }
        
        response = requests.post(f"{BASE_URL}/api/quotes", json=quote_data, timeout=10)
        assert response.status_code in [200, 201], f"Failed to create step quote: {response.text}"
        
        quote = response.json()
        assert quote['quote_type'] == 'step'
        assert len(quote['steps']) == 2
        
        # Verify step structure
        step1 = quote['steps'][0]
        assert step1['step_number'] == 1
        assert step1['title'] == "Fase 1: Onboarding e Set-up"
        assert step1['duration'] == "5 giorni"
        assert step1['output'] == "Brief approvato, Calendario condiviso"
        assert step1['description'] == "Raccolta informazioni e setup iniziale del progetto"
        assert len(step1['services']) == 1
        
        step2 = quote['steps'][1]
        assert step2['step_number'] == 2
        assert len(step2['services']) == 2
        
        # Verify total calculation
        expected_total = sum(s['price'] for step in quote['steps'] for s in step['services'])
        assert quote['total_amount'] == expected_total
        
        print(f"Created step quote #{quote['quote_number']} with {len(quote['steps'])} phases, total: {quote['total_amount']}")
        
        # Verify via GET
        get_response = requests.get(f"{BASE_URL}/api/quotes/{quote['id']}", timeout=10)
        assert get_response.status_code == 200
        fetched_quote = get_response.json()
        assert len(fetched_quote['steps']) == 2
        assert fetched_quote['steps'][0]['title'] == "Fase 1: Onboarding e Set-up"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/quotes/{quote['id']}", timeout=10)


class TestIbridoQuote:
    """Test IBRIDO type quote creation with phases AND standalone services"""
    
    @pytest.fixture
    def setup_client(self):
        """Create a test client and return its ID"""
        client_data = {
            "company_name": f"TEST_IbridoQuote_{uuid.uuid4().hex[:8]}",
            "vat_number": "IT12345678901",
            "address": "Via Test 123, 60035 Jesi (AN)",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.it"
        }
        response = requests.post(f"{BASE_URL}/api/clients", json=client_data, timeout=10)
        client = response.json()
        yield client['id']
        requests.delete(f"{BASE_URL}/api/clients/{client['id']}", timeout=10)
    
    def test_create_ibrido_quote(self, setup_client):
        """Create an IBRIDO quote with phases AND standalone services"""
        client_id = setup_client
        
        # Get services
        services_response = requests.get(f"{BASE_URL}/api/services", timeout=10)
        services = services_response.json()[:5]
        
        quote_data = {
            "client_id": client_id,
            "subject": "TEST Ibrido Quote",
            "quote_type": "ibrido",
            "services": [
                # Standalone services
                {
                    "service_id": services[3]['id'],
                    "service_name": services[3]['name'],
                    "description": services[3].get('description', ''),
                    "sub_items": services[3].get('sub_items', []),
                    "price": services[3]['price'],
                    "price_type": services[3]['price_type'],
                    "quantity": 1,
                    "is_selected": True
                },
                {
                    "service_id": services[4]['id'],
                    "service_name": services[4]['name'],
                    "description": services[4].get('description', ''),
                    "sub_items": services[4].get('sub_items', []),
                    "price": services[4]['price'],
                    "price_type": services[4]['price_type'],
                    "quantity": 1,
                    "is_selected": True
                }
            ],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Fase 1: Analisi",
                    "description": "Analisi iniziale",
                    "duration": "3 giorni",
                    "output": "Report analisi",
                    "services": [
                        {
                            "service_id": services[0]['id'],
                            "service_name": services[0]['name'],
                            "description": services[0].get('description', ''),
                            "sub_items": services[0].get('sub_items', []),
                            "price": services[0]['price'],
                            "price_type": services[0]['price_type'],
                            "quantity": 1,
                            "is_selected": True
                        }
                    ]
                },
                {
                    "step_number": 2,
                    "title": "Fase 2: Implementazione",
                    "description": "Implementazione del progetto",
                    "duration": "10 giorni",
                    "output": "Deliverable finale",
                    "services": [
                        {
                            "service_id": services[1]['id'],
                            "service_name": services[1]['name'],
                            "description": services[1].get('description', ''),
                            "sub_items": services[1].get('sub_items', []),
                            "price": services[1]['price'],
                            "price_type": services[1]['price_type'],
                            "quantity": 1,
                            "is_selected": True
                        },
                        {
                            "service_id": services[2]['id'],
                            "service_name": services[2]['name'],
                            "description": services[2].get('description', ''),
                            "sub_items": services[2].get('sub_items', []),
                            "price": services[2]['price'],
                            "price_type": services[2]['price_type'],
                            "quantity": 1,
                            "is_selected": True
                        }
                    ]
                }
            ],
            "premise": "Test premise for ibrido quote",
            "validity_days": 30,
            "payment_terms": "30% all'accettazione, 70% alla consegna"
        }
        
        response = requests.post(f"{BASE_URL}/api/quotes", json=quote_data, timeout=10)
        assert response.status_code in [200, 201], f"Failed to create ibrido quote: {response.text}"
        
        quote = response.json()
        assert quote['quote_type'] == 'ibrido'
        assert len(quote['steps']) == 2
        assert len(quote['services']) == 2  # Standalone services
        
        # Verify total includes both steps and standalone services
        step_total = sum(s['price'] for step in quote['steps'] for s in step['services'])
        standalone_total = sum(s['price'] for s in quote['services'])
        expected_total = step_total + standalone_total
        assert quote['total_amount'] == expected_total
        
        print(f"Created ibrido quote #{quote['quote_number']}")
        print(f"  - {len(quote['steps'])} phases with {sum(len(s['services']) for s in quote['steps'])} services")
        print(f"  - {len(quote['services'])} standalone services")
        print(f"  - Total: {quote['total_amount']}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/quotes/{quote['id']}", timeout=10)


class TestPDFGeneration:
    """Test PDF generation for different quote types"""
    
    @pytest.fixture
    def setup_client(self):
        """Create a test client and return its ID"""
        client_data = {
            "company_name": f"TEST_PDFQuote_{uuid.uuid4().hex[:8]}",
            "vat_number": "IT12345678901",
            "address": "Via Test 123, 60035 Jesi (AN)",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.it"
        }
        response = requests.post(f"{BASE_URL}/api/clients", json=client_data, timeout=10)
        client = response.json()
        yield client['id']
        requests.delete(f"{BASE_URL}/api/clients/{client['id']}", timeout=10)
    
    def test_pdf_generation_standard_quote(self, setup_client):
        """Test PDF generation for standard quote"""
        client_id = setup_client
        
        services_response = requests.get(f"{BASE_URL}/api/services", timeout=10)
        services = services_response.json()[:2]
        
        quote_data = {
            "client_id": client_id,
            "subject": "TEST PDF Standard Quote",
            "quote_type": "standard",
            "services": [
                {
                    "service_id": svc['id'],
                    "service_name": svc['name'],
                    "description": svc.get('description', ''),
                    "sub_items": svc.get('sub_items', []),
                    "price": svc['price'],
                    "price_type": svc['price_type'],
                    "quantity": 1,
                    "is_selected": True
                } for svc in services
            ],
            "validity_days": 30
        }
        
        create_response = requests.post(f"{BASE_URL}/api/quotes", json=quote_data, timeout=10)
        quote = create_response.json()
        
        # Generate PDF
        pdf_response = requests.get(f"{BASE_URL}/api/quotes/{quote['id']}/pdf", timeout=30)
        assert pdf_response.status_code == 200
        assert pdf_response.headers.get('content-type') == 'application/pdf'
        assert len(pdf_response.content) > 1000  # PDF should have content
        
        print(f"Generated PDF for standard quote #{quote['quote_number']}: {len(pdf_response.content)} bytes")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/quotes/{quote['id']}", timeout=10)
    
    def test_pdf_generation_step_quote(self, setup_client):
        """Test PDF generation for step-based quote"""
        client_id = setup_client
        
        services_response = requests.get(f"{BASE_URL}/api/services", timeout=10)
        services = services_response.json()[:3]
        
        quote_data = {
            "client_id": client_id,
            "subject": "TEST PDF Step Quote",
            "quote_type": "step",
            "services": [],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Fase 1: Setup",
                    "description": "Setup iniziale",
                    "duration": "5 giorni",
                    "output": "Ambiente configurato",
                    "services": [
                        {
                            "service_id": services[0]['id'],
                            "service_name": services[0]['name'],
                            "description": services[0].get('description', ''),
                            "sub_items": services[0].get('sub_items', []),
                            "price": services[0]['price'],
                            "price_type": services[0]['price_type'],
                            "quantity": 1,
                            "is_selected": True
                        }
                    ]
                },
                {
                    "step_number": 2,
                    "title": "Fase 2: Sviluppo",
                    "description": "Sviluppo principale",
                    "duration": "10 giorni",
                    "output": "Prodotto finale",
                    "services": [
                        {
                            "service_id": services[1]['id'],
                            "service_name": services[1]['name'],
                            "description": services[1].get('description', ''),
                            "sub_items": services[1].get('sub_items', []),
                            "price": services[1]['price'],
                            "price_type": services[1]['price_type'],
                            "quantity": 1,
                            "is_selected": True
                        }
                    ]
                }
            ],
            "validity_days": 30
        }
        
        create_response = requests.post(f"{BASE_URL}/api/quotes", json=quote_data, timeout=10)
        quote = create_response.json()
        
        # Generate PDF
        pdf_response = requests.get(f"{BASE_URL}/api/quotes/{quote['id']}/pdf", timeout=30)
        assert pdf_response.status_code == 200
        assert pdf_response.headers.get('content-type') == 'application/pdf'
        assert len(pdf_response.content) > 1000
        
        print(f"Generated PDF for step quote #{quote['quote_number']}: {len(pdf_response.content)} bytes")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/quotes/{quote['id']}", timeout=10)


class TestQuoteDetailRetrieval:
    """Test quote detail retrieval shows phases correctly"""
    
    @pytest.fixture
    def setup_step_quote(self):
        """Create a step quote for testing"""
        # Create client
        client_data = {
            "company_name": f"TEST_DetailQuote_{uuid.uuid4().hex[:8]}",
            "vat_number": "IT12345678901",
            "address": "Via Test 123, 60035 Jesi (AN)",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.it"
        }
        client_response = requests.post(f"{BASE_URL}/api/clients", json=client_data, timeout=10)
        client = client_response.json()
        
        # Get services
        services_response = requests.get(f"{BASE_URL}/api/services", timeout=10)
        services = services_response.json()[:2]
        
        # Create step quote
        quote_data = {
            "client_id": client['id'],
            "subject": "TEST Detail Step Quote",
            "quote_type": "step",
            "services": [],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Fase Test",
                    "description": "Descrizione fase test",
                    "duration": "7 giorni",
                    "output": "Output test",
                    "services": [
                        {
                            "service_id": services[0]['id'],
                            "service_name": services[0]['name'],
                            "description": services[0].get('description', ''),
                            "sub_items": services[0].get('sub_items', []),
                            "price": services[0]['price'],
                            "price_type": services[0]['price_type'],
                            "quantity": 1,
                            "is_selected": True
                        }
                    ]
                }
            ],
            "validity_days": 30
        }
        
        quote_response = requests.post(f"{BASE_URL}/api/quotes", json=quote_data, timeout=10)
        quote = quote_response.json()
        
        yield quote, client
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/quotes/{quote['id']}", timeout=10)
        requests.delete(f"{BASE_URL}/api/clients/{client['id']}", timeout=10)
    
    def test_quote_detail_shows_phases(self, setup_step_quote):
        """Verify quote detail endpoint returns phases correctly"""
        quote, client = setup_step_quote
        
        response = requests.get(f"{BASE_URL}/api/quotes/{quote['id']}", timeout=10)
        assert response.status_code == 200
        
        detail = response.json()
        assert detail['quote_type'] == 'step'
        assert len(detail['steps']) == 1
        
        step = detail['steps'][0]
        assert step['step_number'] == 1
        assert step['title'] == "Fase Test"
        assert step['description'] == "Descrizione fase test"
        assert step['duration'] == "7 giorni"
        assert step['output'] == "Output test"
        assert len(step['services']) == 1
        
        # Verify sub_items in services
        service = step['services'][0]
        assert 'sub_items' in service
        
        print(f"Quote detail shows phase correctly: {step['title']}")
        print(f"  - Duration: {step['duration']}")
        print(f"  - Output: {step['output']}")
        print(f"  - Services: {len(step['services'])}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
