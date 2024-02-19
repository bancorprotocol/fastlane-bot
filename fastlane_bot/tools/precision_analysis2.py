# %%
from decimal import *
getcontext().prec = 100
from typing import List, Dict, Tuple, Callable, TypeVar, Any, Union
from tabulate import tabulate

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib.font_manager as font_manager
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import MaxNLocator

GT_America_Mono_Regular = font_manager.FontProperties(fname='fonts/GT-America-Mono-Regular.ttf')
GT_America_Standard_Light = font_manager.FontProperties(fname='fonts/GT-America-Standard-Light.ttf')
GT_America_Extended_Medium = font_manager.FontProperties(fname='fonts/GT-America-Extended-Medium.ttf')

# %%
class CustomFormatter(FuncFormatter):
    """
    ### Custom Formatter Class

    This class extends `FuncFormatter` to provide a custom format for numerical labels, particularly for plotting. It adjusts the display of numbers based on specified thresholds, displaying very small or very large numbers in scientific notation.

    ## Attributes:
    | Attribute Name   | Type      | Description                                                                                            |
    |------------------|-----------|--------------------------------------------------------------------------------------------------------|
    | `low_threshold`  | `Decimal` | Numbers below this threshold (and non-zero) are displayed in scientific notation. Default is 0.001.    |
    | `high_threshold` | `Decimal` | Numbers equal to or above this threshold are displayed in scientific notation. Default is 1e7 (10^7).  |
    | `total_digits`   | `Decimal` | The total number of significant digits to display for numbers within the thresholds. Default is 7.     |

    ## Methods:
    | Method Name   | Description                                                                                              |
    |---------------|----------------------------------------------------------------------------------------------------------|
    | `format_label`| Formats a numerical label based on the thresholds and total digits specified, adjusting its display.     |

    ## Usage:
    Used for custom formatting of numerical labels in plots, making them more readable especially when dealing with a wide range of values.

    ## Example:
    ```
    formatter = CustomFormatter(low_threshold=Decimal('0.001'), high_threshold=Decimal('1e7'), total_digits=Decimal('7'))
    ax.xaxis.set_major_formatter(formatter)
    ```
    """

    def __init__(
        self, 
        low_threshold: Decimal = Decimal('0.001'), 
        high_threshold: Decimal = Decimal('1e7'), 
        total_digits: Decimal = Decimal('7')
        ):
        """
        Initializes the CustomFormatter with specified thresholds and total digits for formatting.

        ## Parameters:
        | Parameter Name   | Type      | Description                                                                                           |
        |------------------|-----------|-------------------------------------------------------------------------------------------------------|
        | `low_threshold`  | `Decimal` | Numbers below this value (and non-zero) are displayed in scientific notation. Default is 0.001.       |
        | `high_threshold` | `Decimal` | Numbers equal to or above this value are displayed in scientific notation. Default is 1e7 (10^7).     |
        | `total_digits`   | `Decimal` | Specifies the total number of significant digits to display for numbers within the thresholds.        |
        """
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.total_digits = total_digits
        super().__init__(self.format_label)
        
    def format_label(
        self, 
        x: float, 
        pos: Union[int, None] = None
        ) -> str:
        """
        ### Formats a numerical label based on defined thresholds and total digits.

        ## Parameters:
        | Parameter Name | Type                | Description                                                                         |
        |----------------|---------------------|-------------------------------------------------------------------------------------|
        | `x`            | `float`             | The numerical value to be formatted.                                                |
        | `pos`          | `Union[int, None]`  | An optional position argument, which can be used if needed for custom formatting.   |

        ## Returns:
        | Return Name | Type  | Description                                                             |
        |-------------|-------|-------------------------------------------------------------------------|
        | `label`     | `str` | The formatted label as a string, adjusted for readability based on `x`. |

        ## Notes:
        - For values between `low_threshold` and `high_threshold`, formats numbers using fixed-point notation with a dynamic number of decimal places.
        - For values outside these thresholds, formats numbers in scientific notation.
        - The method aims to improve the readability of labels in plots by adjusting the format based on the magnitude of the value.
        """
        if 0 < abs(x) < self.low_threshold or abs(x) >= self.high_threshold:
            exponent = Decimal(np.floor(np.log10(abs(x))))
            mantissa = Decimal(x) / (Decimal('10')**exponent)
            sign_str = "-" if x < 0 else ""
            label = f"{sign_str}{abs(mantissa):.2f}×10$^{{{exponent}}}$"
        else:
            integer_digits = len(str(int(x)))
            decimal_places = max(0, self.total_digits - integer_digits - 1)
            format_string = f"{{:.{decimal_places}f}}"
            label = format_string.format(x)
        return label


