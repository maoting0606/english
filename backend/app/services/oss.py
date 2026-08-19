from datetime import datetime
from app.core.config import settings

class OssService:
    def object_key(self, prefix: str, filename: str, user_id: int = 1) -> str:
        now = datetime.utcnow()
        return f"{prefix}/{now:%Y}/{now:%m}/{user_id}/{filename}"

    def signed_placeholder(self, object_key: str, action: str = "download", expire: int = 300) -> dict:
        return {"object_key": object_key, "upload_url" if action == "upload" else "download_url": f"oss://{settings.oss_bucket}/{object_key}?expire={expire}", "expire": expire}

oss_service = OssService()
