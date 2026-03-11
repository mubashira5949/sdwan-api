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
