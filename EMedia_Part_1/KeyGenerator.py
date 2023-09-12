from math import gcd


def KeysG(p,q):
    O = (p-1)*(q-1)
    n = p*q
    e = pub(O)
    d = priv(O,e)

    return (e,d,n)

def pub(O):
    e = int(O/8)
    while 1:
        NWD = gcd(e,O)
        if NWD == 1:
            return e
        else:
            e=e-1
    return

def priv(O,e):
    d = 0
    while 1:
        if (d*e)%O == 1:
            return d
        else: d=d+1
    return