import httpx
import asyncio
from typing import Dict, Any, Optional
from app.config import settings


class AgentClient:
    def __init__(self, timeout: int = None):
        self.timeout = timeout or settings.agent_timeout
        self.verify_ssl = settings.agent_verify_ssl

    async def start_instance(self, agent_url: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a PX4 instance on an agent"""
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{agent_url}/agent/start",
                    json=request_data
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise Exception(f"Failed to communicate with agent: {e}")
            except httpx.HTTPStatusError as e:
                raise Exception(f"Agent returned error {e.response.status_code}: {e.response.text}")

    async def stop_instance(self, agent_url: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stop a PX4 instance on an agent"""
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{agent_url}/agent/stop",
                    json=request_data
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise Exception(f"Failed to communicate with agent: {e}")
            except httpx.HTTPStatusError as e:
                raise Exception(f"Agent returned error {e.response.status_code}: {e.response.text}")

    async def get_status(self, agent_url: str) -> Dict[str, Any]:
        """Get status from an agent"""
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
            try:
                response = await client.get(f"{agent_url}/agent/status")
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise Exception(f"Failed to communicate with agent: {e}")
            except httpx.HTTPStatusError as e:
                raise Exception(f"Agent returned error {e.response.status_code}: {e.response.text}")

    async def health_check(self, agent_url: str) -> bool:
        """Check if agent is healthy"""
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=5) as client:
            try:
                response = await client.get(f"{agent_url}/health")
                return response.status_code == 200
            except:
                return False


# Global agent client instance
agent_client = AgentClient()
