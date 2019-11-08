# LMC Evaluator
A Little Minion Computer (edited version of Little Man Computer) Evaluator that helps user test the correctness of the algorithms.

## Requirement
1. python 3 runtime
2. lmc assembly code (source code in any format is appreciated) 

## Usage
In the shell (or cmd), run:

```
python3 evaluate.py <filename> [start] [end:optional] <task> <tailing_zero>
```

task: `bsc` for the basic task testing and `adv` for the advanced task testing.

tailing_zero: `t` if the program would output zero (when overflow) and then halt. `f` if the program would halt directly.

## Example

### 1:

Input:

```
python3 evaluate.py basicCOMP1071.txt 329 333 bsc f
```

will take the input from 329 to 333 for the basic task and testing each input.

Output:

```
Start at: 329
> 329 988 494 247 742 371
> fetch-execute cycles: 7254

Start at: 330
> 330 165 496 248 124 62 31 94 47 142 71 214 107 322 161 484 242 121 364 182 91 274 137 412 206 103 310
155 466 233 700 350 175 526 263 790 395
> fetch-execute cycles: 22314

Start at: 331
> 331 994 497
> fetch-execute cycles: 4165

Start at: 332
> 332 166 83 250 125 376 188 94 47 142 71 214 107 322 161 484 242 121 364 182 91 274 137 412 206 103 310 155 466 233 700 350 175 526 263 790 395
> fetch-execute cycles: 22458

Start at: 333
> 333
> fetch-execute cycles: 773
```

### 2:

Input:

```
python3 evaluate.py advancedCOMP1071.txt 995 999 adv t
```

will take the input from 995 to 999 for the advanced task and testing each input.

Output:

```
Start at: 995
> 995 0
> fetch-execute cycles: 2268

Start at: 996
> 996 498 249 374 187 281 422 211 317 476 238 119 179 269 404 202 101 152 76 38 19 29 44 22 11 17 26 13
20 10 5 8 4 2 1
> fetch-execute cycles: 14248

Start at: 997
> 997 0
> fetch-execute cycles: 2276

Start at: 998
> 998 499 749 0
> fetch-execute cycles: 5130

Start at: 999
> 999 0
> fetch-execute cycles: 2277

All test passed!
Total mailboxes used: 42
Average fetch-execute cycles: 5239
```



**PS:** I assume that your program will always output the given input **whatever it is**. For instance, it will output 0 and halt if the input is 0.

**PPS:** You should not rely on this project as the correctness cannot be ensured. Use it just for fun!