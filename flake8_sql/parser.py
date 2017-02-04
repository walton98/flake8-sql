from typing import Any, Generator

import sqlparse

from .keywords import ROOT_KEYWORDS


class Token:

    def __init__(self, token: sqlparse.sql.Token, row: int, col: int) -> None:
        self._token = token
        self.row = row
        self.col = col

    @property
    def is_whitespace(self) -> bool:
        return self._token.is_whitespace

    @property
    def is_keyword(self) -> bool:
        return self._token.is_keyword

    @property
    def is_root_keyword(self) -> bool:
        return self.is_keyword and self.value.upper() in ROOT_KEYWORDS

    @property
    def is_function_name(self) -> bool:
        # Note the only name-token who's grandparent is a function is
        # the function identifier.
        return (
            self._token.ttype == sqlparse.tokens.Name and
            self._token.within(sqlparse.sql.Function) and
            isinstance(self._token.parent.parent, sqlparse.sql.Function) and
            sqlparse.keywords.is_keyword(self._token.value)[0] == sqlparse.tokens.Token.Keyword
        )

    @property
    def is_name(self) -> bool:
        return self._token.ttype == sqlparse.tokens.Name and not self.is_keyword

    @property
    def is_punctuation(self) -> bool:
        return self._token.ttype == sqlparse.tokens.Punctuation

    @property
    def is_comparison(self) -> bool:
        return self._token.ttype == sqlparse.tokens.Comparison

    @property
    def is_newline(self) -> bool:
        return self._token.ttype == sqlparse.tokens.Text.Whitespace.Newline

    @property
    def value(self) -> str:
        return self._token.value


class Parser:

    def __init__(self, sql: str, initial_offset: int) -> None:
        self.sql = sql
        self._initial_offset = initial_offset

    def __iter__(self) -> Generator[Token, Any, None]:
        statements = sqlparse.parse(self.sql)
        row = 0
        col = self._initial_offset
        for statement in statements:
            for sql_token in statement.flatten():
                token = Token(sql_token, row, col)
                yield token
                if token.is_newline:
                    row += 1
                    col = 0
                else:
                    col += len(token.value)
