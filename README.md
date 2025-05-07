# Tema LFA
Acest program citeste o serie de regexuri din input.json, expliciteaza concatenarea cu simbolul ^, apoi trece regexul in forma postifxa poloneza folosind
### Shunting-Yard

Dupa aceea, folosind algoritmul lui
### Thompson 
si o stiva de NFA-uri, transforma regexul postfixat si explicitat intr-un λ-NFA

Apoi, folosind un algoritm aproximativ de state removal transforma in DFA

DFA-ul este exportat in format text in formatul standard de laborator intrucat backendul implementarii difera mult intre tema 1 si tema 2 si am dorit sa reciclez codul de la tema 1. Dupa aceea, din fisierul de input se ruleaza testele folosind codul de la tema 1.
