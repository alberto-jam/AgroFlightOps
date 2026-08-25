from unidecode import unidecode


def normalize_for_path(text: str) -> str:
    """Remove acentos e substitui espaços por underscore.

    Utilizado para compor caminhos S3 padronizados a partir de nomes
    de clientes ou outras strings que podem conter caracteres especiais.

    Exemplo:
        >>> normalize_for_path("Fazenda São José")
        'Fazenda_Sao_Jose'
    """
    return unidecode(text).replace(" ", "_")
