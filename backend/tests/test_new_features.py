"""
Test suite for new features:
1. Duplicate quote (POST /api/quotes/{id}/duplicate)
2. Edit quote (PUT /api/quotes/{id})
3. Templates CRUD and from-quote endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestTemplates:
    """Test templates API - 6 predefined templates should exist"""
    
    def test_get_templates_returns_6_predefined(self):
        """Templates page should load with 6 predefined templates"""
        response = requests.get(f"{BASE_URL}/api/templates")
        assert response.status_code == 200
        templates = response.json()
        assert len(templates) == 6, f"Expected 6 templates, got {len(templates)}"
        
        # Verify template names
        template_names = [t['name'] for t in templates]
        expected_names = [
            "Pacchetto Sito Web",
            "Pacchetto Social Media", 
            "Pacchetto E-Commerce",
            "Pacchetto Brand Identity",
            "Pacchetto Google Ads",
            "Pacchetto Lancio Attività"
        ]
        for name in expected_names:
            assert name in template_names, f"Missing template: {name}"
    
    def test_templates_have_correct_types(self):
        """Verify templates have correct quote types"""
        response = requests.get(f"{BASE_URL}/api/templates")
        templates = response.json()
        
        type_map = {t['name']: t['quote_type'] for t in templates}
        assert type_map.get("Pacchetto Sito Web") == "standard"
        assert type_map.get("Pacchetto Social Media") == "moduli"
        assert type_map.get("Pacchetto Brand Identity") == "step"
        assert type_map.get("Pacchetto Lancio Attività") == "ibrido"


class TestQuoteCRUD:
    """Test quote creation, editing, and duplication"""
    
    @pytest.fixture
    def test_client(self):
        """Create or get test client"""
        # Check if test client exists
        response = requests.get(f"{BASE_URL}/api/clients")
        clients = response.json()
        test_client = next((c for c in clients if c['company_name'] == 'TEST_DuplicateEdit_Client'), None)
        
        if not test_client:
            # Create test client
            client_data = {
                "company_name": "TEST_DuplicateEdit_Client",
                "vat_number": "12345678901",
                "address": "Via Test 123, Roma",
                "email": "test_dup@test.it",
                "phone": "+39 123 456789"
            }
            response = requests.post(f"{BASE_URL}/api/clients", json=client_data)
            assert response.status_code == 200
            test_client = response.json()
        
        return test_client
    
    @pytest.fixture
    def test_quote(self, test_client):
        """Create a test quote for duplication/editing tests"""
        # Get a service
        services_res = requests.get(f"{BASE_URL}/api/services")
        services = services_res.json()
        assert len(services) > 0, "No services available"
        
        service = services[0]
        quote_data = {
            "client_id": test_client['id'],
            "subject": "TEST_Original_Quote_For_Dup_Edit",
            "quote_type": "standard",
            "services": [{
                "service_id": service['id'],
                "service_name": service['name'],
                "description": service.get('description', ''),
                "sub_items": service.get('sub_items', []),
                "price": service['price'],
                "price_type": service['price_type'],
                "quantity": 1,
                "is_selected": True
            }],
            "steps": [],
            "premise": "Test premise",
            "methodology": "Test methodology",
            "validity_days": 30,
            "payment_terms": "50% upfront, 50% on delivery",
            "delivery_time": "2 weeks"
        }
        
        response = requests.post(f"{BASE_URL}/api/quotes", json=quote_data)
        assert response.status_code == 200
        return response.json()
    
    def test_duplicate_quote_creates_new_quote(self, test_quote):
        """DUPLICATE: Duplicate an existing quote - verify new quote has new number and draft status"""
        original_id = test_quote['id']
        original_number = test_quote['quote_number']
        
        # Duplicate the quote
        response = requests.post(f"{BASE_URL}/api/quotes/{original_id}/duplicate")
        assert response.status_code == 200
        
        duplicated = response.json()
        
        # Verify new quote has different ID
        assert duplicated['id'] != original_id, "Duplicated quote should have new ID"
        
        # Verify new quote has new (higher) number
        assert duplicated['quote_number'] > original_number, f"New quote number {duplicated['quote_number']} should be > {original_number}"
        
        # Verify status is draft
        assert duplicated['status'] == 'draft', f"Duplicated quote status should be 'draft', got '{duplicated['status']}'"
        
        # Verify content is preserved
        assert duplicated['subject'] == test_quote['subject']
        assert duplicated['client_id'] == test_quote['client_id']
        assert len(duplicated['services']) == len(test_quote['services'])
        
        # Cleanup - delete duplicated quote
        requests.delete(f"{BASE_URL}/api/quotes/{duplicated['id']}")
    
    def test_duplicate_nonexistent_quote_returns_404(self):
        """Duplicate non-existent quote should return 404"""
        response = requests.post(f"{BASE_URL}/api/quotes/nonexistent-id-12345/duplicate")
        assert response.status_code == 404
    
    def test_edit_quote_updates_subject_and_services(self, test_quote, test_client):
        """EDIT: Navigate to edit page for existing quote, change subject and services, save"""
        quote_id = test_quote['id']
        
        # Get another service to add
        services_res = requests.get(f"{BASE_URL}/api/services")
        services = services_res.json()
        new_service = services[1] if len(services) > 1 else services[0]
        
        # Update the quote
        updated_data = {
            "client_id": test_client['id'],
            "subject": "TEST_Updated_Subject_After_Edit",
            "quote_type": "standard",
            "services": [
                test_quote['services'][0],  # Keep original service
                {
                    "service_id": new_service['id'],
                    "service_name": new_service['name'],
                    "description": new_service.get('description', ''),
                    "sub_items": new_service.get('sub_items', []),
                    "price": new_service['price'],
                    "price_type": new_service['price_type'],
                    "quantity": 1,
                    "is_selected": True
                }
            ],
            "steps": [],
            "premise": "Updated premise",
            "methodology": "Updated methodology",
            "validity_days": 45,
            "payment_terms": "100% upfront",
            "delivery_time": "3 weeks"
        }
        
        response = requests.put(f"{BASE_URL}/api/quotes/{quote_id}", json=updated_data)
        assert response.status_code == 200
        
        updated_quote = response.json()
        
        # Verify changes
        assert updated_quote['subject'] == "TEST_Updated_Subject_After_Edit"
        assert len(updated_quote['services']) == 2, "Should have 2 services after edit"
        assert updated_quote['premise'] == "Updated premise"
        assert updated_quote['validity_days'] == 45
        
        # Verify via GET
        get_response = requests.get(f"{BASE_URL}/api/quotes/{quote_id}")
        assert get_response.status_code == 200
        fetched = get_response.json()
        assert fetched['subject'] == "TEST_Updated_Subject_After_Edit"
    
    def test_edit_nonexistent_quote_returns_404(self, test_client):
        """Edit non-existent quote should return 404"""
        update_data = {
            "client_id": test_client['id'],
            "subject": "Test",
            "quote_type": "standard",
            "services": [],
            "steps": []
        }
        response = requests.put(f"{BASE_URL}/api/quotes/nonexistent-id-12345", json=update_data)
        assert response.status_code == 404


class TestSaveAsTemplate:
    """Test saving a quote as template"""
    
    @pytest.fixture
    def quote_for_template(self):
        """Create a quote to save as template"""
        # Get client
        clients_res = requests.get(f"{BASE_URL}/api/clients")
        clients = clients_res.json()
        client = clients[0] if clients else None
        
        if not client:
            client_data = {
                "company_name": "TEST_Template_Client",
                "vat_number": "99999999999",
                "address": "Via Template 1",
                "email": "template@test.it"
            }
            client = requests.post(f"{BASE_URL}/api/clients", json=client_data).json()
        
        # Get services
        services_res = requests.get(f"{BASE_URL}/api/services")
        services = services_res.json()[:2]
        
        quote_data = {
            "client_id": client['id'],
            "subject": "TEST_Quote_For_Template_Save",
            "quote_type": "standard",
            "services": [{
                "service_id": s['id'],
                "service_name": s['name'],
                "description": s.get('description', ''),
                "sub_items": s.get('sub_items', []),
                "price": s['price'],
                "price_type": s['price_type'],
                "quantity": 1,
                "is_selected": True
            } for s in services],
            "steps": [],
            "premise": "Template premise",
            "methodology": "Template methodology"
        }
        
        response = requests.post(f"{BASE_URL}/api/quotes", json=quote_data)
        return response.json()
    
    def test_save_quote_as_template(self, quote_for_template):
        """TEMPLATES: Save a quote as template from detail page"""
        quote_id = quote_for_template['id']
        template_name = "TEST_Saved_Template"
        
        # Save as template
        response = requests.post(
            f"{BASE_URL}/api/templates/from-quote/{quote_id}",
            params={"name": template_name, "description": "Test template from quote"}
        )
        assert response.status_code == 200
        
        template = response.json()
        assert template['name'] == template_name
        assert template['quote_type'] == quote_for_template['quote_type']
        assert len(template['services']) == len(quote_for_template['services'])
        
        # Cleanup - delete the template
        requests.delete(f"{BASE_URL}/api/templates/{template['id']}")
        # Cleanup - delete the quote
        requests.delete(f"{BASE_URL}/api/quotes/{quote_id}")
    
    def test_save_nonexistent_quote_as_template_returns_404(self):
        """Save non-existent quote as template should return 404"""
        response = requests.post(
            f"{BASE_URL}/api/templates/from-quote/nonexistent-id-12345",
            params={"name": "Test"}
        )
        assert response.status_code == 404


class TestPDFGeneration:
    """Test PDF download for edited/duplicated quotes"""
    
    def test_pdf_download_for_existing_quote(self):
        """PDF download works for edited/duplicated quotes"""
        # Get any existing quote
        quotes_res = requests.get(f"{BASE_URL}/api/quotes")
        quotes = quotes_res.json()
        
        if not quotes:
            pytest.skip("No quotes available for PDF test")
        
        quote = quotes[0]
        
        # Download PDF
        response = requests.get(f"{BASE_URL}/api/quotes/{quote['id']}/pdf")
        assert response.status_code == 200
        assert response.headers.get('content-type') == 'application/pdf'
        assert len(response.content) > 1000, "PDF should have substantial content"


class TestQuotesListActions:
    """Test quotes list shows Edit and Copy icons"""
    
    def test_quotes_list_returns_quotes_with_required_fields(self):
        """Quotes list shows Edit and Copy icons for each quote - verify data structure"""
        response = requests.get(f"{BASE_URL}/api/quotes")
        assert response.status_code == 200
        
        quotes = response.json()
        if quotes:
            quote = quotes[0]
            # Verify required fields for list display
            assert 'id' in quote
            assert 'quote_number' in quote
            assert 'client_name' in quote
            assert 'subject' in quote
            assert 'status' in quote
            assert 'total_amount' in quote


# Cleanup fixture
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_data():
    """Cleanup TEST_ prefixed data after all tests"""
    yield
    # Cleanup quotes
    quotes_res = requests.get(f"{BASE_URL}/api/quotes")
    for q in quotes_res.json():
        if 'TEST_' in q.get('subject', ''):
            requests.delete(f"{BASE_URL}/api/quotes/{q['id']}")
    
    # Cleanup clients
    clients_res = requests.get(f"{BASE_URL}/api/clients")
    for c in clients_res.json():
        if 'TEST_' in c.get('company_name', ''):
            requests.delete(f"{BASE_URL}/api/clients/{c['id']}")
    
    # Cleanup templates
    templates_res = requests.get(f"{BASE_URL}/api/templates")
    for t in templates_res.json():
        if 'TEST_' in t.get('name', ''):
            requests.delete(f"{BASE_URL}/api/templates/{t['id']}")
