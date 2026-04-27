"""Parse variable formulas into detailed operation nodes."""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import yaml


class FormulaParser:
    """Parse formulas to extract operations, parameters, and computation structure."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.parameters_path = repo_path / "policyengine_us/parameters"
        self._param_cache = {}

    def parse_formula_to_operations(
        self, var_name: str, formula_node: ast.FunctionDef, formula_source: str
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Parse a formula into operation nodes and edges.

        Returns:
            Tuple of (operation_nodes, operation_edges)
        """
        if not formula_node:
            return [], []

        nodes = []
        edges = []
        operation_counter = [0]  # Mutable counter for unique IDs

        def create_operation_node(
            op_type: str,
            label: str,
            details: Optional[str] = None,
            value: Optional[str] = None,
            parent_var: str = var_name
        ) -> str:
            """Create a unique operation node."""
            operation_counter[0] += 1
            node_id = f"{parent_var}__op_{operation_counter[0]}_{op_type}"

            node = {
                "id": node_id,
                "label": label,
                "type": "operation",
                "op_type": op_type,
                "parent_variable": parent_var,
                "details": details,
                "value": value,
            }
            nodes.append(node)
            return node_id

        # Parse the formula body
        for stmt in formula_node.body:
            self._parse_statement(stmt, var_name, nodes, edges, create_operation_node)

        return nodes, edges

    def _parse_statement(
        self,
        stmt: ast.AST,
        parent_var: str,
        nodes: List[Dict],
        edges: List[Dict],
        create_node_fn,
    ):
        """Parse a single statement in the formula."""

        if isinstance(stmt, ast.Assign):
            # Assignment: var_name = expression
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    # Parse the right-hand side expression
                    expr_node = self._parse_expression(
                        stmt.value, parent_var, nodes, edges, create_node_fn
                    )

                    # Create assignment node
                    assign_node = create_node_fn(
                        "assign",
                        f"Assign: {var_name}",
                        details=f"Store result in {var_name}"
                    )

                    if expr_node:
                        edges.append({
                            "source": expr_node,
                            "target": assign_node,
                            "type": "dataflow"
                        })

        elif isinstance(stmt, ast.Return):
            # Return statement
            return_expr = self._parse_expression(
                stmt.value, parent_var, nodes, edges, create_node_fn
            )

            return_node = create_node_fn(
                "return",
                f"Return",
                details="Final output"
            )

            if return_expr:
                edges.append({
                    "source": return_expr,
                    "target": return_node,
                    "type": "dataflow"
                })

                # Connect return to parent variable
                edges.append({
                    "source": return_node,
                    "target": parent_var,
                    "type": "output"
                })

    def _parse_expression(
        self,
        expr: ast.AST,
        parent_var: str,
        nodes: List[Dict],
        edges: List[Dict],
        create_node_fn,
    ) -> Optional[str]:
        """Parse an expression and return the node ID of the result."""

        if isinstance(expr, ast.BinOp):
            # Binary operation: a + b, a * b, etc.
            op_symbol = self._get_op_symbol(expr.op)
            left_node = self._parse_expression(expr.left, parent_var, nodes, edges, create_node_fn)
            right_node = self._parse_expression(expr.right, parent_var, nodes, edges, create_node_fn)

            op_node = create_node_fn(
                "binary_op",
                f"{op_symbol}",
                details=f"Binary operation: {op_symbol}"
            )

            if left_node:
                edges.append({"source": left_node, "target": op_node, "type": "dataflow"})
            if right_node:
                edges.append({"source": right_node, "target": op_node, "type": "dataflow"})

            return op_node

        elif isinstance(expr, ast.Call):
            # Function call
            func_name = self._get_func_name(expr.func)

            if func_name in ["max_", "min_", "where", "select"]:
                # Special PolicyEngine functions
                return self._parse_special_function(
                    func_name, expr, parent_var, nodes, edges, create_node_fn
                )
            elif func_name == "add":
                # Add function - sums multiple variables
                return self._parse_add_function(
                    expr, parent_var, nodes, edges, create_node_fn
                )
            elif func_name == "parameters":
                # Parameter access
                return self._parse_parameter_access(
                    expr, parent_var, nodes, edges, create_node_fn
                )
            else:
                # Entity variable access: person("var", period)
                return self._parse_variable_access(
                    expr, parent_var, nodes, edges, create_node_fn
                )

        elif isinstance(expr, ast.Attribute):
            # Attribute access: obj.attr
            return self._parse_attribute_access(
                expr, parent_var, nodes, edges, create_node_fn
            )

        elif isinstance(expr, ast.Constant):
            # Constant value
            const_node = create_node_fn(
                "constant",
                f"Value: {expr.value}",
                value=str(expr.value)
            )
            return const_node

        elif isinstance(expr, ast.Name):
            # Variable reference
            var_ref_node = create_node_fn(
                "var_ref",
                f"Var: {expr.id}",
                details=f"Reference to {expr.id}"
            )
            return var_ref_node

        return None

    def _parse_special_function(
        self, func_name: str, call_node: ast.Call, parent_var: str,
        nodes: List[Dict], edges: List[Dict], create_node_fn
    ) -> str:
        """Parse special functions like max_, min_, where, select."""

        if func_name in ["max_", "min_"]:
            arg_nodes = []
            for arg in call_node.args:
                arg_node = self._parse_expression(arg, parent_var, nodes, edges, create_node_fn)
                if arg_node:
                    arg_nodes.append(arg_node)

            op_node = create_node_fn(
                func_name,
                f"{func_name}(...)",
                details=f"Take {func_name[:-1]} of inputs"
            )

            for arg_node in arg_nodes:
                edges.append({"source": arg_node, "target": op_node, "type": "dataflow"})

            return op_node

        elif func_name == "where":
            # where(condition, true_value, false_value)
            cond_node = self._parse_expression(call_node.args[0], parent_var, nodes, edges, create_node_fn) if len(call_node.args) > 0 else None
            true_node = self._parse_expression(call_node.args[1], parent_var, nodes, edges, create_node_fn) if len(call_node.args) > 1 else None
            false_node = self._parse_expression(call_node.args[2], parent_var, nodes, edges, create_node_fn) if len(call_node.args) > 2 else None

            where_node = create_node_fn(
                "where",
                "Conditional",
                details="If-then-else conditional"
            )

            if cond_node:
                edges.append({"source": cond_node, "target": where_node, "type": "condition"})
            if true_node:
                edges.append({"source": true_node, "target": where_node, "type": "true_branch"})
            if false_node:
                edges.append({"source": false_node, "target": where_node, "type": "false_branch"})

            return where_node

        return create_node_fn(func_name, f"{func_name}(...)", details=f"Function: {func_name}")

    def _parse_add_function(
        self, call_node: ast.Call, parent_var: str,
        nodes: List[Dict], edges: List[Dict], create_node_fn
    ) -> str:
        """Parse add() function which sums variables."""

        add_node = create_node_fn(
            "add",
            "Sum",
            details="Sum multiple variables"
        )

        # add(entity, period, [var1, var2, ...])
        if len(call_node.args) >= 3:
            var_list_arg = call_node.args[2]
            if isinstance(var_list_arg, ast.List):
                for var_elt in var_list_arg.elts:
                    if isinstance(var_elt, ast.Constant):
                        var_name = var_elt.value
                        # This references another variable
                        edges.append({
                            "source": var_name,
                            "target": add_node,
                            "type": "sum_input"
                        })

        return add_node

    def _parse_parameter_access(
        self, call_node: ast.Call, parent_var: str,
        nodes: List[Dict], edges: List[Dict], create_node_fn
    ) -> str:
        """Parse parameters(period) call."""

        param_node = create_node_fn(
            "param_root",
            "Parameters",
            details="Load parameters for period"
        )

        return param_node

    def _parse_variable_access(
        self, call_node: ast.Call, parent_var: str,
        nodes: List[Dict], edges: List[Dict], create_node_fn
    ) -> str:
        """Parse entity variable access: entity('variable_name', period)."""

        if len(call_node.args) > 0 and isinstance(call_node.args[0], ast.Constant):
            var_name = call_node.args[0].value

            # Create edge to referenced variable
            edges.append({
                "source": var_name,
                "target": parent_var,
                "type": "variable_reference"
            })

            access_node = create_node_fn(
                "var_access",
                f"Get: {var_name}",
                details=f"Load variable {var_name}"
            )

            return access_node

        return None

    def _parse_attribute_access(
        self, attr_node: ast.Attribute, parent_var: str,
        nodes: List[Dict], edges: List[Dict], create_node_fn
    ) -> str:
        """Parse attribute access like p.max.rate."""

        # Build the full path
        path_parts = []
        current = attr_node

        while isinstance(current, ast.Attribute):
            path_parts.insert(0, current.attr)
            current = current.value

        if isinstance(current, ast.Name):
            path_parts.insert(0, current.id)

        full_path = ".".join(path_parts)

        # Try to get parameter value
        param_value = self._get_parameter_value(full_path)

        param_node = create_node_fn(
            "parameter",
            f"Param: {full_path}",
            details=f"Parameter value",
            value=param_value
        )

        return param_node

    def _get_parameter_value(self, param_path: str) -> Optional[str]:
        """Get parameter value from YAML files."""
        # This is a simplified version - would need to navigate the parameter tree
        # For now, return None
        return None

    def _get_op_symbol(self, op: ast.operator) -> str:
        """Get symbol for binary operator."""
        op_map = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.Mod: "%",
        }
        return op_map.get(type(op), "?")

    def _get_func_name(self, func: ast.AST) -> str:
        """Get function name from call."""
        if isinstance(func, ast.Name):
            return func.id
        elif isinstance(func, ast.Attribute):
            return func.attr
        return "unknown"
