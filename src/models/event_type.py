from enum import Enum


class EventType(str, Enum):
    Eat = 'Eat'
    Pee = 'Pee'
    Poo = 'Poo'
    FishOil = 'Fish oil'
    VitaminB = 'Vitamin B'
    BrushTeeth = 'Brush teeth'

    @staticmethod
    def has_value(item):
        return item in [v.value for v in EventType.__members__.values()]
