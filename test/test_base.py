from CryptoGladiator.balance import (Balance, BalanceDelta)

def test_balance():
    a=Balance()
    b=Balance({ETH:11, USD:88 })
    c=Balance({ETH:22, EUR:12, LTC:0 })
    d=Balance({ETH:22, EUR:12, BTC:0})
    s=Balance({ETH:33, EUR:12, USD:88})

    d1 = BalanceDelta({ETH:22, LTC:15, GNT:22 })

    assert d==c
    assert c==d
    assert b+c==s
    assert d+d1 == Balance({ETH:44, LTC:15, GNT:22, EUR:12})
    assert d.add(ETH,10) == Balance({ETH:32, EUR:12, BTC:0})

    x,y = s.split(d1)
    assert x == Balance({ETH:22, EUR:0, GNT:0})
    assert y == Balance({ETH:11, EUR:12, USD:88})

    assert s-BalanceDelta({ETH:33, EUR:2}) == BalanceDelta({ETH:0, EUR:10 , USD:88, BTC:0 })
    assert s+BalanceDelta({ETH:1, GNT:2}) == Balance({ETH:34, EUR:12, USD:88, GNT:2})

    b['ETH'] = 123
    assert b['eth'] == 123
