# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Balancer Arbitrage Code

# ## Documentation

# The $r_k$ are the asset weight factors in the pool
# $$
# \forall r_{_{k}} \in \left \{ r_{_{1}}, r_{_{2}}, \cdots r_{_{n}} \right \}, \; r_{_{k}} > 0
# $$

# They are normalized to sum up to unity
# $$
# \sum_{k = 1} ^ {n} r_{_{k}} \equiv r_{_{1}} + r_{_{2}} \cdots + r_{_{n}} = 1
# $$

# The $x_l$ are the token balances in the pool, in native units
# $$
# \forall x_{_{k}} \in \left \{ x_{_{1}}, x_{_{2}}, \cdots x_{_{n}} \right \}, \; x_{_{k}} > 0
# $$

# **Equation 1 (Pool Invariant)**

# $$
# \prod_{k = 1}^{n} 
# x_{_{k}} ^ {r_{_{k}}}
# \equiv
# x_{_{1}} ^ {r_{_{1}}}
# x_{_{2}} ^ {r_{_{2}}}
# \cdots\
# x_{_{n}} ^ {r_{_{n}}}
# = \kappa
# = {constant}
# $$

# **Equation 2 (Isolation)**
# $$
# x_{_{i}} =
# \left(
# \kappa \prod_{\substack{ k = 1 \\ k \neq i}}^{n} x_{_{k}} ^ {- r_{_{k}} }
# \right) ^ { \frac{ 1 }{ r_{_{i}} }}
# $$

# **Equation 3 (Marginal Price)**
#
# Note: the $P_i$ are prices in any numeraire (they only ever appear as ratio so any numeraire factor will divide out)

# $$
# - \frac{ \partial x_{_{i}} } { \partial x_{_{j}} } 
# = \frac {P_i} {P_j}
# =
# \frac{ 
#         x_{_{i}} 
#     } 
#     {  
#         x_{_{j}} 
#     }
# \left(
# \frac{ r_{_{i}} } { r_{_{j}} } 
# \right) ^ { - 1 }
# = \frac{x_i\,r_j}{x_j\,r_i}
# $$

# **Equation 4 (Rebalancing)**

# $$
# x_i = 
# \kappa P_{_{i}} r_{_{i}} \prod_{k = 1} ^ {n} \left( P_{_{k}} r_{_{k}} \right) ^ {- r_{_{k}}}
# $$

# $$
# x_i = 
# \frac{\kappa P_{_{i}} r_{_{i}}}
# {\prod_{k = 1} ^ {n} \left( P_{_{k}} r_{_{k}} \right) ^ {r_{_{k}}}}
# $$

# If we define $\pi_i = P_i r_i$ the "weighted price i" then the above formula becomes
# $$
# x_i = 
# \frac{ \kappa \pi_i }
# {\prod_{k = 1} ^ {n} \pi_k ^ {r_{_{k}}}}
# $$

# We can also substitute $\kappa$ using the invariant equation and token balances
# $$
# x_i 
# = P_i r_i \prod_{k = 1} ^ {n} \left( \frac {x_k}{P_k r_k} \right)^{r_k}
# = P_i r_i \prod_{k = 1} ^ {n} \left( \frac {x_k}{P_k r_k} \right)^{r_k}
# $$

# We can also substitute $\kappa$ using the invariant equation and token balances
# $$
# x_i 
# = 
# P_i r_i \prod_{k = 1} ^ {n} \left( \frac {x_k}{P_k r_k} \right)^{r_k}
# =
# \pi_i \prod_{k = 1} ^ {n} \left( \frac {x_k}{\pi_k} \right)^{r_k}
# = 
# \frac 
# {P_i r_i  \prod_{k = 1} ^ {n} x_k{}^{r_k}}
# {\prod_{k = 1} ^ {n} (P_k r_k)^{r_k}} 
# = 
# \frac 
# {\pi_i  \prod_{k = 1} ^ {n} x_k{}^{r_k}}
# {\prod_{k = 1} ^ {n} \pi_k{}^{r_k}} 
# $$

# **Equation 5 (Delta x)**

# $$
# \forall \Delta{x_{_{k}}} \in \left \{ \Delta{x_{_{1}}}, \Delta{x_{_{2}}}, \cdots \Delta{x_{_{n}}} \right \}, \; \Delta{x_{_{k}}} > 0
# $$

# $$
# \Delta{x_{_{j}}}
# =
# x_{_{j}}
# \left( 
# 1 - 
# \left(
# \frac{ x_{_{i}} } { \left( x_{_{i}} + \Delta{x_{_{i}}} \right) }
# \right) ^ { \frac{ r_{i} } { r_{j} } }
# \right)
# $$
#

