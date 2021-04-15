# %%
from sympy import *

from IPython.display import display

# Strain tensor elements
e11, e22, e33, e12, e13, e23 = symbols('epsilon_11, epsilon_22, epsilon_33, epsilon_12, epsilon_13, epsilon_23')

# Stress tensor elements
s11, s22, s33, s12, s13, s23 = symbols('sigma_11, sigma_22, sigma_33, sigma_12, sigma_13, sigma_23')

# Stiffness matrix elements
c11, c22, c33, c44, c55, c66 = symbols('C_11, C_22, C_33, C_44, C_55, C_66')
c12, c13, c23, c21, c31, c32 = symbols('C_12, C_13, C_23, C_21, C_31, C_32')

# Transformation matrix elements
q11, q22, q33, q12, q13, q23 = symbols('q_11, q_22, q_33, q_12, q_13, q_23')

# Strength
R = symbols('R')

e = Matrix([[e11],
    [e22],
    [e33],
    [e12],
    [e13],
    [e23]])

s = Matrix([[s11],
    [s22],
    [s33],
    [s12],
    [s13],
    [s23]])

Q = Matrix([[q11,q12,q13],
    [q12,q22,q23],
    [q13,q23,q33]])

C = Matrix([[c11,c12,c13,0,0,0],
    [c12,c22,c23,0,0,0],
    [c13,c23,c33,0,0,0],
    [0,0,0,c44,0,0],
    [0,0,0,0,c55,0],
    [0,0,0,0,0,c66]])

Q_t = Q.transpose()

s = C*e

S_e = Matrix([[s[0],s[3],s[4]],
    [s[3],s[1],s[5]],
    [s[4],s[5],s[2]]])

S_p = Q*S_e*Q_t

# failure function 1
f1 = S_p[0,0]/R

# failure function 2
f2 = S_p[1,1]/R

# failure function 3
f3 = S_p[2,2]/R

# get derivatives of the first (by position in the matrix, not value) principle stress
df1_de11 = diff(f1, e11)
df1_de22 = diff(f1, e22)
df1_de33 = diff(f1, e33)
df1_de12 = diff(f1, e12)
df1_de13 = diff(f1, e13)
df1_de23 = diff(f1, e23)

# get derivatives of the second (by position in the matrix, not value) principle stress
df2_de11 = diff(f2, e11)
df2_de22 = diff(f2, e22)
df2_de33 = diff(f2, e33)
df2_de12 = diff(f2, e12)
df2_de13 = diff(f2, e13)
df2_de23 = diff(f2, e23)

# get derivatives of the third (by position in the matrix, not value) principle stress
df3_de11 = diff(f3, e11)
df3_de22 = diff(f3, e22)
df3_de33 = diff(f3, e33)
df3_de12 = diff(f3, e12)
df3_de13 = diff(f3, e13)
df3_de23 = diff(f3, e23)

print('Failure functions written via strain components:')
display(f1)
display(f2)
display(f3)

print('First failure function derivatives w/respect to strain components:')
display(df1_de11)
display(df1_de22)
display(df1_de33)
display(df1_de12)
display(df1_de13)
display(df1_de23)

print('Second failure function derivatives w/respect to strain components:')
display(df2_de11)
display(df2_de22)
display(df2_de33)
display(df2_de12)
display(df2_de13)
display(df2_de23)

print('Third failure function derivatives w/respect to strain components:')
display(df3_de11)
display(df3_de22)
display(df3_de33)
display(df3_de12)
display(df3_de13)
display(df3_de23)

# %%
