from pydantic import BaseModel
from typing import Optional, List
from abc import ABC

class APIResponse(BaseModel, ABC):
    """
    Tüm response modellerinin miras aldığı soyut (abstract) ana response modelidir.
    Doğrudan örneklenemez, sadece alt sınıflar tarafından kullanılabilir.
    Ortak alanlar: success, message, timestamp.
    Her spesifik response modeli bu sınıftan türetilir ve kendi data alanını ekler.
    """
    success: bool                  # İstek başarılı mı?
    message: Optional[str] = None  # Hata veya bilgi mesajı (opsiyonel)
    timestamp: Optional[int] = None # Yanıt zamanı, milisaniye cinsinden (Unix epoch)

    def __init__(self, *args, **kwargs):
        if type(self) is APIResponse:
            raise TypeError("APIResponse doğrudan örneklenemez, sadece alt sınıflar tarafından kullanılabilir.")
        super().__init__(*args, **kwargs)