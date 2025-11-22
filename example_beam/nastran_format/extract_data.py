import struct
import logging
from typing import List, Optional

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# All data in this NASTRAN version is typically Little-Endian
INT4 = "<i"  # Little-endian 32-bit signed integer
REAL8 = "<d"  # Little-endian 64-bit double-precision float (for matrix data)


def extract_data_blocks(filename: str) -> List[bytes]:
    """Reads a raw unformatted FORTRAN sequential file and extracts data blocks.

    This function opens a binary file written by a FORTRAN program that uses
    unformatted sequential access. It reads the file block by block, where each
    block is framed by 4-byte integer markers indicating the block's size.

    The structure of each record is expected to be:
    [4-byte size] [data] [4-byte size]

    Args:
        filename: The path to the FORTRAN binary file.

    Returns:
        A list of byte strings, where each string is a data block from the file.
        Returns None if the file cannot be found or a critical error occurs.
    """
    raw_blocks: List[bytes] = []
    logging.info(f"Attempting to read data blocks from '{filename}'.")

    try:
        with open(filename, "rb") as f:
            while True:
                # 1. Read the Start Marker (4-byte integer)
                start_marker_bytes = f.read(4)
                if not start_marker_bytes:
                    logging.info("Reached end of file.")
                    break

                if len(start_marker_bytes) != 4:
                    logging.error(
                        f"Failed to read start marker. Expected 4 bytes, got {len(start_marker_bytes)}. "
                        f"File position: {f.tell() - len(start_marker_bytes)}."
                    )
                    break

                (record_size,) = struct.unpack(INT4, start_marker_bytes)

                # 2. Read the Data Block
                data_block = f.read(record_size)
                if len(data_block) != record_size:
                    logging.error(
                        f"Incomplete data block. Expected {record_size} bytes, got {len(data_block)}. "
                        f"File position: {f.tell() - len(data_block)}."
                    )
                    break

                # 3. Read the End Marker (4-byte integer)
                end_marker_bytes = f.read(4)
                if len(end_marker_bytes) != 4:
                    logging.error(
                        f"Failed to read end marker. Expected 4 bytes, got {len(end_marker_bytes)}. "
                        f"File position: {f.tell() - len(end_marker_bytes)}."
                    )
                    break

                (end_marker_size,) = struct.unpack(INT4, end_marker_bytes)

                # 4. Verify that Start and End Markers match
                if record_size != end_marker_size:
                    logging.error(
                        f"Record size mismatch! Start marker: {record_size}, End marker: {end_marker_size}. "
                        f"File position: {f.tell() - 4}. This indicates a corrupted or misaligned file."
                    )
                    break

                raw_blocks.append(data_block)

    except FileNotFoundError:
        logging.error(f"File not found: '{filename}'.")
        raise
    except struct.error as e:
        logging.error(f"A struct unpacking error occurred: {e}. File may be corrupt.")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise

    logging.info(
        f"Successfully extracted {len(raw_blocks)} data blocks from '{filename}'."
    )
    return raw_blocks
