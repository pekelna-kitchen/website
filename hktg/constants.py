
from enum import Enum


class State(Enum):
    CHOOSING_ACTION = 1
    CHOOSING_LOCATION = 2
    CHOOSING_PRODUCT = 3
    ENTERING_AMOUNT = 4
    ENTERING_LOCATION = 5
    ENTERING_PRODUCT = 6
    FILTERED_VIEW = 7
    CHOOSING_CONTAINER = 8
    ENTERING_CONTAINER_SYMBOL = 9
    ENTERING_CONTAINER_DESCRIPTION = 10
    VIEWING_ENTRY = 11


class Action(Enum):
    HOME = 1
    FILTER = 2
    CREATE = 3
    DELETE = 4
    MODIFY = 5
    VIEW_ENTRY = 6
    VIEW_AMOUNT = 7
    EXIT = 8
    BACK = 9

ActionDescriptions = {
    Action.HOME: "🏠 Додому",
    Action.FILTER: "🔍 Шукати",
    Action.CREATE: "➕ Додати",
    Action.DELETE: "➖ Видалити",
    Action.MODIFY: "🖊️ Змінити",
    Action.VIEW_ENTRY: "🖊️ Змінити",
    Action.VIEW_AMOUNT: "🖊️ Змінити",
    Action.EXIT: "🚪 Вийти",
    Action.BACK: "< Назад",
}

class UserDataKey(Enum):
    ACTION = 1
    PRODUCT = 2
    LOCATION = 3
    CONTAINER = 4
    AMOUNT = 5
    CONTAINER_SYMBOL = 6
    FIELD_TYPE = 7
    LIMIT = 8
    CURRENT_ID = 9
