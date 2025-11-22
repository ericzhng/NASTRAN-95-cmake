import logging
import numpy as np
from typing import List, Dict, Any, Optional

log = logging.getLogger(__name__)


class NastranMatrix:
    """
    A data class to hold a NASTRAN matrix and its associated metadata,
    including all associated variable names.
    """

    def __init__(
        self,
        names: List[str],
        data: np.ndarray,
        info: Dict[str, Any],
    ):
        """
        Initializes the NastranMatrix object.

        Args:
            names: A list of names associated with the matrix.
            data: The matrix data as a NumPy array.
            info: A dictionary containing metadata about the matrix.
        """
        self.names: List[str] = names
        self.data: np.ndarray = data
        self.solution_type: Optional[int] = info.get("solution_type")
        self.matrix_type: Optional[int] = info.get("matrix_type")
        self.data_format: Optional[int] = info.get("data_format")
        self.is_symmetric: bool = info.get("is_symmetric", False)
        self.matrix_size: Optional[int] = info.get("matrix_size")
        self.user_identifier: Optional[int] = info.get("user_identifier")
        self.load_case_id: Optional[int] = info.get("load_case_id")
        log.debug(f"Created NastranMatrix: {self!r}")

    @property
    def name(self) -> str:
        """Returns the primary name of the matrix."""
        return self.names[0] if self.names else "UNKNOWN"

    def __repr__(self) -> str:
        """Returns a string representation of the NastranMatrix object."""
        return f"NastranMatrix(name='{self.name}', shape={self.data.shape}, names={self.names})"

    def summary(self) -> str:
        """Returns a formatted string summary of the matrix and its metadata."""
        info_str = "\n".join(
            [
                f"  - Primary Name: {self.name}",
                f"  - All Names: {self.names}",
                f"  - Shape: {self.data.shape}",
                f"  - Data Type: {self.data.dtype}",
                "  - Metadata:",
                f"    - Solution Type: {self.solution_type}",
                f"    - Matrix Type: {self.matrix_type}",
                f"    - Data Format: {self.data_format}",
                f"    - Is Symmetric: {self.is_symmetric}",
                f"    - Matrix Size: {self.matrix_size}",
                f"    - User Identifier: {self.user_identifier}",
                f"    - Load Case ID: {self.load_case_id}",
            ]
        )
        return info_str
