import base64

AARUSH_BASE_URL = "https://backend.aarushdiam.com/api/inventory/66900bb094a26f"
AARUSH_USERNAME = "api_user_purple_carats@aarushdiam.com"
AARUSH_PASSWORD = "Nhf@3@1#894g"

def build_basic_auth_header(username: str, password: str):
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def normalize_color(raw: str):
    if not raw:
        return None
    val = str(raw).strip().upper()
    allowed = ['D', 'E', 'F', 'G', 'H', 'I', 'J']
    return val if val in allowed else None


def normalize_clarity(raw: str):
    if not raw:
        return None
    val = str(raw).strip().upper()
    mapping = {
        'VVS1':'VVS1','VVS2':'VVS2','VS1':'VS1','VS2':'VS2',
        'SI1':'SI1','SI2':'SI2','I1':'I1','I2':'I2','I3':'I3',
        'IF':'IF','FL':'FL'
    }
    return mapping.get(val)
