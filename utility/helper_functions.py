from fastapi import HTTPException
from fastapi.responses import JSONResponse

class Utility:
    
    @staticmethod
    def check_required_keys(data: dict, required_keys: list):
        missing_keys = [key for key in required_keys if key not in data]
        empty_keys = [key for key in required_keys if not data.get(key)]
        if missing_keys or empty_keys:
            raise HTTPException(status_code=400, detail="missing or empty keys")
            