# ------------------------------------------------------------
# Auto generated test file `test_049_CPCBalancer.py`
# ------------------------------------------------------------
# source file   = NBTest_049_CPCBalancer.py
# test id       = 049
# test comment  = CPCBalancer
# ------------------------------------------------------------



from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
#from flbtools.cpc import ConstantProductCurve as CPC
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))

from fastlane_bot.testing import *
#from flbtesting import *
from math import sqrt




# ------------------------------------------------------------
# Test      049
# File      test_049_CPCBalancer.py
# Segment   Constant product constructor
# ------------------------------------------------------------
def test_constant_product_constructor():
# ------------------------------------------------------------
    
    c0 = CPC.from_xy(100, 200)
    assert c0.x == 100
    assert c0.y == 200
    assert c0.k == 20000
    assert c0.x == c0.x_act
    assert c0.y == c0.y_act
    assert c0.alpha == 0.5
    assert c0.eta == 1
    assert c0.constr == "xy"
    assert c0.is_constant_product() == True
    c0
    
    assert c0.asdict() == {
        'k': 20000,
        'x': 100,
        'x_act': 100,
        'y_act': 200.0,
        'alpha': 0.5,
        'pair': 'TKNB/TKNQ',
        'cid': 'None',
        'fee': None,
        'descr': None,
        'constr': 'xy',
        'params': {}
    }
    
    c1 = CPC.from_xyal(100, 200)
    assert c1.constr == "xyal"
    assert c1.is_constant_product() == True
    assert c1==c0
    c1
    
    assert c1.asdict() == {
        'k': 20000,
        'x': 100,
        'x_act': 100,
        'y_act': 200.0,
        'alpha': 0.5,
        'pair': 'TKNB/TKNQ',
        'cid': 'None',
        'fee': None,
        'descr': None,
        'constr': 'xyal',
        'params': {}
    }
    
    c2 = CPC.from_xyal(100, 200, alpha=0.5)
    assert c2.constr == "xyal"
    assert c2.is_constant_product() == True
    assert c2==c0
    assert c2.asdict() == c1.asdict()
    c2
    
    c3 = CPC.from_xyal(100, 200, eta=1)
    assert c3.constr == "xyal"
    assert c3.is_constant_product() == True
    assert c3==c0
    assert c3.asdict() == c1.asdict()
    c3
    
    assert raises(CPC.from_xyal, 100, 200, 
           alpha=0.5, eta=1) == 'at most one of alpha and eta must be given [0.5, 1]'
    

# ------------------------------------------------------------
# Test      049
# File      test_049_CPCBalancer.py
# Segment   Weighted constructor
# ------------------------------------------------------------
def test_weighted_constructor():
# ------------------------------------------------------------
    
    c0 = CPC.from_xy(100, 200)
    assert c0.x == 100
    assert c0.y == 200
    assert c0.k == 20000
    assert c0.x == c0.x_act
    assert c0.y == c0.y_act
    assert c0.alpha == 0.5
    assert c0.eta == 1
    assert c0.constr == "xy"
    assert c0.is_constant_product() == True
    c0
    
    c1 = CPC.from_xyal(100, 200)
    assert c1.constr == "xyal"
    assert c1.is_constant_product() == True
    assert c1 == c0
    assert c1.asdict()["alpha"] == 0.5
    c1
    
    c2 = CPC.from_xyal(100, 200, alpha=0.25)
    assert c2.constr == "xyal"
    assert c2.is_constant_product() == False
    assert c2.alpha == 0.25
    assert c2.asdict()["alpha"] == 0.25
    assert iseq(c2.eta, 0.25/0.75)
    assert c2 != c0
    assert c2 != c1
    c2
    
    c3 = CPC.from_xyal(100, 200, alpha=0.8)
    assert c3.constr == "xyal"
    assert c3.is_constant_product() == False
    assert iseq(c3.alpha, 0.8)
    assert c3.asdict()["alpha"] == 0.8
    assert iseq(c3.eta, 0.8/0.2)
    assert c3 != c0
    assert c3 != c1
    assert c3 != c2
    c2
    
    c3b = CPC.fromdict(c3.asdict())
    assert c3b == c3
    c3b
    
    assert raises(CPC.from_xyal,100, 200, alpha=0) == 'alpha must be > 0 [0]'
    assert raises(CPC.from_xyal,100, 200, alpha=-1) == 'alpha must be > 0 [-1]'
    assert raises(CPC.from_xyal,100, 200, alpha=1) == 'alpha must be < 1 [1]'
    assert raises(CPC.from_xyal,100, 200, alpha=2) == 'alpha must be < 1 [2]'
    
    raises(CPC.from_xyal,100, 200, alpha=0)
    
    assert not raises(CPC.from_xyal,100, 200, alpha=1-1e-10)
    assert not raises(CPC.from_xyal,100, 200, alpha=0.01)
    
    raises(CPC.from_xyal,100, 200, alpha=0.001)
    

