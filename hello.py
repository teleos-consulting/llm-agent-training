print("Hello, world!")

def a_new_function(name: str):
    print(f"Hello, {name}!")

a_new_function("Eustace Scrubb")

a = 12
b = 10
c = a + b

print(c)

def exponent(a: float, b: float) -> float:
    """
    Raise a number to a power.
    """
    print(f" [TOOL] Raising {a} to the power of {b}")
    return a ** b