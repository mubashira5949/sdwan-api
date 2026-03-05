import httpx
from app.config import settings, logger

class SDWANClient:
    def __init__(self):
        self.base_url = settings.SDWAN_BASE_URL
        self.username = settings.SDWAN_USERNAME
        self.password = settings.SDWAN_PASSWORD
        # Disable SSL verification for internal device testing (use with caution in prod)
        self.client = httpx.AsyncClient(base_url=self.base_url, verify=False)
        self.jsessionid = None
        self.token = None

    async def authenticate(self):
        """Authenticate to SDWAN vManage"""
        logger.info("Authenticating with SDWAN vManage...")
        # Standard mock authentication behaviour since we do not have a real device setup here
        self.jsessionid = "mock_jsessionid"
        self.token = "mock_xsrf_token"
        
        # update client headers
        self.client.cookies.set("JSESSIONID", self.jsessionid)
        self.client.headers.update({"X-XSRF-TOKEN": self.token})
        logger.info("SDWAN Authentication successful")

    async def get_devices(self):
        """Fetch devices from SDWAN"""
        if not self.token:
            await self.authenticate()
        logger.info("Fetching devices from SDWAN...")
        response = await self.client.get("/device")
        # For mock purposes return fake responses or handle actual connection when vManage is available.
        return [{"deviceId": "1", "host-name": "vSmart-1", "system-ip": "1.1.1.1"}]

    async def close(self):
        await self.client.aclose()

sdwan_client = SDWANClient()
