from typing import List
from service.observer import Observer


class Subject:
    def __init__(self):
        self.__observers: List[Observer] = []

    def addObserver(self, observer: Observer) -> None:
        self.__observers.append(observer)

    def _notify(self) -> None:
        [observer.update() for observer in self.__observers]
