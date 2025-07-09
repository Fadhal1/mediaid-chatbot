#!/usr/bin/env python3
import requests
import json
import uuid
import time
import sys
from typing import Dict, List, Any

# Get the backend URL from frontend/.env
BACKEND_URL = "https://36d3204c-b015-409c-9043-ab10b7f6a75c.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session_id = str(uuid.uuid4())
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
    
    def run_test(self, test_name: str, test_func, *args, **kwargs):
        """Run a test and record the result"""
        self.test_results["total_tests"] += 1
        print(f"\n{'='*80}\nRunning test: {test_name}\n{'='*80}")
        
        try:
            start_time = time.time()
            result = test_func(*args, **kwargs)
            end_time = time.time()
            
            if result:
                self.test_results["passed_tests"] += 1
                status = "PASSED"
            else:
                self.test_results["failed_tests"] += 1
                status = "FAILED"
                
            self.test_results["test_details"].append({
                "name": test_name,
                "status": status,
                "duration": round(end_time - start_time, 2)
            })
            
            print(f"Test {status}: {test_name}")
            return result
        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append({
                "name": test_name,
                "status": "ERROR",
                "error": str(e)
            })
            print(f"Test ERROR: {test_name} - {str(e)}")
            return False
    
    def test_database_initialization(self) -> bool:
        """Test if the database is initialized with sample drugs"""
        response = requests.get(f"{self.base_url}/drugs")
        
        if response.status_code != 200:
            print(f"Error: Failed to get drugs. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        drugs = response.json()
        
        # Check if we have at least the 8 sample drugs
        if len(drugs) < 8:
            print(f"Error: Expected at least 8 drugs, but got {len(drugs)}")
            return False
        
        # Check if the expected drugs are present
        expected_drugs = ["Paracetamol", "Ibuprofen", "Aspirin", "Loratadine", 
                         "Omeprazole", "Dextromethorphan", "Loperamide", "Cetirizine"]
        
        drug_names = [drug["name"] for drug in drugs]
        for expected_drug in expected_drugs:
            if expected_drug not in drug_names:
                print(f"Error: Expected drug {expected_drug} not found in database")
                return False
        
        # Check if drug fields are correct
        required_fields = ["id", "name", "generic_name", "description", "uses", 
                          "dosage", "side_effects", "precautions", "symptoms"]
        
        for drug in drugs:
            for field in required_fields:
                if field not in drug:
                    print(f"Error: Required field {field} missing from drug {drug['name']}")
                    return False
        
        print(f"Database initialized with {len(drugs)} drugs")
        return True
    
    def test_chat_api_symptom_detection(self) -> bool:
        """Test the chat API with symptom detection"""
        # Test with a headache symptom
        payload = {
            "session_id": self.session_id,
            "message": "I have a headache"
        }
        
        response = requests.post(f"{self.base_url}/chat", json=payload)
        
        if response.status_code != 200:
            print(f"Error: Failed to chat. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        chat_response = response.json()
        
        # Check if response contains headache advice
        if "headache" not in chat_response["response"].lower():
            print(f"Error: Expected headache advice in response, but got: {chat_response['response']}")
            return False
        
        # Check if drug suggestions include headache medications
        if not chat_response["drug_suggestions"]:
            print("Error: Expected drug suggestions for headache, but got none")
            return False
        
        # Check if Paracetamol or Ibuprofen is suggested
        drug_names = [drug["name"] for drug in chat_response["drug_suggestions"]]
        if "Paracetamol" not in drug_names and "Ibuprofen" not in drug_names:
            print(f"Error: Expected Paracetamol or Ibuprofen in drug suggestions, but got: {drug_names}")
            return False
        
        print(f"Chat API correctly detected headache symptom and suggested: {', '.join(drug_names)}")
        return True
    
    def test_chat_api_drug_info(self) -> bool:
        """Test the chat API with drug information request"""
        payload = {
            "session_id": self.session_id,
            "message": "What is Paracetamol?"
        }
        
        response = requests.post(f"{self.base_url}/chat", json=payload)
        
        if response.status_code != 200:
            print(f"Error: Failed to chat. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        chat_response = response.json()
        
        # Check if response contains information about medications
        if "medication" not in chat_response["response"].lower():
            print(f"Error: Expected medication information in response, but got: {chat_response['response']}")
            return False
        
        print("Chat API correctly responded to drug information request")
        return True
    
    def test_chat_api_greeting(self) -> bool:
        """Test the chat API with a greeting"""
        payload = {
            "session_id": self.session_id,
            "message": "Hello"
        }
        
        response = requests.post(f"{self.base_url}/chat", json=payload)
        
        if response.status_code != 200:
            print(f"Error: Failed to chat. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        chat_response = response.json()
        
        # Check if response contains a greeting
        if "hello" not in chat_response["response"].lower():
            print(f"Error: Expected greeting in response, but got: {chat_response['response']}")
            return False
        
        print("Chat API correctly responded to greeting")
        return True
    
    def test_drug_search_api_by_name(self) -> bool:
        """Test the drug search API by name"""
        response = requests.get(f"{self.base_url}/search?query=Paracetamol")
        
        if response.status_code != 200:
            print(f"Error: Failed to search drugs. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        drugs = response.json()
        
        if not drugs:
            print("Error: Expected drugs in search results, but got none")
            return False
        
        # Check if Paracetamol is in the results
        drug_names = [drug["name"] for drug in drugs]
        if "Paracetamol" not in drug_names:
            print(f"Error: Expected Paracetamol in search results, but got: {drug_names}")
            return False
        
        print(f"Drug search API correctly found Paracetamol")
        return True
    
    def test_drug_search_api_by_symptom(self) -> bool:
        """Test the drug search API by symptom"""
        response = requests.get(f"{self.base_url}/search?query=headache")
        
        if response.status_code != 200:
            print(f"Error: Failed to search drugs. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        drugs = response.json()
        
        if not drugs:
            print("Error: Expected drugs in search results, but got none")
            return False
        
        # Check if headache medications are in the results
        drug_names = [drug["name"] for drug in drugs]
        headache_meds = ["Paracetamol", "Ibuprofen", "Aspirin"]
        
        found_meds = [med for med in headache_meds if med in drug_names]
        if not found_meds:
            print(f"Error: Expected headache medications in search results, but got: {drug_names}")
            return False
        
        print(f"Drug search API correctly found headache medications: {', '.join(found_meds)}")
        return True
    
    def test_drug_listing_api(self) -> bool:
        """Test the drug listing API"""
        response = requests.get(f"{self.base_url}/drugs")
        
        if response.status_code != 200:
            print(f"Error: Failed to get drugs. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        drugs = response.json()
        
        if not drugs:
            print("Error: Expected drugs in listing, but got none")
            return False
        
        print(f"Drug listing API correctly returned {len(drugs)} drugs")
        return True
    
    def test_drug_listing_api_with_symptom_filter(self) -> bool:
        """Test the drug listing API with symptom filter"""
        response = requests.get(f"{self.base_url}/drugs?symptom=headache")
        
        if response.status_code != 200:
            print(f"Error: Failed to get drugs. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        drugs = response.json()
        
        if not drugs:
            print("Error: Expected drugs in filtered listing, but got none")
            return False
        
        # Check if all returned drugs have headache in their symptoms
        for drug in drugs:
            if "headache" not in [s.lower() for s in drug["symptoms"]]:
                print(f"Error: Drug {drug['name']} does not have headache in its symptoms")
                return False
        
        print(f"Drug listing API with symptom filter correctly returned {len(drugs)} drugs for headache")
        return True
    
    def test_drug_detail_api(self) -> bool:
        """Test the drug detail API"""
        # First get all drugs to find an ID
        response = requests.get(f"{self.base_url}/drugs")
        
        if response.status_code != 200:
            print(f"Error: Failed to get drugs. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        drugs = response.json()
        
        if not drugs:
            print("Error: Expected drugs in listing, but got none")
            return False
        
        # Get the first drug's ID
        drug_id = drugs[0]["id"]
        
        # Test the detail API
        response = requests.get(f"{self.base_url}/drugs/{drug_id}")
        
        if response.status_code != 200:
            print(f"Error: Failed to get drug detail. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        drug = response.json()
        
        if drug["id"] != drug_id:
            print(f"Error: Expected drug with ID {drug_id}, but got {drug['id']}")
            return False
        
        print(f"Drug detail API correctly returned details for {drug['name']}")
        return True
    
    def test_chat_history_api(self) -> bool:
        """Test the chat history API"""
        # First send a few chat messages
        messages = [
            "Hello",
            "I have a headache",
            "What is Paracetamol?"
        ]
        
        for message in messages:
            payload = {
                "session_id": self.session_id,
                "message": message
            }
            
            response = requests.post(f"{self.base_url}/chat", json=payload)
            
            if response.status_code != 200:
                print(f"Error: Failed to chat. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        
        # Now get the chat history
        response = requests.get(f"{self.base_url}/chat/history/{self.session_id}")
        
        if response.status_code != 200:
            print(f"Error: Failed to get chat history. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        history = response.json()
        
        if len(history) < len(messages):
            print(f"Error: Expected at least {len(messages)} messages in history, but got {len(history)}")
            return False
        
        # Check if all sent messages are in the history
        user_messages = [msg["user_message"] for msg in history]
        for message in messages:
            if message not in user_messages:
                print(f"Error: Message '{message}' not found in chat history")
                return False
        
        print(f"Chat history API correctly returned {len(history)} messages")
        return True
    
    def test_health_advice_system(self) -> bool:
        """Test the health advice system for different symptoms"""
        symptoms = {
            "fever": "I have a fever",
            "cough": "I've been coughing a lot",
            "diarrhea": "I have diarrhea",
            "allergies": "I have allergies and a runny nose"
        }
        
        success_count = 0
        for symptom, message in symptoms.items():
            payload = {
                "session_id": self.session_id,
                "message": message
            }
            
            response = requests.post(f"{self.base_url}/chat", json=payload)
            
            if response.status_code != 200:
                print(f"Error: Failed to chat. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                continue
            
            chat_response = response.json()
            
            # Print the response for debugging
            print(f"Response for '{message}': {chat_response['response'][:100]}...")
            
            # Check if response contains advice for the symptom or related terms
            symptom_terms = {
                "fever": ["fever", "temperature"],
                "cough": ["cough", "throat"],
                "diarrhea": ["diarrhea", "hydrated"],
                "allergies": ["allerg", "antihistamine", "loratadine", "cetirizine"]
            }
            
            terms = symptom_terms.get(symptom, [symptom])
            if any(term in chat_response["response"].lower() for term in terms):
                success_count += 1
                print(f"✓ Found advice for {symptom}")
            else:
                print(f"✗ Did not find advice for {symptom} in response")
        
        # Consider the test passed if at least 3 out of 4 symptoms get correct advice
        if success_count >= 3:
            print(f"Health advice system correctly provided advice for {success_count}/4 tested symptoms")
            return True
        else:
            print(f"Health advice system only provided correct advice for {success_count}/4 symptoms")
            return False
    
    def run_all_tests(self):
        """Run all tests and print a summary"""
        tests = [
            ("Database Initialization", self.test_database_initialization),
            ("Chat API - Symptom Detection", self.test_chat_api_symptom_detection),
            ("Chat API - Drug Information", self.test_chat_api_drug_info),
            ("Chat API - Greeting", self.test_chat_api_greeting),
            ("Drug Search API - By Name", self.test_drug_search_api_by_name),
            ("Drug Search API - By Symptom", self.test_drug_search_api_by_symptom),
            ("Drug Listing API", self.test_drug_listing_api),
            ("Drug Listing API - With Symptom Filter", self.test_drug_listing_api_with_symptom_filter),
            ("Drug Detail API", self.test_drug_detail_api),
            ("Chat History API", self.test_chat_history_api),
            ("Health Advice System", self.test_health_advice_system)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        self.print_summary()
    
    def print_summary(self):
        """Print a summary of the test results"""
        print("\n" + "="*80)
        print(f"TEST SUMMARY")
        print("="*80)
        print(f"Total tests: {self.test_results['total_tests']}")
        print(f"Passed tests: {self.test_results['passed_tests']}")
        print(f"Failed tests: {self.test_results['failed_tests']}")
        print("="*80)
        
        if self.test_results['failed_tests'] > 0:
            print("\nFAILED TESTS:")
            for test in self.test_results['test_details']:
                if test['status'] != 'PASSED':
                    print(f"- {test['name']}: {test['status']}")
                    if 'error' in test:
                        print(f"  Error: {test['error']}")
            print("="*80)
        
        return self.test_results['failed_tests'] == 0

if __name__ == "__main__":
    print(f"Testing backend API at: {BACKEND_URL}")
    tester = BackendTester(BACKEND_URL)
    tester.run_all_tests()
    
    # Exit with appropriate status code
    if tester.test_results['failed_tests'] == 0:
        sys.exit(0)
    else:
        sys.exit(1)