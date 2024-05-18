from typing_extensions import Self


class CA:
    _t: Self | None = None

    def __new__(cls, *args, **kwargs) -> Self:
        print("new")
        if cls._t:
            return cls._t
        obj = super().__new__(cls)
        cls._t = obj
        return obj

    def __init__(self, p: int) -> None:
        print("init")
        self.p = 1


a = CA(10)

b = CA(20)

if a is b:
    print("10")


class Singleton:
    _instance = None  # 用于存储单例实例

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # 如果没有实例存在，创建一个新实例
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, value):
        # 初始化方法在对象创建时总是被调用
        self.value = value


# 使用示例
if __name__ == "__main__":
    singleton1 = Singleton(10)
    print(f"Singleton1 value: {singleton1.value}")  # Output: 10

    singleton2 = Singleton(20)
    print(f"Singleton2 value: {singleton2.value}")  # Output: 10

    print(f"singleton1 is singleton2: {singleton1 is singleton2}")  # Output: True
    print(
        f"singleton1 id: {id(singleton1)}, singleton2 id: {id(singleton2)}"
    )  # IDs will be the same