# %%
class AnalysisPlotter:
    """
    ### This class is designed for plotting and analyzing bonding curve invariants and price functions in a liquidity pool scenario. It utilizes custom formatting for numerical labels and integrates several plotting functionalities to visually represent the relationships and dynamics of the liquidity pool parameters.

    ## Attributes:
    | Attribute Name       | Type             | Description                                                                               |
    |----------------------|------------------|-------------------------------------------------------------------------------------------|
    | `y_token`            | `str`            | Identifier for the y-axis token (usually the quote currency).                             |
    | `x_token`            | `str`            | Identifier for the x-axis token (usually the base currency).                              |
    | `A`                  | `Decimal`        | Parameter A of the bonding curve, representing an aspect of the curve's shape.            |
    | `B`                  | `Decimal`        | Parameter B of the bonding curve, another aspect influencing the curve's dynamics.        |
    | `z`                  | `Decimal`        | The invariant z, crucial for the bonding curve's behavior and price function calculation. |
    | `scaling_constant`   | `Decimal`        | A scaling constant used for adjusting curve parameters and calculations.                  |
    | `y_coord`            | `Decimal`        | The y-coordinate used for certain curve calculations and plotting reference points.       |
    | `custom_formatter`   | `CustomFormatter`| An instance of `CustomFormatter` for adjusting the display of numerical labels in plots.  |

    ## Methods:
    | Method Name               | Description                                                                                         |
    |---------------------------|-----------------------------------------------------------------------------------------------------|
    | `calculate_P_a`           | Calculates the highest price point on the curve based on parameters A, B, and the scaling constant. |
    | `calculate_P_b`           | Calculates the lowest price point on the curve using parameter B and the scaling constant.          |
    | `calculate_x_int`         | Determines the x-intercept of the curve, a key point for understanding curve behavior.              |
    | `invariant_function_y`    | Computes the y-coordinate based on a given x-coordinate, illustrating the bonding curve.            |
    | `invariant_function_x`    | Calculates the x-coordinate for a given y-coordinate, inverse to `invariant_function_y`.            |
    | `price_function`          | Determines the price function of the y-token in terms of the x-token for a given y-coordinate.      |
    | `plot_functions`          | Generates and displays the plots for the invariant curve and the price curve.                       |

    ## Notes:
    - The `AnalysisPlotter` class is utilized to graphically analyze and interpret the behavior of a liquidity pool under various parameter configurations. 
    - It provides insights into the pool's price dynamics, invariant curve shape, and the impact of adjustments to parameters A and B.

    """
    def __init__(
        self,
        y_token: str = 'DAI',
        x_token: str = 'BTC',
        A: Decimal = Decimal('664472284688849694199.099910773256515459122465701016535306218447578512405258580776854145882507220256'),
        B: Decimal = Decimal('5629499534213120000000.000000000000000000000000000000000000000000000000000000000000000000000000000000'),
        z: Decimal = Decimal('19458235162657264888232.42962965072071503107604160064938596025112075472147696292028588076752687180552'),
        scaling_constant: Decimal = Decimal('2') ** Decimal('48'),
        y_coord: Decimal = Decimal('10000000000000000000000'),
        custom_formatter = CustomFormatter
        ):
        """
        ### Initializes the AnalysisPlotter class with curve parameters and token identifiers.

        ## Parameters:
        | Parameter Name     | Type              | Description                                                                                                   |
        |--------------------|-------------------|---------------------------------------------------------------------------------------------------------------|
        | `y_token`          | `str`             | Identifier for the y-axis token.                                                                              |
        | `x_token`          | `str`             | Identifier for the x-axis token.                                                                              |
        | `A`                | `Decimal`         | Parameter A of the bonding curve, representing the width of the price range.                                  |
        | `B`                | `Decimal`         | Parameter B of the bonding curve, representing the low-bound of the price range.                              |
        | `z`                | `Decimal`         | Parameter z of the bonding curve, representing the y-intercept, or the relative size of the curve.            |
        | `scaling_constant` | `Decimal`         | A scaling constant used to scale-up the curve parameters, mostly for fixed-point arithmetic precision's sake. |                |
        | `y_coord`          | `Decimal`         | The current liquidity balance; the y-coordinate of the curve.                                                 |
        | `custom_formatter` | `CustomFormatter` | An instance of CustomFormatter for adjusting the display of numerical labels in plots, with specified digits. |

        ## Notes:
        - Upon initialization, the class calculates several key parameters of the bonding curve (P_a, P_b, x_int, P_m) based on the input values. 
        - It then proceeds to plot the invariant curve and price curve utilizing these parameters and the custom formatting rules for numerical labels.

        This example sets up an `AnalysisPlotter` instance for visualizing the dynamics of a liquidity pool with specified parameters.
        """
        self.ONE = Decimal('1')
        self.TWO = Decimal('2')
        self.y_token = y_token
        self.x_token = x_token
        self.A = A
        self.B = B
        self.z = z
        self.y_coord = y_coord
        self.scaling_constant = scaling_constant
        self.P_a = self.calculate_P_a()
        self.P_b = self.calculate_P_b()
        self.x_int = self.calculate_x_int()
        self.P_m = self.price_function(self.y_coord)
        self.x_coord = self.invariant_function_x(self.y_coord)
        self.custom_formatter = custom_formatter(total_digits=Decimal('7'))
        self.plot_functions()

    def calculate_P_a(self) -> Decimal:
        """
        ### Calculates the high-bound price parameter, P_a, of the bonding curve.

        ## Description:
        - This method computes the P_a parameter, which represents the higher price bound within the bonding curve model. 
        - P_a is determined by the formula `(A + B) / scaling_constant)^2`, where A and B are curve parameters representing the price range width and lower price bound, respectively, and the scaling constant is used for precision adjustment in fixed-point arithmetic.

        ## Parameters:
        None

        ## Returns:
        | Return Name | Type      | Description                                                                              |
        |-------------|-----------|------------------------------------------------------------------------------------------|
        | `P_a`       | `Decimal` | The high-bound price parameter of the bonding curve, representing the upper price limit. |

        """
        numerator = self.A + self.B
        denominator = self.scaling_constant
        P_a = (numerator / denominator) ** self.TWO
        return P_a

    def calculate_P_b(self) -> Decimal:
        """
        Calculates the low-bound price parameter, P_b, of the bonding curve.

        ## Description:
        - This method computes the P_b parameter, which signifies the lower price bound within the bonding curve model. 
        - P_b is calculated using the formula `(B / scaling_constant)^2`, where B is a curve parameter denoting the low-bound of the price range, and the scaling_constant facilitates precision adjustment for fixed-point arithmetic.

        ## Parameters:
        None

        ## Returns:
        | Return Name | Type      | Description                                                                           |
        |-------------|-----------|---------------------------------------------------------------------------------------|
        | `P_b`       | `Decimal` | The low-bound price parameter of the bonding curve, indicating the lower price limit. |

        """
        numerator = self.B
        denominator = self.scaling_constant
        P_b = (numerator / denominator) ** self.TWO
        return P_b

    def calculate_x_int(self) -> Decimal:
        """
        ### Calculates the x-intercept of the bonding curve.

        ## Parameters:
        None

        ## Returns:
        | Return Name | Type      | Description                                                                                      |
        |-------------|-----------|--------------------------------------------------------------------------------------------------|
        | `x_int`     | `Decimal` | The x-intercept of the bonding curve, indicating the point where the curve intersects the x-axis.|

        ## Notes:
        This method computes the x-intercept, `x_int`, of the bonding curve, which is a critical point where the curve intersects the x-axis. 
        - The x-intercept is calculated using the formula: `(scaling_constant^2 * z) / (A * B + B^2)`, where:
            - `scaling_constant` is used for precision adjustment in fixed-point arithmetic.
            - `z` represents the y-intercept or the relative size of the curve.
            - `A` and `B` are curve parameters defining the width of the price range and the lower price bound, respectively.
        """
        numerator = self.scaling_constant ** self.TWO * self.z
        denominator = self.A * self.B + self.B ** self.TWO
        x_int = numerator / denominator
        return x_int


    def invariant_function_y(self, x: Decimal) -> Decimal:
        """
        ### Calculates the y-value on the bonding curve for a given x-value.

        ## Parameters:
        | Parameter Name | Type      | Description                                                                                 |
        |----------------|-----------|---------------------------------------------------------------------------------------------|
        | `x`            | `Decimal` | The x-value (independent variable) for which to calculate the y-value (dependent variable). |

        ## Returns:
        | Return Name | Type      | Description                                                                     |
        |-------------|-----------|---------------------------------------------------------------------------------|
        | `y`         | `Decimal` | The calculated y-value on the bonding curve corresponding to the given x-value. |

        ## Notes:
        - This method computes the y-value on the bonding curve based on a given x-value, according to the bonding curve equation.
        - The equation used is: `(z * (scaling_constant^2 * z - x * (A * B + B^2))) / (scaling_constant^2 * z + x * (A * B + A^2))`, where:
            - `z` represents the y-intercept or the relative size of the curve.
            - `scaling_constant` is used for precision adjustment in fixed-point arithmetic.
            - `A` and `B` are curve parameters defining the width of the price range and the lower price bound, respectively.
        - This calculation is essential for analyzing the shape of the bonding curve and understanding its behavior at specific points.
        """
        numerator = self.z * (self.scaling_constant ** self.TWO * self.z - x * (self.A * self.B + self.B ** self.TWO))
        denominator = self.scaling_constant ** self.TWO * self.z + x * (self.A * self.B + self.A ** self.TWO)
        y = numerator / denominator
        return y

    
    def invariant_function_x(self, y: Decimal) -> Decimal:
        """
        ### Calculates the x-value on the bonding curve for a given y-value.

        ## Parameters:
        | Parameter Name | Type      | Description                                                                                 |
        |----------------|-----------|---------------------------------------------------------------------------------------------|
        | `y`            | `Decimal` | The y-value (independent variable) for which to calculate the x-value (dependent variable). |

        ## Returns:
        | Return Name | Type      | Description                                                                     |
        |-------------|-----------|---------------------------------------------------------------------------------|
        | `x`         | `Decimal` | The calculated x-value on the bonding curve corresponding to the given y-value. |

        ## Notes:
        - This method computes the x-value on the bonding curve based on a given y-value, according to the bonding curve equation.
        - The equation utilized is: `(scaling_constant^2 * z * (z - y)) / ((A + B) * (A * y + B * z))`, where:
            - `z` is the y-intercept or the relative size of the curve.
            - `scaling_constant` is used for precision adjustment in fixed-point arithmetic.
            - `A` and `B` are curve parameters that define the width of the price range and the lower price bound, respectively.
        - This calculation is vital for analyzing the shape of the bonding curve and understanding its behavior at specific points.
        """
        numerator = self.scaling_constant ** self.TWO * self.z * (self.z - y)
        denominator = (self.A + self.B) * (self.A * y + self.B * self.z)
        x = numerator / denominator
        return x


    def price_function(self, y: Decimal) -> Decimal:
        """
        ### Calculates the price function dy/dx for a given y-value on the bonding curve.

        ## Parameters:
        | Parameter Name | Type      | Description                                                  |
        |----------------|-----------|--------------------------------------------------------------|
        | `y`            | `Decimal` | The y-value for which to calculate the price function dy/dx. |

        ## Returns:
        | Return Name | Type      | Description                                                                                               |
        |-------------|-----------|-----------------------------------------------------------------------------------------------------------|
        | `dydx`      | `Decimal` | The derivative of y with respect to x (dy/dx), representing the price function at the given y-value.      |

        ## Notes:
        - This method computes the price function dy/dx at a specific y-value along the bonding curve.
        - The price function is determined using the formula: `((A * y + B * z)^2) / ((scaling_constant * z)^2)`, where:
            - `A` and `B` are curve parameters defining the width of the price range and the lower price bound, respectively.
            - `z` represents the y-intercept or the relative size of the curve.
            - `scaling_constant` is used to adjust precision in fixed-point arithmetic.
        - The price function dy/dx is crucial for understanding the instantaneous price change along the bonding curve, providing insights into the liquidity pool's behavior and market dynamics.
        """
        numerator = (self.A * y + self.B * self.z) ** self.TWO
        denominator = (self.scaling_constant * self.z) ** self.TWO
        dydx = numerator / denominator
        return dydx


    def plot_functions(self) -> None:
        """
        ### Visualizes the bonding curve and the price function based on current parameters.

        ## Functionality:
        - Generates two plots in a single figure:
            1. **Invariant Curve**: Illustrates the relationship between the change in the x-token (ΔBTC in wei scale) and the y-token (DAI in wei scale).
            2. **Price Curve**: Shows the price change (dy/dx in wei scale) as a function of the y-token (DAI in wei scale).

        ## Custom Formatting:
        - Utilizes `CustomFormatter` for label formatting, ensuring clarity and readability of numerical values across the plots.
        
        ## Key Features:
        - Highlights significant values such as `z`, `y_coord` (current liquidity balance), `P_a`, `P_b`, and `P_m` with horizontal and vertical lines and annotations.
        - Adjusts plot styles for a dark background theme and applies custom font properties for aesthetic enhancements.

        ## Usage:
        This method is automatically called upon the initialization of the `AnalysisPlotter` instance, immediately providing a visual analysis of the specified bonding curve and price dynamics.

        ## Parameters:
        None

        ## Returns:
        None

        ## Notes:
        - The method plots the invariant curve showing how the liquidity pool's y-token balance changes with respect to the x-token.
        - The price curve plot illustrates the rate of change in price as liquidity (y-token balance) varies, providing insights into the price impact and slippage within the pool.
        - Custom annotations and formatting applied to the plots aid in the interpretation and analysis of the liquidity pool's behavior under various scenarios.
        """
        formatted_P_a, \
        formatted_P_b, \
        formatted_P_m, \
        formatted_y_coord, \
        formatted_z = map(self.custom_formatter.format_label, (self.P_a, self.P_b, self.P_m, self.y_coord, self.z))
        x_coord = float(self.x_coord)
        z_high = float(self.z) * 1.20
        x_int_high = float(self.x_int) * 1.20
        P_a_high = float(self.P_a) * 1.20
        P_b_low = float(self.P_b) - float(self.P_a) * 0.2
        x_array = np.linspace(0, x_int_high, 500)
        x_array_adjusted = x_array - x_coord
        y_array = np.array([self.invariant_function_y(Decimal(x)) for x in x_array])
        price_array = np.array([self.price_function(Decimal(y)) for y in y_array])

        # plot
        plt.style.use('dark_background')
        fig, axs = plt.subplots(1, 2, figsize=(12, 6), gridspec_kw={'wspace': 0.4}, dpi=300)

        # first subplot
        axs[0].plot(x_array_adjusted, y_array, 'w-')
        axs[0].set_xlabel(f'$\\Delta {self.x_token}$ (wei scale)')
        axs[0].set_ylabel(f'{self.y_token} (wei scale)')
        axs[0].set_title('Invariant Curve', fontproperties=GT_America_Standard_Light)
        axs[0].grid(True, which='both', linestyle='--', linewidth='0.5', color='gray')
        axs[0].set_ylim(bottom = 0, top = z_high)
        axs[0].set_xlim(left = 0 - x_coord, right = x_int_high - x_coord)
        axs[0].axhline(y=float(self.z), color='#d5db27ff', linestyle='--', linewidth=0.5)
        text_z = axs[0].text((x_int_high - x_coord) * 0.8, float(self.z), f"z = {formatted_z}", 
                            fontsize=9, va='center', ha='center', color='#d5db27ff',
                            fontproperties=GT_America_Mono_Regular)
        text_z.set_path_effects([path_effects.withStroke(linewidth=2, foreground='black')])
        axs[0].axhline(y=float(self.y_coord), color='#10bbd5ff', linestyle='--', linewidth=0.5)
        text_y_coord = axs[0].text((x_int_high - x_coord) * 0.8, float(self.y_coord), f"y = {formatted_y_coord}", 
                            fontsize=9, va='center', ha='center', color='#10bbd5ff',
                            fontproperties=GT_America_Mono_Regular)
        text_y_coord.set_path_effects([path_effects.withStroke(linewidth=2, foreground='black')])
        
        # Second subplot
        axs[1].plot(y_array, price_array, 'w-')
        axs[1].set_xlabel(f'{self.y_token} (wei scale)')
        axs[1].set_ylabel(f"$-\\frac{{\\partial{{{self.y_token}}}}}{{\\partial{{{self.x_token}}}}}$ (wei scale)")
        axs[1].set_title('Price Curve', fontproperties=GT_America_Standard_Light)
        axs[1].grid(True, which='both', linestyle='--', linewidth='0.5', color='gray')
        axs[1].set_ylim(bottom=P_b_low, top=P_a_high)
        axs[1].set_xlim(right=0, left=float(self.z))
        axs[1].axhline(y=float(self.P_a), color='#d5db27ff', linestyle='--', linewidth=0.5)
        text_pa = axs[1].text(float(self.z) * 0.8, self.P_a, f"$P_{{\\mathrm{{a}}}} =$ {formatted_P_a}", 
                            fontsize=9, va='center', ha='center', color='#d5db27ff',
                            fontproperties=GT_America_Mono_Regular)
        text_pa.set_path_effects([path_effects.withStroke(linewidth=2, foreground='black')])
        axs[1].axhline(y=float(self.P_b), color='#d5db27ff', linestyle='--', linewidth=0.5)
        text_pb = axs[1].text(float(self.z) * 0.8, self.P_b, f"$P_{{\\mathrm{{b}}}} =$ {formatted_P_b}", 
                            fontsize=9, va='center', ha='center', color='#d5db27ff',
                            fontproperties=GT_America_Mono_Regular)
        text_pb.set_path_effects([path_effects.withStroke(linewidth=2, foreground='black')])
        axs[1].axhline(y=self.P_m, color='#10bbd5ff', linestyle='--', linewidth=0.5)
        text_pm = axs[1].text(float(self.z) * 0.8, self.P_m, f"$P_{{\\mathrm{{m}}}} =$ {formatted_P_m}", 
                            fontsize=9, va='center', ha='center', color='#10bbd5ff',
                            fontproperties=GT_America_Mono_Regular)
        text_pm.set_path_effects([path_effects.withStroke(linewidth=2, foreground='black')])
        axs[1].axvline(x=float(self.y_coord), color='#10bbd5ff', linestyle='--', linewidth=0.5)
        text_y_coord = axs[1].text(float(self.y_coord), P_b_low, f"y = {formatted_y_coord}", 
                            fontsize=9, va='center', ha='center', color='#10bbd5ff',
                            fontproperties=GT_America_Mono_Regular)
        text_y_coord.set_path_effects([path_effects.withStroke(linewidth=2, foreground='black')])

        # Setting the number of ticks on the x-axis and y-axis
        axs[0].xaxis.set_major_locator(MaxNLocator(4))
        axs[0].yaxis.set_major_locator(MaxNLocator(4))
        axs[1].xaxis.set_major_locator(MaxNLocator(4))
        axs[1].yaxis.set_major_locator(MaxNLocator(4))
        # Apply the custom formatter and font properties
        axs[0].yaxis.set_major_formatter(FuncFormatter(self.custom_formatter.format_label))
        axs[1].yaxis.set_major_formatter(FuncFormatter(self.custom_formatter.format_label))
        axs[0].xaxis.set_major_formatter(FuncFormatter(self.custom_formatter.format_label))
        axs[1].xaxis.set_major_formatter(FuncFormatter(self.custom_formatter.format_label))

        for label in axs[0].get_xticklabels() + axs[0].get_yticklabels():
            label.set_fontproperties(GT_America_Mono_Regular)
        for label in axs[1].get_xticklabels() + axs[1].get_yticklabels():
            label.set_fontproperties(GT_America_Mono_Regular)

        plt.show()

