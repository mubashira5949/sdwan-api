import httpx
from logger import logger

class SDWANClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.auth = (username, password)

    async def login(self):
        logger.info(f"Logging into SDWAN at {self.base_url}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/j_security_check",
                data={
                    "j_username": self.auth[0],
                    "j_password": self.auth[1]
                }
            )
            return response.cookies

    async def add_device(self, device):
        # type hint `device` as `schemas.DeviceCreate` depending on your import approach
        logger.info(f"Simulating SDWAN call to add device: {device.hostname}")
        # Here we would typically make a POST request with the new device info.
        # Example pseudo-code (assuming API takes JSON payload matching device attributes):
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(f"{self.base_url}/api/v1/device", json=device.model_dump())
        #     response.raise_for_status()
        #     return response.json()
        
        # Simulating successful internal SDWAN response
        return {"status": "success", "message": f"Successfully added {device.hostname} to SDWAN"}
