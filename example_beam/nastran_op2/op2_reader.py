import struct
import logging
import numpy as np
from typing import List, Optional, IO, Dict, Any

from .nastran_matrix import NastranMatrix

log = logging.getLogger(__name__)

# All data in this NASTRAN version is typically Little-Endian
INT4 = "<i"
REAL8 = "<d"

# Control block values used in the OP2 file format
_MATRIX_HEADER_FLAG = -1
_NEW_VARIABLE_NAME_FLAG = -2
_DATA_BLOCK_FLAG = -3


class OP2Reader:
    """
    A class to read NASTRAN 95 compatible OP2 (Output2) binary files.

    This class is designed to be used as a context manager to ensure
    proper file handling.

    Example:
        with OP2Reader("my_file.op2") as reader:
            reader.parse()
            stiffness_matrix = reader.get_matrix_by_name("KGG")
    """

    def __init__(self, filename: str):
        """
        Initializes the OP2Reader.

        Args:
            filename: The path to the OP2 file.
        """
        self.filename: str = filename
        self.nastran_matrices: List[NastranMatrix] = []
        self._blocks: List[bytes] = []
        self._file: Optional[IO[bytes]] = None

    def __enter__(self) -> "OP2Reader":
        """Opens the OP2 file for reading."""
        log.info(f"Opening file: '{self.filename}'")
        self._file = open(self.filename, "rb")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the OP2 file."""
        if self._file:
            log.info(f"Closing file: '{self.filename}'")
            self._file.close()
            self._file = None

    def _extract_data_blocks(self) -> None:
        """
        Reads the OP2 file and extracts all data blocks.

        A data block in a NASTRAN OP2 file is a record enclosed by two
        4-byte integers specifying the record's length.
        """
        if not self._file:
            raise IOError(
                "File is not open. Use the 'with' statement for proper handling."
            )

        self._blocks = []
        while True:
            start_marker = self._file.read(4)
            if not start_marker:
                break  # End of file

            (record_size,) = struct.unpack(INT4, start_marker)
            data_block = self._file.read(record_size)
            end_marker = self._file.read(4)

            if not end_marker:
                log.error(
                    "File ended unexpectedly after reading a data block. File may be corrupt."
                )
                break

            (end_size,) = struct.unpack(INT4, end_marker)
            if record_size != end_size:
                log.error(
                    f"Record size mismatch ({record_size} != {end_size}). File may be corrupt."
                )
                break

            self._blocks.append(data_block)
        log.info(f"Extracted {len(self._blocks)} data blocks from the file.")

    def _parse_matrix_header(self, index: int) -> Dict[str, Any]:
        """Parses a matrix header block."""
        data_list = np.frombuffer(self._blocks[index], dtype=INT4)
        info = {
            "solution_type": data_list[0],
            "matrix_type": data_list[1],
            "data_format": data_list[3],
            "is_symmetric": data_list[4] == 2,
            "matrix_size": data_list[5],
            "user_identifier": data_list[6],
            "load_case_id": data_list[7],
        }
        log.debug(f"Parsed matrix header: {info}")
        return info

    def _create_and_store_matrix(
        self, names: List[str], rows: List[np.ndarray], info: Dict[str, Any]
    ) -> None:
        """Creates a NastranMatrix and stores it."""
        if not rows or not names:
            log.warning("Attempted to create a matrix with no data or names. Skipping.")
            return

        try:
            matrix_data = np.stack(rows)
            matrix_obj = NastranMatrix(names, matrix_data, info)
            self.nastran_matrices.append(matrix_obj)
            log.info(f"Successfully created and stored {matrix_obj!r}.")
        except Exception as e:
            log.error(f"Failed to create NastranMatrix: {e}")

    def parse(self) -> None:
        """
        Parses the extracted data blocks to find and construct matrices.
        """
        if self._file is None:
            # This allows calling parse() outside a 'with' block for convenience,
            # though it's not the recommended pattern.
            with self as reader:
                reader.parse()
            return

        self._extract_data_blocks()

        if not self._blocks:
            log.warning("No data blocks found to parse.")
            return

        num_blocks = len(self._blocks)
        current_names = [self._blocks[1].strip().decode("utf-8")]
        current_matrix_rows = []
        current_matrix_info = {}
        end_of_matrix_found = False

        index = 1
        while index < num_blocks - 1:
            index += 1
            try:
                control_block_val = np.frombuffer(self._blocks[index], dtype=INT4)[0]
            except IndexError:
                log.warning(
                    f"Could not read control block at index {index}. Stopping parse."
                )
                break

            if control_block_val == _MATRIX_HEADER_FLAG:
                index += 2
                current_matrix_info = self._parse_matrix_header(index)
            elif control_block_val == _NEW_VARIABLE_NAME_FLAG:
                index += 2
                new_name = self._blocks[index].strip().decode("utf-8")
                current_names.append(new_name)
                log.debug(f"Found new variable name: '{new_name}'")
            elif control_block_val <= _DATA_BLOCK_FLAG:
                index += 1
                data_size_bytes = np.frombuffer(self._blocks[index], dtype=INT4)[0]
                if data_size_bytes == 0:
                    end_of_matrix_found = True
                    log.debug("End of matrix marker found.")
                else:
                    index += 1
                    row_data = np.frombuffer(self._blocks[index], dtype=np.float64)
                    current_matrix_rows.append(row_data)

            if end_of_matrix_found:
                self._create_and_store_matrix(
                    current_names, current_matrix_rows, current_matrix_info
                )
                # Reset for the next matrix
                current_matrix_rows = []
                current_matrix_info = {}
                current_names = []
                end_of_matrix_found = False

    def print_matrix_info(self) -> None:
        """Prints a summary of all parsed matrices to the console."""
        if not self.nastran_matrices:
            print("No matrices have been parsed or stored.")
            return
        print("\n--- Parsed Matrix Information ---")
        for matrix_obj in self.nastran_matrices:
            print(f"\n{matrix_obj.summary()}")
        print("\n---------------------------------")

    def get_matrix_by_name(self, name: str) -> Optional[NastranMatrix]:
        """
        Finds the first matrix that has the given name in its list of names.

        Args:
            name: The name to search for.

        Returns:
            The matching NastranMatrix object, or None if not found.
        """
        return next((m for m in self.nastran_matrices if name in m.names), None)
