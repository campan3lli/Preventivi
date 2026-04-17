#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class LimoneBluAPITester:
    def __init__(self, base_url="https://quote-builder-217.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_ids = {
            'clients': [],
            'services': [],
            'suppliers': [],
            'quotes': []
        }

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        return success

    def test_api_health(self):
        """Test if API is accessible"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            return self.log_test("API Health Check", response.status_code == 200, f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("API Health Check", False, str(e))

    def test_seed_data(self):
        """Test seeding initial data"""
        try:
            response = requests.post(f"{self.api_url}/seed", timeout=30)
            success = response.status_code in [200, 201]
            if success:
                data = response.json()
                details = f"Services: {data.get('services_count', 0)}, Suppliers: {data.get('suppliers_count', 0)}"
            else:
                details = f"Status: {response.status_code}"
            return self.log_test("Seed Data", success, details)
        except Exception as e:
            return self.log_test("Seed Data", False, str(e))

    def test_get_services(self):
        """Test getting all services"""
        try:
            response = requests.get(f"{self.api_url}/services", timeout=10)
            success = response.status_code == 200
            if success:
                services = response.json()
                details = f"Found {len(services)} services"
            else:
                details = f"Status: {response.status_code}"
            return self.log_test("Get Services", success, details)
        except Exception as e:
            return self.log_test("Get Services", False, str(e))

    def test_get_suppliers(self):
        """Test getting all suppliers"""
        try:
            response = requests.get(f"{self.api_url}/suppliers", timeout=10)
            success = response.status_code == 200
            if success:
                suppliers = response.json()
                details = f"Found {len(suppliers)} suppliers"
            else:
                details = f"Status: {response.status_code}"
            return self.log_test("Get Suppliers", success, details)
        except Exception as e:
            return self.log_test("Get Suppliers", False, str(e))

    def test_create_client(self):
        """Test creating a new client"""
        try:
            client_data = {
                "company_name": "Test Company SRL",
                "vat_number": "IT12345678901",
                "address": "Via Test 123, 60035 Jesi (AN)",
                "email": "test@testcompany.it",
                "phone": "+39 123 456 7890"
            }
            response = requests.post(f"{self.api_url}/clients", json=client_data, timeout=10)
            success = response.status_code in [200, 201]
            if success:
                client = response.json()
                self.created_ids['clients'].append(client['id'])
                details = f"Created client: {client['company_name']}"
            else:
                details = f"Status: {response.status_code}"
            return self.log_test("Create Client", success, details)
        except Exception as e:
            return self.log_test("Create Client", False, str(e))

    def test_get_clients(self):
        """Test getting all clients"""
        try:
            response = requests.get(f"{self.api_url}/clients", timeout=10)
            success = response.status_code == 200
            if success:
                clients = response.json()
                details = f"Found {len(clients)} clients"
            else:
                details = f"Status: {response.status_code}"
            return self.log_test("Get Clients", success, details)
        except Exception as e:
            return self.log_test("Get Clients", False, str(e))

    def test_create_service(self):
        """Test creating a new service"""
        try:
            service_data = {
                "name": "Test Service",
                "description": "A test service for API testing",
                "price": 500.00,
                "price_type": "una_tantum",
                "category": "test",
                "is_active": True
            }
            response = requests.post(f"{self.api_url}/services", json=service_data, timeout=10)
            success = response.status_code in [200, 201]
            if success:
                service = response.json()
                self.created_ids['services'].append(service['id'])
                details = f"Created service: {service['name']}"
            else:
                details = f"Status: {response.status_code}"
            return self.log_test("Create Service", success, details)
        except Exception as e:
            return self.log_test("Create Service", False, str(e))

    def test_create_quote(self):
        """Test creating a new quote"""
        try:
            # First get a client and some services
            clients_response = requests.get(f"{self.api_url}/clients", timeout=10)
            services_response = requests.get(f"{self.api_url}/services", timeout=10)
            
            if clients_response.status_code != 200 or services_response.status_code != 200:
                return self.log_test("Create Quote", False, "Failed to get clients or services")
            
            clients = clients_response.json()
            services = services_response.json()
            
            if not clients or not services:
                return self.log_test("Create Quote", False, "No clients or services available")
            
            # Use first client and first 2 services
            client = clients[0]
            selected_services = services[:2]
            
            quote_data = {
                "client_id": client['id'],
                "subject": "Test Quote for API Testing",
                "quote_type": "standard",
                "services": [
                    {
                        "service_id": svc['id'],
                        "service_name": svc['name'],
                        "description": svc.get('description', ''),
                        "price": svc['price'],
                        "price_type": svc['price_type'],
                        "quantity": 1,
                        "is_selected": True
                    } for svc in selected_services
                ],
                "premise": "This is a test quote created by the API testing suite.",
                "methodology": "Standard testing methodology",
                "validity_days": 30,
                "payment_terms": "30% all'accettazione, 70% alla consegna"
            }
            
            response = requests.post(f"{self.api_url}/quotes", json=quote_data, timeout=10)
            success = response.status_code in [200, 201]
            if success:
                quote = response.json()
                self.created_ids['quotes'].append(quote['id'])
                details = f"Created quote #{quote['quote_number']} for {quote['client_name']}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            return self.log_test("Create Quote", success, details)
        except Exception as e:
            return self.log_test("Create Quote", False, str(e))

    def test_get_quotes(self):
        """Test getting all quotes"""
        try:
            response = requests.get(f"{self.api_url}/quotes", timeout=10)
            success = response.status_code == 200
            if success:
                quotes = response.json()
                details = f"Found {len(quotes)} quotes"
            else:
                details = f"Status: {response.status_code}"
            return self.log_test("Get Quotes", success, details)
        except Exception as e:
            return self.log_test("Get Quotes", False, str(e))

    def test_pdf_generation(self):
        """Test PDF generation for a quote"""
        try:
            # Get quotes first
            quotes_response = requests.get(f"{self.api_url}/quotes", timeout=10)
            if quotes_response.status_code != 200:
                return self.log_test("PDF Generation", False, "Failed to get quotes")
            
            quotes = quotes_response.json()
            if not quotes:
                return self.log_test("PDF Generation", False, "No quotes available for PDF test")
            
            # Test PDF generation for first quote
            quote = quotes[0]
            response = requests.get(f"{self.api_url}/quotes/{quote['id']}/pdf", timeout=30)
            success = response.status_code == 200 and response.headers.get('content-type') == 'application/pdf'
            if success:
                details = f"Generated PDF for quote #{quote['quote_number']} ({len(response.content)} bytes)"
            else:
                details = f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type')}"
            return self.log_test("PDF Generation", success, details)
        except Exception as e:
            return self.log_test("PDF Generation", False, str(e))

    def test_quote_detail(self):
        """Test getting quote details"""
        try:
            # Get quotes first
            quotes_response = requests.get(f"{self.api_url}/quotes", timeout=10)
            if quotes_response.status_code != 200:
                return self.log_test("Quote Detail", False, "Failed to get quotes")
            
            quotes = quotes_response.json()
            if not quotes:
                return self.log_test("Quote Detail", False, "No quotes available")
            
            # Test getting detail for first quote
            quote_id = quotes[0]['id']
            response = requests.get(f"{self.api_url}/quotes/{quote_id}", timeout=10)
            success = response.status_code == 200
            if success:
                quote = response.json()
                details = f"Retrieved quote #{quote['quote_number']} with {len(quote.get('services', []))} services"
            else:
                details = f"Status: {response.status_code}"
            return self.log_test("Quote Detail", success, details)
        except Exception as e:
            return self.log_test("Quote Detail", False, str(e))

    def test_client_detail(self):
        """Test getting client details"""
        try:
            # Get clients first
            clients_response = requests.get(f"{self.api_url}/clients", timeout=10)
            if clients_response.status_code != 200:
                return self.log_test("Client Detail", False, "Failed to get clients")
            
            clients = clients_response.json()
            if not clients:
                return self.log_test("Client Detail", False, "No clients available")
            
            # Test getting detail for first client
            client_id = clients[0]['id']
            response = requests.get(f"{self.api_url}/clients/{client_id}", timeout=10)
            success = response.status_code == 200
            if success:
                client = response.json()
                details = f"Retrieved client: {client['company_name']}"
            else:
                details = f"Status: {response.status_code}"
            return self.log_test("Client Detail", success, details)
        except Exception as e:
            return self.log_test("Client Detail", False, str(e))

    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete test quotes
        for quote_id in self.created_ids['quotes']:
            try:
                requests.delete(f"{self.api_url}/quotes/{quote_id}", timeout=10)
                print(f"  Deleted quote: {quote_id}")
            except:
                pass
        
        # Delete test clients
        for client_id in self.created_ids['clients']:
            try:
                requests.delete(f"{self.api_url}/clients/{client_id}", timeout=10)
                print(f"  Deleted client: {client_id}")
            except:
                pass
        
        # Delete test services
        for service_id in self.created_ids['services']:
            try:
                requests.delete(f"{self.api_url}/services/{service_id}", timeout=10)
                print(f"  Deleted service: {service_id}")
            except:
                pass

    def run_all_tests(self):
        """Run all API tests"""
        print(f"🚀 Starting Limone Blu Studio API Tests")
        print(f"📍 Testing: {self.base_url}")
        print("=" * 60)
        
        # Core API tests
        self.test_api_health()
        self.test_seed_data()
        
        # Data retrieval tests
        self.test_get_services()
        self.test_get_suppliers()
        self.test_get_clients()
        self.test_get_quotes()
        
        # CRUD tests
        self.test_create_client()
        self.test_create_service()
        self.test_create_quote()
        
        # Detail tests
        self.test_client_detail()
        self.test_quote_detail()
        
        # Advanced functionality
        self.test_pdf_generation()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    tester = LimoneBluAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())