import httpx
from typing import Optional

ANALYTICS_URL = "http://localhost:3003"

class AnalyticsClient:
    
    @staticmethod
    async def get_user_cluster(user_id: int) -> Optional[str]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{ANALYTICS_URL}/clustering/users/{user_id}/cluster",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    cluster_name = data.get('cluster_name')
                    confidence = data.get('confidence', 0)
                    
                    print(f"\n[ANALYTICS] Usuario {user_id}: {cluster_name} (confianza: {confidence:.2f})")
                    
                    return cluster_name
                elif response.status_code == 404:
                    print(f"\n[ANALYTICS] Usuario {user_id}: sin datos suficientes")
                    return None
                else:
                    print(f"\n[ANALYTICS] Error {response.status_code}")
                    return None
                    
        except httpx.TimeoutException:
            print(f"\n[ANALYTICS] Timeout consultando cluster para usuario {user_id}")
            return None
        except Exception as e:
            print(f"\n[ANALYTICS] Error: {e}")
            return None