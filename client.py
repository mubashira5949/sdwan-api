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

    async def deploy_config(self, system_ip: str, config_group: str):
        logger.info(f"Simulating SDWAN template API call to deploy {config_group} to device {system_ip}")
        # Example pseudo-code (assuming API uses the system_ip or device ID to assign the template):
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         f"{self.base_url}/dataservice/template/device/config/attachFeatureDeviceTemplate",
        #         json={"deviceIP": system_ip, "templateName": config_group}
        #     )
        #     response.raise_for_status()
        
        return {"status": "success", "message": f"Config {config_group} deployed to {system_ip}"}

    async def get_config(self, system_ip: str):
        logger.info(f"Simulating SDWAN fetch for current config of {system_ip}")
        return {
            "system_ip": system_ip,
            "running_config": f"hostname Router-{system_ip}\n!\ninterface GigabitEthernet0/0/0\n ip address dhcp\n!"
        }

    async def deploy_group_config(self, group_name: str, devices: list[str]):
        logger.info(f"Simulating SDWAN template API call to deploy group {group_name} to devices: {devices}")
        # Example pseudo-code for multiple devices:
        # device_list = [{"deviceIP": ip} for ip in devices]
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         f"{self.base_url}/dataservice/template/device/config/attachFeatureDeviceTemplate",
        #         json={"deviceTemplateList": [{"templateName": group_name, "device": device_list}]}
        #     )
        #     response.raise_for_status()
        
        return {"status": "success", "message": f"Config group {group_name} deployment initiated for {len(devices)} devices."}

    async def deploy_policy(self, policy_name: str, devices: list[str]):
        logger.info(f"Simulating SDWAN Policy API call to deploy policy {policy_name} to devices: {devices}")
        # Example pseudo-code for policy assignment (Centralized Policy execution):
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         f"{self.base_url}/dataservice/template/policy/vsmart/activate/{policy_id}",
        #         json={"isEdited": True} 
        #     )
        #     response.raise_for_status()
        
        return {"status": "success", "message": f"Policy {policy_name} deployment initiated targeting {len(devices)} devices."}

    async def deploy_topology(self, topology_type: str, hub: str | None, spokes: list[str]):
        logger.info(f"Simulating SDWAN Topology API linking {topology_type} - Hub: {hub} to Spokes: {spokes}")
        # Example pseudo-code (Pushing vSmart central control policies that bind sites/system IPs):
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         f"{self.base_url}/dataservice/template/policy/custom/topology",
        #         json={"topologyType": topology_type, "hub_router": hub, "spoke_routers": spokes} 
        #     )
        #     response.raise_for_status()
        
        return {"status": "success", "message": f"{topology_type.capitalize()} deployed successfully connecting {len(spokes)} spokes."}
