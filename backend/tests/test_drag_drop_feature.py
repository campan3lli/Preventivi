"""
Test suite for Drag & Drop feature for reordering phases in 'A Step' and 'Ibrido' quotes.
Tests the new feature: drag & drop per riordinare le fasi nei preventivi 'A Step' e 'Ibrido'.
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://quote-builder-217.preview.emergentagent.com').rstrip('/')


class TestDragDropStepQuote:
    """Test drag & drop reordering for A Step quotes"""
    
    @pytest.fixture
    def setup_client(self):
        """Create a test client and return its ID"""
        client_data = {
            "company_name": f"TEST_DragDrop_{uuid.uuid4().hex[:8]}",
            "vat_number": "IT12345678901",
            "address": "Via Test 123, 60035 Jesi (AN)",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.it"
        }
        response = requests.post(f"{BASE_URL}/api/clients", json=client_data, timeout=10)
        client = response.json()
        yield client['id']
        requests.delete(f"{BASE_URL}/api/clients/{client['id']}", timeout=10)
    
    def test_create_step_quote_with_ordered_phases(self, setup_client):
        """Create a step quote with 3 phases and verify order is preserved"""
        client_id = setup_client
        
        # Get services
        services_response = requests.get(f"{BASE_URL}/api/services", timeout=10)
        services = services_response.json()[:3]
        
        # Create quote with 3 phases in specific order
        quote_data = {
            "client_id": client_id,
            "subject": "TEST Drag Drop Order Verification",
            "quote_type": "step",
            "services": [],
            "steps": [
                {
                    "step_number": 1,
                    "title": "First Phase",
                    "description": "This is the first phase",
                    "duration": "5 giorni",
                    "output": "Output 1",
                    "services": [{
                        "service_id": services[0]['id'],
                        "service_name": services[0]['name'],
                        "description": services[0].get('description', ''),
                        "sub_items": services[0].get('sub_items', []),
                        "price": services[0]['price'],
                        "price_type": services[0]['price_type'],
                        "quantity": 1,
                        "is_selected": True
                    }]
                },
                {
                    "step_number": 2,
                    "title": "Second Phase",
                    "description": "This is the second phase",
                    "duration": "10 giorni",
                    "output": "Output 2",
                    "services": [{
                        "service_id": services[1]['id'],
                        "service_name": services[1]['name'],
                        "description": services[1].get('description', ''),
                        "sub_items": services[1].get('sub_items', []),
                        "price": services[1]['price'],
                        "price_type": services[1]['price_type'],
                        "quantity": 1,
                        "is_selected": True
                    }]
                },
                {
                    "step_number": 3,
                    "title": "Third Phase",
                    "description": "This is the third phase",
                    "duration": "15 giorni",
                    "output": "Output 3",
                    "services": [{
                        "service_id": services[2]['id'],
                        "service_name": services[2]['name'],
                        "description": services[2].get('description', ''),
                        "sub_items": services[2].get('sub_items', []),
                        "price": services[2]['price'],
                        "price_type": services[2]['price_type'],
                        "quantity": 1,
                        "is_selected": True
                    }]
                }
            ],
            "validity_days": 30
        }
        
        response = requests.post(f"{BASE_URL}/api/quotes", json=quote_data, timeout=10)
        assert response.status_code in [200, 201], f"Failed to create quote: {response.text}"
        
        quote = response.json()
        assert quote['quote_type'] == 'step'
        assert len(quote['steps']) == 3
        
        # Verify order is preserved
        assert quote['steps'][0]['step_number'] == 1
        assert quote['steps'][0]['title'] == "First Phase"
        assert quote['steps'][1]['step_number'] == 2
        assert quote['steps'][1]['title'] == "Second Phase"
        assert quote['steps'][2]['step_number'] == 3
        assert quote['steps'][2]['title'] == "Third Phase"
        
        print(f"Created step quote #{quote['quote_number']} with 3 phases in correct order")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/quotes/{quote['id']}", timeout=10)
    
    def test_update_step_quote_with_reordered_phases(self, setup_client):
        """Create a step quote, then update with reordered phases (simulating drag & drop)"""
        client_id = setup_client
        
        # Get services
        services_response = requests.get(f"{BASE_URL}/api/services", timeout=10)
        services = services_response.json()[:3]
        
        # Create initial quote
        quote_data = {
            "client_id": client_id,
            "subject": "TEST Drag Drop Reorder",
            "quote_type": "step",
            "services": [],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Alpha",
                    "description": "Alpha phase",
                    "duration": "5 giorni",
                    "output": "Alpha output",
                    "services": [{
                        "service_id": services[0]['id'],
                        "service_name": services[0]['name'],
                        "description": services[0].get('description', ''),
                        "sub_items": services[0].get('sub_items', []),
                        "price": services[0]['price'],
                        "price_type": services[0]['price_type'],
                        "quantity": 1,
                        "is_selected": True
                    }]
                },
                {
                    "step_number": 2,
                    "title": "Beta",
                    "description": "Beta phase",
                    "duration": "10 giorni",
                    "output": "Beta output",
                    "services": [{
                        "service_id": services[1]['id'],
                        "service_name": services[1]['name'],
                        "description": services[1].get('description', ''),
                        "sub_items": services[1].get('sub_items', []),
                        "price": services[1]['price'],
                        "price_type": services[1]['price_type'],
                        "quantity": 1,
                        "is_selected": True
                    }]
                },
                {
                    "step_number": 3,
                    "title": "Gamma",
                    "description": "Gamma phase",
                    "duration": "15 giorni",
                    "output": "Gamma output",
                    "services": [{
                        "service_id": services[2]['id'],
                        "service_name": services[2]['name'],
                        "description": services[2].get('description', ''),
                        "sub_items": services[2].get('sub_items', []),
                        "price": services[2]['price'],
                        "price_type": services[2]['price_type'],
                        "quantity": 1,
                        "is_selected": True
                    }]
                }
            ],
            "validity_days": 30
        }
        
        create_response = requests.post(f"{BASE_URL}/api/quotes", json=quote_data, timeout=10)
        quote = create_response.json()
        quote_id = quote['id']
        
        print(f"Created quote with order: Alpha(1), Beta(2), Gamma(3)")
        
        # Now simulate drag & drop reorder: move Gamma to first position
        # New order should be: Gamma(1), Alpha(2), Beta(3)
        reordered_data = {
            "client_id": client_id,
            "subject": "TEST Drag Drop Reorder",
            "quote_type": "step",
            "services": [],
            "steps": [
                {
                    "step_number": 1,  # Gamma is now first
                    "title": "Gamma",
                    "description": "Gamma phase",
                    "duration": "15 giorni",
                    "output": "Gamma output",
                    "services": [{
                        "service_id": services[2]['id'],
                        "service_name": services[2]['name'],
                        "description": services[2].get('description', ''),
                        "sub_items": services[2].get('sub_items', []),
                        "price": services[2]['price'],
                        "price_type": services[2]['price_type'],
                        "quantity": 1,
                        "is_selected": True
                    }]
                },
                {
                    "step_number": 2,  # Alpha is now second
                    "title": "Alpha",
                    "description": "Alpha phase",
                    "duration": "5 giorni",
                    "output": "Alpha output",
                    "services": [{
                        "service_id": services[0]['id'],
                        "service_name": services[0]['name'],
                        "description": services[0].get('description', ''),
                        "sub_items": services[0].get('sub_items', []),
                        "price": services[0]['price'],
                        "price_type": services[0]['price_type'],
                        "quantity": 1,
                        "is_selected": True
                    }]
                },
                {
                    "step_number": 3,  # Beta is now third
                    "title": "Beta",
                    "description": "Beta phase",
                    "duration": "10 giorni",
                    "output": "Beta output",
                    "services": [{
                        "service_id": services[1]['id'],
                        "service_name": services[1]['name'],
                        "description": services[1].get('description', ''),
                        "sub_items": services[1].get('sub_items', []),
                        "price": services[1]['price'],
                        "price_type": services[1]['price_type'],
                        "quantity": 1,
                        "is_selected": True
                    }]
                }
            ],
            "validity_days": 30
        }
        
        update_response = requests.put(f"{BASE_URL}/api/quotes/{quote_id}", json=reordered_data, timeout=10)
        assert update_response.status_code == 200, f"Failed to update quote: {update_response.text}"
        
        updated_quote = update_response.json()
        
        # Verify new order
        assert updated_quote['steps'][0]['step_number'] == 1
        assert updated_quote['steps'][0]['title'] == "Gamma"
        assert updated_quote['steps'][1]['step_number'] == 2
        assert updated_quote['steps'][1]['title'] == "Alpha"
        assert updated_quote['steps'][2]['step_number'] == 3
        assert updated_quote['steps'][2]['title'] == "Beta"
        
        print(f"Updated quote with new order: Gamma(1), Alpha(2), Beta(3)")
        
        # Verify via GET
        get_response = requests.get(f"{BASE_URL}/api/quotes/{quote_id}", timeout=10)
        fetched_quote = get_response.json()
        
        assert fetched_quote['steps'][0]['title'] == "Gamma"
        assert fetched_quote['steps'][1]['title'] == "Alpha"
        assert fetched_quote['steps'][2]['title'] == "Beta"
        
        print("Verified reordered phases are persisted correctly")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/quotes/{quote_id}", timeout=10)


class TestDragDropIbridoQuote:
    """Test drag & drop reordering for Ibrido quotes"""
    
    @pytest.fixture
    def setup_client(self):
        """Create a test client and return its ID"""
        client_data = {
            "company_name": f"TEST_DragDropIbrido_{uuid.uuid4().hex[:8]}",
            "vat_number": "IT12345678901",
            "address": "Via Test 123, 60035 Jesi (AN)",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.it"
        }
        response = requests.post(f"{BASE_URL}/api/clients", json=client_data, timeout=10)
        client = response.json()
        yield client['id']
        requests.delete(f"{BASE_URL}/api/clients/{client['id']}", timeout=10)
    
    def test_ibrido_quote_phases_reorder(self, setup_client):
        """Create an ibrido quote with phases and standalone services, then reorder phases"""
        client_id = setup_client
        
        # Get services
        services_response = requests.get(f"{BASE_URL}/api/services", timeout=10)
        services = services_response.json()[:5]
        
        # Create ibrido quote with 2 phases and 1 standalone service
        quote_data = {
            "client_id": client_id,
            "subject": "TEST Ibrido Drag Drop",
            "quote_type": "ibrido",
            "services": [
                # Standalone service
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
                    "title": "Phase One",
                    "description": "First phase",
                    "duration": "5 giorni",
                    "output": "Output 1",
                    "services": [{
                        "service_id": services[0]['id'],
                        "service_name": services[0]['name'],
                        "description": services[0].get('description', ''),
                        "sub_items": services[0].get('sub_items', []),
                        "price": services[0]['price'],
                        "price_type": services[0]['price_type'],
                        "quantity": 1,
                        "is_selected": True
                    }]
                },
                {
                    "step_number": 2,
                    "title": "Phase Two",
                    "description": "Second phase",
                    "duration": "10 giorni",
                    "output": "Output 2",
                    "services": [{
                        "service_id": services[1]['id'],
                        "service_name": services[1]['name'],
                        "description": services[1].get('description', ''),
                        "sub_items": services[1].get('sub_items', []),
                        "price": services[1]['price'],
                        "price_type": services[1]['price_type'],
                        "quantity": 1,
                        "is_selected": True
                    }]
                }
            ],
            "validity_days": 30
        }
        
        create_response = requests.post(f"{BASE_URL}/api/quotes", json=quote_data, timeout=10)
        assert create_response.status_code in [200, 201]
        
        quote = create_response.json()
        quote_id = quote['id']
        
        assert quote['quote_type'] == 'ibrido'
        assert len(quote['steps']) == 2
        assert len(quote['services']) == 1  # Standalone service
        
        print(f"Created ibrido quote with order: Phase One(1), Phase Two(2)")
        
        # Reorder: swap Phase One and Phase Two
        reordered_data = {
            "client_id": client_id,
            "subject": "TEST Ibrido Drag Drop",
            "quote_type": "ibrido",
            "services": [
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
                    "step_number": 1,  # Phase Two is now first
                    "title": "Phase Two",
                    "description": "Second phase",
                    "duration": "10 giorni",
                    "output": "Output 2",
                    "services": [{
                        "service_id": services[1]['id'],
                        "service_name": services[1]['name'],
                        "description": services[1].get('description', ''),
                        "sub_items": services[1].get('sub_items', []),
                        "price": services[1]['price'],
                        "price_type": services[1]['price_type'],
                        "quantity": 1,
                        "is_selected": True
                    }]
                },
                {
                    "step_number": 2,  # Phase One is now second
                    "title": "Phase One",
                    "description": "First phase",
                    "duration": "5 giorni",
                    "output": "Output 1",
                    "services": [{
                        "service_id": services[0]['id'],
                        "service_name": services[0]['name'],
                        "description": services[0].get('description', ''),
                        "sub_items": services[0].get('sub_items', []),
                        "price": services[0]['price'],
                        "price_type": services[0]['price_type'],
                        "quantity": 1,
                        "is_selected": True
                    }]
                }
            ],
            "validity_days": 30
        }
        
        update_response = requests.put(f"{BASE_URL}/api/quotes/{quote_id}", json=reordered_data, timeout=10)
        assert update_response.status_code == 200
        
        updated_quote = update_response.json()
        
        # Verify new order
        assert updated_quote['steps'][0]['title'] == "Phase Two"
        assert updated_quote['steps'][0]['step_number'] == 1
        assert updated_quote['steps'][1]['title'] == "Phase One"
        assert updated_quote['steps'][1]['step_number'] == 2
        
        # Verify standalone service is still there
        assert len(updated_quote['services']) == 1
        
        print(f"Updated ibrido quote with new order: Phase Two(1), Phase One(2)")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/quotes/{quote_id}", timeout=10)


class TestStepNumberAutoUpdate:
    """Test that step_number is automatically updated after reorder"""
    
    @pytest.fixture
    def setup_client(self):
        """Create a test client and return its ID"""
        client_data = {
            "company_name": f"TEST_StepNumber_{uuid.uuid4().hex[:8]}",
            "vat_number": "IT12345678901",
            "address": "Via Test 123, 60035 Jesi (AN)",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.it"
        }
        response = requests.post(f"{BASE_URL}/api/clients", json=client_data, timeout=10)
        client = response.json()
        yield client['id']
        requests.delete(f"{BASE_URL}/api/clients/{client['id']}", timeout=10)
    
    def test_step_numbers_are_sequential_after_reorder(self, setup_client):
        """Verify step_number values are always 1, 2, 3... after any reorder"""
        client_id = setup_client
        
        # Get services
        services_response = requests.get(f"{BASE_URL}/api/services", timeout=10)
        services = services_response.json()[:4]
        
        # Create quote with 4 phases
        quote_data = {
            "client_id": client_id,
            "subject": "TEST Step Number Sequential",
            "quote_type": "step",
            "services": [],
            "steps": [
                {"step_number": 1, "title": "A", "description": "", "duration": "1d", "output": "A", "services": []},
                {"step_number": 2, "title": "B", "description": "", "duration": "2d", "output": "B", "services": []},
                {"step_number": 3, "title": "C", "description": "", "duration": "3d", "output": "C", "services": []},
                {"step_number": 4, "title": "D", "description": "", "duration": "4d", "output": "D", "services": []}
            ],
            "validity_days": 30
        }
        
        create_response = requests.post(f"{BASE_URL}/api/quotes", json=quote_data, timeout=10)
        quote = create_response.json()
        quote_id = quote['id']
        
        # Verify initial order
        for i, step in enumerate(quote['steps']):
            assert step['step_number'] == i + 1, f"Initial step {i} has wrong number"
        
        print("Initial order: A(1), B(2), C(3), D(4)")
        
        # Reorder to: D, B, A, C (simulating multiple drag operations)
        reordered_data = {
            "client_id": client_id,
            "subject": "TEST Step Number Sequential",
            "quote_type": "step",
            "services": [],
            "steps": [
                {"step_number": 1, "title": "D", "description": "", "duration": "4d", "output": "D", "services": []},
                {"step_number": 2, "title": "B", "description": "", "duration": "2d", "output": "B", "services": []},
                {"step_number": 3, "title": "A", "description": "", "duration": "1d", "output": "A", "services": []},
                {"step_number": 4, "title": "C", "description": "", "duration": "3d", "output": "C", "services": []}
            ],
            "validity_days": 30
        }
        
        update_response = requests.put(f"{BASE_URL}/api/quotes/{quote_id}", json=reordered_data, timeout=10)
        updated_quote = update_response.json()
        
        # Verify step numbers are sequential
        expected_titles = ["D", "B", "A", "C"]
        for i, step in enumerate(updated_quote['steps']):
            assert step['step_number'] == i + 1, f"Step {i} has wrong number after reorder"
            assert step['title'] == expected_titles[i], f"Step {i} has wrong title"
        
        print("Reordered: D(1), B(2), A(3), C(4) - step numbers are sequential")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/quotes/{quote_id}", timeout=10)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