# $$
# \Delta{x_{_{i}}}
# =
# x_{_{i}} 
# \left( 
# \left(
# \frac{  x_{_{j}} } { \left( x_{_{j}} - \Delta{x_{_{j}}} \right) } 
# \right) ^ { \frac{ r_{j} } { r_{i} } }
# - 1
# \right)
# $$

# ## Code

from decimal import *
getcontext().prec = 100
from math import prod
from typing import List, Dict, Tuple
from tabulate import tabulate


class BalancerArbitrage:
    def __init__(
        self,
        x_: Dict[str, Decimal],
        r_: Dict[str, Decimal],
        P_: Dict[str, Decimal],
        ):
        self.ZERO = Decimal('0')
        self.ONE = Decimal('1')
        self.x_ = x_
        self.r_ = r_
        self.P_ = P_
        self.k, self.n = self.initialize_k_n()
        self.kappa = self.calculate_kappa()
        
    def isclose_decimal(
        self,
        num_1: Decimal, 
        num_2: Decimal, 
        rel_tol: Decimal = Decimal('1') / Decimal('2') ** Decimal('256')
        ) -> bool:
        return abs(num_1 - num_2) <= max(abs(num_1), abs(num_2)) * rel_tol
        
    def initialize_k_n(
        self
        ) -> Tuple[List[str], int]:
        assert all(val > self.ZERO for val in self.x_.values()), "Not all values in x_ are > 0"
        assert all(val > self.ZERO for val in self.r_.values()), "Not all values in r_ are > 0"
        assert all(val > self.ZERO for val in self.P_.values()), "Not all values in P_ are > 0"
        if self.x_.keys() == self.r_.keys() and self.r_.keys() == self.P_.keys():
            return list(self.x_.keys()), int(len(self.x_.keys()))
        else:
            raise ValueError("Keys of input dictionaries do not match.")
        
    def calculate_kappa(
        self
        ) -> Decimal:
        return prod(self.x_[k] ** self.r_[k] for k in self.k)
    
    def calculate_marginal_price(
        self,
        i: str,
        j: str
        ) -> Decimal:
        return (self.x_[i] / self.x_[j]) / (self.r_[i] / self.r_[j]) 
    
    def adjust_reserves_after_trade(
        self,
        i: str, # source
        j: str, # target
        Dx_i: Decimal, # source amount
        Dx_j: Decimal # target amount
        ) -> None:
        self.x_[i] += Dx_i
        self.x_[j] -= Dx_j
        return None
    
    def trade_by_source(
        self,
        i: str, # source
        j: str, # target
        Dx_i: Decimal, # source amount
        commit: bool = True
        ) -> Decimal:
        Dx_j = self.x_[j] * (self.ONE - (self.x_[i] / (self.x_[i] + Dx_i)) ** (self.r_[i] / self.r_[j]))
        assert self.x_[j] >= Dx_j, f"Insufficient {j} reserves to support this trade. Something is wrong."
        if commit:
            self.adjust_reserves_after_trade(i, j, Dx_i, Dx_j)
        return Dx_j
    
    def trade_by_target(
        self,
        i: str, # source
        j: str, # target
        Dx_j: Decimal, # target amount
        commit: bool = True
        ) -> Decimal:
        Dx_i = self.x_[i] * ((self.x_[j] / (self.x_[j] - Dx_j)) ** (self.r_[j] / self.r_[i]) - self.ONE)
        assert self.x_[j] >= Dx_j, f"Insufficient {j} reserves to support this trade. Something is wrong."
        if commit:
            self.adjust_reserves_after_trade(i, j, Dx_i, Dx_j)
        return Dx_i
    
    def calculate_balanced_coordinate(
        self, 
        i: str
        ) -> Decimal:
        return self.kappa * self.P_[i] * self.r_[i] * prod((self.P_[k] * self.r_[k]) ** (- self.r_[k]) for k in self.k)
    
    def determine_balanced_pool_state(
        self
        ) -> Dict[str, Decimal]:
        return {i: self.calculate_balanced_coordinate(i) for i in self.k}
    
    def get_rebalance_trade_sets(
        self,
        balanced_coordinates_: Dict[str, Decimal]
        ) -> Tuple[Dict[str, Decimal], Dict[str, Decimal]]:
        target_x_ = {}
        source_x_ = {}
        for k in self.k:
            difference = balanced_coordinates_[k] - self.x_[k]
            if difference < 0:
                target_x_[k] = abs(difference)
            elif difference > 0:
                source_x_[k] = abs(difference)
        return (target_x_, source_x_)
    
    def get_largest_value_from_trade_set(
        self,
        trade_set: Dict[str, Decimal]
        ) -> Tuple[str, Decimal]:
        return max(trade_set.items(), key=lambda x: x[1])
    
    def find_rebalancing_path(
        self,
        target_x_: Tuple[str, Decimal], 
        source_x_: Tuple[str, Decimal]
        ) -> Tuple[Dict[str, Decimal], Dict[str, Decimal]]:
        target_id, target_amount = self.get_largest_value_from_trade_set(target_x_)
        source_id, source_amount = self.get_largest_value_from_trade_set(source_x_)
        try:
            target_amount = self.trade_by_source(source_id, target_id, source_amount)
            message = f"Swap {source_amount:.18f} x_{source_id} for {target_amount:.18f} x_{target_id}"
        except AssertionError:
            source_amount = self.trade_by_target(source_id, target_id, target_amount)
            message = f"Swap {source_amount:.18f} x_{source_id} for {target_amount:.18f} x_{target_id}"
        return message
    
    def rebalance_pool(
        self
        ):
        rebalance_instructions = []
        balanced_coordinates_ = self.determine_balanced_pool_state()
        target_x_, source_x_ = self.get_rebalance_trade_sets(balanced_coordinates_)
        while any(not self.isclose_decimal(v, self.ZERO) for v in target_x_.values()):
            rebalance_instructions.append(self.find_rebalancing_path(target_x_, source_x_))
            target_x_, source_x_ = self.get_rebalance_trade_sets(balanced_coordinates_)
            if len(target_x_) == 0 or len(source_x_) == 0:
                break
        return rebalance_instructions
    
    def update_oracle_prices(
        self,
        updated_P_: Dict[str, Decimal]
        ) -> None:
        assert all(val > self.ZERO for val in updated_P_.values()), "Not all values in P_ are > 0"
        if self.P_.keys() == updated_P_.keys():
            self.P_ = updated_P_
        else:
            raise ValueError("Keys do not match. Are these the correct oracle prices?.")
    
    def initialize_k_n(
        self
        ) -> Tuple[List[str], int]:
        assert all(val > self.ZERO for val in self.x_.values()), "Not all values in x_ are > 0"
        assert all(val > self.ZERO for val in self.r_.values()), "Not all values in r_ are > 0"
        
        if self.x_.keys() == self.r_.keys() and self.r_.keys() == self.P_.keys():
            return list(self.x_.keys()), int(len(self.x_.keys()))
    
    def state_printer(
        self
        ) -> None:
        data1 = [[k, 
                  f"{self.x_[k]:.18f}", 
                  f"{self.r_[k]:.18f}", 
                  f"${1/self.P_[k]:.2f}" # inverse of P_ for Oracle price
                 ] for k in self.k]
        data2 = [[i] + [f"{self.calculate_marginal_price(i, j):.18f}" for j in self.k] for i in self.k]
        print("Table 1: Reserves, Ratios, and Oracle Prices\n")
        print(tabulate(data1, 
                       headers=["token", "Reserve balance", "Reserve ratio", "Oracle price"],
                       tablefmt="pretty"))
        print("\n")
        print("Table 2: Exchange Rates\n")
        print(tabulate(data2, 
                       headers=[""] + self.k, 
                       tablefmt="pretty"))
        return(None)


# +
x_ = {'a' : Decimal('100'), 'b' : Decimal('75'), 'c' : Decimal('16') + Decimal('2')/Decimal('3'), 'd' : Decimal('18.75'), 'e' : Decimal('25')}
r_ = {'a' : Decimal('0.2'), 'b' : Decimal('0.3'), 'c' : Decimal('0.1'), 'd' : Decimal('0.15'), 'e' : Decimal('0.25')}
P_ = {'a' : Decimal('1')/Decimal('1.4'), 'b' : Decimal('1')/Decimal('2.55'), 'c' : Decimal('1')/Decimal('3'), 'd' : Decimal('1')/Decimal('4'), 'e' : Decimal('1')/Decimal('5')}

pool = BalancerArbitrage(x_, r_, P_)
# -

pool.state_printer()

pool.rebalance_pool()

pool.state_printer()

updated_P_ = {'a' : Decimal('1'), 'b' : Decimal('1'), 'c' : Decimal('1'), 'd' : Decimal('1'), 'e' : Decimal('1')}
pool.update_oracle_prices(updated_P_)
pool.state_printer()

pool.rebalance_pool()

pool.state_printer()


