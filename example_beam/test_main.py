# import modules from same directory
#
import struct
import numpy as np
from nastran_format import extract_data_blocks, INT4, REAL8

file_to_read = "OUTPUT/test.f11"
blocks = extract_data_blocks(file_to_read)

nblocks = len(blocks)

variable_names = []
content = np.frombuffer(blocks[0], dtype=INT4)
nvars = content[0]
variable_names.append(blocks[1].strip().decode("utf-8"))


solution_type = None  # 101 for static analysis
matrix_type = None  # 66 for stiffness matrix
data_format = None  # 6 for double precision
matrix_symmetric = None  # 2 for symmetric, else 1 for unsymmetric
matrix_size = None  # size of the KLL matrix
user_identifier = None  # identifier of the subDMAP created the matrix
load_case_id = None  # load case ID

index = 1
data_entry = 0

matrix_rows_list = []
while index < nblocks - 3:
    # read control block
    index += 1
    content = np.frombuffer(blocks[index], dtype=INT4)
    control_block = content[0]

    if control_block == -1:
        index += 1
        content = np.frombuffer(blocks[index], dtype=INT4)
        nsize = content[0]

        index += 1
        data_list = np.frombuffer(blocks[index], dtype=INT4)

        # check if data_block has nsize elements
        if len(data_list) != nsize:
            print(f"Data block size mismatch: expected {nsize}, got {len(data_list)}")

        solution_type = data_list[0]  # 101 for static analysis
        solution_type = data_list[0]  # 101 for static analysis
        matrix_type = data_list[1]  # 66 for stiffness matrix
        data_format = data_list[3]  # 6 for double precision
        matrix_symmetric = data_list[4]  # 2 for symmetric, else 1 for unsymmetric
        matrix_size = data_list[5]  # size of the KLL matrix
        user_identifier = data_list[6]  # identifier of the subDMAP created the matrix
        load_case_id = data_list[7]  # load case ID
    elif control_block == -2:
        index += 1
        content = np.frombuffer(blocks[index], dtype=INT4)
        nsize = content[0]

        # if nsize != nvars:
        #     print(f"Variable names block size mismatch: expected {nvars}, got {nsize}")

        index += 1
        variable_names.append(blocks[index].strip().decode("utf-8"))

    elif control_block <= -3:
        index += 1
        content = np.frombuffer(blocks[index], dtype=INT4)
        nsize = round(content[0] / 2)

        if nsize == 0:
            # reset matrix
            KGG = np.stack(matrix_rows_list)
            matrix_rows_list = []
            # print(KGG)
            print(KGG.shape)
            print(variable_names)

            # control code == 0, means end of matrix
            continue

        index += 1
        content = np.frombuffer(blocks[index], dtype=np.float64)
        # add content to KGG
        matrix_rows_list.append(content)

        data_entry += 1

        if data_entry == 66:
            print("Reached 66 data entries, stopping read.")

# reset matrix
KGG = np.stack(matrix_rows_list)
matrix_rows_list = []
# print(KGG)
print(KGG.shape)
print(variable_names)
