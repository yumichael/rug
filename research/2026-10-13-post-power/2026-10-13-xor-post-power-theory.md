# XOR post-power theory for the rug generator

## Purpose and motivation

The rug generator applies a **post-power** after its diagonal XOR combiner. Historically, the generator chose a fairly large integer exponent $p$, and chose the power-of-two modulus $M$ from both the coordinate domain and $p$. That construction was originally motivated empirically: it seemed to preserve the intended motif period while producing visually varied rugs.

The questions behind this research were therefore practical:

- Does sampling larger and larger integer exponents actually produce new XOR patterns, or does it mostly revisit old ones?
- Why does the historical rule $M = C \mathrm{lowbit}(p)$ preserve the intended repetition period?
- What happens if the coordinate domain $C$ and modulus $M$ are varied independently?
- Given a desired spatial period $R$, what choices of $C$, $M$, and $p$ are sufficient or redundant?
- If $p = 2^v u$ with $u$ odd, what does the odd part $u$ control, and what does the power-of-two valuation $v$ control?
- Is there a finite point beyond which increasing $v$ gives no new spatial arithmetic motifs?
- If the goal is to sample **distinct exponent patterns uniformly**, rather than integers uniformly, how should $v$ and $u$ be sampled?

The resulting theory separates naturally into three parts:

1. **$C/M$ theory:** how the coordinate domain and modulus determine the surviving spatial period;
2. **odd-part theory:** exact repetitions as the odd factor $u$ of the exponent changes;
3. **valuation theory:** what genuinely new structure appears as $v$ increases, and where the high-$v$ tail becomes redundant.

This document focuses only on the **diagonal XOR combiner**. OR-family combiners are intentionally deferred to a later addendum.

---

## 1. Construction and assumptions

### 1.1 Coordinate domain and diagonal XOR

Let

$$
C=2^c
$$

be the power-of-two coordinate lookup domain.

The earlier research document used $D$ for this quantity. This report uses $C$ instead so that $R$ can denote a spatial repetition period.

For integer cell coordinates $(x,y)$, define

$$
a_C(x,y)=(y-x-1)\bmod C,
$$

$$
b_C(x,y)=(y+x)\bmod C.
$$

The value sent into the post-power is

$$
z_C(x,y)=a_C(x,y)\mathbin{\mathrm{XOR}}b_C(x,y).
$$

#### Lemma 1: every diagonal-XOR input is odd

Modulo $2$,

$$
a_C+b_C\equiv (y-x-1)+(y+x)=2y-1\equiv1.
$$

Thus $a_C$ and $b_C$ have opposite parity. XOR preserves the low bit as the XOR of the low bits, so

$$
\boxed{z_C(x,y)\text{ is always odd}.}
$$

This is the central simplification behind the XOR theory: post-powering acts only on odd residues modulo powers of two.

#### Lemma 2: the complete motif encounters every odd residue modulo _C_

Let $z$ be any odd residue with $1\le z<C$. Choose

$$
x=\frac{z-1}{2}, \qquad y=\frac{z+1}{2}.
$$

Then

$$
y-x-1=0, \qquad y+x=z,
$$

and therefore

$$
z_C(x,y)=0\mathbin{\mathrm{XOR}}z=z.
$$

After the natural periodic wrapping of the motif, this shows that every odd residue modulo $C$ is represented.

Consequently, a distinction that can be witnessed on one odd residue such as $5$ is a genuine distinction somewhere in the complete XOR motif.

---

### 1.2 Exponent decomposition

The post-power exponent is assumed positive:

$$
p>0.
$$

Write it uniquely as

$$
\boxed{p=2^v u}
$$

where

$$
v=\nu_2(p)\ge0
$$

is the number of factors of $2$ dividing $p$, and

$$
u\ge1
$$

is odd.

Equivalently,

$$
2^v=\mathrm{lowbit}(p).
$$

The case $p=0$ is separate: $z^0=1$ for all XOR inputs, so it gives a constant post-power value for a fixed positive modulus. Under the bitwise definition, $\mathrm{lowbit}(0)=0$, while $\nu_2(0)$ is undefined or conventionally $+\infty$. The balanced rule would give $M=0$, so it does not define a valid modulus in this case.

---

### 1.3 Modulus and post-power

Let the modulus be a power of two,

$$
M=2^m.
$$

The arithmetic post-power motif is

$$
F_{C,p,M}(x,y) = z_C(x,y)^p\bmod M.
$$

The historical rug rule is

$$
\boxed{M=C\,2^v=C\mathrm{lowbit}(p).}
$$

We will call this the **balanced rule**.

For a general power-of-two $M$, define

$$
\boxed{ K=\frac{M}{2^v} =\frac{M}{\mathrm{lowbit}(p)} =2^{m-v}. }
$$

The quantity $K$ is the effective post-power domain. It will be the second participant, alongside $C$, in the period theorem.

Unless explicitly discussing tiny degeneracies, the clean $C/M$ theorems below assume

$$
C\ge8,\qquad K\ge8.
$$

These are the nondegenerate sizes relevant to normal rug motifs.

---

## 2. Several notions of “the same pattern”

Before giving the main results, it is important to distinguish different equivalence notions.

Two parameter choices can have:

1. **the same exact post-power values** $z^p\bmod M$;

2. **the same normalized spatial arithmetic motif**, meaning the same position-dependent structure after a constant phase-like term is removed;

3. **the same channel values with the existing channel parameters held fixed**;

4. **the same family of possible colored rugs after channel phases or multipliers are allowed to be retuned**;

5. **the same final RGB pixels** after all color-space transformations, sine mappings, quantization, and other rendering operations.

These are not equivalent statements.

The odd-part theorem below gives exact equality of the raw post-power values at fixed $v$.

The high-$v$ valuation theory eventually gives equality only of the **spatial coefficient motif** unless one additionally compensates for a changing global channel phase.

This distinction is essential when deciding which repetitions should count as redundant for a generator.

---

## 3. _C_/_M_ theory

The first question is:

> For fixed $p$, how do $C$ and $M$ determine the exact spatial repetition period?

The answer is especially clean for powers of two.

---

