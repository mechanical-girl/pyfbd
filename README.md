# pyfbd

The following input produces an incorrect diagram:

```
Yashas-MacBook-Pro:source yasha$ pyfbd
==== Defining Beam ====
Beam length in m (or 1 if unknown): 2

==== Defining Forces ====
Force name: 6kN
Is the force acting downwards? Y/n
Force value:
Is force a UDL? Y/nn
Distance from right-hand side? 0.4
Force name: R1
Is the force acting downwards? Y/n n
Force value:
Is force a UDL? Y/nn
Distance from right-hand side? 2
Force name: R2
Is the force acting downwards? Y/n n
Force value:
Is force a UDL? Y/nn
Distance from right-hand side? 0
Force name: ^C
3 forces defined.
Making cut between 2.0 and 0.4 at 1.2
Making cut between 0.4 and 0.0 at 0.2
Force R1 has value 1.2kN
Force 6kN has value
pyfbd4.png
```
