from typing import Any


_FIELD_LABELS = {
    "active": "ativo",
    "email": "e-mail",
    "password": "senha",
    "profile_id": "ID do perfil",
    "user_uuid": "ID do usuário",
    "username": "nome de usuário",
}


def format_validation_errors(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    formatted_errors: list[dict[str, Any]] = []

    for error in errors:
        field_name = _extract_field_name(error.get("loc", ()))
        formatted_errors.append(
            {
                **error,
                "ctx": None,  # remove o ctx — contém objetos não serializáveis
                "msg": _translate_error(error, field_name),
            }
        )

    return formatted_errors


def _extract_field_name(location: Any) -> str:
    if not location:
        return ""

    path = [str(part) for part in location if part not in {"body", "query", "path", "header"}]
    return path[-1] if path else ""


def _label_for(field_name: str) -> str:
    return _FIELD_LABELS.get(field_name, field_name.replace("_", " "))


def _translate_error(error: dict[str, Any], field_name: str) -> str:
    error_type = str(error.get("type", ""))
    context = error.get("ctx") or {}
    label = _label_for(field_name)

    if error_type == "missing":
        return f"O campo {label} é obrigatório."

    if error_type == "string_too_short":
        min_length = context.get("min_length")
        if min_length is not None:
            return f"O campo {label} deve ter pelo menos {min_length} caracteres."
        return f"O campo {label} está muito curto."

    if error_type == "string_too_long":
        max_length = context.get("max_length")
        if max_length is not None:
            return f"O campo {label} deve ter no máximo {max_length} caracteres."
        return f"O campo {label} está muito longo."

    if error_type in {"string_type", "string_sub_type"}:
        return f"O campo {label} deve ser um texto válido."

    if error_type in {"uuid_parsing", "uuid_type"}:
        return f"O campo {label} deve ser um UUID válido."

    if error_type in {"bool_parsing", "bool_type"}:
        return f"O campo {label} deve ser verdadeiro ou falso."

    if field_name == "email" and error_type in {"value_error", "string_pattern_mismatch"}:
        return "O e-mail informado é inválido."

    if error_type == "value_error":
        message = str(error.get("msg", "Valor inválido."))
        if message.startswith("Value error, "):
            return message.replace("Value error, ", "", 1)
        return message

    return f"O campo {label} é inválido."