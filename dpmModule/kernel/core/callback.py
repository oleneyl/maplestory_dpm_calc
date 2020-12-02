from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .graph_element import GraphElement, Task
    from .result_object import ResultObject

class Callback:
    def __init__(self, task: Task, time: float) -> None:
        self.task: Task = task
        self.time: float = time

    def resolve(self) -> ResultObject:
        return self.task.do()

    def adjust_by_current_time(self, current_time: float) -> Callback:
        return Callback(self.task, self.time + current_time)

    @staticmethod
    def from_graph_element(graph_element: GraphElement, time: float) -> Callback:
        return Callback(graph_element.build_task(None), time)
