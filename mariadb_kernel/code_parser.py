"""A simple parser for extracting some meaning out of a code cell

The parser walks to the code coming from the kernel and separates it into
SQL code and magic commands.
The SQL code is passed further by the kernel to the MariaDB client for
execution.
The magic objects created here are invoked in the kernel to perform
their duties.
"""

# Copyright (c) MariaDB Foundation.
# Distributed under the terms of the Modified BSD License.

from mariadb_kernel.maria_magics.magic_factory import MagicFactory

class CodeParser:
    def __init__(self, log, cell_code):
        self.code = cell_code
        self.magics = []
        self.sql = []
        self.log = log
        self.magic_factory = MagicFactory(log)
        self._parse()

    def get_sql(self):
        return self.sql

    def get_magics(self):
        return self.magics

    def _is_magic(self, code):
        return code.startswith("%")

    def _parse_magic(self, code):
        args = ""
        magic_cmd = None
        if code.startswith("%%"):
            magic_cmd = code.split(" ", 1)[0][2:]
            args = self.sql
        else:
            split = code.split(" ", 1)
            magic_cmd = split[0][1:]

            if len(split) > 1:
                args = split[1]

        return self.magic_factory.create_magic(magic_cmd, args)

    def _parse(self):
        lines = self.code.split("\n")
        magic_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if self._is_magic(line):
                magic_lines.append(line)
                i += 1
                continue
            j = i
            code = ""
            while j < len(lines):
                code = code + lines[j] + " "
                if lines[j].find(";") >= 0:
                    break
                j += 1

            # Raise an exception if no SQL delimiter was found
            if j == len(lines):
                raise ValueError("No delimiter was found in the SQL code")

            self.sql.append(code)
            i = j + 1

        for line in magic_lines:
            self.magics.append(self._parse_magic(line))