# ------------------------------------------------------------
# Test      049
# File      test_049_CPCBalancer.py
# Segment   High level testing of all functions
# ------------------------------------------------------------
def test_high_level_testing_of_all_functions():
# ------------------------------------------------------------
    #
    # (including not YET implemented)
    
    c0 = CPC.from_xyal(100, 200)
    assert c0.is_constant_product() == True
    c0
    
    c1 = CPC.from_xyal(100, 200, alpha=0.25)
    assert c1.is_constant_product() == False
    c1
    
    # #### Not (yet) implemented functions
    #
    # Those function groups are not currently planned to be implemented at all
    #
    # - `execute` as there is no need to simulate those curves for the time being; that was a Carbon thing
    #
    # The functions we may implement at a later stage are
    #
    # - `description` should probably be updated, but it is tedious; `format` ditto
    # - `x_max`, `x_min`, `p_max`, `p_min` and the other leverage functions once we consider it important and safe
    
    # execute
    
    assert not raises(c0.execute)
    assert raises(c1.execute).startswith("only implemented for")
    
    # description and format
    
    assert not raises(c0.description)
    assert raises(c1.description).startswith("only implemented for")
    
    assert not raises(c0.format)
    assert raises(c1.format).startswith("only implemented for")
    
    # leverage related functions (primary)
    
    assert not raises(lambda: c0.p_max)
    assert raises(lambda: c1.p_max).startswith("only implemented for")
    
    assert not raises(lambda: c0.p_min)
    assert raises(lambda: c1.p_min).startswith("only implemented for")
    
    assert not raises(lambda: c0.x_min)
    assert raises(lambda: c1.x_min).startswith("only implemented for")
    
    assert not raises(lambda: c0.x_max)
    assert raises(lambda: c1.x_max).startswith("only implemented for")
    
    assert not raises(lambda: c0.y_min)
    assert raises(lambda: c1.y_min).startswith("only implemented for")
    
    assert not raises(lambda: c0.y_max)
    assert raises(lambda: c1.y_max).startswith("only implemented for")
    
    # leverage related functions (secondary, ie calling primary ones)
    
    assert not raises(c0.p_max_primary)
    assert raises(c1.p_max_primary).startswith("only implemented for")
    
    assert not raises(c0.p_min_primary)
    assert raises(c1.p_min_primary).startswith("only implemented for")
    
    assert not raises(lambda: c0.at_xmin)
    assert raises(lambda: c1.at_xmin).startswith("only implemented for")
    
    assert not raises(lambda: c0.at_xmax)
    assert raises(lambda: c1.at_xmax).startswith("only implemented for")
    
    assert not raises(lambda: c0.at_ymin)
    assert raises(lambda: c1.at_ymin).startswith("only implemented for")
    
    assert not raises(lambda: c0.at_ymax)
    assert raises(lambda: c1.at_ymax).startswith("only implemented for")
    
    assert not raises(lambda: c0.at_boundary)
    assert raises(lambda: c1.at_boundary).startswith("only implemented for")
    
    # todo
    
    assert not raises(c0.xyfromp_f)
    assert raises(c1.xyfromp_f).startswith("only implemented for")
    
    assert not raises(c0.dxdyfromp_f)
    assert raises(c1.dxdyfromp_f).startswith("only implemented for")
    
    # #### Implemented functions
    
    assert not raises(lambda: c0.y)
    assert not raises(lambda: c1.y)
    
    assert not raises(lambda: c0.p)
    assert not raises(lambda: c1.p)
    
    assert not raises(lambda: c0.kbar)
    assert not raises(lambda: c1.kbar)
    
    assert not raises(c0.tvl)
    assert not raises(c1.tvl)
    
    assert not raises(c0.yfromx_f, 110)
    assert not raises(c1.yfromx_f, 110, ignorebounds=True)
    assert raises(c1.yfromx_f, 110, ignorebounds=False)
    
    assert not raises(c0.xfromy_f, 210)
    assert not raises(c1.xfromy_f, 110, ignorebounds=True)
    assert raises(c1.xfromy_f, 110, ignorebounds=False)
    
    assert not raises(c0.dyfromdx_f, 1)
    assert not raises(c1.dyfromdx_f, 1, ignorebounds=True)
    assert raises(c1.dyfromdx_f, 1, ignorebounds=False)
    
    assert not raises(c0.dxfromdy_f, 1)
    assert not raises(c1.dxfromdy_f, 1, ignorebounds=True)
    assert raises(c1.dxfromdy_f, 1, ignorebounds=False)
    