### 3.1 _A_ standard 2-adic lemma

We will repeatedly use the following form of the lifting-the-exponent principle.

If $x$ and $y$ are odd and $n$ is even, then

$$
\nu_2(x^n-y^n) = \nu_2(x-y)+\nu_2(x+y)+\nu_2(n)-1.
$$

Because two odd integers have even sum,

$$
\nu_2(x+y)\ge1.
$$

This is the mechanism by which a factor $2^v$ in the exponent supplies an additional $2^v$ of congruence in the output.

---

### 3.2 The post-power only needs the input modulo _K_

#### Claim: The post-power only needs the input modulo _K_

Let

$$
p=2^v u,\qquad u\text{ odd},
$$

$$
M=2^m,
$$

and

$$
K=2^{m-v}.
$$

For odd integers $z_1,z_2$,

$$
z_1\equiv z_2\pmod K
$$

implies

$$
\boxed{ z_1^p\equiv z_2^p\pmod M. }
$$

#### Proof: The post-power only needs the input modulo _K_

If $v=0$, then $K=M$, so the claim is immediate.

Now suppose $v\ge1$. By the 2-adic lifting formula,

$$
\nu_2(z_1^p-z_2^p) = \nu_2(z_1-z_2) + \nu_2(z_1+z_2) + v-1.
$$

Since

$$
z_1\equiv z_2\pmod K,
$$

we have

$$
\nu_2(z_1-z_2)\ge m-v.
$$

Since both are odd,

$$
\nu_2(z_1+z_2)\ge1.
$$

Therefore

$$
\nu_2(z_1^p-z_2^p) \ge (m-v)+1+v-1 = m.
$$

Hence

$$
M=2^m \mid z_1^p-z_2^p,
$$

which proves the claim.

#### Interpretation

Once $p$ and $M$ are fixed, the post-power cannot distinguish two odd inputs that agree modulo

$$
K=M/\mathrm{lowbit}(p).
$$

So $K$, rather than $M$ alone, is the effective amount of input information surviving exponentiation.

---

### 3.3 Growing _C_ eventually changes nothing at all

#### Claim: Growing _C_ eventually changes nothing at all

If

$$
C\ge K,
$$

then increasing the power-of-two coordinate domain $C$ further does not merely preserve the same period. It preserves the **entire post-powered arithmetic motif**:

$$
\boxed{ F_{C,p,M}(x,y)=F_{K,p,M}(x,y) }
$$

for every cell $(x,y)$.

#### Proof: Growing _C_ eventually changes nothing at all

Because $C$ and $K$ are powers of two and $C\ge K$,

$$
K\mid C.
$$

Therefore

$$
a_C(x,y)\equiv a_K(x,y)\pmod K,
$$

and

$$
b_C(x,y)\equiv b_K(x,y)\pmod K.
$$

Reduction modulo a power of two keeps only the low bits. Bitwise XOR in those low bits depends only on the low bits of its operands. Hence

$$
z_C(x,y)\equiv z_K(x,y)\pmod K.
$$

Both values are odd. By the preceding theorem,

$$
z_C(x,y)^p \equiv z_K(x,y)^p \pmod M.
$$

Thus the exact residue modulo $M$ is identical at every cell.

#### Consequence

$$
\boxed{ C\ge K \quad\Longrightarrow\quad \text{all larger }C\text{ are exactly redundant for the post-power motif.} }
$$

This is stronger than merely saying that the repetition period has stopped growing.

---

### 3.4 The raw XOR motif has axis period _C_/2

Let

$$
T=C/2.
$$

Shift $x$ by $T$. Modulo $C$, this toggles the top bit of both diagonal coordinates:

$$
a_C(x+T,y)=a_C(x,y)\mathbin{\mathrm{XOR}}T,
$$

$$
b_C(x+T,y)=b_C(x,y)\mathbin{\mathrm{XOR}}T.
$$

XORing both operands with the same top bit does not change their XOR:

$$
(a\mathbin{\mathrm{XOR}}T) \mathbin{\mathrm{XOR}} (b\mathbin{\mathrm{XOR}}T) = a\mathbin{\mathrm{XOR}}b.
$$

Therefore

$$
z_C(x+T,y)=z_C(x,y).
$$

The same argument applies to a shift of $y$ by $T$. Hence every post-powered motif has an axis period dividing

$$
C/2.
$$

---

### 3.5 Why the balanced modulus preserves the full period

Under the balanced rule,

$$
M=C\,2^v.
$$

We now show that the period is not merely a divisor of $C/2$, but exactly $C/2$.

Consider the two cells

$$
(y,x)=(1,0)
$$

and

$$
(y,x)=\left(1,\frac C4\right).
$$

Their XOR inputs are

$$
1
$$

and

$$
1+\frac C2.
$$

We compare their post-powers.

By the binomial theorem,

$$
\left(1+\frac C2\right)^p = 1 + p\frac C2 + \binom p2\left(\frac C2\right)^2 +\cdots.
$$

Since

$$
p=2^v u
$$

with $u$ odd,

$$
p\frac C2 = u\frac{C2^v}{2} = u\frac M2 \equiv \frac M2 \pmod M.
$$

For $C\ge8$, every higher binomial term is divisible by $M$. Hence

$$
\left(1+\frac C2\right)^p \equiv 1+\frac M2 \pmod M.
$$

The first cell gives

$$
1^p=1.
$$

Thus the two cells differ by exactly $M/2$, so an $x$-shift by $C/4$ cannot be a period.

For the $y$-axis, consider $(x,y)=(0,0)$ and $(x,y)=(0,C/4)$. Their XOR inputs are $C-1$ and $C/2-1$. Their difference has 2-adic valuation $c-1$, and their sum has valuation $1$ because $C\ge8$. For even $p$, the lifting-the-exponent formula therefore gives

$$
\nu_2\left((C-1)^p-(C/2-1)^p\right) =(c-1)+1+v-1 =c+v-1.
$$

For odd $p$, factoring the difference of powers leaves an odd quotient, giving the same formula with $v=0$. Thus these post-powers also differ by $M/2$ modulo $M$, so a $y$-shift by $C/4$ cannot be a period.

