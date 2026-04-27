"""Extract variable metadata from PolicyEngine Python source code."""

import ast
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set

from app.services.formula_parser import FormulaParser


class CodeExtractor:
    """Extract variable metadata from Python source code using AST."""

    def __init__(self, repo_path: Path):
        """
        Initialize code extractor.

        Args:
            repo_path: Path to policyengine-us repository root
        """
        self.repo_path = repo_path
        self.variables_path = repo_path / "policyengine_us/variables"
        self.parameters_path = repo_path / "policyengine_us/parameters"
        self.formula_parser = FormulaParser(repo_path)

    def extract_qbi_variables(self) -> Dict[str, dict]:
        """
        Extract all QBI-related variables.

        Returns:
            Dictionary mapping variable names to metadata
        """
        qbi_base = (
            self.variables_path
            / "gov/irs/income/taxable_income/deductions/qualified_business_income_deduction"
        )

        variables = {}

        # Process all Python files in QBI directory
        for py_file in qbi_base.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue

            try:
                var_data = self.extract_variable_from_file(py_file)
                if var_data:
                    variables[var_data["name"]] = var_data
            except Exception as e:
                print(f"Warning: Failed to parse {py_file}: {e}")

        # Extract related input variables
        input_vars = self._extract_input_variables(variables)
        variables.update(input_vars)

        return variables

    def extract_variable_from_file(self, file_path: Path) -> Optional[dict]:
        """
        Extract variable metadata from a Python file using AST.

        Args:
            file_path: Path to Python file

        Returns:
            Dictionary with variable metadata, or None if not a variable file
        """
        source = file_path.read_text()

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            raise Exception(f"Syntax error in {file_path}: {e}")

        # Find the Variable class
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a Variable subclass
                if any(
                    isinstance(base, ast.Name) and base.id == "Variable"
                    for base in node.bases
                ):
                    return self._extract_from_class(node, file_path, source)

        return None

    def _extract_from_class(
        self, class_node: ast.ClassDef, file_path: Path, source: str
    ) -> dict:
        """Extract metadata from a Variable class node."""
        var_name = self._camel_to_snake(class_node.name)

        metadata = {
            "name": var_name,
            "class_name": class_node.name,
            "file_path": str(file_path.relative_to(self.repo_path)),
            "label": None,
            "entity": None,
            "definition_period": None,
            "value_type": None,
            "unit": None,
            "reference": [],
            "documentation": None,
            "defined_for": None,
            "formula": None,
            "formula_source": None,
            "formula_line_start": None,
            "formula_line_end": None,
            "dependencies": [],
            "adds": [],
            "parameters": [],
            "has_formula": False,
            "is_input": False,
            "operation_nodes": [],
            "operation_edges": [],
        }

        # Store formula AST node for later parsing
        formula_ast_node = None

        # Extract class attributes
        for item in class_node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attr_name = target.id

                        if attr_name == "label":
                            metadata["label"] = self._extract_string(item.value)
                        elif attr_name == "entity":
                            metadata["entity"] = self._extract_entity(item.value)
                        elif attr_name == "definition_period":
                            metadata["definition_period"] = self._extract_constant(
                                item.value
                            )
                        elif attr_name == "value_type":
                            metadata["value_type"] = self._extract_type(item.value)
                        elif attr_name == "unit":
                            metadata["unit"] = self._extract_constant(item.value)
                        elif attr_name == "reference":
                            metadata["reference"] = self._extract_reference(item.value)
                        elif attr_name == "documentation":
                            metadata["documentation"] = self._extract_string(item.value)
                        elif attr_name == "defined_for":
                            metadata["defined_for"] = self._extract_string(item.value)

            # Extract formula
            elif isinstance(item, ast.FunctionDef) and item.name == "formula":
                metadata["has_formula"] = True
                metadata["formula_line_start"] = item.lineno
                metadata["formula_line_end"] = item.end_lineno
                formula_ast_node = item

                # Get source code of formula
                metadata["formula_source"] = ast.get_source_segment(source, item)

                # Parse dependencies
                metadata["dependencies"] = self._extract_dependencies(item)
                metadata["adds"] = self._extract_adds(item)
                metadata["parameters"] = self._extract_parameters(item)

                # Store unparsed formula
                metadata["formula"] = ast.unparse(item)

                # Parse formula into detailed operations
                try:
                    op_nodes, op_edges = self.formula_parser.parse_formula_to_operations(
                        var_name, item, metadata["formula_source"]
                    )
                    metadata["operation_nodes"] = op_nodes
                    metadata["operation_edges"] = op_edges
                except Exception as e:
                    print(f"Warning: Failed to parse formula for {var_name}: {e}")
                    metadata["operation_nodes"] = []
                    metadata["operation_edges"] = []

        # Determine if this is an input variable
        metadata["is_input"] = not metadata["has_formula"]

        return metadata

    def _extract_dependencies(self, formula_node: ast.FunctionDef) -> List[str]:
        """Find all variable dependencies in formula."""
        dependencies = set()

        for node in ast.walk(formula_node):
            # Look for: entity("variable_name", period)
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ["person", "tax_unit", "household", "spm_unit"]:
                        if node.args and isinstance(node.args[0], ast.Constant):
                            dependencies.add(node.args[0].value)
                # Also handle direct entity calls
                elif isinstance(node.func, ast.Name) and node.func.id in [
                    "person",
                    "tax_unit",
                    "household",
                ]:
                    if node.args and isinstance(node.args[0], ast.Constant):
                        dependencies.add(node.args[0].value)

        return sorted(list(dependencies))

    def _extract_adds(self, formula_node: ast.FunctionDef) -> List[str]:
        """Find variables combined with add() function."""
        adds = []

        for node in ast.walk(formula_node):
            # Look for: add(entity, period, ["var1", "var2"])
            # or add(entity, period, parameter.list)
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "add":
                    if len(node.args) >= 3:
                        vars_arg = node.args[2]
                        if isinstance(vars_arg, ast.List):
                            for elt in vars_arg.elts:
                                if isinstance(elt, ast.Constant):
                                    adds.append(elt.value)

        return adds

    def _extract_parameters(self, formula_node: ast.FunctionDef) -> List[str]:
        """Find parameter paths accessed in formula."""
        parameters = set()

        # Look for parameters(period) assignment
        param_var = None
        for node in ast.walk(formula_node):
            if isinstance(node, ast.Assign):
                # Check if this is p = parameters(period).gov...
                if isinstance(node.value, ast.Attribute):
                    current = node.value
                    path_parts = []

                    while isinstance(current, ast.Attribute):
                        path_parts.insert(0, current.attr)
                        current = current.value

                    # Check if it starts with parameters()
                    if isinstance(current, ast.Call):
                        if (
                            isinstance(current.func, ast.Name)
                            and current.func.id == "parameters"
                        ):
                            # This is the parameter prefix
                            if path_parts:
                                param_prefix = ".".join(path_parts)
                                # Store the variable name used for parameters
                                for target in node.targets:
                                    if isinstance(target, ast.Name):
                                        param_var = target.id
                                        parameters.add(param_prefix)

        return sorted(list(parameters))

    def _extract_variables_from_qbi_parameters(self) -> Set[str]:
        """
        Extract variable names from QBI parameter YAML files.

        Returns:
            Set of variable names found in parameter lists
        """
        variables = set()

        # Path to QBI parameters
        qbi_params_path = (
            self.parameters_path / "gov/irs/deductions/qbi"
        )

        if not qbi_params_path.exists():
            return variables

        # Read income_definition.yaml
        income_def_file = qbi_params_path / "income_definition.yaml"
        if income_def_file.exists():
            try:
                with open(income_def_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if 'values' in data:
                        # Get the most recent value
                        for date_key in sorted(data['values'].keys(), reverse=True):
                            var_list = data['values'][date_key]
                            if isinstance(var_list, list):
                                variables.update(var_list)
                                # Also add _would_be_qualified variants
                                for var in var_list:
                                    variables.add(f"{var}_would_be_qualified")
                            break
            except Exception as e:
                print(f"Warning: Failed to parse {income_def_file}: {e}")

        # Read deduction_definition.yaml
        deduction_def_file = qbi_params_path / "deduction_definition.yaml"
        if deduction_def_file.exists():
            try:
                with open(deduction_def_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if 'values' in data:
                        # Get the most recent value
                        for date_key in sorted(data['values'].keys(), reverse=True):
                            var_list = data['values'][date_key]
                            if isinstance(var_list, list):
                                variables.update(var_list)
                            break
            except Exception as e:
                print(f"Warning: Failed to parse {deduction_def_file}: {e}")

        return variables

    def _extract_input_variables(self, qbi_vars: Dict[str, dict]) -> Dict[str, dict]:
        """
        Extract input variables (those referenced but not in QBI module).

        Args:
            qbi_vars: Already extracted QBI variables

        Returns:
            Dictionary of input variable stubs
        """
        all_deps: Set[str] = set()
        for var in qbi_vars.values():
            all_deps.update(var["dependencies"])
            all_deps.update(var["adds"])

        # Also add variables from QBI parameter files
        param_vars = self._extract_variables_from_qbi_parameters()
        all_deps.update(param_vars)

        # Remove variables already extracted
        input_vars = all_deps - set(qbi_vars.keys())

        # Create stub entries
        stubs = {}
        for var_name in input_vars:
            # Try to find the actual file
            var_file = self._find_variable_file(var_name)

            if var_file:
                try:
                    var_data = self.extract_variable_from_file(var_file)
                    if var_data:
                        stubs[var_name] = var_data
                        continue
                except:
                    pass

            # Fallback: create minimal stub
            stubs[var_name] = {
                "name": var_name,
                "label": var_name.replace("_", " ").title(),
                "entity": "Unknown",
                "definition_period": "YEAR",
                "value_type": "float",
                "is_input": True,
                "has_formula": False,
                "file_path": "unknown",
                "dependencies": [],
                "parameters": [],
            }

        return stubs

    def _find_variable_file(self, var_name: str) -> Optional[Path]:
        """Try to find the file for a variable by name."""
        possible_files = list(self.variables_path.rglob(f"{var_name}.py"))
        return possible_files[0] if possible_files else None

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        """Convert CamelCase to snake_case."""
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    @staticmethod
    def _extract_string(node: ast.AST) -> Optional[str]:
        """Extract string value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        return None

    @staticmethod
    def _extract_constant(node: ast.AST) -> Optional[str]:
        """Extract constant value."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Attribute):
            return node.attr
        elif isinstance(node, ast.Name):
            return node.id
        return None

    @staticmethod
    def _extract_entity(node: ast.AST) -> Optional[str]:
        """Extract entity (Person, TaxUnit, etc)."""
        if isinstance(node, ast.Name):
            entity_map = {
                "Person": "person",
                "TaxUnit": "tax_unit",
                "Household": "household",
                "SPMUnit": "spm_unit",
            }
            return entity_map.get(node.id, node.id)
        return None

    @staticmethod
    def _extract_type(node: ast.AST) -> Optional[str]:
        """Extract value type."""
        if isinstance(node, ast.Name):
            return node.id.lower()
        elif isinstance(node, ast.Attribute):
            return node.attr.lower()
        return None

    @staticmethod
    def _extract_reference(node: ast.AST) -> List[str]:
        """Extract reference URLs/citations."""
        refs = []

        if isinstance(node, ast.List):
            for elt in node.elts:
                if isinstance(elt, ast.Constant):
                    refs.append(elt.value)
        elif isinstance(node, ast.Tuple):
            for elt in node.elts:
                if isinstance(elt, ast.Constant):
                    refs.append(elt.value)
        elif isinstance(node, ast.Constant):
            refs.append(node.value)

        return refs