# ------------------------------------------------------------
# Test      049
# File      test_049_CPCBalancer.py
# Segment   Simple Tests
# ------------------------------------------------------------
def test_simple_tests():
# ------------------------------------------------------------
    
    c0 = CPC.from_xyal(100, 200)
    c1 = CPC.from_xyal(100, 200, eta=2)
    c2 = CPC.from_xyal(100, 200, eta=0.5)
    
    assert iseq(c0.alpha, 1/2)
    assert iseq(c1.alpha, 2/3)
    assert iseq(c2.alpha, 1/3)
    
    # #### Current token balance $y$
    #
    # $$
    # y = \left( \frac k x \right)^\eta
    # $$
    
    assert iseq(c0.y, 200)
    assert iseq(c1.y, 200)
    assert iseq(c2.y, 200)
    
    # #### Current price $p$
    #
    # $$
    # p = \eta\, \frac y x
    # $$
    
    assert iseq(c0.p, 2 * c0.eta)
    assert iseq(c1.p, 2 * c1.eta)
    assert iseq(c2.p, 2 * c2.eta)
    
    # #### TVL
    #
    # $$
    # \mathrm{TVL} = x_a*p + y_a
    # $$
    
    assert c0.x == c0.x_act
    assert c0.y == c0.y_act
    assert c1.x == c1.x_act
    assert c1.y == c1.y_act
    assert c2.x == c2.x_act
    assert c2.y == c2.y_act
    
    assert iseq(c0.tvl(), 100 * c0.p + 200)
    assert iseq(c1.tvl(), 100 * c1.p + 200)
    assert iseq(c2.tvl(), 100 * c2.p + 200)
    
    # #### Pool constant $k$
    #
    # $$
    # k^\alpha = x^\alpha\, y^{1-\alpha}
    # $$
    #
    # $$
    # k = x\,y^\frac{1-\alpha}{\alpha} = x\,y^{\frac 1 \eta}
    # $$
    #
    
    assert iseq(c0.k**(1/2), c0.x**(1/2) * c0.y**(1/2))
    assert iseq(c1.k**(2/3), c1.x**(2/3) * c1.y**(1/3))
    assert iseq(c2.k**(1/3), c1.x**(1/3) * c1.y**(2/3))
    
    # #### Pool constant $\bar k$
    #
    # $$
    # x^\alpha\, y^{1-\alpha} = \bar k = k^\alpha
    # $$
    
    assert iseq(c0.kbar, c0.x**(1/2) * c0.y**(1/2))
    assert iseq(c1.kbar, c1.x**(2/3) * c1.y**(1/3))
    assert iseq(c2.kbar, c1.x**(1/3) * c1.y**(2/3))
    
    assert iseq(c0.kbar, c0.k**c0.alpha)
    assert iseq(c1.kbar, c1.k**c1.alpha)
    assert iseq(c2.kbar, c2.k**c2.alpha)
    
    # #### Token balance function $y(x)$
    #
    # $$
    # y(x) = \left( \frac k x \right)^\eta
    # $$
    
    assert c0.eta == 1
    assert iseq(c0.yfromx_f(100, ignorebounds=True),  200)
    assert iseq(c0.yfromx_f( 50, ignorebounds=True),  400)
    assert iseq(c0.yfromx_f(200, ignorebounds=True),  100)
    
    assert iseq(c1.eta, 2)
    assert iseq(c1.yfromx_f(100, ignorebounds=True),  200)
    assert iseq(c1.yfromx_f( 50, ignorebounds=True),  200*2**2)
    assert iseq(c1.yfromx_f(200, ignorebounds=True),  200/2**2)
    
    assert iseq(c2.eta, 1/2)
    assert iseq(c2.yfromx_f(100, ignorebounds=True),  200)
    assert iseq(c2.yfromx_f( 50, ignorebounds=True),  200*sqrt(2))
    assert iseq(c2.yfromx_f(200, ignorebounds=True),  200/sqrt(2))
    
    # #### Token balance function $x(y)$
    #
    # $$
    # x(y) 
    # = \frac{k}{ y^{\frac{1-\alpha}{\alpha}} }
    # = \frac{k}{ y^{\frac{1}{\eta}} }
    # $$
    
    assert c0.eta == 1
    assert iseq(c0.xfromy_f(200, ignorebounds=True),  100)
    assert iseq(c0.xfromy_f(100, ignorebounds=True),  200)
    assert iseq(c0.xfromy_f(400, ignorebounds=True),   50)
    
    assert iseq(c1.eta, 2)
    assert iseq(c1.xfromy_f(200, ignorebounds=True),  100)
    assert iseq(c1.xfromy_f(100, ignorebounds=True),  100*2**0.5)
    assert iseq(c1.xfromy_f(400, ignorebounds=True),  100/2**0.5)
    
    assert iseq(c2.eta, 1/2)
    assert iseq(c2.xfromy_f(200, ignorebounds=True),  100)
    assert iseq(c2.xfromy_f(100, ignorebounds=True),  100*2**2)
    assert iseq(c2.xfromy_f(400, ignorebounds=True),  100/2**2)
    
    # #### Price response function $(x(p), y(p))$
    #
    # $$
    # x(p) 
    # = 
    # \left(\frac \eta p\right)^{1-\alpha} k^\alpha
    # $$
    #
    # $$
    # y(p) = \left( \frac{kp}{\eta}  \right)^\alpha
    # $$
    
    assert iseq(c0.xyfromp_f(c0.p, ignorebounds=True)[0], c0.x)
    assert iseq(c1.xyfromp_f(c1.p, ignorebounds=True)[0], c1.x)
    assert iseq(c2.xyfromp_f(c2.p, ignorebounds=True)[0], c2.x)
    
    assert iseq(c0.xyfromp_f(c0.p, ignorebounds=True)[1], c0.y)
    assert iseq(c1.xyfromp_f(c1.p, ignorebounds=True)[1], c1.y)
    assert iseq(c2.xyfromp_f(c2.p, ignorebounds=True)[1], c2.y)
    
    for ci in [c0, c1, c2]:
        for p in [2, 1, 4]:
            eta_over_p = ci.eta / p
            x = eta_over_p ** (1-ci.alpha) * ci.kbar
            y = 1/eta_over_p**ci.alpha * ci.kbar
            xx, yy, pp = ci.xyfromp_f  (p, ignorebounds=True)
            dx, dy, _  = ci.dxdyfromp_f(p, ignorebounds=True)
            assert iseq(x, xx)
            assert iseq(y, yy)
            assert iseq(p, pp)
            assert iseq(dx, xx-ci.x)
            assert iseq(dy, yy-ci.y)
    

