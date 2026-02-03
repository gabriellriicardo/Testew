import requests
import uuid
import time

class PaymentManager:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.mercadopago.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def create_pix_payment(self, amount, description, payer_email="cliente@boletim.com"):
        url = f"{self.base_url}/payments"
        
        # Idempotency for safety (prevents double charge on retry)
        self.headers["X-Idempotency-Key"] = str(uuid.uuid4())
        
        payload = {
            "transaction_amount": float(amount),
            "description": description,
            "payment_method_id": "pix",
            "payer": {
                "email": payer_email,
                "first_name": "Doador",
                "last_name": "AlfaVision"
            },
            "installments": 1
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Extract necessary info
            payment_id = data.get('id')
            poi = data.get('point_of_interaction', {}).get('transaction_data', {})
            
            qr_code = poi.get('qr_code') # Copia e Cola
            qr_code_base64 = poi.get('qr_code_base64') # Imagem em base64
            ticket_url = poi.get('ticket_url') # Link externo
            
            return {
                "id": payment_id,
                "qr_code": qr_code,
                "qr_code_base64": qr_code_base64,
                "ticket_url": ticket_url,
                "status": data.get('status')
            }
        except Exception as e:
            print(f"❌ Erro Mercado Pago (Create): {e}")
            if 'response' in locals() and response is not None:
                print(f"Detalhes: {response.text}")
            return None

    def get_payment_status(self, payment_id):
        url = f"{self.base_url}/payments/{payment_id}"
        
        # Remove idempotency key for GET requests
        headers = self.headers.copy()
        if "X-Idempotency-Key" in headers:
            del headers["X-Idempotency-Key"]
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('status')
            return None
        except Exception as e:
            print(f"❌ Erro Mercado Pago (Status): {e}")
            return None
