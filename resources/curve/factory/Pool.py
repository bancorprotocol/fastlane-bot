from .Contract import Contract
from .Host import Host

PRECISION: int = 10 ** 18
FEE_DENOM: int = 10 ** 10

abi = [
    {"name":"fee","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"},
    {"name":"initial_A","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"},
    {"name":"future_A","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"},
    {"name":"initial_A_time","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"},
    {"name":"future_A_time","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"},
    {"name":"get_dy","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"int128","name":""},{"type":"int128","name":""},{"type":"uint256","name":""}],"stateMutability":"view","type":"function"}
]

class Pool(Contract):
    def __init__(self, address: str, abi_ex: list[dict]):
        super().__init__(address, abi + abi_ex)
        self.fee = self.contract.functions.fee().call()
        self.initial_A = self.contract.functions.initial_A().call()
        self.future_A = self.contract.functions.future_A().call()
        self.initial_A_time = self.contract.functions.initial_A_time().call()
        self.future_A_time = self.contract.functions.future_A_time().call()
        self.timestamp = Host.web3.eth.get_block('latest')['timestamp']

    def swap_read(self, sourceToken: str, targetToken: str, sourceAmount: int) -> int:
        indexes = {self.coins[n].symbol: n for n in range(len(self.coins))}
        return self.contract.functions.get_dy(indexes[sourceToken], indexes[targetToken], sourceAmount).call()

    def swap_calc(self, sourceToken: str, targetToken: str, sourceAmount: int) -> int:
        indexes = {self.coins[n].symbol: n for n in range(len(self.coins))}
        return self._get_dy(indexes[sourceToken], indexes[targetToken], sourceAmount)

    def _get_dy(self, i: int, j: int, dx: int) -> int:
        balances: list[int] = self._get_balances()
        factors: list[int] = self._get_factors(PRECISION)
        rates: list[int] = self._get_rates([PRECISION // 10 ** coin.decimals * factor for coin, factor in zip(self.coins, factors)])
        xp: list[int] = [balance * rate // PRECISION for balance, rate in zip(balances, rates)]
        x: int = xp[i] + dx * rates[i] // PRECISION
        y: int = self._get_y(xp, i, j, x)
        dy: int = (xp[j] - y - self.Y_FLAG) * PRECISION ** self.P_FLAG // rates[j] ** self.P_FLAG
        fee: int = self._get_fee(xp, i, j, x, y, dy)
        return (dy - fee) * PRECISION ** (1 - self.P_FLAG) // rates[j] ** (1 - self.P_FLAG)

    def _get_y(self, xp: list[int], i: int, j: int, x: int) -> int:
        amp: int = self._get_A()
        Ann: int = amp * len(xp)
        D: int = self._get_D(xp, amp)
        c: int = D
        S: int = 0
        for n in [k for k in range(len(xp)) if k != j]:
            s: int = xp[n] if n != i else x
            S += s
            c = c * D // (s * len(xp))
        c = c * D * self.A_PREC // (Ann * len(xp))
        b: int = S + D * self.A_PREC // Ann
        y: int = D
        for _ in range(255):
            y_prev: int = y
            y = (y * y + c) // (2 * y + b - D)
            if abs(y - y_prev) <= 1:
                break
        return y

    def _get_A(self) -> int:
        t1: int = self.future_A_time
        A1: int = self.future_A
        if self.timestamp < t1:
            A0: int = self.initial_A
            t0: int = self.initial_A_time
            if A1 > A0:
                return A0 + (A1 - A0) * (self.timestamp - t0) // (t1 - t0)
            else:
                return A0 - (A0 - A1) * (self.timestamp - t0) // (t1 - t0)
        else:
            return A1

    def _get_D(self, xp: list[int], amp: int) -> int:
        S: int = sum(xp)
        if S > 0:
            D: int = S
            Ann: int = amp * len(xp)
            for _ in range(255):
                D_P: int = D
                for x in xp:
                    D_P = D_P * D // (x * len(xp) + self.D_FLAG)
                Dprev: int = D
                D = (Ann * S // self.A_PREC + D_P * len(xp)) * D // ((Ann - self.A_PREC) * D // self.A_PREC + D_P * (len(xp) + 1))
                if abs(D - Dprev) <= 1:
                    break
            return D
        return 0

    def _get_fee(self, xp: list[int], i: int, j: int, x: int, y: int, dy: int) -> int:
        fee: int = self.fee
        fee_mul: int = self._get_fee_mul()
        if fee_mul > FEE_DENOM:
            xpi: int = (xp[i] + x) // 2
            xpj: int = (xp[j] + y) // 2
            fee = fee * fee_mul // ((fee_mul - FEE_DENOM) * xpi * xpj * 4 // (xpi + xpj) ** 2 + FEE_DENOM)
        return fee * dy // FEE_DENOM

    def _get_rates(self, values: list[int]) -> list[int]:
        return values

    def _get_factors(self, default: int) -> list[int]:
        return [default] * len(self.coins)

    def _get_balances(self) -> list[int]:
        return self.balances

    def _get_fee_mul(self) -> int:
        return 0
