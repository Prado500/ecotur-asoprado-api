"""Field rule shared by the partial-update DTOs: explicit null only where the column admits it.

In a partial update an absent field means "leave it as it is" and an explicit null means "empty
it". Only a column that admits empty can store the second, so every other optional field of
UserUpdate and ServiceUpdate rejects null at the boundary, with a 422, before any policy,
storage call or audit row runs (ADR-0020).
"""

from typing import Any

from pydantic import BeforeValidator

_NULL_MESSAGE = "Este campo no puede quedar vacío."


def _reject_explicit_null(value: Any) -> Any:
    """Lets every value through except an explicit null.

    Runs before the field's own type and constraints, and only for a field present in the
    payload: an absent field keeps its None default without reaching this check.

    Args:
        value: The raw value received for the field.

    Returns:
        The same value, untouched.

    Raises:
        ValueError: If the value is None; the 422 handler shows its message.
    """
    if value is None:
        raise ValueError(_NULL_MESSAGE)
    return value


# Usage: Annotated[T | None, NoExplicitNull] on an update field whose column is NOT NULL. The
# annotation keeps "| None" because an absent field is None on the model (ADR-0020).
NoExplicitNull = BeforeValidator(_reject_explicit_null)
