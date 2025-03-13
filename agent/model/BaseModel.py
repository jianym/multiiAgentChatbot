class BaseModel:
    async def acall(self, messages: str) -> str:
        pass

    def call(self, messages: str) -> str:
        pass