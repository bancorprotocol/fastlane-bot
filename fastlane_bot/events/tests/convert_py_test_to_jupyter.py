# coding=utf-8
"""
Converts traditional pytest test files into Jupyter notebooks.

Example Usage:
    python fastlane_bot/events/tests/convert_py_test_to_jupyter.py fastlane_bot/events/tests/test_manager.py NBTest_036_events_Manager.ipynb

"""
import ast
import textwrap

import nbformat as nbf
import click
from astunparse import unparse


class RewriteFunctions(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        # If the function is a test function or a pytest fixture, transform it to standalone code
        if node.name.startswith("test_") or any(
            decorator.__dict__["attr"] in ["fixture", "mark"]
            for decorator in node.decorator_list
            if hasattr(decorator, "__dict__") and "attr" in decorator.__dict__
        ):
            node.decorator_list = []  # Remove decorators
            return node  # Return the modified function
        return node  # Leave the function definition unchanged for non-test functions

    def return_function_body(self, node):
        # Return the body of the function as a string
        if node.name.startswith("test_") or any(
            decorator.__dict__["attr"] in ["fixture", "mark"]
            for decorator in node.decorator_list
            if hasattr(decorator, "__dict__") and "attr" in decorator.__dict__
        ):
            # node.decorator_list = []  # Remove decorators
            # return node  # Return the modified function
            return unparse(node.body)
        return node  # Leave the function definition unchanged for non-test functions


@click.command()
@click.argument("python_filename", type=click.Path(exists=True))
@click.argument("output_notebook", type=click.Path())
def convert_python_to_notebook(python_filename, output_notebook):
    # Open and read the python file
    with open(python_filename, "r") as file:
        python_code = file.read()

    # Find the last import statement line (assume it's "require("3.0", __VERSION__)")
    last_import_line = python_code.index('require("3.0", __VERSION__)')
    last_import_line += len('require("3.0", __VERSION__)')

    # Split python_code into import statements and the rest of the code
    import_statements, rest_of_code = (
        python_code[:last_import_line],
        python_code[last_import_line:],
    )

    # Create a new notebook
    nb = nbf.v4.new_notebook()

    # Add import statements to the first cell
    nb["cells"].append(nbf.v4.new_code_cell(import_statements.strip()))

    # Parse the rest of the code into an Abstract Syntax Tree (AST)
    module = ast.parse(rest_of_code)

    # Rewrite test functions and fixtures to standalone code
    transformer = RewriteFunctions()
    module = transformer.visit(module)

    # Unparse each function (now standalone code) back to Python code and add the Python code to a new notebook cell
    for stmt in ast.iter_child_nodes(module):
        if isinstance(stmt, ast.FunctionDef):  # Only include function definitions
            standalone_code = unparse(ast.Module(body=[stmt]))

            # Remove the function definition (first line of standalone_code)
            standalone_code = "\n".join(standalone_code.split("\n")[3:])
            standalone_code = "\n".join(standalone_code.split("\n")[:-2])

            # Dedent the code
            standalone_code = textwrap.dedent(standalone_code)

            # Add the standalone code to a new notebook cell
            nb["cells"].append(nbf.v4.new_code_cell(standalone_code))

    # Write the notebook to a file
    with open(output_notebook, "w") as file:
        nbf.write(nb, file)


if __name__ == "__main__":
    convert_python_to_notebook()
