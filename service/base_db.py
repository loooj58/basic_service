from abc import ABC, abstractmethod
from typing import List, Dict, Any

Record = Dict[str, Any]
SubTable = List[Record]

class BaseDB(ABC):
    @abstractmethod
    async def insert_data(
        self,
        table_name: str,
        records: SubTable
    ) -> None:
        pass

    @abstractmethod
    async def get_data(
        self,
        table_name: str,
        offset: int,
        limit: int
    ) -> SubTable:
        pass

    @abstractmethod
    async def update_data(
        self,
        table_name: str,
        conditions: SubTable,
        values: SubTable
    ) -> None:
        pass

    @abstractmethod
    async def get_item(
        self,
        table_name: str,
        id: int
    ) -> Record:
        pass
