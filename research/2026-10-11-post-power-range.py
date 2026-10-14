"""Exact arithmetic experiments for the rug's dimension-dependent post-power."""
from collections import Counter
import json
from pathlib import Path


def valuation(p):
    return (p & -p).bit_length() - 1


def odd_inputs(domain):
    return range(1, domain, 2)


def exponent_key(domain, p):
    """Exact canonical exponent for all odd inputs, D >= 8."""
    v = valuation(p)
    return v, (p >> v) % (domain // 4)


def values(domain, p, bases):
    modulus = domain * (p & -p)
    return tuple(pow(z, p, modulus) for z in bases)


def coefficient(domain, v, u, bases):
    modulus = domain << v
    return tuple((pow(z, (1 << v) * u, modulus) - 1) // (1 << v) for z in bases)


def or_inputs(domain, pre, diagonal):
    """Complete motif, in its actual diagonal or straight coordinates."""
    side = domain // 2
    outputs = set()
    for y in range(side):
        for x in range(side):
            a, b = ((y - x - 1) % domain, (y + x) % domain) if diagonal else (y, x)
            outputs.add((pow(a, pre, domain) | pow(b, pre, domain)))
    return sorted(outputs)


def run():
    checks = Counter()
    range_results = []
    for d in range(3, 10):
        domain = 1 << d
        count = domain * domain // 32 - 1
        keys = {exponent_key(domain, 2*q) for q in range(1, count+1)}
        assert len(keys) == (d-1)*domain//8 - 1
        range_results.append({"domain": domain,"old_q_choices": count,
            "odd_function_choices": domain//8,"even_function_modulus_pairs": len(keys),
            "largest_v": 2*d-5,"normalized_stability_v": max(1,d-3)})
        for v in range(0, 2*d+2):
            modulus = domain << v
            for u in [1,3,5,domain//4-1,domain//4+1,3*domain//4+3]:
                p = (1 << v)*u
                canonical = (1 << v)*(u % (domain//4))
                for z in odd_inputs(domain):
                    assert pow(z,p,modulus) == pow(z,canonical,modulus)
                    checks['odd_exponent_equivalence'] += 1
            start = max(1,d-3)
            if v >= start:
                assert coefficient(domain,v,1,odd_inputs(domain)) == coefficient(domain,start,1,odd_inputs(domain))
                checks['normalized_xor_stability'] += 1
            if v >= max(1,d-4):
                a = coefficient(domain,v,1,odd_inputs(domain))
                for u in [3,5,7,11]:
                    au = coefficient(domain,v,u,odd_inputs(domain))
                    assert au == tuple(u*x % domain for x in a)
                    checks['odd_part_is_channel_multiplier'] += 1
        if d >= 5:
            early = max(1,d-3)-1
            assert coefficient(domain,early,1,odd_inputs(domain)) != coefficient(domain,early+1,1,odd_inputs(domain))
            checks['stability_bound_sharp'] += 1
    # Exhaustively classify actual raw odd tables for the smaller domains.
    for d in range(3, 8):
        domain = 1 << d
        for v in range(0, d+2):
            tables = {values(domain,(1 << v)*u,odd_inputs(domain)) for u in range(1,domain//4,2)}
            assert len(tables) == domain//8
            checks['distinct_odd_tables'] += 1
    or_results=[]
    for d in range(3, 10):
        domain = 1 << d
        for pre in [2,4]:
            period = max(1,domain//(1 << pre))
            for diagonal in [True,False]:
                bases = or_inputs(domain,pre,diagonal)
                odd = [z for z in bases if z%2]
                even = [z for z in bases if z and not z%2]
                assert all(z % (1 << pre) == 1 for z in odd)
                assert all(valuation(z) >= pre for z in even)
                for v in range(0,d+2):
                    modulus = domain << v
                    delta = (1 << v)*period
                    # Odd inputs have the short period; even inputs require saturation.
                    for u in [1,3,5,7]:
                        p=(1 << v)*u
                        for z in bases:
                            if z%2 or pre*p >= d+v or not z:
                                assert pow(z,p,modulus) == pow(z,p+delta,modulus)
                                checks['or_period_and_saturated_tail'] += 1
                    if odd:
                        start=max(0,d-(2*pre-1))
                        if v>=start:
                            assert coefficient(domain,v,1,odd)==coefficient(domain,start,1,odd)
                            checks['or_normalized_stability'] += 1
                or_results.append({"domain":domain,"pre":pre,"diagonal":diagonal,
                    "combined_values":len(bases),"odd_values":len(odd),"even_nonzero_values":len(even),
                    "odd_part_period":period,"odd_stability_v":max(0,d-(2*pre-1))})
    assert pow(4,1,64) != pow(4,17,64)
    assert pow(5,1,64) == pow(5,17,64)
    # Fixed draw values: stable coefficients leave only a cyclic channel offset.
    for d in [6,8,11,15]:
        domain=1 << d; start=max(1,d-3)
        a=2*0xACF51234321+1; b=0xFA241623124
        for v in range(start,start+5):
            modulus=domain << v
            for z,A in zip(odd_inputs(domain),coefficient(domain,v,3,odd_inputs(domain))):
                assert (a*pow(z,3 << v,modulus)+b)%modulus == (a+b+(1 << v)*(a%domain)*A)%modulus
                checks['stable_channel_offset_identity'] += 1
    result={"checks":dict(checks),"total_checks":sum(checks.values()),"range_results":range_results,"or_results":or_results}
    target=Path(__file__).with_suffix('.json')
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({"total_checks":result['total_checks'],"range_results":range_results},indent=2))




def favorite_examples():
    """Verify reductions against saved random arithmetic, without editing files."""
    root=Path(__file__).resolve().parents[1]
    results=[]
    for file in sorted((root/'saved-settings').glob('*.json')):
        s=json.loads(file.read_text())
        for name in ['field','inner','main','outer']:
            source_name='inner' if name=='outer' and s['lock'] else name
            style=s['styles'][source_name]
            ref=s.get('references',{}).get(source_name)
            if s.get('resizeModes',{}).get(source_name)=='adapt':
                ref=None
            if ref:
                domain=2*ref['period'] if ref['period'] else 2*(1 << (max(ref['width'],ref['height'])-1).bit_length())
            else:
                domain=2*(1 << (int((2**s['k'])*s['aspect'])-1).bit_length()) if name=='field' else s['border']*(2 if name=='main' else 1)
            p=style['power'];v=valuation(p);u=p >> v;d=domain.bit_length()-1
            pre=1 if style['family']=='xor' else int(style['family'])
            if pre==1:
                period=max(1,domain//4) if v or domain>=8 else max(1,domain//2)
                bases=list(odd_inputs(domain))
            else:
                period=max(1,domain//(1 << pre))
                bases=[z for z in range(domain) if (z%2 and z%(1<<pre)==1) or (not z%2 and z%(1<<pre)==0)]
            candidate=(1 << v)*(u%period if period>1 else 1)
            straight=pre!=1 and style.get('basis')=='straight'
            if straight:
                if pre*p < d+v:
                    candidate=p
                else:
                    while pre*candidate<d+v:
                        candidate+=(1 << v)*max(2,period)
            if not straight:
                bases=[z for z in bases if z%2]
            M=domain << v
            assert values(domain,p,bases)==values(domain,candidate,bases)
            # The stored affine channel parameters have the same modulus.
            assert valuation(candidate)==v
            results.append({'file':file.name,'region':name,'domain':domain,'power':p,'equivalent_power':candidate,'v':v,'bases_checked':len(bases)})
    target=Path(__file__).with_suffix('.json')
    result=json.loads(target.read_text());result['favorite_reductions']=results
    result['favorite_bases_checked']=sum(x['bases_checked'] for x in results)
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(f"Verified {len(results)} saved region reductions across {result['favorite_bases_checked']} reachable/superset bases.")




def spatial_periods():
    results=[]
    for d in range(3,9):
        D=1 << d;T=D//2
        for pre in [1,2,4]:
            for diagonal in ([True] if pre==1 else [True,False]):
                combined=[]
                for y in range(T):
                    for x in range(T):
                        a,b=((y-x-1)%D,(y+x)%D) if diagonal else (x,y)
                        a,b=pow(a,pre,D),pow(b,pre,D)
                        combined.append(a^b if pre==1 else a|b)
                for v in range(0,d+2):
                    for u in [1,3,5]:
                        p=(1 << v)*u;M=D << v
                        lookup={z:pow(z,p,M) for z in set(combined)}
                        table=[lookup[z] for z in combined]
                        def period(axis):
                            shift=1
                            while shift<T:
                                if all(table[y*T+x]==table[((y+shift)%T)*T+x if axis=='y' else y*T+(x+shift)%T] for y in range(T) for x in range(T)):
                                    return shift
                                shift*=2
                            return T
                        px,py=period('x'),period('y')
                        expected=T if pre in [1,2] else D//4 if D>=32 else 1 if diagonal else 2
                        assert px==py==expected,(D,pre,diagonal,p,px,py,expected)
                        results.append({'domain':D,'pre':pre,'diagonal':diagonal,'power':p,'axis_period':px})
    target=Path(__file__).with_suffix('.json')
    result=json.loads(target.read_text());result['spatial_period_checks']=len(results)
    result['spatial_periods']=results
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(f'Confirmed {len(results)} complete motif spatial-period cases.')


if __name__ == '__main__':
    run()
    favorite_examples()
    spatial_periods()