Along either axis, the least positive period divides the known period $C/2$. Since $C/2$ is a power of two, any smaller least positive period would divide $C/4$, making $C/4$ a period as well. The witnesses above rule this out, so the exact period on each axis is

$$
\boxed{C/2.}
$$

This is the theoretical explanation of the empirical behavior that originally motivated the rug rule.

---

### 3.6 General exact period theorem

#### Theorem: General exact period theorem

Assume

$$
C=2^c\ge8,
$$

$$
M=2^m,
$$

$$
p=2^v u,\qquad u\text{ odd},
$$

and

$$
K=\frac{M}{2^v}\ge8.
$$

Then the exact diagonal-XOR arithmetic axis period is

$$
\boxed{ R(C,p,M) = \frac12\min(C,K). }
$$

Equivalently,

$$
\boxed{ R(C,p,M) = \min\left( \frac C2, \frac{M}{2\mathrm{lowbit}(p)} \right). }
$$

#### Proof: General exact period theorem

There are two cases.

##### Case 1: _C_ ≥ _K_

Section 3.3 proved that the entire motif is exactly the same as the motif with coordinate domain $K$.

For that smaller motif,

$$
M=K\,2^v,
$$

so it is precisely the balanced construction. Section 3.5 gives exact period

$$
K/2.
$$

Therefore

$$
R=K/2.
$$

##### Case 2: _C_ ≤ _K_

The raw XOR construction already has period $C/2$, so the post-powered motif has period at most $C/2$.

Suppose it had a shorter period. Reduce every output modulo

$$
M_0=C\,2^v.
$$

Because $C\le K$,

$$
M_0\mid M.
$$

Thus reducing the $M$-modulus motif modulo $M_0$ produces exactly the balanced $C$-domain motif.

Any spatial period of the original motif would remain a period after reduction. But the balanced motif has exact period $C/2$, contradicting the assumption of a shorter period.

Therefore

$$
R=C/2.
$$

Combining the two cases gives

$$
R=\frac12\min(C,K).
$$

---

### 3.7 Interpretation: two independent bottlenecks

The theorem can be read as

$$
\boxed{ R = \min\left( \underbrace{C/2}_{\text{coordinate-domain limit}}, \underbrace{M/(2\mathrm{lowbit}(p))}_{\text{post-power/modulus limit}} \right). }
$$

The coordinate system can only offer period $C/2$.

The post-power can only preserve period

$$
M/(2\mathrm{lowbit}(p)).
$$

Whichever is smaller is the actual period.

---

### 3.8 Why the historical _M_ rule is natural

The historical rule is

$$
M=C\mathrm{lowbit}(p).
$$

Substituting it into the period theorem gives

$$
\frac{M}{2\mathrm{lowbit}(p)} = \frac C2.
$$

So the two bottlenecks are exactly equal.

Thus:

$$
\boxed{ M=C\mathrm{lowbit}(p) }
$$

is the **smallest power-of-two modulus that preserves the full coordinate-domain period $C/2$**.

A smaller power-of-two modulus shortens the period.

A larger modulus preserves the same period but retains additional arithmetic distinctions that are not needed merely to preserve that period.

This explains the old empirically discovered rule in structural terms.

---

### 3.9 Designing for a fixed target period _R_

Suppose

$$
R=2^r
$$

is the desired exact axis period.

The period theorem says

$$
\min(C,K)=2R.
$$

Therefore the necessary and sufficient nondegenerate condition is

$$
C\ge2R, \qquad K\ge2R,
$$

with at least one of $C$ or $K$ equal to $2R$.

Since

$$
K=M/2^v,
$$

this can also be written

$$
M\ge 2R\,2^v.
$$

The most economical and symmetric choice is

$$
\boxed{ C=2R, \qquad K=2R, \qquad M=2R\,2^v. }
$$

This is just the balanced rule with $C=2R$.

#### If _C_ is made larger while _R_ is held fixed

Set

$$
K=2R,
$$

or equivalently

$$
M=2R\,2^v.
$$

Then every

$$
C\ge2R
$$

produces the **same exact post-powered arithmetic motif**, not merely the same period.

Thus if the only purpose of $C$ is to feed this diagonal-XOR post-power, there is no arithmetic benefit in choosing

$$
C>2R
$$

once $K=2R$.

#### If _M_ is made larger instead

If

$$
C=2R
$$

but

$$
K>2R,
$$

the period remains $R$, because the coordinate domain is now the bottleneck.

However, the exact arithmetic motif need not be the same as the balanced one. A larger $M$ can preserve additional residue information while leaving the spatial period unchanged.

So “same target period” does not by itself mean “same motif.”

---

## 4. Odd-part theory

We now return to the balanced construction

$$
M=C\,2^v.
$$

At fixed $v$, how many genuinely different odd values of $u$ are there?

The answer is exact.

---

### 4.1 _A_ useful fact about 5 modulo powers of two

For odd $t$,

$$
\nu_2(5^t-1)=2.
$$

More generally, if

$$
n=2^s t,\qquad t\text{ odd},
$$

then the lifting-the-exponent formula gives

$$
\boxed{ \nu_2(5^n-1)=s+2. }
$$

Therefore the multiplicative order of $5$ modulo $2^q$, for $q\ge3$, is

$$
\boxed{2^{q-2}.}
$$

This is the standard cyclic principal-unit part of the group of odd residues modulo $2^q$.

---

### 4.2 Exact period of the odd part _u_

#### Theorem: Exact period of the odd part _u_

For fixed $v$ under the balanced rule,

$$
M=C\,2^v,
$$

two odd factors $u,u'$ give the same post-power function on the entire diagonal XOR motif if and only if

