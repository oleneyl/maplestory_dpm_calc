from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Final, List, Optional

from ..graph import DynamicVariableOperation
from .modifier import CharacterModifier

if TYPE_CHECKING:
    from .callback import Callback
    from .graph_element import Task


class ResultObject:
    def __init__(self, delay: float, mdf: CharacterModifier, damage: float, hit: float, sname: str, spec: str,
                 kwargs={}, cascade=[], callbacks: List[Callback] = []) -> None:
        """Result object must be static; alway to be ensure it is revealed.
        """
        self.delay: float = DynamicVariableOperation.reveal_argument(delay)
        self.damage: float = DynamicVariableOperation.reveal_argument(damage)
        self.hit: float = DynamicVariableOperation.reveal_argument(hit)
        self.mdf: CharacterModifier = DynamicVariableOperation.reveal_argument(mdf)
        self.sname: str = DynamicVariableOperation.reveal_argument(sname)
        self.spec: str = DynamicVariableOperation.reveal_argument(spec)  # buff, deal, summon
        self.kwargs: Dict[Any, Any] = DynamicVariableOperation.reveal_argument(kwargs)
        self.cascade: List[Task] = DynamicVariableOperation.reveal_argument(cascade)
        self.callbacks: List[Callback] = callbacks
        self.time: Optional[float] = None

    def setTime(self, time: float) -> None:
        self.time = time


'''Default Values. Forbidden to editting.
'''
taskTerminater: Final = ResultObject(0, CharacterModifier(), 0, 0, sname='terminator', spec='graph control')
