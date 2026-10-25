"""Exact research checks and figures; run with Python 3 + NumPy + Matplotlib.

No application changes. All equality/classification tests use Python integers.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
CHECKS = Counter()


def check(condition, category):
    CHECKS[category] += 1
    if not condition:
        raise AssertionError(category)


def valuation(n):
    return math.inf if n == 0 else (abs(n) & -abs(n)).bit_length() - 1


def combine(a, b, op):
    return a ^ b if op == 'xor' else a & b if op == 'and' else a | b


def poly(x, coefficients):
    result = 0
    for coefficient in reversed(coefficients):
        result = result * x + coefficient
    return result


def raw_grid(C, op='xor', q=1, basis='diagonal', sample=(1, 0, 0, 1, 0, 0), pre=None):
    """Rows y, columns x. sample = integer matrix B followed by phase e."""
    b00, b01, b10, b11, e0, e1 = sample
    rows = []
    for j in range(C):
        row = []
        for i in range(C):
            x, y = b00*i+b01*j+e0, b10*i+b11*j+e1
            a, b = (y-x-1, y+x) if basis == 'diagonal' else (x, y)
            a, b = a % C, b % C
            a = pow(a, q, C) if pre is None else poly(a, pre) % C
            b = pow(b, q, C) if pre is None else poly(b, pre) % C
            row.append(combine(a, b, op))
        rows.append(row)
    return rows


def power_grid(raw, p, M):
    return [[pow(z, p, M) for z in row] for row in raw]


def flat(grid):
    return tuple(itertools.chain.from_iterable(grid))


def periods(grid):
    C = len(grid)
    def okay(d, axis):
        return all(grid[y][x] == grid[(y+d*(axis == 1)) % C][(x+d*(axis == 0)) % C]
                   for y in range(C) for x in range(C))
    return tuple(next(d for d in (1 << k for k in range(C.bit_length())) if okay(d, axis))
                 for axis in (0, 1))


def primitive(values, M):
    origin = values[0]
    s = min([valuation(M)] + [valuation(z-origin) for z in values])
    Q = M >> int(s)
    return Q, tuple(((z-origin) % M) >> int(s) for z in values)


def affine_key(values, M):
    """Anchor first position at zero; first odd difference at one.

    This is linear-time and unique, unlike trying all odd multipliers.
    """
    Q, values = primitive(tuple(values), M)
    if Q == 1:
        return 1, values
    odd = next(z for z in values if z & 1)
    inverse = pow(odd, -1, Q)
    return Q, tuple(z * inverse % Q for z in values)


def partition_key(values):
    names = {}
    return tuple(names.setdefault(z, len(names)) for z in values)


def symmetries(grid, k=0, l=0):
    """D4 about (k/2,l/2), restricted to lattice-preserving transforms."""
    C = len(grid)
    transforms = {
        'mx': lambda x,y:(k-x,y), 'my': lambda x,y:(x,l-y),
        'r180':lambda x,y:(k-x,l-y),
    }
    if (k-l) % 2 == 0:
        transforms.update({
            'diag':lambda x,y:(y+(k-l)//2,x+(l-k)//2),
            'anti':lambda x,y:((k+l)//2-y,(k+l)//2-x),
            'r90':lambda x,y:((k+l)//2-y,x+(l-k)//2),
            'r270':lambda x,y:(y+(k-l)//2,(k+l)//2-x),
        })
    result = []
    for name, transform in transforms.items():
        if all(grid[y][x] == grid[transform(x,y)[1] % C][transform(x,y)[0] % C]
               for y in range(C) for x in range(C)):
            result.append(name)
    return result


def shift_depth(raw, p, shift, axis):
    C = len(raw)
    return min(power_difference_valuation(raw[y][x], raw[(y+shift*(axis == 1)) % C][(x+shift*(axis == 0)) % C], p)
               for y in range(C) for x in range(C))


def power_difference_valuation(a, b, p):
    if a == b:
        return math.inf
    if a == 0 or b == 0:
        return p * valuation(a or b)
    t, u = valuation(a), valuation(b)
    if t != u:
        return p * min(t, u)
    a, b = a >> t, b >> t
    return p*t + valuation(a-b) if p & 1 else p*t+valuation(a-b)+valuation(a+b)+valuation(p)-1


def modulus_interval(raw, p, R):
    lower = max(shift_depth(raw, p, R//2, axis) for axis in (0,1)) + 1 if R > 1 else 1
    upper = min(shift_depth(raw, p, R, axis) for axis in (0,1))
    return lower, upper


def pre_power_period(c, q):
    if q & 1:
        return 1 << c
    w = valuation(q)
    return 2 if c <= min(q, w+2) else 1 << max(2, c-w)


def samples():
    return {
        'full': (1,0,0,1,0,0),
        'checker-even': (1,1,1,-1,0,0),
        'checker-odd': (1,1,1,-1,1,0),
        **{f'decimate-{a}{b}':(2,0,0,2,a,b) for a in (0,1) for b in (0,1)},
    }


def factorial_ranges(m):
    ranges = []
    factorial = 1
    k = 0
    while valuation(factorial) < m:
        ranges.append(1 << (m-valuation(factorial)))
        k += 1
        factorial *= k
    return ranges


def exponent_classes(raw, M):
    values=set(flat(raw))
    evens=[valuation(z) for z in values if z and not z&1]
    S=math.ceil(valuation(M)/min(evens)) if evens else 1
    T=1
    for z in values:
        if z&1:
            order=1
            while pow(z,order,M)!=1:
                order*=2
            T=max(T,order)
    return S,T


def falling_table(coefficients, M):
    values = []
    for x in range(M):
        product, value = 1, 0
        for k, coefficient in enumerate(coefficients):
            value += coefficient*product
            product *= x-k
        values.append(value % M)
    return tuple(values)


def run_checks():
    results = {'source_commit':'e1fde1ca97c9644511d4b4e9a264f532a75b1090'}
    for a in range(32):
        for b in range(32):
            for p in range(1,17):
                check(power_difference_valuation(a,b,p) == valuation(a**p-b**p), 'power_difference_LTE')
    for c in range(1,9):
        C = 1 << c
        for q in range(1,65):
            values = [pow(x,q,C) for x in range(C)]
            actual = next(1<<k for k in range(c+1) if all(values[x] == values[(x+(1<<k)) % C] for x in range(C)))
            check(actual == pre_power_period(c,q), 'pre_power_period')
    xor_counts = []
    for c in range(5,10):
        C = 1 << c
        rows, orbit_sets, partitions = [], [], set()
        for v in range(c-3):
            exact, affine = set(), set()
            M = C << v
            for u in range(1,C//4,2):
                A = tuple(((pow(z,(1<<v)*u,M)-1) % M) >> v for z in range(1,C,2))
                exact.add(A)
                affine.add(affine_key(A,C))
                partitions.add(partition_key(A))
            rows.append(len(exact))
            orbit_sets.append(affine)
        xor_counts.append({'C':C,'exact_per_v':rows,'affine_per_v':[len(s) for s in orbit_sets],
                           'affine_union':len(set.union(*orbit_sets)), 'partitions':len(partitions),
                           'affine_overlaps':[[i,j,len(orbit_sets[i]&orbit_sets[j])] for i in range(len(rows)) for j in range(i) if orbit_sets[i]&orbit_sets[j]]})
        check(rows == [C//8]*(c-3), 'old_XOR_count')
    results['xor_classes'] = xor_counts
    for item in xor_counts:
        C=item['C']; c=C.bit_length()-1
        expected=[C//8]+[1<<max(0,c-v-5) for v in range(1,c-3)]
        check(item['affine_per_v']==expected,'XOR_affine_count')
        check(item['affine_union']==5*C//32,'XOR_affine_union')
        check(item['partitions']==2,'XOR_two_partitions')
    # An even affine class is indexed by k in Z/(C/32), through 25**k.
    for c in range(5,10):
        C=1<<c; W=C//32
        keys=set()
        for k in range(W):
            v,u=(c-4,1) if k==0 else (valuation(k)+1,k>>valuation(k))
            M=C<<v
            A=tuple(((pow(z,(1<<v)*u,M)-1)%M)>>v for z in range(1,C,2))
            keys.add(affine_key(A,C))
        check(len(keys)==W,'XOR_even_single_index')
        if c>5:
            # Restriction to low odd residues, then reduction, is the natural
            # projection of the primitive coefficient motifs.
            smallC=C//2
            for k in range(W):
                v,u=(c-4,1) if k==0 else (valuation(k)+1,k>>valuation(k))
                sk=k%(smallC//32)
                sv,su=(c-5,1) if sk==0 else (valuation(sk)+1,sk>>valuation(sk))
                left=tuple(((pow(z,(1<<v)*u,C<<v)-1)%(C<<v))>>v for z in range(1,smallC,2))
                right=tuple(((pow(z,(1<<sv)*su,smallC<<sv)-1)%(smallC<<sv))>>sv for z in range(1,smallC,2))
                check(affine_key(left,smallC)==affine_key(right,smallC),'XOR_even_projective_index')
    inventory = []
    for C in (8,16,32):
        for op,q,basis in itertools.product(('xor','and','or'), (1,2,3,4,6,8), ('straight','diagonal')):
            raw = raw_grid(C,op,q,basis)
            for p in (1,2,3,4,6,8):
                v = valuation(p)
                M = C << v
                grid = power_grid(raw,p,M)
                rx,ry = periods(grid)
                if rx == ry:
                    lower,upper = modulus_interval(raw,p,rx)
                    check(lower <= valuation(M) <= upper, 'modulus_interval')
                    if lower != math.inf:
                        check(periods(power_grid(raw,p,1<<int(lower))) == (rx,ry), 'minimal_modulus')
                inventory.append({'C':C,'op':op,'q':q,'basis':basis,'p':p,'M':M,'period':[rx,ry],
                                  'support':len(set(flat(grid))), 'sym_cell':symmetries(grid,-1,-1),
                                  'sym_vertex':symmetries(grid,0,0),'sym_legacy':symmetries(grid,-1,0)})
    results['inventory'] = inventory
    for op,q,p in itertools.product(('xor','and','or'),(2,4,6,8),(1,2,3,4)):
        grid=power_grid(raw_grid(32,op,q),p,32 << valuation(p))
        check(len(symmetries(grid,-1,1))==7,'even_pre_centered_D4')
    sample_inventory=[]
    for op,q,p in itertools.product(('xor','and','or'),(1,2,4),(1,2,4)):
        for name,sample in samples().items():
            C=32; M=C << valuation(p)
            grid=power_grid(raw_grid(C,op,q,'diagonal',sample),p,M)
            sample_inventory.append({'op':op,'q':q,'p':p,'sample':name,'period':periods(grid),
                                     'support':len(set(flat(grid))),'sym_cell':symmetries(grid,-1,-1),
                                     'sym_vertex':symmetries(grid,0,0),'sym_legacy':symmetries(grid,-1,0)})
    results['samples']=sample_inventory
    for C in (8,16,32,64,128):
        for p in (1,2,3,4,6,8,10,16):
            M=C << valuation(p)
            grids=[power_grid(raw_grid(C,'xor',1,'diagonal',samples()[name]),p,M)
                   for name in ('checker-even','checker-odd')]
            check(grids[0]==grids[1],'checker_phases_equal')
            if not p&1:
                check(len(symmetries(grids[0],-1,-1))==7,'checker_even_D4')
            check(periods(grids[0])==(C//2,C//2),'checker_exact_period')
    finite_catalogue=[]
    for op,q,basis in itertools.product(('xor','and','or'),(1,2,4),('straight','diagonal')):
        C=32;M=64;raw=raw_grid(C,op,q,basis);S,T=exponent_classes(raw,M)
        all_tables={};selected={}
        for p in range(1,S+T):
            grid=power_grid(raw,p,M);table=flat(grid);all_tables[table]=p
            if periods(grid)==(16,16):selected[table]=p
        check(len(all_tables)==S-1+T,'fixed_modulus_exponent_count')
        for p in range(S+T,S+T+20):
            can=S+(p-S)%T
            check(power_grid(raw,p,M)==power_grid(raw,can,M),'fixed_modulus_exponent_tail')
        finite_catalogue.append({'op':op,'q':q,'basis':basis,'C':C,'M':M,'S':S,'T':T,
                                 'all_power_tables':len(all_tables),'period16_tables':len(selected),
                                 'period16_affine_classes':len({affine_key(t,M) for t in selected}),
                                 'period16_partitions':len({partition_key(t) for t in selected})})
    results['fixed_precision_catalogue']=finite_catalogue
    and_depths=[]
    for q in range(1,9):
        C=512;values=flat(raw_grid(C,'and',q));nonzero=[z for z in values if z]
        d=min(map(valuation,nonzero),default=math.inf)
        check(d==(4 if q==2 else q),'AND_minimum_valuation')
        and_depths.append({'C':C,'q':q,'minimum_nonzero_valuation':d})
    results['and_depths']=and_depths
    and_raw=raw_grid(64,'and',2)
    check(set(flat(and_raw))=={0,16,32},'AND_infinite_family_support')
    and_unbounded=[]
    for p in range(1,17):
        lo,hi=modulus_interval(and_raw,p,32)
        M=1<<(5*p+1)
        grid=power_grid(and_raw,p,M)
        check(lo==5*p+1 and hi==math.inf,'AND_infinite_family_minimal_modulus')
        check(primitive(flat(grid),M)[0]==1<<(p+1),'AND_infinite_family_precision')
        and_unbounded.append({'p':p,'minimal_m':int(lo),'primitive_Q':1<<(p+1)})
    results['AND_infinite_fixed_period_family']=and_unbounded
    infinite_example=[]
    raw=raw_grid(4,'and',1,'straight')
    for N in range(1,9):
        M=1<<(N+2)
        g=[[poly(z,(0,10+(1<<N),-9,2))%M for z in row] for row in raw]
        lower=[[z%(M//2) for z in row] for row in g]
        check(periods(g)==(4,4) and periods(lower)==(2,2),'unbounded_minimal_modulus')
        check(primitive(flat(g),M)[0]==M,'unbounded_primitive_precision')
        infinite_example.append({'N':N,'minimal_M':M,'primitive_Q':M})
        evenM=1<<(N+3)
        even_grid=[[poly(z*z,(0,68+(1<<N),-25,2))%evenM for z in row] for row in raw]
        even_lower=[[z%(evenM//2) for z in row] for row in even_grid]
        check(periods(even_grid)==(4,4) and periods(even_lower)==(2,2),'even_polynomial_unbounded_modulus')
        check(primitive(flat(even_grid),evenM)[0]==evenM,'even_polynomial_unbounded_precision')
    results['infinite_fixed_period_example']=infinite_example
    for c in range(3,7):
        C=1<<c;lam=C//4
        tables={tuple(pow(x,q,C) for x in range(C)) for q in range(1,c+lam)}
        check(len(tables)==c-1+lam,'pre_power_function_count')
        for q in range(c,c+3*lam):
            can=c+(q-c)%lam
            check(all(pow(x,q,C)==pow(x,can,C) for x in range(C)),'pre_power_function_tail')
    pre_list=[(0,1),(0,1,1),(0,0,1,0,2),(1,1,2)]
    post_list=[(0,1),(0,1,1),(0,0,1,0,1),(0,2,1)]
    for op,basis,pre,post in itertools.product(('xor','and','or'),('straight','diagonal'),pre_list,post_list):
        C=8;raw=raw_grid(C,op,basis=basis,pre=pre)
        integer=[[poly(z,post) for z in row] for row in raw]
        def depth(d,axis):
            return min(valuation(integer[y][x]-integer[(y+d*(axis==1))%C][(x+d*(axis==0))%C]) for y in range(C) for x in range(C))
        for R in (2,4,8):
            lo=1+max(depth(R//2,axis) for axis in (0,1));hi=min(depth(R,axis) for axis in (0,1))
            for m in range(1,9):
                reduced=[[z%(1<<m) for z in row] for row in integer]
                check((periods(reduced)==(R,R))==(lo<=m<=hi),'polynomial_modulus_interval')
    # Complete arbitrary integer pre/post polynomial functions at C=M=4.
    polynomial_tables={falling_table(c,4) for c in itertools.product(range(4),range(4),range(2),range(2))}
    unrestricted=[]
    for basis in ('straight','diagonal'):
        family_sets={}
        for op in ('xor','and','or'):
            attained=set()
            for pre in polynomial_tables:
                raw=[]
                for y in range(4):
                    for x in range(4):
                        a,b=((y-x-1)%4,(y+x)%4) if basis=='diagonal' else (x,y)
                        raw.append(combine(pre[a],pre[b],op))
                for post in polynomial_tables:
                    attained.add(tuple(post[z] for z in raw))
            family_sets[op]=attained
            unrestricted.append({'C':4,'M':4,'basis':basis,'op':op,'exact_tables':len(attained),
                                 'affine_classes':len({affine_key(t,4) for t in attained})})
        check(family_sets['and']==family_sets['or'],'unrestricted_polynomial_AND_OR_duality')
    results['unrestricted_polynomial_small_catalogue']=unrestricted
    for C in (8,16,32):
        for q in (1,2,3,4,6,8):
            for basis in ('straight','diagonal'):
                grids={op:raw_grid(C,op,q,basis) for op in ('xor','and','or')}
                for y in range(C):
                    for x in range(C):
                        a,b=((y-x-1)%C,(y+x)%C) if basis=='diagonal' else (x,y)
                        a,b=pow(a,q,C),pow(b,q,C)
                        check((a|b)==C-1-((C-1-a)&(C-1-b)), 'De_Morgan')
                        check((a^b)==(a|b)-(a&b), 'Boolean_identity')
                        if basis=='diagonal':
                            check(grids['xor'][y][x] == grids['xor'][y][(-x-1)%C], 'shared_pre_mirror')
    for m in (1,2,3):
        M=1<<m; ranges=factorial_ranges(m)
        tables={falling_table(c,M) for c in itertools.product(*(range(r) for r in ranges))}
        check(len(tables)==math.prod(ranges), 'factorial_uniqueness')
        results.setdefault('polynomial_counts',[]).append({'M':M,'ranges':ranges,'functions':len(tables)})
    # Canonical affine key against an independently enumerated group action.
    for M in (2,4,8):
        groups={}
        for table in itertools.product(range(M),repeat=3):
            key=affine_key(table,M)
            orbit=min(tuple((a*z+b)%M for z in table) for a in range(1,M,2) for b in range(M))
            if key in groups:
                check(groups[key]==orbit,'affine_key_complete')
            groups[key]=orbit
        check(len(groups)==len(set(groups.values())),'affine_key_injective')
    results['check_counts']=dict(CHECKS)
    return results


def metrics(grid, M):
    a=np.array(grid,dtype=np.int64); counts=np.unique(a,return_counts=True)[1]
    probability=counts/counts.sum()
    phase=np.exp(1j*math.tau*a/M)
    return {'support':len(counts),'entropy_bits':float(-np.sum(probability*np.log2(probability))),
            'largest_mass':float(probability.max()),
            'phase_resultant':float(abs(phase.mean())),
            'equality_x':float(np.mean(a==np.roll(a,1,axis=1))),
            'equality_y':float(np.mean(a==np.roll(a,1,axis=0))),
            'phase_difference_x':float(np.mean(abs(phase-np.roll(phase,1,axis=1))**2)),
            'phase_difference_y':float(np.mean(abs(phase-np.roll(phase,1,axis=0))**2))}


def figures():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    configurations=[('XOR · pre 1','xor',1,2),('AND · pre 2','and',2,2),
                    ('OR · pre 2','or',2,2),('OR · pre 4','or',4,2)]
    fig,axes=plt.subplots(2,4,figsize=(13,7),layout='constrained')
    output=[]
    for column,(name,op,q,p) in enumerate(configurations):
        for row,C in enumerate((128,512)):
            M=C << valuation(p)
            grid=power_grid(raw_grid(C,op,q),p,M)
            axes[row,column].imshow(np.array(grid)/M,cmap='gray',vmin=0,vmax=1,interpolation='nearest')
            axes[row,column].set_title(f'{name}\nC={C}, p={p}, M={M}',fontsize=10)
            axes[row,column].set_axis_off()
            output.append({'op':op,'q':q,'p':p,'C':C,'M':M,**metrics(grid,M)})
    fig.suptitle('Numerical motifs under the historical modulus rule\nSame phase mapping; panels show a C × C window, before color styling',fontsize=13)
    fig.savefig(ROOT/'scale-comparison.png',dpi=160)
    plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(11,4),layout='constrained')
    C=64
    for axis,(name,sample) in zip(axes,[('Full lattice',samples()['full']),('Checkerboard phase 0',samples()['checker-even']),('Checkerboard phase 1',samples()['checker-odd'])]):
        grid=power_grid(raw_grid(C,'xor',1,'diagonal',sample),2,2*C)
        axis.imshow(np.array(grid)/(2*C),cmap='gray',vmin=0,vmax=1,interpolation='nearest')
        axis.set_title(name);axis.set_axis_off()
    fig.suptitle('Sampling changes the displayed lattice, period, and symmetry',fontsize=13)
    fig.savefig(ROOT/'sampling-comparison.png',dpi=160)
    plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(12,3.8),layout='constrained')
    lags=[1,2,4,8,16,32,64,128]
    lag_metrics=[]
    for axis,(title,op,q,sample) in zip(axes,[('XOR, full lattice','xor',1,samples()['full']),
                                           ('XOR, checkerboard','xor',1,samples()['checker-even']),
                                           ('OR, pre-power 2','or',2,samples()['full'])]):
        a=np.array(power_grid(raw_grid(512,op,q,'diagonal',sample),2,1024))
        ex=[float(np.mean(a==np.roll(a,d,axis=1))) for d in lags]
        ey=[float(np.mean(a==np.roll(a,d,axis=0))) for d in lags]
        axis.plot(lags,ex,'o-',color='black',label='horizontal')
        axis.plot(lags,ey,'s--',color='0.55',label='vertical')
        axis.set_xscale('log',base=2);axis.set_ylim(-0.03,1.03)
        axis.set_title(title);axis.set_xlabel('Lag in material cells');axis.set_ylabel('Equal-value fraction')
        axis.legend(fontsize=8)
        lag_metrics.append({'name':title,'lags':lags,'horizontal':ex,'vertical':ey})
    fig.suptitle('Directional equality across scales · C=512, p=2, M=1024',fontsize=13)
    fig.savefig(ROOT/'directional-equality.png',dpi=160)
    plt.close(fig)
    (ROOT/'lag-metrics.json').write_text(json.dumps(lag_metrics,indent=2)+'\n')
    return output


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--figures',action='store_true');args=parser.parse_args()
    results=run_checks()
    if args.figures:
        results['scale_metrics']=figures()
    (ROOT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({'checks':results['check_counts'],'xor_classes':results['xor_classes'],
                      'polynomial_counts':results['polynomial_counts']},indent=2))
