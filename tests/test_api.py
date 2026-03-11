import pytest

@pytest.mark.asyncio
async def test_onboard_device(async_client):
    response = await async_client.post(
        "/devices/onboard",
        json={
            "hostname": "branch-5",
            "system_ip": "10.0.0.5",
            "site_id": "site-5",
            "status": "unconfigured"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["hostname"] == "branch-5"
    assert data["id"] is not None

@pytest.mark.asyncio
async def test_get_devices(async_client):
    await async_client.post(
        "/devices/onboard",
        json={"hostname": "branch-6", "system_ip": "10.0.0.6", "site_id": "site-6", "status": "unconfigured"}
    )
    response = await async_client.get("/devices")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(d["hostname"] == "branch-6" for d in data)

@pytest.mark.asyncio
async def test_deploy_device_config(async_client):
    # Setup
    device_res = await async_client.post(
        "/devices/onboard",
        json={"hostname": "branch-cf", "system_ip": "10.0.0.cf", "site_id": "cf", "status": "unconfigured"}
    )
    device_id = device_res.json()["id"]

    # Act
    res = await async_client.post(
        f"/devices/{device_id}/deploy-config",
        json={"config_group": "base-template"}
    )
    assert res.status_code == 200
    assert "successfully" in res.json()["message"]

@pytest.mark.asyncio
async def test_config_groups_api(async_client):
    res_create = await async_client.post("/config-groups", json={"name": "core-routers"})
    assert res_create.status_code == 200

    res_get = await async_client.get("/config-groups")
    assert any(g["name"] == "core-routers" for g in res_get.json())

    res_deploy = await async_client.post(
        "/config-groups/deploy", 
        json={"group_name": "core-routers", "devices": ["branch-6"]}
    )
    assert res_deploy.status_code == 200

@pytest.mark.asyncio
async def test_policies_api(async_client):
    res_create = await async_client.post("/policies", json={"name": "guest-wifi", "policy_type": "QoS"})
    assert res_create.status_code == 200

    res_deploy = await async_client.post(
        "/policies/deploy", 
        json={"policy_name": "guest-wifi", "devices": ["branch-6"]}
    )
    assert res_deploy.status_code == 200

@pytest.mark.asyncio
async def test_topology_api(async_client):
    res_create = await async_client.post("/topology", json={"name": "euro-mesh", "type": "mesh"})
    assert res_create.status_code == 200

    res_deploy = await async_client.post(
        "/topology/deploy", 
        json={"type": "mesh", "spokes": ["branch-6", "branch-5"]}
    )
    assert res_deploy.status_code == 200

@pytest.mark.asyncio
async def test_security_api(async_client):
    res_create = await async_client.post("/security/policy", json={"name": "edge-firewall", "type": "firewall"})
    assert res_create.status_code == 200

    res_deploy = await async_client.post(
        "/security/deploy", 
        json={"policy": "edge-firewall", "devices": ["branch-6"]}
    )
    assert res_deploy.status_code == 200
