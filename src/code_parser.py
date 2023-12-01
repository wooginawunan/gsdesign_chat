import re
import ast
from abc import ABC, abstractmethod
from typing import Any, List
from langchain.docstore.document import Document

class CodeSegmenter(ABC):
    """Abstract class for the code segmenter."""
    def __init__(self, code: str):
        self.code = code

    def is_valid(self) -> bool:
        return True

    @abstractmethod
    def simplify_code(self) -> str:
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def extract_functions_classes(self) -> List[str]:
        raise NotImplementedError()  # pragma: no cover


class PythonSegmenter(CodeSegmenter):
    """Code segmenter for `Python`."""

    def __init__(self, code: str):
        super().__init__(code)
        self.source_lines = self.code.splitlines()


    def is_valid(self) -> bool:
        try:
            ast.parse(self.code)
            return True
        except SyntaxError:
            return False

    def _extract_code(self, node: Any) -> str:
        start = node.lineno - 1
        end = node.end_lineno
        return "\n".join(self.source_lines[start:end])

    def extract_functions_classes(self) -> List[str]:
        tree = ast.parse(self.code)
        functions_classes = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                functions_classes.append(self._extract_code(node))

        return functions_classes

    def simplify_code(self) -> str:
        tree = ast.parse(self.code)
        simplified_lines = self.source_lines[:]

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = node.lineno - 1
                simplified_lines[start] = f"# Code for: {simplified_lines[start]}"

                assert isinstance(node.end_lineno, int)
                for line_num in range(start + 1, node.end_lineno):
                    simplified_lines[line_num] = None  # type: ignore

        return "\n".join(line for line in simplified_lines if line is not None)


class RSegmenter(CodeSegmenter):
    '''parse R script'''
    def __init__(self, code: str):
        super().__init__(code)
        self.source_lines = self.code.splitlines()
    
    def _extract_code(self, match) -> str:

        start = match.start()
        end = match.end()

        # Extract initial match
        func = self.code[start:end]

        # Check subsequent lines for continuation
        max_lines = 10
        lines_checked = 0
        
        while not func.endswith("}") and lines_checked < max_lines:
            end = self.code.find("}", end+1)
            if end == -1: # Reached end of code without finding }
                break 
            func = self.code[start:end+1]
            lines_checked += 1

        # If we didn't find closing }, just return initial match
        if not func.endswith("}"): 
            func = self.code[start:end]

        return func

    def extract_functions_classes(self) -> List[str]:
        functions = []
        pattern = r"^(\w+)\s*<-\s*{?|\bfun|\bfunction"
        
        matches = re.finditer(pattern, self.code, re.M)
        
        for match in matches:
            func = self._extract_code(match)
            functions.append(func)

        return functions

    def simplify_code(self) -> str:
        simplified_lines = self.source_lines[:]
        pattern = r"^(\w+)\s*\<\-|\bfun|\bfunction"

        for i, line in enumerate(simplified_lines):
            if re.search(pattern, line):
                simplified_lines[i] = f"# Code for: {simplified_lines[i]}"
        
        return "\n".join(simplified_lines)