# %%
class Solidity:
    """
    ### Simulates Solidity's fixed-point arithmetic operations and overflow checks in Python.

    ## Description:
    This class provides static methods to simulate arithmetic operations akin to those in Solidity smart contracts, incorporating checks for integer overflows and ensuring values remain within the bounds of Solidity's uint128 and uint256 types.

    ## Attributes:
    | Attribute Name | Type | Description                                          |
    |----------------|------|------------------------------------------------------|
    | `MAX_UINT128`  | `int`| Maximum value for a 128-bit unsigned integer.        |
    | `MAX_UINT256`  | `int`| Maximum value for a 256-bit unsigned integer.        |

    ## Methods:
    | Method Name | Description                                                                 |
    |-------------|-----------------------------------------------------------------------------|
    | `check`     | Ensures a given integer is within the specified maximum value.              |
    | `uint128`   | Asserts that a number fits within the bounds of a 128-bit unsigned integer. |
    | `add`       | Performs addition with overflow checking for uint256.                       |
    | `sub`       | Performs subtraction with overflow checking for uint256.                    |
    | `mul`       | Performs multiplication with overflow checking for uint256.                 |
    | `mulDivF`   | Multiplies two numbers and divides by a third, flooring the result.         |
    | `mulDivC`   | Multiplies two numbers and divides by a third, ceiling the result.          |

    ## Usage:
    - The class methods are designed to be used statically, without needing to instantiate the `Solidity` class.
    - These methods are particularly useful for developers writing Python simulations or tests for Solidity smart contracts, requiring precise arithmetic behavior modeling.
    """
    MAX_UINT128 = int(2**128 - 1)
    MAX_UINT256 = int(2**256 - 1)

    @staticmethod
    def check(val: int, max: int) -> int:
        """
        Ensures a given integer is within 0 and a specified maximum value.

        ## Parameters:
        | Parameter Name | Type  | Description                         |
        |----------------|-------|-------------------------------------|
        | `val`          | `int` | The integer to check.               |
        | `max`          | `int` | The maximum allowed value.          |

        ## Returns:
        | Return Name | Type  | Description                          |
        |-------------|-------|--------------------------------------|
        | `val`       | `int` | The original value if within bounds. |

        ## Raises:
        - `AssertionError` if `val` is not within the specified bounds.
        """
        assert 0 <= val <= max, f"Error: expected 0 <= {val} <= {max}"
        return val
    
    @staticmethod
    def uint128(n: int) -> int:
        """
        Asserts that a number fits within the bounds of a 128-bit unsigned integer.

        ## Parameters:
        | Parameter Name | Type  | Description           |
        |----------------|-------|-----------------------|
        | `n`            | `int` | The integer to check. |

        ## Returns:
        | Return Name | Type  | Description                                      |
        |-------------|-------|--------------------------------------------------|
        | `n`         | `int` | The original number if within uint128 bounds.    |

        ## Raises:
        - `AssertionError` if `n` exceeds `MAX_UINT128`.
        """
        return Solidity.check(n, Solidity.MAX_UINT128)
    
    @staticmethod
    def add(a: int, b: int) -> int:
        """
        Performs addition with overflow checking against the maximum uint256 value.

        ## Parameters:
        | Parameter Name | Type  | Description        |
        |----------------|-------|--------------------|
        | `a`            | `int` | The first summand. |
        | `b`            | `int` | The second summand.|

        ## Returns:
        | Return Name | Type  | Description                                  |
        |-------------|-------|----------------------------------------------|
        | `result`    | `int` | The sum of `a` and `b` within uint256 bounds.|

        ## Raises:
        - `AssertionError` if the sum exceeds `MAX_UINT256`.
        """
        return Solidity.check(a + b, Solidity.MAX_UINT256)
    
    @staticmethod
    def sub(a: int, b: int) -> int:
        """
        Performs subtraction with overflow checking for uint256.

        ## Parameters:
        | Parameter Name | Type  | Description     |
        |----------------|-------|-----------------|
        | `a`            | `int` | The minuend.    |
        | `b`            | `int` | The subtrahend. |

        ## Returns:
        | Return Name | Type  | Description                                         |
        |-------------|-------|-----------------------------------------------------|
        | `result`    | `int` | The difference of `a` and `b` within uint256 bounds.|

        ## Raises:
        - `AssertionError` if the operation results in a negative value or exceeds `MAX_UINT256`.
        """
        return Solidity.check(a - b, Solidity.MAX_UINT256)
    
    @staticmethod
    def mul(a: int, b: int) -> int:
        """
        Performs multiplication with overflow checking for uint256.

        ## Parameters:
        | Parameter Name | Type  | Description       |
        |----------------|-------|-------------------|
        | `a`            | `int` | The first factor. |
        | `b`            | `int` | The second factor.|

        ## Returns:
        | Return Name | Type  | Description                                      |
        |-------------|-------|--------------------------------------------------|
        | `result`    | `int` | The product of `a` and `b` within uint256 bounds.|

        ## Raises:
        - `AssertionError` if the product exceeds `MAX_UINT256`.
        """
        return Solidity.check(a * b, Solidity.MAX_UINT256)
    
    @staticmethod
    def mulDivF(a: int, b: int, c: int) -> int:
        """
        Multiplies two numbers and divides by a third, rounding towards zero.

        ## Parameters:
        | Parameter Name | Type  | Description             |
        |----------------|-------|-------------------------|
        | `a`            | `int` | The first multiplicand. |
        | `b`            | `int` | The second multiplicand.|
        | `c`            | `int` | The divisor.            |

        ## Returns:
        | Return Name | Type  | Description                                                              |
        |-------------|-------|--------------------------------------------------------------------------|
        | `result`    | `int` | The result of `(a * b) // c` within uint256 bounds, rounded towards zero.|

        ## Raises:
        - `AssertionError` if the intermediate or final result exceeds `MAX_UINT256`.
        """
        return Solidity.check(a * b // c, Solidity.MAX_UINT256)
    
    @staticmethod
    def mulDivC(a: int, b: int, c: int) -> int:
        """
        Multiplies two numbers and divides by a third, rounding towards infinity.

        ## Parameters:
        | Parameter Name | Type  | Description             |
        |----------------|-------|-------------------------|
        | `a`            | `int` | The first multiplicand. |
        | `b`            | `int` | The second multiplicand.|
        | `c`            | `int` | The divisor.            |

        ## Returns:
        | Return Name | Type  | Description                                                            |
        |-------------|-------|------------------------------------------------------------------------|
        | `result`    | `int` | The result of `(a * b + c - 1) // c` within uint256 bounds, rounded up.|

        ## Raises:
        - `AssertionError` if the intermediate or final result exceeds `MAX_UINT256`.
        """
        return Solidity.check((a * b + c - 1) // c, Solidity.MAX_UINT256)


# %%
class AccuracyAnalysis:
    """
    ### Analyzes the accuracy of bonding curve calculations comparing precise arithmetic with fixed-point arithmetic used in blockchain contracts.

    ## Description:
    - This class facilitates the comparison between the outcomes of bonding curve calculations performed with high precision arithmetic (Python's `Decimal`) and fixed-point arithmetic akin to that found in blockchain environments (simulated by integer operations).
    - It aims to highlight the precision loss and potential impact on financial calculations within DeFi smart contract implementations.

    ## Attributes:
    | Attribute Name                          | Type                 | Description                                                                                                                      |
    |-----------------------------------------|----------------------|----------------------------------------------------------------------------------------------------------------------------------|
    | `risk_token`                            | `str`                | Identifier for the asset considered as the risk token in the strategy.                                                           |
    | `cash_token`                            | `str`                | Identifier for the asset considered as the cash token in the strategy.                                                           |
    | `strategy_mode`                         | `str`                | Trading strategy applied ('buy' or 'sell'), indicating the direction of asset exchange.                                          |
    | `risk_decimals`                         | `Decimal`            | Number of decimal places for the risk token, affecting its divisibility and quantity precision.                                  |
    | `cash_decimals`                         | `Decimal`            | Number of decimal places for the cash token, affecting its divisibility and quantity precision.                                  |
    | `low_price`                             | `Decimal`            | The lower price in the price range within which the bonding curve operates.                                                      |
    | `high_price`                            | `Decimal`            | The upper price in the price range within which the bonding curve operates.                                                      |
    | `marginal_price`                        | `Decimal`            | The price at which the next incremental trade is expected to execute.                                                            |
    | `liquidity`                             | `Decimal`            | Total liquidity available on the order within the strategy.                                                                      |
    | `trade_mode`                            | `str`                | Specifies whether the trade is executed by providing a source amount ('trade_by_source') or a target amount ('trade_by_target'). |
    | `trade_input`                           | `Decimal`            | Input amount for executing the trade, which can be specified in terms of either the risk or cash token.                          |
    | `analysis_plotter`                      | `AnalysisPlotter`    | Optional utility for visualizing the bonding curve and related trade outcomes.                                                   |
    | `scaling_constant`                      | `Decimal`            | A scaling constant used for precision adjustment in bonding curve calculations.                                                  |
    | `cleaned_inputs`                        | `Dict[str, Decimal]` | Standardized inputs derived from initial parameters for curve analysis.                                                          |
    | `maker_precise_curve_parameters`        | `Dict[str, Decimal]` | Curve parameters calculated with high precision for the maker side of trades.                                                    |
    | `contract_precise_curve_parameters`     | `Dict[str, Decimal]` | Precise curve parameters intended for use in contract simulations.                                                               |
    | `contract_fixed_point_curve_parameters` | `Dict[str, int]`     | Fixed-point curve parameters simulated to mimic blockchain contract storage and calculations.                                    |
    | `trade_input_output_information`        | `Tuple`              | Cleaned and processed trade input and output information for analysis.                                                           |

    ## Methods:
    | Method Name                         | Description                                                                                     |
    |-------------------------------------|-------------------------------------------------------------------------------------------------|
    | `clean_strategy_inputs`             | Standardizes input values for curve parameter calculations.                                     |
    | `encode_bonding_curve_precise`      | Encodes bonding curve parameters for precise arithmetic calculations.                           |
    | `encode_bonding_curve_fixed_point`  | Encodes bonding curve parameters for fixed-point arithmetic simulations.                        |
    | `calculate_trade_output`            | Computes the output of a trade given the input amount and selected trade function.              |
    | `print_trade_output`                | Outputs the results of a trade simulation in a readable format.                                 |
    | `print_curve_parameters`            | Displays calculated curve parameters for both precise and fixed-point arithmetic.               |
    | `compress_rate_parameter`           | Compresses curve parameters to fit within blockchain storage limitations.                       |
    | `decompress_rate_parameter`         | Decompresses curve parameters from their compressed storage format.                             |
    | `process_rate`                      | Processes rate values to prepare them for curve parameter calculations.                         |
    | `calculate_z_parameter`             | Calculates the z-parameter of the bonding curve based on other curve parameters and liquidity.  |
    | `encode_bonding_curve_precise`      | Encodes curve parameters for calculations with high precision.                                  |
    | `encode_bonding_curve_fixed_point`  | Encodes curve parameters for fixed-point arithmetic, simulating blockchain calculations.        |
    | `trade_by_source_amount_precise`    | Simulates a trade by source amount using precise arithmetic.                                    |
    | `trade_by_target_amount_precise`    | Simulates a trade by target amount using precise arithmetic.                                    |
    | `trade_by_source_amount_fixed_point`| Simulates a trade by source amount using fixed-point arithmetic, mimicking blockchain behavior. |
    | `trade_by_target_amount_fixed_point`| Simulates a trade by target amount using fixed-point arithmetic, mimicking blockchain behavior. |
    | `get_trade_functions`               | Selects the appropriate trade function based on the specified trade mode.                       |

    ## Usage:
    - Detailed in the class documentation, including methods for cleaning inputs, encoding curve parameters, simulating trades, and visualizing outcomes.
    - Instantiated with specific parameters for the risk and cash tokens, this class performs a series of calculations and simulations to evaluate the precision of bonding curve trades.
    - Instantiate with specific parameters for the risk and cash tokens to perform a series of calculations and simulations.
    - Evaluate the precision of bonding curve trades and their representation in a blockchain environment.
    """
    def __init__(
        self,
        risk_token: str = 'BTC',
        cash_token: str = 'DAI',
        strategy_mode: str = 'buy',
        risk_decimals: Decimal = Decimal('8'),
        cash_decimals: Decimal = Decimal('18'),
        low_price: Decimal = Decimal('40_000'),
        high_price: Decimal = Decimal('50_000'),
        marginal_price: Decimal = Decimal('45_000'),
        liquidity: Decimal = Decimal('10_000'),
        trade_mode: str = 'trade_by_target',
        trade_input: Decimal = Decimal('5_000'),
        analysis_plotter = AnalysisPlotter,
        ):
        """
        ### Initializes the AccuracyAnalysis class with parameters for analyzing trade accuracy on bonding curves.

        ## Parameters:
        | Parameter Name     | Type              | Description                                                                                                   |
        |--------------------|-------------------|---------------------------------------------------------------------------------------------------------------|
        | `risk_token`       | `str`             | Identifier for the asset considered as the risk token in the strategy.                                        |
        | `cash_token`       | `str`             | Identifier for the asset considered as the cash token in the strategy.                                        |
        | `strategy_mode`    | `str`             | Trading strategy applied ('buy' or 'sell'), indicating the direction of asset exchange.                       |
        | `risk_decimals`    | `Decimal`         | Number of decimal places for the risk token, affecting its divisibility and quantity precision.               |
        | `cash_decimals`    | `Decimal`         | Number of decimal places for the cash token, affecting its divisibility and quantity precision.               |
        | `low_price`        | `Decimal`         | The lower price in the price range within which the bonding curve operates.                                   |
        | `high_price`       | `Decimal`         | The upper price in the price range within which the bonding curve operates.                                   |
        | `marginal_price`   | `Decimal`         | The price at which the next incremental trade is expected to execute.                                         |
        | `liquidity`        | `Decimal`         | Total liquidity available on the order within the strategy.                                                   |
        | `trade_mode`       | `str`             | Specifies whether the trade is executed by providing a source amount ('trade_by_source') or a target amount.  |
        | `trade_input`      | `Decimal`         | Input amount for executing the trade, which can be specified in terms of either the risk or cash token.       |
        | `analysis_plotter` | `AnalysisPlotter` | Optional utility for visualizing the bonding curve and related trade outcomes.                                |

        ## Functionality:
        - Sets up the environment for conducting trade accuracy analysis on a specified bonding curve.
        - Calculates and prints both precise and fixed-point representations of curve parameters and trade outputs.
        - Visualizes the bonding curve and trade outcomes using the specified AnalysisPlotter instance.
        """
        self.ONE = Decimal('1')
        self.TWO = Decimal('2')
        self.TEN = Decimal('10')
        self.scaling_constant = Decimal('2') ** Decimal('48')
        self.scaling_constant_int = int(self.scaling_constant)
        self.risk_token = risk_token
        self.cash_token = cash_token
        self.strategy_mode = strategy_mode
        self.risk_decimals = risk_decimals
        self.cash_decimals = cash_decimals
        self.low_price = low_price
        self.high_price = high_price
        self.marginal_price = marginal_price
        self.liquidity = liquidity
        self.trade_mode = trade_mode
        self.trade_input = trade_input
        self.analysis_plotter = analysis_plotter
        self.cleaned_inputs = self.clean_strategy_inputs()
        self.maker_precise_curve_parameters = self.encode_bonding_curve_precise(self.cleaned_inputs)
        self.contract_precise_curve_parameters, \
        self.contract_fixed_point_curve_parameters = self.encode_bonding_curve_fixed_point()
        self.print_curve_parameters()
        self.trade_input_output_information = self.clean_trade_inputs_and_outputs()
        self.print_trade_output()
        analysis_plotter(y_token = risk_token if strategy_mode == 'sell' else cash_token,
                         x_token = risk_token if strategy_mode == 'buy' else cash_token,
                         A = self.maker_precise_curve_parameters['A'],
                         B = self.maker_precise_curve_parameters['B'],
                         z = self.maker_precise_curve_parameters['z'],
                         y_coord = self.maker_precise_curve_parameters['y'],
                         scaling_constant = self.scaling_constant)
        
    def clean_strategy_inputs(self) -> Dict[str, Decimal]:
        """
        ### Standardizes and prepares input values for bonding curve parameter calculations.

        ## Parameters:
        None

        ## Returns:
        A dictionary containing the standardized parameters for the bonding curve:
        | Key   | Type      | Description                                                                |
        |-------|-----------|----------------------------------------------------------------------------|
        | `y`   | `Decimal` | The liquidity in the pool, adjusted for the appropriate decimal precision. |
        | `P_a` | `Decimal` | The adjusted high price parameter for the bonding curve.                   |
        | `P_m` | `Decimal` | The adjusted marginal price parameter for the bonding curve.               |
        | `P_b` | `Decimal` | The adjusted low price parameter for the bonding curve.                    |

        ## Notes:
        - Adjusts input values based on the trading strategy, token decimals, and specified prices to ensure consistent and accurate calculations.
        - Calculates the effective liquidity and price parameters in the appropriate scale, considering the differences in token decimals.
        - The method internally adjusts the price parameters (`P_a`, `P_m`, `P_b`) based on the `strategy_mode` ('buy' or 'sell'), scaling them to reflect the wei scale difference between risk and cash tokens.
        - The liquidity (`y`) is also adjusted to reflect the actual amount in the pool, taking into account the decimal precision of the involved tokens.
        """
        wei_scale = self.TEN ** self.cash_decimals / self.TEN ** self.risk_decimals
        exponent = self.ONE if self.strategy_mode == 'buy' else -self.ONE
        P_a_base, P_b_base = (self.high_price, self.low_price) if self.strategy_mode == 'buy' else (self.low_price, self.high_price)
        y_decimals = self.cash_decimals if self.strategy_mode == 'buy' else self.risk_decimals
        y = self.liquidity * self.TEN ** y_decimals
        P_a, P_m, P_b = ((rate * wei_scale) ** exponent for rate in (P_a_base, self.marginal_price, P_b_base))
        return {'y': y, 'P_a': P_a, 'P_m': P_m, 'P_b': P_b}

    def compare_values(
        self, 
        precise_value: Decimal, 
        imprecise_value: Union[Decimal, int]
        ) -> str:
        """
        ### Compares precise and imprecise (or fixed-point) numerical values and generates a comparison string.

        ## Parameters:
        | Parameter Name    | Type                  | Description                                                            |
        |-------------------|-----------------------|------------------------------------------------------------------------|
        | `precise_value`   | `Decimal`             | The value calculated with high precision arithmetic.                   |
        | `imprecise_value` | `Union[Decimal, int]` | The value calculated with reduced precision or fixed-point arithmetic. |

        ## Returns:
        | Return Name       | Type      | Description                                                                     |
        |-------------------|-----------|---------------------------------------------------------------------------------|
        | `comparison_str`  | `str`     | A string representing the comparison between the precise and imprecise values.  |

        ## Notes:
        - Generates a visual representation comparing the two values, using '|' to denote matching digits and ':' for mismatches.
        - This method helps visualize the precision loss or differences between calculations performed with different levels of arithmetic precision.
        - The comparison covers both the integer part and, if applicable, the decimal part of the numbers.
        """
        precise_str = f"{precise_value}".split('.')
        imprecise_str = f"{imprecise_value}".split('.')
        int_part_length = max(len(precise_str[0]), len(imprecise_str[0]))
        precise_int_part = precise_str[0].rjust(int_part_length, ' ')
        imprecise_int_part = imprecise_str[0].rjust(int_part_length, ' ')
        comparison_str_int = ''.join(['|' if precise_int_part[i] == imprecise_int_part[i] else ':' for i in range(int_part_length)])
        if len(precise_str) > 1 and len(imprecise_str) > 1:
            dec_part_length = max(len(precise_str[1]), len(imprecise_str[1]))
            precise_dec_part = precise_str[1].ljust(dec_part_length, '0')
            fixed_dec_part = imprecise_str[1].ljust(dec_part_length, '0')
            comparison_str_dec = ''.join(['|' if precise_dec_part[i] == fixed_dec_part[i] else ':' for i in range(dec_part_length)])
            comparison_str = f"{comparison_str_int} {comparison_str_dec}"
        else:
            comparison_str = comparison_str_int
        return comparison_str

    def print_curve_parameters(self) -> None:
        """
        ### Prints the bonding curve parameters in a table format, comparing precise and fixed-point values.

        ## Parameters:
        None

        ## Returns:
        None. This method outputs the comparison directly to the console.

        ## Notes:
        - Displays a table where each row represents a parameter of the bonding curve.
        - For each parameter, shows the value calculated with high precision (with respect to the maker's intent) and the value in fixed-point arithmetic (contract).
        - Utilizes the `compare_values` method to generate a visual comparison ('|' for match, ':' for mismatch) between precise and imprecise values.
        - This method aids in understanding the discrepancies that might arise due to the precision differences in calculations.
        """
        combined_data = []
        keys = ['y', 'z', 'A', 'B']
        for key in keys:
            precise_value = self.maker_precise_curve_parameters.get(key, 'N/A')
            fixed_point_value = self.contract_fixed_point_curve_parameters.get(key, 'N/A')
            comparison_str = self.compare_values(precise_value, fixed_point_value)
            combined_data.append([f'{key} precise (maker)', precise_value])
            combined_data.append(["", comparison_str])
            combined_data.append([f'{key} fixed point (contract)', fixed_point_value])
            if key != keys[-1]:
                combined_data.append(["", ""])
        print(tabulate(combined_data, headers=['Parameter', 'Value'], tablefmt='pretty', colalign=('right', 'left'), disable_numparse=True))
        print('\n')
    
    def get_trade_decimals(self) -> Tuple[Decimal, Decimal]:
        """
        ### Determines the decimal precision for trade input and output based on strategy and trade mode.

        ## Parameters:
        None

        ## Returns:
        | Return Name       | Type                      | Description                                                                 |
        |-------------------|---------------------------|-----------------------------------------------------------------------------|
        | `trade_decimals`  | `Tuple[Decimal, Decimal]` | A tuple containing the decimal precision for trade input and output tokens. |

        ## Notes:
        - The method adjusts decimal precision based on the strategy mode ('buy' or 'sell') and trade mode ('tradeBySource' or not).
        - For 'buy' strategy:
            - 'tradeBySource' uses risk token decimals for input and cash token decimals for output.
            - Otherwise, cash token decimals for input and risk token decimals for output.
        - For 'sell' strategy:
            - 'tradeBySource' uses cash token decimals for input and risk token decimals for output.
            - Otherwise, risk token decimals for input and cash token decimals for output.
        - This distinction is crucial for accurately simulating trades and ensuring that decimal precision aligns with the expected blockchain contract behavior.
        """
        if self.strategy_mode == 'buy':
            if self.trade_mode == 'tradeBySource':
                return self.risk_decimals, self.cash_decimals
            else:
                return self.cash_decimals, self.risk_decimals
        else:
            if self.trade_mode == 'tradeBySource':
                return self.cash_decimals, self.risk_decimals
            else:
                return self.risk_decimals, self.cash_decimals

    def clean_parameter_kwargs(
        self,
        trade_function: Callable, 
        curve_parameters: Dict[str, Decimal]
        ):
        """
        ### Filters curve parameters to match the expected arguments of the trade function.

        ## Parameters:
        | Parameter Name    | Type                 | Description                                                                                       |
        |-------------------|----------------------|---------------------------------------------------------------------------------------------------|
        | `trade_function`  | `Callable`           | The trade function for which parameters are being prepared.                                       |
        | `curve_parameters`| `Dict[str, Decimal]` | The dictionary of curve parameters that may include more keys than needed for the trade function. |

        ## Returns:
        | Return Name       | Type                 | Description                                                                                      |
        |-------------------|----------------------|--------------------------------------------------------------------------------------------------|
        | `filtered_params` | `Dict[str, Decimal]` | A dictionary of curve parameters filtered to include only those expected by the trade function.  |

        ## Notes:
        - This method dynamically matches the expected parameter names of any given trade function to the keys present in the curve parameters dictionary.
        - It ensures that only relevant parameters are passed to the trade function, preventing errors from unexpected or extraneous arguments.
        - The method utilizes the function's code object to introspect the names of expected parameters, offering flexibility for use with various trade functions.
        """
        valid_keys = trade_function.__code__.co_varnames[:trade_function.__code__.co_argcount]
        return {k: v for k, v in curve_parameters.items() if k in valid_keys}

    def calculate_trade_output(
        self, 
        trade_input_wei: int, 
        trade_function: Callable, 
        curve_parameters: Dict[str, Decimal]
        ) -> Union[Decimal, int]:
        """
        ### Calculates the output of a trade given the input amount and a trade function.

        ## Parameters:
        | Parameter Name     | Type                 | Description                                                                                                               |
        |--------------------|----------------------|---------------------------------------------------------------------------------------------------------------------------|
        | `trade_input_wei`  | `int`                | The input amount for the trade, represented in wei units to match blockchain transaction precision.                       |
        | `trade_function`   | `Callable`           | The function used to simulate the trade, which can be a precise arithmetic function or a fixed-point arithmetic function. |
        | `curve_parameters` | `Dict[str, Decimal]` | The dictionary of bonding curve parameters relevant to the trade function.                                                |

        ## Returns:
        | Return Name       | Type                  | Description                                                                                                                                                |
        |-------------------|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `trade_output`    | `Union[Decimal, int]` | The output of the trade, which may be returned in wei units (int) for fixed-point arithmetic functions or as a `Decimal` for precise arithmetic functions. |

        ## Notes:
        - This method dynamically adapts the curve parameters to the expected inputs of the provided trade function.
        - For fixed-point arithmetic functions (identified by the function name ending with 'fixed_point'), it filters the curve parameters to match the function's expected arguments.
        - It then executes the trade function with the prepared inputs and returns the trade output, simulating the execution of a trade on a blockchain with either precise or fixed-point arithmetic.
        """
        cleaned_parameters = self.clean_parameter_kwargs(trade_function, curve_parameters) if trade_function.__name__.endswith('fixed_point') else curve_parameters
        return trade_function(trade_input_wei, **cleaned_parameters)

    def clean_trade_inputs_and_outputs(self) -> Tuple[Tuple[int, Tuple[Decimal, Decimal, int]], Tuple[float, Tuple[Decimal, Decimal, float]]]:
        """
        ### Processes and standardizes trade inputs and outputs for analysis.

        ## Parameters:
        None

        ## Returns:
        A tuple of tuples, organized as follows:

        | Part                       | Type                                        | Description                                                                                                                                                                        |
        |----------------------------|---------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | First Tuple                | `(int, Tuple[Decimal, Decimal, int])`       | Contains the trade input amount in wei and trade outputs in wei for precise and fixed-point arithmetic calculations.                                                               |
        | Second Tuple               | `(float, Tuple[Decimal, Decimal, float])`   | Contains the trade input amount in raw format (adjusted for decimals) and trade outputs in raw format (adjusted for decimals) for precise and fixed-point arithmetic calculations. |

        ### Detailed Breakdown:
        1. **First Tuple Elements:**
        - **Trade Input (Wei):** The amount of the trade input expressed in wei units.
        - **Trade Outputs (Wei):** A tuple containing the trade output amounts in wei units, calculated using precise and fixed-point arithmetic methods.

        2. **Second Tuple Elements:**
        - **Trade Input (Raw):** The trade input amount adjusted for token decimals, presenting a more intuitive view of the trade size.
        - **Trade Outputs (Raw):** A tuple containing the trade output amounts adjusted for token decimals, facilitating a direct comparison of outcomes across different arithmetic methods.

        ## Notes:
        - This method calculates the trade input amount in wei units based on the specified `trade_input` and the relevant decimals for the input token.
        - It then simulates the trade using both precise and fixed-point arithmetic functions to calculate outputs in wei units.
        - The method converts these outputs into a raw format by adjusting for the output token's decimals, allowing the results to be inspected more intuitively.
        - This structured return format supports detailed analysis and comparison of trade outcomes as calculated by different arithmetic approaches.
        """
        trade_input_decimals, trade_output_decimals = self.get_trade_decimals()
        trade_input_wei = int(self.trade_input * self.TEN ** trade_input_decimals)
        precise_trade_function, fixed_point_trade_function = self.get_trade_functions()
        trade_outputs_wei = {'maker_precise': self.calculate_trade_output(trade_input_wei, precise_trade_function, self.maker_precise_curve_parameters),
                             'contract_precise': self.calculate_trade_output(trade_input_wei, precise_trade_function, self.contract_precise_curve_parameters),
                             'contract_fixed_point': self.calculate_trade_output(trade_input_wei, fixed_point_trade_function, self.contract_fixed_point_curve_parameters)}
        trade_outputs_raw = {key: value / 10 ** trade_output_decimals for key, value in trade_outputs_wei.items()}
        return ((trade_input_wei, tuple(trade_outputs_wei.values())), (self.trade_input, tuple(trade_outputs_raw.values())))
    
    def get_trade_tokens(self) -> Tuple[str, str]:
        """
        ### Determines the order of trade tokens based on the strategy and trade modes.

        ## Parameters:
        None

        ## Returns:
        | Return Name                   | Type              | Description                                                                                          |
        |-------------------------------|-------------------|------------------------------------------------------------------------------------------------------|
        | `(input_token, output_token)` | `Tuple[str, str]` | A tuple containing identifiers for the input and output tokens, respectively, for a trade operation. |

        ## Notes:
        - The method determines the order of tokens (risk and cash) based on the `strategy_mode` ('buy' or 'sell') and `trade_mode` ('tradeBySource' or 'tradeByTarget').
        - In 'buy' strategy mode:
            - If `trade_mode` is 'tradeBySource', the risk token is the input, and the cash token is the output.
            - If `trade_mode` is 'tradeByTarget', the cash token is the input, and the risk token is the output.
        - In 'sell' strategy mode:
            - If `trade_mode` is 'tradeBySource', the cash token is the input, and the risk token is the output.
            - If `trade_mode` is 'tradeByTarget', the risk token is the input, and the cash token is the output.
        - This method ensures that the correct token is used for input and output calculations in subsequent trade simulations.
        """
        if self.strategy_mode == 'buy':
            if self.trade_mode == 'tradeBySource':
                return (self.risk_token, self.cash_token)
            else:
                return (self.cash_token, self.risk_token)
        else:
            if self.trade_mode == 'tradeBySource':
                return (self.cash_token, self.risk_token)
            else:
                return (self.risk_token, self.cash_token)

    def generate_trade_table_data(
        self, 
        labels: List[str], 
        trade_outputs: Tuple[Union[Decimal, int]]
        ):
        """
        ### Generates tabular data for displaying trade outputs.

        ## Parameters:
        | Parameter Name  | Type                         | Description                                       |
        |-----------------|------------------------------|---------------------------------------------------|
        | `labels`        | `List[str]`                  | Labels for each row, typically precision labels.  |
        | `trade_outputs` | `Tuple[Union[Decimal, int]]` | The trade output values to be displayed.          |

        ## Returns:
        | Return Name   | Type               | Description                                            |
        |---------------|--------------------|--------------------------------------------------------|
        | `table_data`  | `List[List[str]]`  | List of lists, each containing row data for the table. |

        ## Notes:
        - The method iterates over labels and trade_outputs to create rows for a table.
        - For each pair of trade outputs, it also generates a comparison string to visually indicate the precision difference.
        - This method aids in visualizing the differences in trade outputs across different precision calculations.
        """
        table_data = []
        for i, label in enumerate(labels):
            table_data.append([label, str(trade_outputs[i])])
            if i < len(labels) - 1:
                comparison_str = self.compare_values(trade_outputs[i], trade_outputs[i + 1])
                table_data.append(["", comparison_str])
        return table_data

    def print_trade_output(self) -> None:
        """
        ### Prints the trade output information in a tabular format for easy comparison.

        ## Parameters:
        None

        ## Returns:
        None

        ## Notes:
        - Retrieves the input and output tokens based on the trading strategy and mode.
        - Extracts and prints the trade input amount in wei, showing the initial trade value.
        - Generates and prints two tables:
            1. The first table shows trade outputs in wei units for arbitrary precision (Maker), arbitrary precision (Contract), and fixed-point precision (Contract).
            2. The second table displays the trade input and output amounts in a more readable format, adjusted for token decimals.
        - Utilizes `generate_trade_table_data` to prepare data for each table, highlighting the precision levels used in calculations.
        - The method is designed to visually represent the outcomes of trade simulations, comparing the results of different arithmetic precision levels.
        - It helps in assessing the impact of precision loss in fixed-point arithmetic, commonly used in blockchain contracts, versus arbitrary precision arithmetic.
        - By presenting the data in tabular form, it facilitates a clear and comparative analysis of the numerical outcomes of trades under various calculation methods.
        """
        input_token, output_token = self.get_trade_tokens()
        trade_input_wei, trade_outputs_wei = self.trade_input_output_information[0]
        trade_input_raw, trade_outputs_raw = self.trade_input_output_information[1]
        labels = ['Arbitrary Precision (Maker)', 'Arbitrary Precision (Contract)', 'Fixed-point Precision (Contract)']
        table1_data, table2_data = map(lambda outputs: self.generate_trade_table_data(labels, outputs), (trade_outputs_wei, trade_outputs_raw))
        colalign = ('right', 'left')
        print(f'Function Called: {self.trade_mode}\n')
        print(f'Trade Input (Token Wei): {trade_input_wei} {input_token}wei\n')
        print(tabulate(table1_data, headers=['Precision', f'Trade Output {output_token}wei'], tablefmt='pretty', colalign=colalign, disable_numparse=True))
        print(f'\nTrade Input (Ignoring Decimals): {str(trade_input_raw)} {input_token}\n')
        print(tabulate(table2_data, headers=['Precision', f'Trade Output {output_token}'], tablefmt='pretty', colalign=colalign, disable_numparse=True))
        print('\n')

    def generate_guide_label(
        self,
        word: str, 
        total_length: int
        ) -> str:
        """
        ### Generates a visual guide label centered within a specified length.

        ## Parameters:
        | Parameter Name | Type     | Description                                               |
        |----------------|----------|-----------------------------------------------------------|
        | `word`         | `str`    | The word or phrase to be centered within the guide label. |
        | `total_length` | `int`    | The total length of the guide label, including hyphens.   |

        ## Returns:
        | Return Name | Type  | Description                                                                                           |
        |-------------|-------|-------------------------------------------------------------------------------------------------------|
        | `label`     | `str` | A string representing the guide label with the specified word centered and padded with hyphens (`-`). |

        ## Functionality:
        - Calculates the total number of hyphens needed to pad the word to reach the specified total length.
        - If the number of hyphens needed is even, the word is centered with an equal number of hyphens on each side.
        - If the number of hyphens needed is odd, one extra hyphen is added to the right side to maintain the total length.
        - Encloses the centered word with vertical bars (`|`) to visually demarcate the label.

        ## Notes:
        - This method is typically used to create visually distinct labels or headers within a console output or text display.
        - It aids in improving the readability and presentation of dynamic output, especially in tabulated data or summaries.
        """
        hyphens_total = total_length - len(word) - 2 
        if hyphens_total % 2 == 0:
            hyphens_side = hyphens_total // 2
            label = f"|{'-' * hyphens_side}{word}{'-' * hyphens_side}|"
        else:
            hyphens_left = hyphens_total // 2
            hyphens_right = hyphens_total - hyphens_left
            label = f"|{'-' * hyphens_left}{word}{'-' * hyphens_right}|"
        return label

    def print_compression_process_summary(
        self,
        parameter_name: str,
        rate_parameter_int: int, 
        truncated_rate_parameter: int, 
        exponent: int, 
        mantissa: int, 
        compressed_rate_parameter: int
        ) -> None:
        """
        ### Prints a detailed summary of the rate parameter compression process.

        ## Parameters:
        | Parameter Name             | Type  | Description                                                                                     |
        |----------------------------|-------|-------------------------------------------------------------------------------------------------|
        | `parameter_name`           | `str` | The name of the parameter being compressed.                                                     |
        | `rate_parameter_int`       | `int` | The integer representation of the rate parameter before compression.                            |
        | `truncated_rate_parameter` | `int` | The rate parameter after truncating to remove trailing zeroes.                                  |
        | `exponent`                 | `int` | The exponent extracted during compression, representing the number of trailing zeroes removed.  |
        | `mantissa`                 | `int` | The significant digits of the rate parameter after truncation.                                  |
        | `compressed_rate_parameter`| `int` | The final compressed form of the rate parameter combining exponent and mantissa.                |

        ## Returns:
        None. This method outputs the comparison directly to the console.

        ## Notes:
        - The method visualizes the compression process of a rate parameter, showing its transformation from a precise decimal to a compressed binary format.
        - It highlights the steps involved in truncating trailing zeroes, extracting the exponent and mantissa, and finally, combining these to form the compressed parameter.
        - Binary representations are used to illustrate how the parameter is manipulated at the bit level, including the segmentation of the binary string into exponent and mantissa parts.
        - Special characters (up arrows `↑` and down arrows `↓`) and appropriate labels are used to describe the parts of the binary numbers undergoing the compression.
        - This summary aids in understanding the efficiency and potential precision loss inherent in storing large numerical values in blockchain environments, where storage space is limited and costly.
        """
        up_arrow = '\u2191'
        down_arrow = '\u2193'
        bin_exponent = format(exponent, '06b')  
        bin_rate_param_int = bin(rate_parameter_int)[2:] 
        bin_truncated = bin(truncated_rate_parameter)[2:]
        bin_mantissa = bin(mantissa)[2:]
        bin_compressed = bin(compressed_rate_parameter)[2:].zfill(54)
        number_of_bits = rate_parameter_int.bit_length()
        down_arrow_string_length = min(number_of_bits, 48)
        up_arrow_string_length = number_of_bits - down_arrow_string_length
        down_arrow_string = down_arrow * down_arrow_string_length  
        up_arrow_string = up_arrow * up_arrow_string_length
        six_up_arrows = up_arrow * 6
        significand_label = self.generate_guide_label("significand", down_arrow_string_length)
        trailing_zeroes_label = self.generate_guide_label("trailing-zeroes", up_arrow_string_length) if up_arrow_string_length > 0 else ""
        mantissa_label = self.generate_guide_label("mantissa", down_arrow_string_length)
        table_data = [(f'precise {parameter_name} parameter (decimal float)', f'>>> {str(self.maker_precise_curve_parameters[parameter_name])}', ''),
                      (f'{parameter_name} parameter (decimal integer)', f'>>> {rate_parameter_int}', ''),
                      (f'{parameter_name} parameter (binary integer)', f'>>>       {bin_rate_param_int}', '(max 96 bits)'),
                      (f'truncated {parameter_name} parameter (binary integer)', f'>>>       {bin_truncated}', '(max 96 bits)'),
                      ('', f'>>>       {down_arrow_string + up_arrow_string}', ''),
                      ('', f'>>>       {significand_label + trailing_zeroes_label}', ''),
                      (f'{parameter_name} exponent (binary integer)', f'>>> {bin_exponent}', '(max 6 bits)'),
                      (f'{parameter_name} mantissa (binary integer)', f'>>>       {bin_mantissa}', '(max 48 bits)'),
                      (f'compressed {parameter_name} parameter (binary integer)', f'>>> {bin_compressed}', '(max 54 bits)'),
                      ('', f'>>> {six_up_arrows + down_arrow_string}', ''),
                      ('', f'>>> |expt|{mantissa_label}', ''),
                      (f'compressed {parameter_name} parameter (decimal integer)', f'>>> {compressed_rate_parameter}', '')]
        print(tabulate(table_data, headers=['Variable', 'Value', 'Note'], tablefmt='pretty', colalign=('right', 'left', 'left')))
        print('\n')

    def compress_rate_parameter(
        self,
        parameter_name: str, 
        print_process_summary: bool = True
        ) -> int:
        """
        ### Compresses a rate parameter for storage in blockchain environments.

        ## Parameters:
        | Parameter Name          | Type      | Description                                                                           |
        |-------------------------|-----------|---------------------------------------------------------------------------------------|
        | `parameter_name`        | `str`     | The name of the parameter to be compressed.                                           |
        | `print_process_summary` | `bool`    | Whether to print a detailed summary of the compression process (default is `True`).   |

        ## Returns:
        | Return Name                | Type  | Description                                                                      |
        |----------------------------|-------|----------------------------------------------------------------------------------|
        | `compressed_rate_parameter`| `int` | The compressed form of the rate parameter, optimized for blockchain storage.     |

        ## Notes:
        - This method reduces the size of rate parameters, making them suitable for efficient storage and processing on blockchain platforms.
        - The compression process involves:
            1. Converting the parameter to an integer, if not already.
            2. Truncating any trailing zeroes to minimize the parameter's size.
            3. Extracting an exponent representing the scale of truncation.
            4. Identifying the mantissa as the significant part of the parameter.
            5. Combining the exponent and mantissa into a single integer.
        - Optionally, a detailed visual summary of the compression process can be printed, illustrating the transformation of the parameter into its compressed form.
        - This method is crucial for understanding the use of smart contract storage, reducing gas costs, and maintaining acceptable accuracy.
        """
        rate_parameter_int = int(self.maker_precise_curve_parameters[parameter_name])
        number_of_bits = (rate_parameter_int // self.scaling_constant_int).bit_length()
        truncated_rate_parameter = (rate_parameter_int >> number_of_bits) << number_of_bits
        exponent = (truncated_rate_parameter // self.scaling_constant_int).bit_length()
        mantissa = truncated_rate_parameter >> exponent
        compressed_rate_parameter = mantissa | (exponent * self.scaling_constant_int)
        if print_process_summary:
            self.print_compression_process_summary(parameter_name,
                                                   rate_parameter_int,
                                                   truncated_rate_parameter,
                                                   exponent,
                                                   mantissa,
                                                   compressed_rate_parameter)
        return compressed_rate_parameter

    def decompress_rate_parameter(
        self, 
        compressed_rate_parameter : int
        ) -> int:
        """
        ### Decompresses a rate parameter back to its original form.

        ## Parameters:
        | Parameter Name              | Type  | Description                                                    |
        |-----------------------------|-------|----------------------------------------------------------------|
        | `compressed_rate_parameter` | `int` | The compressed form of the rate parameter to be decompressed.  |

        ## Returns:
        | Return Name                    | Type  | Description                                                             |
        |--------------------------------|-------|-------------------------------------------------------------------------|
        | `decompressed_rate_parameter`  | `int` | The decompressed rate parameter, restored to its pre-compression value. |

        ## Notes:
        - This method reverses the compression process applied to a rate parameter, reconstructing the original parameter from its compressed form.
        - The decompression process involves:
            1. Extracting the exponent and mantissa from the compressed parameter.
            2. Shifting the mantissa left by the value of the exponent to reintroduce the truncated bits.
        - The method leverages the fact that the compressed parameter combines the mantissa and exponent in a specific format, where the mantissa occupies the lower bits and the exponent the higher bits.
        - It is crucial for restoring rate parameters to their full precision for calculations or when presenting data outside the blockchain environment.
        - Decompression ensures that data can be accurately processed or analyzed after being retrieved from a compressed storage state.
        """
        decompressed_rate_parameter = (compressed_rate_parameter % self.scaling_constant_int) \
                                   << (compressed_rate_parameter // self.scaling_constant_int)
        return decompressed_rate_parameter

    def process_rate(
        self, 
        rate_value : Decimal,
        ) -> Decimal:
        """
        ### Processes a rate value for use in bonding curve calculations.

        ## Parameters:
        | Parameter Name | Type      | Description                                                     |
        |----------------|-----------|-----------------------------------------------------------------|
        | `rate_value`   | `Decimal` | The original rate value to be processed.                        |

        ## Returns:
        | Return Name        | Type      | Description                                                    |
        |--------------------|-----------|----------------------------------------------------------------|
        | `sqrt_rate_scaled` | `Decimal` | The processed rate value, scaled and adjusted for calculation. |

        ## Notes:
        - This method adjusts the rate value for use in subsequent bonding curve calculations, specifically for operations involving square roots.
        - The process involves taking the square root of the rate value (`rate_value ** (1 / 2)`) and then scaling it by a predefined scaling constant to ensure numerical stability and precision in the calculations.
        - The scaling constant is a significant factor in the processing, as it adjusts the magnitude of the rate value to fit within the expected range of values used in the bonding curve calculations.
        - This method is critical for preparing rate values, especially when dealing with large or small numbers, to prevent overflow or underflow in calculations.
        - The use of the `Decimal` type for both input and output ensures high precision in the mathematical operations, necessary for financial calculations where accuracy is paramount.
        """
        sqrt_rate_scaled = rate_value ** (self.ONE / self.TWO) * self.scaling_constant
        return sqrt_rate_scaled

    def calculate_z_parameter(
        self,
        y: Decimal,
        sqrt_P_a_scaled : Decimal,
        A: Decimal,
        M: Decimal,
        B: Decimal
        ) -> Decimal:
        """
        ### Calculates the z-parameter for a bonding curve.

        ## Parameters:
        | Parameter Name    | Type      | Description                                                                                      |
        |-------------------|-----------|--------------------------------------------------------------------------------------------------|
        | `y`               | `Decimal` | The liquidity in the pool, represented as the y-coordinate on the bonding curve.                 |
        | `sqrt_P_a_scaled` | `Decimal` | The square root of the high price parameter, `P_a`, after being scaled.                          |
        | `A`               | `Decimal` | The parameter representing the width of the price range in the bonding curve equation.           |
        | `M`               | `Decimal` | The marginal price parameter, representing the price at which the next incremental trade occurs. |
        | `B`               | `Decimal` | The low price parameter in the bonding curve equation.                                           |

        ## Returns:
        | Return Name | Type      | Description                                                                                                           |
        |-------------|-----------|-----------------------------------------------------------------------------------------------------------------------|
        | `z`         | `Decimal` | The z-parameter of the bonding curve, representing its y-intercept, calculated based on `y` and the price parameters. |

        ## Notes:
        - The z-parameter is a crucial component in the bonding curve calculations, representing the curve's y-intercept or the "initial liquidity" if the curve were extended backwards to the y-axis.
        - The calculation of `z` varies depending on whether `sqrt_P_a_scaled` equals `M`. If they are equal, `z` is simply `y`. Otherwise, `z` is calculated using the formula `y * A / (M - B)`, which adjusts `y` based on the curve's price parameters.
        - This method is essential for determining the position and shape of the bonding curve, influencing how trades impact the price and liquidity within the curve.
        - The use of `Decimal` for inputs and output ensures high precision in the calculations, which is critical for accurately modeling financial systems and predicting market dynamics.
        """
        z = y if sqrt_P_a_scaled == M else y * A / (M - B)
        return z
        
    def encode_bonding_curve_precise(
        self, 
        cleaned_inputs : Dict[str, Union[Decimal, int]]
        ) -> Dict[str, Decimal]:
        """
        ### Encodes bonding curve parameters using precise arithmetic based on cleaned inputs.

        ## Parameters:
        | Parameter Name    | Type                             | Description                                                              |
        |-------------------|----------------------------------|--------------------------------------------------------------------------|
        | `cleaned_inputs`  | `Dict[str, Union[Decimal, int]]` | A dictionary of standardized inputs for the bonding curve calculations.  |

        ## Returns:
        | Return Name        | Type                 | Description                                                                           |
        |--------------------|----------------------|---------------------------------------------------------------------------------------|
        | `curve_parameters` | `Dict[str, Decimal]` | A dictionary containing the encoded bonding curve parameters: `y`, `z`, `A`, and `B`. |

        ## Notes:
        - This method takes the standardized inputs for the bonding curve and calculates the precise arithmetic values of the curve parameters.
        - `sqrt_P_a_scaled`, `M`, and `B` are calculated from the cleaned inputs using the `process_rate` method, which adjusts the price parameters for precision and scaling.
        - The `A` parameter is derived as the difference between `sqrt_P_a_scaled` and `B`, representing the adjusted width of the price range.
        - The `z` parameter is calculated using the `calculate_z_parameter` method, which determines the initial position of the curve based on liquidity (`y`) and price parameters.
        - This method ensures that all bonding curve parameters are calculated with high precision, suitable for financial modeling and analysis where accuracy is paramount.
        - The returned dictionary of curve parameters is used for precise arithmetic calculations related to trades on the bonding curve, such as price impact and liquidity changes.
        """
        y = cleaned_inputs['y']
        sqrt_P_a_scaled, M, B = map(self.process_rate, (cleaned_inputs['P_a'], cleaned_inputs['P_m'], cleaned_inputs['P_b']))
        A = sqrt_P_a_scaled - B
        z = self.calculate_z_parameter(y, sqrt_P_a_scaled, A, M, B)
        return {'y' : y, 'z' : z, 'A' : A, 'B' : B}

    def encode_bonding_curve_fixed_point(
        self,
        ) -> Tuple[Dict[str, Decimal], Dict[str, int]]:
        """
        ### Encodes bonding curve parameters for fixed-point arithmetic, simulating blockchain contract calculations.

        ## Parameters:
        None

        ## Returns:
        A tuple of two dictionaries, detailed as follows:

        1. **Precise Calculation Parameters**:
            | Key   | Type     | Description                                                                 |
            |-------|----------|-----------------------------------------------------------------------------|
            | `y`   | `Decimal`| The liquidity parameter `y` for precise calculations.                       |
            | `z`   | `Decimal`| The curve parameter `z` for precise calculations.                           |
            | `A`   | `Decimal`| The curve parameter `A` after compression and decompression, for precision. |
            | `B`   | `Decimal`| The curve parameter `B` after compression and decompression, for precision. |

        2. **Fixed-Point Contract Simulation Parameters**:
            | Key            | Type  | Description                                                                  |
            |----------------|-------|------------------------------------------------------------------------------|
            | `y`            | `int` | The liquidity parameter `y` converted to integer for fixed-point arithmetic. |
            | `z`            | `int` | The invariant parameter `z` converted to integer for fixed-point arithmetic. |
            | `A_compressed` | `int` | The compressed value of curve parameter `A`, simulating blockchain storage.  |
            | `B_compressed` | `int` | The compressed value of curve parameter `B`, simulating blockchain storage.  |
            | `A`            | `int` | Decompressed value of `A`, simulating its use in contract calculations.      |
            | `B`            | `int` | Decompressed value of `B`, simulating its use in contract calculations.      |

        ## Notes:
        - This method takes the precise curve parameters calculated earlier and prepares them for simulations of blockchain contract behavior.
        - The `y` and `z` parameters are directly converted to integers from their precise `Decimal` values.
        - The `A` and `B` parameters are first compressed using `compress_rate_parameter` to simulate storage in a blockchain contract, which typically has limited precision and range.
        - The compressed parameters are then decompressed back to integers using `decompress_rate_parameter` to simulate how they would be used in contract calculations.
        - The method returns two representations of the curve parameters: one for precise calculations (as `Decimal`) and one for fixed-point contract simulations (as integers), allowing for comparison and analysis of precision loss.
        - This dual representation enables analysis of how fixed-point arithmetic and compression affect bonding curve operations in a smart contract environment.
        """
        y = int(self.maker_precise_curve_parameters['y'])
        z = int(self.maker_precise_curve_parameters['z'])
        A_compressed, B_compressed = map(self.compress_rate_parameter, ('A', 'B'))
        A, B = map(self.decompress_rate_parameter, (A_compressed, B_compressed))
        return {'y' : Decimal(y), 'z' : Decimal(z), 'A' : Decimal(A), 'B' : Decimal(B)}, \
               {'y' : y, 'z' : z, 'A_compressed' : A_compressed, 'B_compressed' : B_compressed, 'A' : A, 'B' : B}

    def trade_by_source_amount_precise(
        self, 
        Dx : Decimal, 
        y : Decimal, 
        z : Decimal, 
        A : Decimal, 
        B : Decimal
        ) -> Decimal:
        """
        ### Calculates the output amount for a given input when trading by source amount using precise arithmetic.

        ## Parameters:
        | Parameter Name | Type      | Description                                              |
        |----------------|-----------|----------------------------------------------------------|
        | `Dx`           | `Decimal` | The input amount of the source token.                    |
        | `y`            | `Decimal` | The liquidity parameter of the bonding curve.            |
        | `z`            | `Decimal` | The size parameter of the bonding curve (y-intercept).   |
        | `A`            | `Decimal` | The parameter representing the width of the price range. |
        | `B`            | `Decimal` | The low price parameter in the bonding curve equation.   |

        ## Returns:
        | Return Name | Type      | Description                                                 |
        |-------------|-----------|-------------------------------------------------------------|
        | `Dy`        | `Decimal` | The output amount of the target token for the given `Dx`.   |

        ## Notes:
        - This function uses precise decimal arithmetic to calculate the output `Dy` for a given input `Dx` based on the specified bonding curve parameters.
        - It applies the formula for trading by source amount on a bonding curve, utilizing the liquidity (`y`), invariant (`z`), and curve shape parameters (`A` and `B`).
        - The calculation ensures that trades are executed according to the precise dynamics of the bonding curve, allowing for accurate analysis of trade outcomes.
        """
        numerator = Dx * (B * z + A * y) ** self.TWO 
        denominator = Dx * A * (B * z + A * y) + (z * self.scaling_constant) ** self.TWO
        Dy = numerator / denominator
        return Dy

    def trade_by_target_amount_precise(
        self, 
        Dy : Decimal, 
        y : Decimal, 
        z : Decimal, 
        A : Decimal, 
        B : Decimal
        ) -> Decimal:
        """
        ### Calculates the input amount needed for a given target output amount using precise arithmetic.

        ## Parameters:
        | Parameter Name | Type      | Description                                                  |
        |----------------|-----------|--------------------------------------------------------------|
        | `Dy`           | `Decimal` | The target output amount of the target token.                |
        | `y`            | `Decimal` | The liquidity parameter of the bonding curve.                |
        | `z`            | `Decimal` | The size parameter of the bonding curve (y-intercept).       |
        | `A`            | `Decimal` | The parameter representing the width of the price range.     |
        | `B`            | `Decimal` | The low price parameter in the bonding curve equation.       |

        ## Returns:
        | Return Name | Type      | Description                                                     |
        |-------------|-----------|-----------------------------------------------------------------|
        | `Dx`        | `Decimal` | The input amount of the source token needed for the given `Dy`. |

        ## Notes:
        - This function uses precise decimal arithmetic to calculate the input `Dx` needed to achieve a specified output `Dy` based on the bonding curve parameters.
        - It applies the formula for trading by target amount on a bonding curve, utilizing the liquidity (`y`), invariant (`z`), and curve shape parameters (`A` and `B`).
        - The calculation is critical for understanding the cost of obtaining a specific amount of the target token, reflecting the precise mechanics of the bonding curve.
        """
        numerator = Dy * (z * self.scaling_constant) ** self.TWO
        denominator = (B * z + A * y) * ((B * z + A * y) - A * Dy)
        Dx =  numerator / denominator
        return Dx
    
    def trade_by_source_amount_fixed_point(
        self, 
        Dx : int, 
        y : int, 
        z : int, 
        A : int, 
        B : int
        ) -> int:
        """
        ### Simulates trading by source amount using fixed-point arithmetic to mimic smart contract behavior.

        ## Parameters:
        | Parameter Name | Type  | Description                                                                         |
        |----------------|-------|-------------------------------------------------------------------------------------|
        | `Dx`           | `int` | The input amount of the source token in integer units (wei).                        |
        | `y`            | `int` | The liquidity parameter of the bonding curve in integer units (wei).                |
        | `z`            | `int` | The size parameter of the bonding curve (y-intercept) in integer units (wei).       |
        | `A`            | `int` | The parameter representing the width of the price range in integer units (wei).     |
        | `B`            | `int` | The low price parameter in the bonding curve equation in integer units (wei).       |

        ## Returns:
        | Return Name | Type  | Description                                               |
        |-------------|-------|-----------------------------------------------------------|
        | `Dy`        | `int` | The output amount of the target token in integer units.   |

        ## Notes:
        - This method employs fixed-point arithmetic to emulate the computation logic found in blockchain smart contracts.
        - Steps:
            1. Special case handling when `A == 0` to simplify the calculation.
            2. Calculation of intermediate variables `temp1`, `temp2`, and `temp3` for modular computation steps.
            3. Application of scaling factors `factor1` and `factor2` to adjust calculations within uint256 limits.
            4. Final calculation of `Dy`, ensuring operations remain within the numeric bounds of smart contract environments.
        - Emphasizes accurate simulation of contract-level arithmetic and overflow handling.
        """
        if (A == 0):
            return Solidity.mulDivF(Dx, Solidity.mul(B, B), Solidity.mul(self.scaling_constant_int, self.scaling_constant_int))
        temp1 = Solidity.mul(z, self.scaling_constant_int)
        temp2 = Solidity.add(self.mul(y, A), self.mul(z, B))
        temp3 = Solidity.mul(temp2, Dx)
        factor1 = Solidity.mulDivC(temp1, temp1, Solidity.MAX_UINT256)
        factor2 = Solidity.mulDivC(temp3, A, Solidity.MAX_UINT256)
        factor = max(factor1, factor2)
        temp4 = Solidity.mulDivC(temp1, temp1, factor)
        temp5 = Solidity.mulDivC(temp3, A, factor)
        if temp4 + temp5 <= Solidity.MAX_UINT256:
            Dy = Solidity.mulDivF(temp2, temp3 // factor, Solidity.add(temp4, temp5))
        else:
            Dy = temp2 // Solidity.add(A, Solidity.mulDivF(temp1, temp1, temp3))
        return Dy
        
    def trade_by_target_amount_fixed_point(
        self, 
        Dy : int, 
        y : int, 
        z : int, 
        A : int, 
        B: int
        ) -> int:
        """
        ### Simulates trading by target amount using fixed-point arithmetic to mimic smart contract behavior.

        ## Parameters:
        | Parameter Name | Type  | Description                                                                         |
        |----------------|-------|-------------------------------------------------------------------------------------|
        | `Dy`           | `int` | The target output amount of the target token in integer units (wei).                |
        | `y`            | `int` | The liquidity parameter of the bonding curve in integer units (wei).                |
        | `z`            | `int` | The size parameter of the bonding curve (y-intercept) in integer units (wei).       |
        | `A`            | `int` | The parameter representing the width of the price range in integer units (wei).     |
        | `B`            | `int` | The low price parameter in the bonding curve equation in integer units (wei).       |

        ## Returns:
        | Return Name | Type  | Description                                                            |
        |-------------|-------|------------------------------------------------------------------------|
        | `Dx`        | `int` | The input amount of the source token in integer units needed for `Dy`. |

        ## Notes:
        - Utilizes fixed-point arithmetic to mirror the precision and constraints of smart contract operations.
        - Steps:
            1. Adjusts for a zero `A` parameter to simplify the calculation.
            2. Uses intermediate variables `temp1`, `temp2`, and `temp3` for step-wise calculation.
            3. Applies scaling to manage calculation within the numeric limits of blockchain computations.
            4. Determines `Dx` through fixed-point arithmetic methods, simulating on-chain transaction logic.
        - Aims to provide an accurate emulation of blockchain arithmetic, including overflow protections and scaling.
        """
        if (A == 0):
            return Solidity.mulDivC(Dy, Solidity.Solidity.mul(self.scaling_constant_int, self.scaling_constant_int), Solidity.mul(B, B))
        temp1 = Solidity.mul(z, self.scaling_constant_int)
        temp2 = Solidity.add(Solidity.mul(y, A), Solidity.mul(z, B))
        temp3 = Solidity.sub(temp2, Solidity.mul(Dy, A))
        factor1 = Solidity.mulDivC(temp1, temp1, Solidity.MAX_UINT256)
        factor2 = Solidity.mulDivC(temp2, temp3, Solidity.MAX_UINT256)
        factor = max(factor1, factor2)
        temp4 = Solidity.mulDivC(temp1, temp1, factor)
        temp5 = Solidity.mulDivF(temp2, temp3, factor)
        Dx = Solidity.mulDivC(Dy, temp4, temp5)
        return Dx

    def get_trade_functions(
        self,
        ) -> Tuple[
            Callable[[Decimal, Decimal, Decimal, Decimal, Decimal], Decimal],
            Callable[[int, int, int, int, int], int]]:
        """
        ### Selects the appropriate trade functions based on the specified trade mode.

        ## Parameters:
        None

        ## Returns:
        A tuple containing two functions:
        1. The first function is for precise arithmetic calculations.
        2. The second function is for fixed-point arithmetic calculations to mimic smart contract behavior.

        | Return Type                                                           | Description                                                                 |
        |-----------------------------------------------------------------------|-----------------------------------------------------------------------------|
        | `Tuple[Callable[[Decimal, ...], Decimal], Callable[[int, ...], int]]` | Tuple of two callables, one for precise and one for fixed-point arithmetic. |

        ## Notes:
        - This method determines which set of trade functions to use based on the `trade_mode` attribute of the class.
        - If `trade_mode` is 'trade_by_source', it selects functions that calculate trade outputs given a source amount.
        - If `trade_mode` is 'trade_by_target', it selects functions that calculate trade inputs required for a target amount.
        - The first function in the tuple uses `Decimal` for inputs and output, suitable for high-precision calculations.
        - The second function uses `int` for inputs and output, simulating the integer-based arithmetic of blockchain smart contracts.
        - This allows for flexible simulation of trade calculations, comparing outcomes between precise and blockchain-like environments.
        """
        return (self.trade_by_source_amount_precise, self.trade_by_source_amount_fixed_point) if self.trade_mode == 'trade_by_source' else \
               (self.trade_by_target_amount_precise, self.trade_by_target_amount_fixed_point)

# %%
# instance = AccuracyAnalysis(
#     risk_token = 'BTC',
#     cash_token = 'DAI',
#     strategy_mode = 'buy',
#     risk_decimals = Decimal('8'),
#     cash_decimals = Decimal('18'),
#     low_price = Decimal('40_000'),
#     high_price = Decimal('50_000'),
#     marginal_price = Decimal('45_000'),
#     liquidity = Decimal('10_000'),
#     trade_mode = 'tradeByTarget',
#     trade_input = Decimal('100'),
# )

# %%



