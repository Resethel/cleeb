from re import sub


def snake_case_to_camel_case(snake_str, capitalize_first=False):
    """Convert a string from snake_case to camelCase."""
    first, *others = snake_str.split('_')
    return ''.join([first.lower() if not capitalize_first else first.title(), *map(str.title, others)])


def snake_case(str_ : str):

    # Replace hyphens with spaces, then apply regular expression substitutions for title case conversion
    # and add an underscore between words, finally convert the result to lowercase
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
            sub('([A-Z]+)', r' \1',
                str_.replace('-', ' '))).split()).lower()
