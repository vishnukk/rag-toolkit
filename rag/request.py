from pydantic import BaseModel


class RequestBody(BaseModel):
    question: str
    rerank: bool = False
    web_search: bool = False
    from_window : bool = False
