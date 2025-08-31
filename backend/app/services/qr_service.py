import qrcode
import base64
import json
from io import BytesIO
from typing import Dict, Any

class QRCodeService:
    def __init__(self):
        self.qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

    def generate_qr_code(self, data: str) -> str:
        """
        Generate QR code from data and return as base64 string
        """
        try:
            # Add data to QR code
            self.qr.add_data(data)
            self.qr.make(fit=True)
            
            # Create QR code image
            img = self.qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            # Clear QR code for next use
            self.qr.clear()
            
            return img_str
            
        except Exception as e:
            raise Exception(f"QR code generation failed: {str(e)}")

    def generate_credential_qr(self, credential_data: Dict[str, Any]) -> str:
        """
        Generate QR code for credential verification
        """
        qr_data = {
            "type": "credential_verification",
            "credential_id": credential_data["id"],
            "document_hash": credential_data["document_hash"],
            "verification_url": credential_data["verification_url"],
            "timestamp": credential_data.get("timestamp")
        }
        
        return self.generate_qr_code(json.dumps(qr_data))

    def generate_document_qr(self, document_data: Dict[str, Any]) -> str:
        """
        Generate QR code for document verification
        """
        qr_data = {
            "type": "document_verification",
            "document_id": document_data["id"],
            "document_hash": document_data["file_hash"],
            "verification_url": document_data["verification_url"],
            "timestamp": document_data.get("timestamp")
        }
        
        return self.generate_qr_code(json.dumps(qr_data))

    def decode_qr_code(self, qr_image_base64: str) -> Dict[str, Any]:
        """
        Decode QR code from base64 image
        """
        try:
            # This would require additional libraries like pyzbar for decoding
            # For now, return a placeholder
            return {
                "type": "credential_verification",
                "credential_id": "sample_id",
                "document_hash": "sample_hash",
                "verification_url": "sample_url"
            }
        except Exception as e:
            raise Exception(f"QR code decoding failed: {str(e)}")
