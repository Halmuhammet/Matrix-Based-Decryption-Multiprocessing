# import necessary modules
import math
from multiprocessing import Pool
import time
import argparse
import os
import re
import copy

# initialize precomputed prime numbers

prime = set([2, 3, 5, 7, 11, 13])
even = set([0, 2, 4, 6, 8, 10, 12, 14, 16])

# this function validates the seed string from command line argument

def valid_directory(output_file_path):
    # get the directory name
    directory = os.path.dirname(output_file_path)
    # if the directory is empty, it means output_file_path is a filename only (in the current directory)
    if not directory:
        directory = '.'
    # check if the directory exists
    if not os.path.exists(directory):
        raise argparse.ArgumentTypeError(f"The directory '{directory}' does not exist.")
    return output_file_path


# this function is used to ensure that a valid input file path is passed from command lin argument


def valid_file_path(input_file_path):
    if not os.path.exists(input_file_path):
        raise argparse.ArgumentTypeError(f"File path {input_file_path} does not exist.")
    return input_file_path


# this function is used to get the column sum of a matrix
# it takes 2 arguments: a matrix and a column index
# and returns a sum for the chosen column

def sum_column(matrix, column_index):
    sum = 0
    for row in range(len(matrix)):
        sum += matrix[row][column_index]
    return sum


# this function generates the decrypted output string
# it takes two arguments: input string and a processed matrix

def generate_output_string(input_string, processed_matrix):
    # initialize the output string
    output_string = ""
    for input_string_index, input_string_character in enumerate(input_string):
        # decrypt each character and append it to the output string
        # sum_column function takes arguments, matrix and a column index number which corresponds to input_string_index
        decrypted_character = decryptLetter(input_string_character, sum_column(processed_matrix, input_string_index))
        # concatenate the decrypted characters to output string
        output_string += decrypted_character
        # return the output string
    return output_string


# this function takes two arguments, char and int, and returns a decrypted character by applying rotation value method

def decryptLetter(letter, rotationValue):
    rotationString = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ "
    currentPosition = rotationString.find(letter)
    return rotationString[(currentPosition + rotationValue) % 95]

# this function is used to update the current cell in a matrix
# it takes 2 arguments: current number in the matrix and its neighbor sum
# it uses the precomputed prime and even hash sets to return an updated number.

def update_current_cell(current_number, sum_neighbor):
    if current_number == 0:
        if sum_neighbor in prime:   
            return 0
        elif sum_neighbor in even:
            return 1
        else:
            return 2
    elif current_number == 1:
        if sum_neighbor in prime:
            return 1
        elif sum_neighbor in even:
            return 2
        else:
            return 0
    else:  # case for current_number = 2
        if sum_neighbor in prime:
            return 2
        elif sum_neighbor in even:
            return 0
        else:
            return 1

# This function is used to divide up the rows in the matrix to be processed
# If the length of input string, L, can be divided equally by process count,
# then each process will get equal rows to process.
# If L cannot be divided equally by process count,
# then processors equal to the number of remainder from L % MAX_PROCESSES
# will work on 1 more rows than processes working on equal rows.

