# Weighted Constant Product Formulas

**Parameter definitions**

- $x,y$ are the token balances in their native units
- $\alpha$ is the weight of the $x$ token ($1/2$ is standard constant product)
- $\lambda = {\alpha}/{1-\alpha}$ is the weight ratio, equivalent to $\alpha$ but providing a different parameterization
- $k$ the pool invariant

Formula D1. (Definition of lambda)
$$
\lambda = \frac{\alpha}{1-\alpha}
$$

Formula D2. (Reverse lambda)
$$
\alpha = \frac{\lambda}{1-\lambda}
$$

Formula D3. (Lambda relationship)
$$
\frac{1}{\lambda-1} = \alpha - 1
$$

Formula 1. (Invariant)
$$
x^\alpha y^{1-\alpha} = k^\alpha
$$

Formula 2, 3. (y in terms of x)
$$
y(x) = 
\left(\frac{k}{x}\right)^{\frac{\alpha}{1-\alpha}} =
\left(\frac{k}{x}\right)^\lambda
$$

Formula 4. (marginal price)
$$
p = \frac{dy}{dx} = \lambda k^\lambda x^{\lambda-1} = \lambda \frac{y}{x}
$$

Formula 5. (x in terms of p)
$$
x(p) = k^\alpha \left(\frac{p}{\lambda}\right)^{\alpha-1}
$$

Formula 6. (x in terms of p)
$$
y(p) = k^\alpha \left(\frac{p}{\lambda}\right)^{\alpha}
$$



