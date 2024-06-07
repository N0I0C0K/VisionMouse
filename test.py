from controllers.flows.flow import start_flow


while True:
    start_flow()

# import pydantic


# class Mod(pydantic.BaseModel):
#     dfsdf: str


# class MouseStateModel(pydantic.BaseModel):
#     baseSpeed: float
#     acceleration: float
#     p: list[Mod]


# model = MouseStateModel(baseSpeed=1.1, acceleration=1.1, p=[Mod(dfsdf="1212")])

# print(model.model_dump())

# print("验证第 299 张, 验证结果: Open_Palm 样本: Open_Palm")
# print("验证第 300 张, 验证结果: One 样本: One")
# print("一共验证 300 张，错误数量：8，正确率: 0.9733333333")
