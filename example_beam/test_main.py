import logging
from nastran_op2.op2_reader import OP2Reader


def setup_logging():
    """Sets up basic logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    # To see debug messages, change level to logging.DEBUG
    # logging.getLogger("nastran_op2").setLevel(logging.DEBUG)


def main(file_to_read: str):
    """
    Main function to read and process the NASTRAN OP2 file.
    """
    print(f"Reading OP2 file: {file_to_read}")

    # Use the OP2Reader class to parse the file
    with OP2Reader(file_to_read) as reader:
        # Parse the file to extract all matrices
        reader.parse()

        # Print a summary of all found matrices and their metadata
        reader.print_matrix_info()

        # --- Verification ---
        # You can now find matrices by searching for any of their associated names
        # using the get_matrix_by_name() method.
        print("\n--- Verification ---")

        # Search for a matrix by one of its secondary names
        search_name = "KGGX"
        print(f"Searching for matrix with name: '{search_name}'...")
        kgg_matrix_obj = reader.get_matrix_by_name(search_name)

        if kgg_matrix_obj:
            print(f"Found matrix with primary name: '{kgg_matrix_obj.name}'")
            # Access the raw numpy data via the .data attribute
            kgg_matrix_data = kgg_matrix_obj.data
            print(f"Successfully retrieved matrix with shape: {kgg_matrix_data.shape}")
            print(f"Is matrix symmetric? {kgg_matrix_obj.is_symmetric}")
            print(f"All names for this matrix: {kgg_matrix_obj.names}")
        else:
            print(f"\nMatrix with name '{search_name}' not found in the file.")


if __name__ == "__main__":
    # Set up logging to see output from the library
    setup_logging()

    # Define the path to the OP2 file
    # This file is a sample output from a NASTRAN run
    file_to_read = "OUTPUT/test.f11"

    main(file_to_read)
