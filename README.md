# LMC Evaluator
A Little Minion Computer (edited version of Little Man Computer) Evaluator that helps user test the correctness of the algorithms.

## Requirement
1. python 3 runtime
2. lmc assembly code (source code in any format is appreciated) 

## Usage
In the shell (or cmd), run:

```
python3 evaluate.py [source_code_path] [start_index] [end_index]
```

## Example
Input:

```
python3 evaluate.py basicCOMP1071.txt 3 5
```

will take the input from 3 to 5 and run the program independently.

Output:

```
Start at: 3
3 10 5 16 8 4 2 1
total fetch-execute cycles: 303

Start at: 4
4 2 1
total fetch-execute cycles: 59

Start at: 5
5 16 8 4 2 1
total fetch-execute cycles: 220

Average fetch-execute cycles: 194
```
