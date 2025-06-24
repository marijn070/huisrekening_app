from decimal import ROUND_DOWN, Decimal


def split_decimal(num: Decimal, n: int) -> list[Decimal]:
    quantize_exp = Decimal("1.00")  # fixed to 2 floating points

    base_part = (num / n).quantize(quantize_exp, rounding=ROUND_DOWN)
    parts = [base_part for _ in range(n)]

    remainder = num - sum(parts)

    i = 0
    while remainder > Decimal("0.00"):
        add = min(remainder, quantize_exp)
        parts[i] += add
        remainder -= add
        i += 1
    return parts


if __name__ == "__main__":
    print(split_decimal(Decimal("-150.01"), 3))
