import app as flask_app
import unittest

class HeartGuardTestCase(unittest.TestCase):
    def setUp(self):
        flask_app.app.testing = True
        self.client = flask_app.app.test_client()

    def test_routes(self):
        routes = ['/', '/about', '/technologies', '/contact', '/chatbot', '/login', '/signup']
        for route in routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200, f"Failed on route {route}")
            print(f"[OK] GET {route} -> HTTP 200 OK")

    def test_prediction_api(self):
        payload = {
            "age": 58,
            "sex": 1,
            "cp": 2,
            "trestbps": 140,
            "chol": 260,
            "fbs": 1,
            "restecg": 1,
            "thalach": 125,
            "exang": 1,
            "oldpeak": 2.5,
            "slope": 1,
            "ca": 2,
            "thal": 3,
            "patient_name": "Test Patient"
        }
        res = self.client.post('/api/predict', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('risk_percentage', data)
        self.assertIn('risk_level', data)
        print(f"[OK] POST /api/predict -> Risk: {data['risk_percentage']}% ({data['risk_level']})")

    def test_chatbot_api(self):
        res = self.client.post('/api/chat', json={"message": "what are heart attack warning signs?"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("heart attack", data['response'].lower())
        print("[OK] POST /api/chat -> Ollama 3.2:3b Medical AI answered correctly")

if __name__ == '__main__':
    unittest.main()