def distribute_workload(L, MAX_PROCESSES):
    # initialize distribution list that will be returned after function call
    distribution = []
    # case for total row numbers divided by process count is even
    if (L % MAX_PROCESSES == 0):
        start_row = 0
        for row_num in range(MAX_PROCESSES):
            # Pack each matrixData list and append it to the aggregate list
            end_row = (start_row + L // MAX_PROCESSES)
            distribution.append((start_row, end_row))
            # increment start_row after the end_row because indexing start from 0
            start_row += L // MAX_PROCESSES
    else:
        # case for when the row count is less than the process count
        if (L / MAX_PROCESSES < 1):
            # initialize start_row to zero to get the first row
            start_row = 0
            for row_num in range(L):
                # Pack each matrixData list and append it to the aggregate list
                end_row = (start_row + 1)
                distribution.append((start_row, end_row))
                # increment start_row after the end_row because indexing start from 0
                start_row += 1
        else:
            # case for row numbers cannot be divided equally among processes

            processes_with_equal_load = MAX_PROCESSES - (L % MAX_PROCESSES)
            processes_with_more_load = MAX_PROCESSES - processes_with_equal_load

            # initialize starting row indexes for equal and unequal loads
            starting_row_unequal_load = 0
            start_row = 0

            for row_num in range(processes_with_equal_load):
                # Pack each matrixData list and append it to the aggregate list
                end_row = (start_row + (L // MAX_PROCESSES))
                starting_row_unequal_load = end_row # the end_row index will be the start_row index for unequal load
                distribution.append((start_row, end_row))
                start_row += (L // MAX_PROCESSES)

            for row_num in range(processes_with_more_load):
                # Pack each matrixData list and append it to the aggregate list
                end_row_unequal_load = (starting_row_unequal_load + (L // MAX_PROCESSES)) + 1
                distribution.append((starting_row_unequal_load, end_row_unequal_load))
                starting_row_unequal_load += (L // MAX_PROCESSES) + 1

    # return the set of sets that contains starting and ending row indices for a matrix to be processed
    return distribution


# this function goes through the matrix cells to get
# the sum of its neighboring value and modifies that cell depending on neighboring sum.
# It first gets the sum of neighboring cells at the edge cell
# then the default case is where the cell is at the middle of matrix, having 8 neighboring cells.
# it takes a list containing matrix, starting row index, and an ending row index

def process_matrix(matrixData):
    # unpack the matrixData
    prev_matrix = matrixData[0]
    start_row = matrixData[1]
    end_row = matrixData[2]
    del (matrixData)  # clear it out of memory.

    # initialize updated rows to however many rows each process needs to work on
    updated_rows = [[0 for i in range(len(prev_matrix[0]))] for j in range(start_row, end_row)]
    mtxLength = len(prev_matrix[0])

    # while loop is used for 100 iterations of cell modification
    for row in range(start_row, end_row):
        # ensure that the index for updated rows is not out of bound
        updated_row_index = row - start_row
        for column in range(mtxLength):
            # depending on current cell number, get its neighbor sum and update the current cell depending on that value
            # top left corner
            if row == 0 and column == 0:
                sum_neighbor = prev_matrix[row+1][column] + prev_matrix[row+1][column+1] + prev_matrix[row][column + 1]
                updated_rows[updated_row_index][column] = update_current_cell(prev_matrix[row][column], sum_neighbor)

            # bottom left corner
            elif row == mtxLength - 1 and column == 0:
                sum_neighbor = prev_matrix[row - 1][column] + prev_matrix[row - 1][column + 1] + prev_matrix[row][column + 1]
                updated_rows[updated_row_index][column] = update_current_cell(prev_matrix[row][column], sum_neighbor)

            # top right corner
            elif row == 0 and column == mtxLength - 1:
                sum_neighbor = prev_matrix[row][column - 1] + prev_matrix[row + 1][column - 1] + prev_matrix[row + 1][column]
                updated_rows[updated_row_index][column] = update_current_cell(prev_matrix[row][column], sum_neighbor)

            # bottom right corner
            elif row == mtxLength - 1 and column == mtxLength - 1:
                sum_neighbor = prev_matrix[row - 1][column] + prev_matrix[row - 1][column - 1] + prev_matrix[row][column - 1]
                updated_rows[updated_row_index][column] = update_current_cell(prev_matrix[row][column], sum_neighbor)

            # top middle edge
            elif row == 0 and (column != 0 and (column != mtxLength - 1)):
                sum_neighbor = (prev_matrix[row][column - 1] + prev_matrix[row][column + 1] + prev_matrix[row + 1][column]
                                + prev_matrix[row + 1][column - 1] + prev_matrix[row + 1][column + 1])
                updated_rows[updated_row_index][column] = update_current_cell(prev_matrix[row][column], sum_neighbor)

            # bottom middle edge
            elif row == mtxLength - 1 and (column != 0 and (column != mtxLength - 1)):
                sum_neighbor = (prev_matrix[row][column - 1] + prev_matrix[row][column + 1] + prev_matrix[row - 1][column]
                                + prev_matrix[row - 1][column - 1] + prev_matrix[row - 1][column + 1])
                updated_rows[updated_row_index][column] = update_current_cell(prev_matrix[row][column], sum_neighbor)

            # left middle edge
            elif (row != 0 and (row != mtxLength - 1)) and column == 0:
                sum_neighbor = (prev_matrix[row - 1][column] + prev_matrix[row + 1][column] + prev_matrix[row][column + 1]
                                + prev_matrix[row - 1][column + 1] + prev_matrix[row + 1][column + 1])
                updated_rows[updated_row_index][column] = update_current_cell(prev_matrix[row][column], sum_neighbor)

            # right middle edge
            elif (row != 0 and (row != mtxLength - 1)) and column == mtxLength - 1:
                sum_neighbor = (prev_matrix[row - 1][column] + prev_matrix[row + 1][column] + prev_matrix[row][column - 1]
                                + prev_matrix[row - 1][column - 1] + prev_matrix[row + 1][column - 1])
                updated_rows[updated_row_index][column] = update_current_cell(prev_matrix[row][column], sum_neighbor)

            # everywhere else; inside of matrix, not the edges
            else:
                sum_neighbor = (prev_matrix[row - 1][column] + prev_matrix[row + 1][column] + prev_matrix[row - 1][column - 1]
                                + prev_matrix[row - 1][column + 1] + prev_matrix[row + 1][column - 1] + prev_matrix[row + 1][column + 1]
                                + prev_matrix[row][column - 1] + prev_matrix[row][column + 1])
                updated_rows[updated_row_index][column] = update_current_cell(prev_matrix[row][column], sum_neighbor)

    # return the updated rows
    return updated_rows


def main():
    start = time.time()
    print("Project :: R11800534")

    # parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=valid_file_path, help="Path to input file", required=True)
    parser.add_argument("-s", type=str, help="Seed string", required=True)
    parser.add_argument("-o", type=valid_directory, help="Path to output file", required=True)
    parser.add_argument("-p", type=int, help="Process count", default=1)
    args = parser.parse_args()

    # for readability, assign the command line argument to a variable with meaningful name
    process_count = args.p
    output_directory_path = args.o
    input_file_path = args.i
    seed_string = args.s

    # get the input string
    with open(input_file_path, 'r') as file:
        input_string = file.readline().strip()

    # length of input string, which is also the size of a square matrix
    L = len(input_string)

    print("length of input string", L)
    print("length of seed string", seed_string)
    print("input string:", input_string)
    print()

    # this dictionary is used to store values depending on character in the seed string
    char_to_num = {'a': 0, 'b': 1, 'c': 2}
    # Initialize an empty matrix which is to be populated
    matrix = []
    seed_index = 0
    # populate the matrix using nested for loops
    for row in range(L):
        matrix_row = []
        for col in range(L):
            # get the seed character
            char = seed_string[seed_index]
            # append the character and its value to the row list
            matrix_row.append(char_to_num[char])
            # move on to the next character in seed string
            seed_index += 1
            # reset the index if end of string is reached
            if seed_index >= len(seed_string):
                seed_index = 0
        # add populated row list in to the matrix
        matrix.append(matrix_row)

    # initialize the process count
    MAX_PROCESSES = process_count
    # spawn max number of processes
    process_pool = Pool(processes=MAX_PROCESSES)
    # distribute the rows among processes by calling distributor function defined above
    row_distribution = distribute_workload(L, MAX_PROCESSES)

    # for a 100 times update the matrix using multiprocessing pool
    for i in range(100):
        # in each iteration initialize the pool_data
        pool_data = []
        # get the starting and ending row for each process
        for start_row, end_row in row_distribution:
            # pack the matrix_data
            matrix_data = [matrix, start_row, end_row]
            pool_data.append(matrix_data)
        finalData = process_pool.map(process_matrix, pool_data)
        # since returned data will be 3D, we need to flatten it to 2D
        matrix = [row for sublist in finalData for row in sublist]

    # clear pool_data out of memory
    del (pool_data)

    # generate the output string
    output = generate_output_string(input_string, matrix)

    # write the output string into the directory provided by command line argument
    with open(output_directory_path, 'w') as file:
        file.write(output.strip())

    print("length of input string", L)
    print("length of seed string", seed_string)
    print("input string:", input_string)
    print()
    print(output)

    end = time.time()
    print(end - start)

if __name__ == '__main__':
    main()