$$
\boxed{ u\equiv u'\pmod{C/4}. }
$$

Equivalently,

$$
u\mapsto u+C/4
$$

is the exact odd-part cycle.

#### Proof: sufficiency

The exponent difference is

$$
2^v(u'-u).
$$

If

$$
u'-u
$$

is divisible by $C/4=2^{c-2}$, then the exponent difference is divisible by

$$
2^v2^{c-2} = 2^{c+v-2}.
$$

But the exponent of the group of odd units modulo

$$
M=2^{c+v}
$$

is $2^{c+v-2}$. Therefore every odd $z$ satisfies

$$
z^{2^vu'} \equiv z^{2^vu} \pmod M.
$$

Since every XOR input is odd, the whole motif is unchanged.

#### Proof: minimality

The complete motif encounters $z=5$.

The order of $5$ modulo $2^{c+v}$ is

$$
2^{c+v-2}.
$$

Therefore equality

$$
5^{2^vu'} \equiv 5^{2^vu} \pmod{2^{c+v}}
$$

forces

$$
2^v(u'-u)
$$

to be divisible by $2^{c+v-2}$, hence

$$
u'-u
$$

must be divisible by

$$
2^{c-2}=C/4.
$$

So no smaller universal period works.

---

### 4.3 Number of exact _u_-classes

The odd residues modulo $C/4$ are

$$
1,3,5,\ldots,C/4-1.
$$

There are exactly

$$
\boxed{C/8}
$$

of them.

Thus, for every fixed $v$,

$$
\boxed{ \text{number of exact odd-part post-power classes}=C/8. }
$$

A canonical representative is

$$
\boxed{ u_{\mathrm{can}} = u\bmod(C/4), }
$$

where the remainder is automatically odd and nonzero.

The corresponding canonical exponent is

$$
\boxed{ p_{\mathrm{can}} = 2^v u_{\mathrm{can}}. }
$$

Because $v$ is preserved, the modulus $M=C2^v$ is also preserved. This is an **exact** simplification: raw post-power values, existing channel draws, and final rendering are unchanged.

---

### 4.4 Generalization to arbitrary _M_

At fixed $v$ with general

$$
K=M/2^v\ge8,
$$

the same proof shows that the odd-part period is

$$
\boxed{K/4}
$$

and the number of odd $u$-classes is

$$
\boxed{K/8}.
$$

The balanced rule is the special case $K=C$.

This is useful conceptually: the number of exponent classes at a fixed $v$ is controlled by the effective post-power domain $K$, not by the decimal magnitude of $p$.

---

## 5. Valuation theory

The odd-part theory completely solves duplication in $u$ at fixed $v$.

The harder question is:

> What genuinely new spatial structure appears as the valuation $v$ grows?

For this section we again assume the balanced rule

$$
M=C2^v.
$$

This is the construction used by the current generator and the cleanest construction for a target period.

---

### 5.1 Separate the spatial term from the constant phase

For odd $z$, define

$$
\boxed{ A_{v,u}(z) = \frac{z^{2^vu}-1}{2^v} \pmod C. }
$$

Then

$$
z^{2^vu} \equiv 1+2^vA_{v,u}(z) \pmod{C2^v}.
$$

After normalization by

$$
M=C2^v,
$$

the post-power is

$$
\boxed{ \frac{z^p\bmod M}{M} \equiv \frac{A_{v,u}(z)}{C} + \frac1{C2^v} \pmod1. }
$$

This decomposition explains nearly all of the high-$v$ behavior.

The term

$$
A_{v,u}(z)/C
$$

varies with the cell and is the **spatial arithmetic motif**.

The term

$$
1/(C2^v)=1/M
$$

is constant over space. It is a global phase-like offset.

Therefore “the spatial motif has stabilized” does **not** by itself mean that the normalized arithmetic values, channel phases, or final colors are identical.

---

### 5.2 Recurrence as _v_ increases

First take $u=1$ and write

$$
A_v=A_{v,1}.
$$

For $v\ge1$,

$$
z^{2^v} \equiv 1+2^vA_v \pmod{C2^v}.
$$

Squaring,

$$
z^{2^{v+1}} = (z^{2^v})^2 \equiv (1+2^vA_v)^2.
$$

Expanding,

$$
z^{2^{v+1}} \equiv 1 + 2^{v+1}A_v + 2^{2v}A_v^2 \pmod{C2^{v+1}}.
$$

After division by $2^{v+1}$,

$$
\boxed{ A_{v+1} \equiv A_v + 2^{v-1}A_v^2 \pmod C. }
$$

This is the central recurrence for the valuation direction.

---

### 5.3 Every _Aᵥ_ is divisible by 4 for _v_ ≥ 1

For odd $z$,

$$
z^2\equiv1\pmod8.
$$

More precisely,

$$
\nu_2(z^{2^v}-1)\ge v+2.
$$

Therefore

$$
\frac{z^{2^v}-1}{2^v}
$$

is always divisible by $4$:

$$
\boxed{ 4\mid A_v(z) \qquad(v\ge1). }
$$

Hence the correction term in the recurrence,

$$
2^{v-1}A_v^2,
$$

is divisible by

$$
2^{v-1}2^4 = 2^{v+3}.
$$

---

### 5.4 Fixed-_u_ stabilization

#### Theorem: Fixed-_u_ stabilization

For a fixed odd $u$,

$$
A_{v,u}
$$

stops changing once

$$
\boxed{ v\ge \max(1,c-3). }
$$

For $c\ge5$, this bound is sharp.

#### Proof: Fixed-_u_ stabilization

Apply the recurrence to the odd base $z^u$. The correction from level $v$ to $v+1$ is divisible by

$$
2^{v+3}.
$$

If

$$
v+3\ge c,
$$

then the correction vanishes modulo

$$
C=2^c.
$$

Thus

$$
A_{v+1,u}=A_{v,u}
$$

for all

$$
v\ge c-3.
$$

The recurrence itself starts at $v=1$, giving the threshold

$$
\max(1,c-3).
$$

For sharpness when $c\ge5$, take $z=3$. The relevant coefficient has exactly the minimal required 2-adic valuation, so the correction immediately before the threshold is nonzero modulo $C$. Thus the preceding level genuinely differs.

#### Example: _C_=256 for Fixed-_u_ stabilization

Here

$$
c=8.
$$

So fixed-$u$ stabilization begins at

$$
v=5.
$$

For $u=1$, the exponents

$$
32,64,128,256,\ldots
$$

all have the same $A$-motif.

---

### 5.5 High-_v_ linearization of the odd part

There is another important simplification one level earlier.

#### Theorem: High-_v_ linearization of the odd part

For

$$
v\ge\max(1,c-4),
$$

$$
\boxed{ A_{v,u}(z) \equiv u\,A_{v,1}(z) \pmod C. }
$$

#### Proof: High-_v_ linearization of the odd part

Choose the integer lift

$$
A=\frac{z^{2^v}-1}{2^v} \equiv A_{v,1}(z)\pmod C.
$$

Then

$$
z^{2^v}=1+2^vA.
$$

Raising to the odd power $u$ gives

$$
z^{2^vu} = (1+2^vA)^u.
$$

Expanding,

$$
(1+2^vA)^u = 1 + u2^vA + \binom u2 2^{2v}A^2 +\cdots.
$$

After subtracting $1$ and dividing by $2^v$,

$$
A_{v,u} \equiv uA + \binom u2 2^vA^2 +\cdots \pmod C.
$$

Since $A$ is divisible by $4$, every nonlinear term is divisible by at least

$$
2^{v+4}.
$$

Thus all nonlinear terms vanish modulo $C=2^c$ once

$$
v+4\ge c.
$$

Hence

$$
A_{v,u}\equiv uA_{v,1}\pmod C.
$$

---

## 6. Stronger valuation result: the whole high-_v_ tail repeats

Fixed-$u$ stabilization is not yet the strongest useful statement for a generator.

A generator samples both $v$ and $u$. So the relevant question is:

> At what point does an entire $v$-row stop adding any spatial motifs that were not already available at a smaller $v$ with a different $u$?

For $C\ge32$, the answer is one level earlier than fixed-$u$ stabilization.

---

### 6.1 The last new valuation level

Let

$$
C=2^c,\qquad c\ge5.
$$

Define

$$
\boxed{ v_0=c-4. }
$$

#### Theorem: The last new valuation level

The complete set of spatial coefficient motifs at

$$
v=v_0+1=c-3
$$

is exactly the same set as at

$$
v=v_0=c-4.
$$

Because fixed-$u$ stabilization begins at $v=c-3$, every later level has the same set as well.

Therefore

$$
\boxed{ v=0,1,\ldots,c-4 }
$$

are the only valuation levels needed to represent every distinct $A$-motif.

All

$$
\boxed{ v\ge c-3 }
$$

are spatially redundant once $u$ is allowed to vary.

---

### 6.2 Proof that the first stabilized row is a permutation of the previous row

Let

$$
v_0=c-4
$$

and write

$$
A=A_{v_0,1}.
$$

The recurrence gives

$$
A_{v_0+1,1} \equiv A + 2^{c-5}A^2 \pmod C.
$$

Since $A$ is divisible by $4$, write

$$
A=4B.
$$

Then

$$
2^{c-5}A^2 = 2^{c-5}16B^2 = 2^{c-1}B^2.
$$

On the other hand,

$$
\frac C8A = 2^{c-3}4B = 2^{c-1}B.
$$

Their difference is

$$
2^{c-1}(B^2-B) = 2^{c-1}B(B-1).
$$

One of $B,B-1$ is even, so this is divisible by

$$
2^c=C.
$$

Therefore

$$
A_{v_0+1,1} \equiv \left(1+\frac C8\right)A \pmod C.
$$

At both $v_0$ and $v_0+1$, the high-$v$ linearization theorem applies. Hence

$$
A_{v_0+1,u} \equiv u\left(1+\frac C8\right)A \pmod C.
$$

Multiplication by the odd number

$$
1+C/8
$$

permutes the odd residue classes modulo $C/4$.

But those odd residue classes are exactly the canonical $u$-classes.

Therefore the complete collection

$$
\{A_{v_0+1,u}\}
$$

is merely a permutation of

$$
\{A_{v_0,u}\}.
$$

No new spatial motif appears.

---

### 6.3 The productive valuation rows are mutually distinct

It remains to prove that the rows

$$
v=0,1,\ldots,c-4
$$

really are different families rather than containing further hidden duplication.

By Section 3.2 with $K=C$, the coefficient $A_{v,u}(z)$ depends only on the odd residue $z\bmod C$: congruent inputs give post-powers congruent modulo $C2^v$, and division of their difference by $2^v$ gives congruent coefficients modulo $C$. Every such residue occurs in the complete motif by Lemma 2. Any equality of complete motifs must therefore hold on powers of $5$, reduced modulo $C$.

For integers $j\ge0$, define

$$
B_{v,u}(j) = A_{v,u}(5^j).
$$

Let

$$
q=5^{2^vu}.
$$

Define the integer lift

$$
\widetilde B_{v,u}(j) = \frac{q^j-1}{2^v} \equiv B_{v,u}(j) \pmod C.
$$

Take its second forward finite difference in $j$:

$$
\Delta^2\widetilde B_{v,u}(j) = \frac{q^j(q-1)^2}{2^v}.
$$

Because $q$ is odd,

$$
\nu_2(q^j)=0.
$$

The standard identity

$$
\nu_2(5^{2^vu}-1)=v+2
$$

gives

$$
\nu_2(\Delta^2\widetilde B_{v,u}(j)) = 2(v+2)-v = \boxed{v+4}.
$$

Therefore, while

$$
v+4<c,
$$

the reduced second difference $\Delta^2 B_{v,u}(j)$ is nonzero modulo $C$, and every integer representative has valuation $v+4$. This valuation directly identifies $v$.

Different valuations below $c-4$ therefore cannot produce the same $A$-motif.

At

$$
v=c-4,
$$

the second difference first vanishes modulo $C$. That row is still distinct from every lower row, because all lower rows have a nonzero second difference.

Thus the rows

$$
\boxed{ v=0,\ldots,c-4 }
$$

are pairwise disjoint as sets of spatial coefficient motifs.

Combined with the preceding section, this completely classifies the valuation direction for $C\ge32$.

---

## 7. Complete count of XOR spatial exponent motifs

For $C\ge32$:

- productive valuation levels: $0,1,\ldots,c-4$;
- number of productive levels: $c-3$;
- exact $u$-classes at every productive level: $C/8$;
- productive rows are pairwise disjoint.

Therefore the total number of distinct normalized spatial exponent motifs over **all positive exponents $p$** is

$$
\boxed{ N_{\mathrm{spatial}}(C) = (c-3)\frac C8. }
$$

If only even exponents are allowed, remove the $v=0$ row:

$$
\boxed{ N_{\mathrm{spatial,even}}(C) = (c-4)\frac C8. }
$$

### Example: _C_=256 for Complete count of XOR spatial exponent motifs

Here

$$
c=8, \qquad C/8=32.
$$

The productive levels are

$$
v=0,1,2,3,4.
$$

Each has $32$ distinct odd-part motifs, and the five rows are disjoint. Therefore

$$
N_{\mathrm{spatial}}=5\cdot32=160.
$$

For even exponents only,

$$
N_{\mathrm{spatial,even}}=4\cdot32=128.
$$

The entire tail

$$
v=5,6,7,\ldots
$$

adds no new $A$-motifs.

---

## 8. Fixed target period _R_

The canonical construction for target period

$$
R=2^r
$$

is

$$
C=2R,
$$

$$
M=2R\,2^v.
$$

Then

$$
c=r+1.
$$

For $R\ge16$, the productive valuations are

$$
\boxed{ v=0,1,\ldots,r-3. }
$$

The first spatially redundant valuation is

$$
\boxed{ v=r-2. }
$$

The fixed-$u$ sequence itself stabilizes starting at that same first redundant row,

$$
v=r-2.
$$

But globally, allowing $u$ to change, the entire stabilized family was already present one level earlier at

$$
v=r-3.
$$

The canonical odd parts are

$$
\boxed{ u=1,3,5,\ldots,R/2-1. }
$$

There are

$$
\boxed{R/4}
$$

of them.

Therefore

$$
\boxed{ N_{\mathrm{spatial}}(R) = (r-2)\frac R4. }
$$

For even exponents only,

$$
\boxed{ N_{\mathrm{spatial,even}}(R) = (r-3)\frac R4. }
$$

### Examples

| Target period _R_ | _C_ = 2*R* | Productive _v_ values | First redundant _v_ | _u_-classes per productive _v_ |
| ----------------: | ---------: | --------------------- | ------------------: | -----------------------------: |
|                16 |         32 | 0,1                   |                   2 |                              4 |
|                32 |         64 | 0,1,2                 |                   3 |                              8 |
|                64 |        128 | 0,1,2,3               |                   4 |                             16 |
|               128 |        256 | 0,1,2,3,4             |                   5 |                             32 |
|               256 |        512 | 0,…,5                 |                   6 |                             64 |
|               512 |       1024 | 0,…,6                 |                   7 |                            128 |
|              1024 |       2048 | 0,…,7                 |                   8 |                            256 |

---

## 9. What happens when the allowed period is unbounded?

There is no universal finite cutoff on $v$ if the allowed spatial period can grow without bound.

At a fixed balanced domain $C$, the last productive valuation is

$$
v_{\max}=c-4.
$$

Since

$$
R=C/2,
$$

this becomes

$$
\boxed{ v_{\max}=\log_2R-3. }
$$

Equivalently, valuation $v$ can introduce a genuinely new spatial family only once

$$
\boxed{ R\ge2^{v+3}. }
$$

Thus higher $v$ is not intrinsically meaningless. It requires exponentially larger periods to reveal a new spatial family.

If the application imposes a maximum period

$$
R_{\max},
$$

then it immediately obtains a global useful valuation cap

$$
\boxed{ v_{\max} = \log_2R_{\max}-3 }
$$

for the canonical XOR construction.

---

## 10. There is no useful reason to sample a contiguous interval of _p_

At fixed $R$, the canonical exponent representatives are

$$
p=2^vu
$$

with

$$
0\le v\le r-3
$$

and

$$
u\in\{1,3,\ldots,R/2-1\}.
$$

The largest numerical representative is

$$
p_{\max} = 2^{r-3}\left(\frac R2-1\right) = \boxed{ \frac R8\left(\frac R2-1\right). }
$$

But this should **not** be interpreted as a recommendation to sample uniformly from

$$
1,\ldots,p_{\max}.
$$

The meaningful parameter space is a rectangular grid of canonical

$$
(v,u)
$$

classes, not a contiguous interval of decimal integers.

Large numerical $p$ is not itself a measure of pattern complexity.

---

## 11. Uniform sampling of distinct exponent motifs

The natural general rule is:

> If valuation $v$ contributes $n_v$ distinct pattern classes, then sampling every pattern uniformly requires
>
> $$
> P(v)=\frac{n_v}{\sum_j n_j}.
> $$

Then, conditional on $v$, sample uniformly among its distinct $u$-classes.

For diagonal XOR under the canonical balanced construction, a simplification occurs:

$$
n_v=C/8
$$

for every productive valuation

$$
0\le v\le c-4,
$$

and the high-$v$ tail contributes no new spatial classes.

Therefore:

$$
\boxed{ \text{To sample distinct XOR spatial exponent motifs uniformly, sample productive }v\text{ uniformly.} }
$$

Then sample canonical odd $u$ uniformly.

For fixed target period $R=2^r$:

$$
\boxed{ v\sim\mathrm{Uniform}\{0,\ldots,r-3\}, }
$$

$$
\boxed{ u\sim\mathrm{Uniform}\{1,3,\ldots,R/2-1\}, }
$$

and set

$$
\boxed{ p=2^vu, \qquad M=2R\,2^v. }
$$

Every canonical $A$-motif then receives the same probability.

### Even exponents only

If only even post-powers are desired, sample

$$
v\in\{1,\ldots,r-3\}
$$

uniformly instead.

### Odd versus even probability

If odd and even exponents are both included and the goal is uniformity over all spatial exponent motifs, then $v=0$ should receive the same probability as each individual productive even-$v$ row.

There are

$$
r-2
$$

productive rows in total, so

$$
P(v=0)=\frac1{r-2}.
$$

The total probability of an even exponent is

$$
\frac{r-3}{r-2}.
$$

Thus a separate 50/50 “odd versus even” choice is generally **not** uniform over distinct exponent motifs.

---

## 12. Why the historical _q_-sampler is nonuniform

In the inherited even-power generator, when

$$
N=C=2^c,
$$

the rule samples

$$
q=1,\ldots,C^2/32-1
$$

uniformly and then sets

$$
p=2q.
$$

Because

$$
\nu_2(p)=1+\nu_2(q),
$$

uniform integers $q$ give an approximately geometric valuation distribution:

$$
P(v=1)\approx\frac12,
$$

$$
P(v=2)\approx\frac14,
$$

$$
P(v=3)\approx\frac18,
$$

and so on.

Exactly, the number of sampled $q$'s at valuation $v$ is

$$
2^{2c-5-v}
$$

for the covered range.

This distribution is very different from uniform sampling of distinct spatial exponent motifs, where every productive $v$-row has the same number of classes.

The old distribution may still be aesthetically desirable. The point is that its low-$v$ bias is a **generator-design choice**, not something forced by the mathematics.

---

## 13. Redundancy in the historical exponent range

The original research quantified how many exact fixed-$v$ post-power/modulus cases the old range revisits.

When

$$
N=C=2^c,
$$

the inherited even-power range has

$$
C^2/32-1
$$

possible $q$'s.

But the number of distinct pairs

$$
(v,\text{exact post-power function})
$$

within that finite range is only

$$
\boxed{ (c-1)\frac C8-1. }
$$

Examples:

| _C_=_N_ | sampled _q_ values | odd-power classes | even function/modulus pairs |
| ------: | -----------------: | ----------------: | --------------------------: |
|      64 |                127 |                 8 |                          39 |
|     128 |                511 |                16 |                          95 |
|     256 |              2,047 |                32 |                         223 |
|     512 |              8,191 |                64 |                         511 |
|   2,048 |            131,071 |               256 |                       2,559 |

This count is **not** the same as the spatial-$A$ count derived later in this report.

Different high-$v$ states can have different moduli and different constant phases even when their spatial $A$-motifs have already repeated.

For example, at

$$
C=256,
$$

the old finite even range contains $223$ distinct exact function/modulus pairs, while the complete set of distinct even spatial coefficient motifs over all positive even exponents contains only

$$
128.
$$

That difference is precisely why the notion of equivalence must be stated explicitly.

---

## 14. How much of the old even sampler lies in the spatially redundant high-_v_ tail?

For $C=2^c\ge32$, the first spatially redundant valuation is

$$
v=c-3.
$$

Under the old even-$q$ sampler, the exact probability mass in

$$
v\ge c-3
$$

is

$$
\boxed{ \frac{2^{c-1}-1}{2^{2c-5}-1}. }
$$

For large $C$, this is approximately

$$
\boxed{ \frac{16}{C} = \frac8R. }
$$

So, for example, at target period

$$
R=128
$$

the high-$v$ tail receives roughly

$$
6.25\%
$$

of the old even sampler's probability.

At large periods this tail is not the dominant source of redundancy. Repeated sampling of equivalent odd parts $u$ is usually much larger.

---

## 15. Why “same spatial motif” does not imply the same channel phases

Suppose two exponent choices have the same spatial coefficient function

$$
A(z).
$$

Their normalized post-power still has the form

$$
\frac{A(z)}C+\frac1M.
$$

If their valuations differ, their moduli

$$
M=C2^v
$$

differ, so the constant term

$$
1/M
$$

differs.

The rug's affine channel arithmetic can be written, for fixed raw multiplier and additive draws $a,b$, as

$$
\boxed{ \mathrm{channel}(z) = \mathrm{frac}\left( \frac{a+b}{M} + \frac{(a\bmod C)A(z)}{C} \right). }
$$

The second term contains the spatially varying motif.

The first term is a constant rotation around the channel's unit circle.

Therefore two exponent states can have:

$$
\boxed{\text{the same }A(z)}
$$

but different

$$
\boxed{\text{global channel phases}.}
$$

A phase shift can materially change HSV, OKLCH, or later RGB values, so identical $A$-motifs do not imply identical final pixels when the existing channel parameters are held fixed.

If channel phase is independently adjustable, however, the phase difference can be regarded as a separate color parameter rather than a new spatial post-power structure.

This is why a generator intended to sample **spatial arithmetic structures** has a finite useful $v$-range even though the exact normalized values continue changing forever.

---

## 16. Three reasonable equivalence choices for generator design

The mathematics supports three different design philosophies.

| What counts as a new exponent state?                                                        | High-_v_ behavior                             |
| ------------------------------------------------------------------------------------------- | --------------------------------------------- |
| New **spatial arithmetic motif** _A_(_z_)                                                   | finite; stop after _v_ = _c_ − 4 for _C_ ≥ 32 |
| Same spatial motif but a different global arithmetic/channel phase counts as new            | no finite exact cutoff from this theory       |
| Different final rendered pixels with all current random channel/color parameters held fixed | no finite cutoff proved                       |

The first choice gives the clean finite canonical sampler.

The second and third deliberately treat color-phase refinements as part of the exponent space.

For a clean generator architecture, there is a strong conceptual argument for letting:

- $p$ choose the spatial arithmetic structure; and
- explicit channel parameters choose channel phases and colors.

Under that interpretation, sampling arbitrarily high $v$ merely to obtain increasingly fine constant phase shifts is unnecessary duplication of responsibilities.

---

## 17. Fixed-_R_ canonical sampler

For a target period

$$
R=2^r\ge16,
$$

a mathematically clean XOR sampler for distinct spatial exponent motifs is:

1. choose $C=2R$;

2. sample $v \in \{0,\ldots,r-3\}$ uniformly;

3. sample $u \in \{1,3,\ldots,R/2-1\}$ uniformly;

4. set $p=2^v u$;

5. set $M=2R\,2^v$.

This gives:

- exact axis period $R$;
- no duplicate odd-part classes;
- no spatially redundant high-$v$ levels;
- equal probability for every canonical spatial exponent motif.

If preserving the visual statistics of the historical generator is more important than uniformity, step 2 can instead use an explicit low-$v$-biased distribution.

---

## 18. Unbounded-period sampler

If the period itself is allowed to be arbitrarily large, then there are infinitely many distinct spatial exponent motifs overall.

There is no uniform probability distribution over a countably infinite set that gives every state equal positive mass.

Therefore a generator with unbounded period must first choose a distribution on the period $R$, or impose a finite maximum period.

For each chosen finite $R$, the conditional exponent sampler can then use the finite canonical construction above.

If the allowed periods form a finite set and the goal is uniformity over **all spatial exponent motifs across all periods**, then period $R=2^r$ should receive weight proportional to

$$
\boxed{ N_{\mathrm{spatial}}(R) = (r-2)\frac R4. }
$$

After choosing $R$ with that weight, sample $v$ and $u$ uniformly within the chosen period.

---

## 19. Small-domain exceptions

The clean valuation classification

$$
v=0,\ldots,c-4
$$

is stated for

$$
C\ge32.
$$

The very small domains have special degeneracies.

The original exact enumeration found that $C=8$ and $C=16$ need separate treatment. They are small enough that some of the finite-difference invariants used in the general proof have already vanished modulo $C$.

Likewise, the general $C/M$ period theorem in its clean symmetric form assumes

$$
C\ge8,\qquad K\ge8.
$$

When $K<8$, additional collapse occurs and the two axes can exhibit tiny special cases.

For normal rug sizes, these exceptions are best handled explicitly rather than complicating the main formulas.

---

## 20. What was verified computationally in the original research

The original exact-integer research script did not rely solely on visual inspection.

For XOR, it directly checked or enumerated:

- the exact odd-part exponent cycle;
- canonical exponent reductions;
- fixed-$u$ coefficient stabilization;
- sharpness of the stabilization threshold;
- high-$v$ linearization in $u$;
- exact raw odd-input tables for domains $8$ through $128$;
- inherited exponent-class counts through larger domains;
- complete spatial axis periods across sampled domains, valuations, and odd parts;
- the channel-offset identity that remains after coefficient stabilization.

The original combined XOR/OR script reported $173{,}018$ exact integer identity checks overall.

The later results in this document add proofs for:

- the general $C/M$ period formula;
- exact motif independence from $C$ once $C \ge K$;
- the setwise collapse of all high-$v$ rows onto the last productive row;
- pairwise distinctness of all productive valuation rows;
- the resulting finite count of spatial XOR exponent motifs;
- the uniform-sampling consequences.

Those extensions were derived mathematically in the follow-up discussion and are not all encoded in the original verification script.

---

## 21. Summary of the three theories

### _C_/_M_ theory

Define

$$
K=\frac{M}{\mathrm{lowbit}(p)}.
$$

For nondegenerate power-of-two $C,K$,

$$
\boxed{ R=\frac12\min(C,K). }
$$

If

$$
C\ge K,
$$

the complete post-powered arithmetic motif is exactly independent of any further increase in $C$.

The historical choice

$$
M=C\mathrm{lowbit}(p)
$$

sets

$$
K=C,
$$

so it is the minimal power-of-two modulus preserving the full period

$$
C/2.
$$

For target period $R$, the canonical economical choice is

$$
\boxed{ C=2R, \qquad M=2R\mathrm{lowbit}(p). }
$$

---

### Odd-part theory

Write

$$
p=2^vu
$$

with $u$ odd.

Under the balanced rule, at fixed $v$,

$$
\boxed{ u\equiv u'\pmod{C/4} }
$$

if and only if the two exponents give the same complete raw XOR post-power function.

Thus there are exactly

$$
\boxed{C/8}
$$

canonical odd-part classes:

$$
1,3,\ldots,C/4-1.
$$

Large decimal values of $u$ merely cycle through these finite classes.

---

### Valuation theory

For

$$
C=2^c\ge32,
$$

define the spatial coefficient motif

$$
A_{v,u}(z) = \frac{z^{2^vu}-1}{2^v} \pmod C.
$$

A fixed $u$ stabilizes at

$$
\boxed{v=c-3.}
$$

But if $u$ may vary, the entire stabilized family is already present one level earlier.

The only valuation rows needed to represent every distinct spatial coefficient motif are

$$
\boxed{ v=0,\ldots,c-4. }
$$

Each productive row has $C/8$ classes, and the rows are mutually disjoint. Therefore

$$
\boxed{ N_{\mathrm{spatial}}=(c-3)C/8. }
$$

For fixed period $R=2^r$ with $C=2R$,

$$
\boxed{ v=0,\ldots,r-3, }
$$

$$
\boxed{ u=1,3,\ldots,R/2-1. }
$$

Every productive $v$-row contains the same number $R/4$ of spatial classes, so **uniform sampling of distinct spatial exponent motifs means uniform sampling of $v$** followed by uniform sampling of canonical $u$.

---

## 22. Recommended interpretation for future generator work

The post-power exponent should not be viewed primarily as one large integer.

Its mathematically meaningful coordinates are

$$
\boxed{(v,u)}.
$$

For XOR:

- $C$ and $M$ determine how much spatial period survives;
- $u$ selects one class from a finite exact cycle;
- $v$ selects a hierarchy of spatial arithmetic families, but only up to a finite cutoff for any fixed period;
- the remaining high-$v$ changes are constant phase refinements rather than new spatial coefficient motifs.

This suggests a future generator in which period, valuation level, odd-part class, and channel phase are explicit independent concepts rather than accidental consequences of drawing a large integer $p$.

The historical generator should still be retained as a versioned legacy recipe if exact seed reproducibility is important.

---

## 23. Reference to the original research

The starting point for this document was:

- `research/2026-10-11-post-power/2026-10-11-post-power-range.md`
- `research/2026-10-11-post-power/2026-10-11-post-power-range.py`

The original report also cites the standard structure of odd units modulo powers of two; a useful reference is Keith Conrad, _Prime Powers, Units, and Finite Subgroups of GL_n(Q)_, especially the discussion of units modulo $2^k$.

This document intentionally stops at the diagonal XOR combiner. A later addendum can develop the corresponding theory for squared OR, fourth-power OR, straight versus diagonal variants, or other future combiners.