# ------------------------------------------------------------
# Test      049
# File      test_049_CPCBalancer.py
# Segment   Consistency tests
# ------------------------------------------------------------
def test_consistency_tests():
# ------------------------------------------------------------
    
    c0 = CPC.from_xyal(100, 200)
    c1 = CPC.from_xyal(100, 200, eta=2)
    c2 = CPC.from_xyal(100, 200, eta=0.5)
    cc = [c0, c1, c2]
    
    assert iseq(c0.alpha, 1/2)
    assert iseq(c1.alpha, 2/3)
    assert iseq(c2.alpha, 1/3)
    
    # ### Assert inversions
    #
    # $$
    # y(x(y)) = y
    # $$
    #
    # and vice versa
    
    for xy in np.logspace(1, 3, 100):
        for ci in cc:
            #print(f"xy={xy}, eta={ci.eta}")
            assert iseq(ci.yfromx_f(ci.xfromy_f(xy, ignorebounds=True), ignorebounds=True), xy)
            assert iseq(ci.xfromy_f(ci.yfromx_f(xy, ignorebounds=True), ignorebounds=True), xy)
    
    # ### Assert that prices are correct
    #
    # $$
    # p \simeq -\frac{\Delta y}{\Delta x}
    # $$
    
    for alpha in np.linspace(0.01, 0.99, 100):
        ci = CPC.from_xyal(100, 200, alpha=alpha)
        dy = ci.yfromx_f(ci.x+0.1, ignorebounds=True)-ci.yfromx_f(ci.x-0.1, ignorebounds=True)
        assert iseq(dy/0.2, -ci.p, eps=1e-2), f"error: {dy/0.2/ci.p+1}"
    
    # ### Check `dyfromdx_f` against `yfromx_f`
    
    for dxy in np.linspace(0.1, 99, 100):
        for ci in cc:
            assert iseq(ci.dyfromdx_f(dxy, ignorebounds=True),
                        (ci.yfromx_f(ci.x+dxy, ignorebounds=True)-ci.y))
            assert iseq(ci.dxfromdy_f(dxy, ignorebounds=True),
                        (ci.xfromy_f(ci.y+dxy, ignorebounds=True)-ci.x))
    

