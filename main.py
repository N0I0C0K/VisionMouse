from filter import SlidingWindowMeanFilter

a = SlidingWindowMeanFilter()
print(a.push((10, 10)))
print(a.data)
print(a.push((0, 0)))
print(a.data)
print(a.push((0, 100)))
print(a.data)
