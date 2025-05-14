# Matrix-Based Decryption System

This Python program implements a matrix-based decryption system using a combination of predefined rules, cellular automata principles, and multiprocessing for performance optimization.

## 🧠 Overview

The core idea is to:
1. Take an input string.
2. Generate a square matrix from it.
3. Evolve this matrix through cellular rules based on prime/even neighbor sums.
4. Use the updated matrix to decrypt the string using a rotation cipher.

The process supports **parallel computation** using Python’s `multiprocessing` module to speed up matrix evolution.

---

## 🧪 Features

- 🔁 100 iterations of matrix evolution based on neighbors.
- 🧮 Prime and even sum rules determine the next matrix state.
- 🔐 Rotation-based decryption using a 95-character rotation string.
- 🚀 Parallel processing of matrix slices.
- ✅ Validates input/output paths.

---

## ⚙️ Functionality Highlights

- `decryptLetter`: Decrypts a character using rotation logic.
- `update_current_cell`: Updates a cell based on its neighbors’ sum using modular logic and hash sets (`prime` and `even`).
- `sum_column`: Computes sum of a specified column in the matrix.
- `process_matrix`: Handles the matrix evolution with edge/corner/middle cases for each cell.
- `distribute_workload`: Splits matrix rows among available processors.

---

## 📂 Input/Output

- **Input File**: Path to a text file containing the encrypted input string.
- **Output File**: Path to save the decrypted result.

```bash
python main.py -i encrypted_input.txt -o decrypted_output.txt
```

### CLI Argument Flags

| Flag | Description |
|------|-------------|
| `-i`, `--input` | Path to input file containing encrypted string |
| `-o`, `--output` | Output file to save decrypted result |

---

## 🧮 Logic Behind Cell Updates

A cell can be 0, 1, or 2. It evolves based on the sum of its 3–8 neighboring cells:

| Current Value | Neighbor Sum is Prime | Neighbor Sum is Even | Else |
|---------------|------------------------|-----------------------|------|
| 0             | 0                      | 1                     | 2    |
| 1             | 1                      | 2                     | 0    |
| 2             | 2                      | 0                     | 1    |

The predefined `prime` set includes: `{2, 3, 5, 7, 11, 13}`  
The predefined `even` set includes: `{0, 2, 4, 6, 8, 10, 12, 14, 16}`

---

## 🛠️ Requirements

- Python 3.x
- No external libraries required beyond the standard library.

---

## ⚡ Performance Notes

- Efficiently utilizes `multiprocessing.Pool` to parallelize matrix evolution.
- `distribute_workload()` balances rows between cores, whether the row count divides evenly or not.

---

## 📝 License

This project is provided as-is under a permissive open-source license (MIT or similar). Feel free to modify and use it for educational or research purposes.

---

## 👤 Author

Halmuhammet Muhamedorazov  
*Inspired by matrix simulation, parallel computing, and cryptography.*
