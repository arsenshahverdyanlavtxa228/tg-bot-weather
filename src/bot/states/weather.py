from aiogram.fsm.state import State, StatesGroup


class FindCity(StatesGroup):
    query = State()
