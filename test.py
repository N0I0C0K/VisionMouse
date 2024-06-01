# from controllers.flows.flow import start_flow


# while True:
#     start_flow()

import pydantic


class Mod(pydantic.BaseModel):
    dfsdf: str


class MouseStateModel(pydantic.BaseModel):
    baseSpeed: float
    acceleration: float
    p: list[Mod]


model = MouseStateModel(baseSpeed=1.1, acceleration=1.1, p=[Mod(dfsdf="1212")])

print(model.model_dump())
