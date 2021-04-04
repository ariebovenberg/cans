from typing import TypeVar

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
U = TypeVar("U")
U_co = TypeVar("U_co", covariant=True)