# ------------------------------------------------------------
# Test      049
# File      test_049_CPCBalancer.py
# Segment   Charts [NOTEST]
# ------------------------------------------------------------
def notest_charts():
# ------------------------------------------------------------
    
    plt.style.use('seaborn-v0_8-dark')
    plt.rcParams['figure.figsize'] = [12,6] # only picked up at second run (?!?)
    
    c0 = CPC.from_xyal(100, 200)
    c1 = CPC.from_xyal(100, 200, eta=2)
    c2 = CPC.from_xyal(100, 200, eta=0.5)
    cc = [c0, c1, c2]
    xvals = np.linspace(50,200)
    pvals = np.linspace(1,4)
    
    for ci in cc:
        plt.plot(xvals, [ci.yfromx_f(x, ignorebounds=True) for x in xvals], label=f"eta={ci.eta:0.2f}")
    plt.grid()
    plt.legend()
    plt.title("Indifference curve token balance y vs token balance x at different weights")
    plt.xlabel("Token balance x [native units]")
    plt.ylabel("Token balance y [native units]")
    plt.show()
    
    for ci in cc:
        plt.plot(
            xvals, 
            [
                -(ci.yfromx_f(x+0.1, ignorebounds=True) - ci.yfromx_f(x-0.1, ignorebounds=True))/0.2
                for x in xvals
            
            ], 
            label=f"eta={ci.eta:0.2f}")
    plt.grid()
    plt.legend()
    plt.title("Price vs token balance x at different weights")
    plt.xlabel("Token balance x [native units]")
    plt.ylabel("Price [dy/dx]")
    plt.show()
    
    for ci in cc:
        plt.plot(
            pvals, 
            [
                ci.xyfromp_f(p, ignorebounds=True)[1]
                for p in pvals
            
            ], 
            label=f"eta={ci.eta:0.2f}")
    plt.grid()
    plt.legend()
    plt.title("Token balance y vs price at different weights")
    plt.xlabel("Price [dy/dx]")
    plt.ylabel("Token balance y [native units]")
    plt.show()
    
    
    
    