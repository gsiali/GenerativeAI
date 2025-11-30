"""
Enhanced Data Flow Graph Generator
Generates cleaner, more readable data flow graphs showing variable dependencies.
"""

import ast
import os
from typing import Dict, List, Set, Tuple
import logging
from graphviz import Digraph
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataFlowAnalyzer(ast.NodeVisitor):
    """Analyzes data flow in a Python function."""
    
    def __init__(self, function_name: str):
        self.function_name = function_name
        self.variables = {}  # var_name -> {'type': str, 'dependencies': set, 'line': int}
        self.current_target = None
        self.current_dependencies = set()
        self.in_target_function = False
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definition."""
        if node.name == self.function_name:
            self.in_target_function = True
            
            # Add parameters as input variables
            for arg in node.args.args:
                self.variables[arg.arg] = {
                    'type': 'parameter',
                    'dependencies': set(),
                    'line': node.lineno
                }
            
            # Visit function body
            for stmt in node.body:
                self.visit(stmt)
                
            self.in_target_function = False
    
    def visit_Assign(self, node: ast.Assign):
        """Visit assignment statement."""
        if not self.in_target_function:
            return
            
        # Get variables used in the right-hand side
        self.current_dependencies = set()
        self.visit(node.value)
        dependencies = self.current_dependencies.copy()
        
        # Add each target variable
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables[target.id] = {
                    'type': 'variable',
                    'dependencies': dependencies,
                    'line': node.lineno
                }
            elif isinstance(target, (ast.Tuple, ast.List)):
                # Handle tuple unpacking
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        self.variables[elt.id] = {
                            'type': 'variable',
                            'dependencies': dependencies,
                            'line': node.lineno
                        }
    
    def visit_AugAssign(self, node: ast.AugAssign):
        """Visit augmented assignment (+=, -=, etc.)."""
        if not self.in_target_function:
            return
            
        # Get dependencies from right side
        self.current_dependencies = set()
        self.visit(node.value)
        dependencies = self.current_dependencies.copy()
        
        # Add the variable itself as a dependency (it uses its old value)
        if isinstance(node.target, ast.Name):
            var_name = node.target.id
            dependencies.add(var_name)
            
            self.variables[var_name] = {
                'type': 'variable',
                'dependencies': dependencies,
                'line': node.lineno
            }
    
    def visit_For(self, node: ast.For):
        """Visit for loop."""
        if not self.in_target_function:
            return
            
        # Get dependencies from iterator
        self.current_dependencies = set()
        self.visit(node.iter)
        dependencies = self.current_dependencies.copy()
        
        # Add loop variable
        if isinstance(node.target, ast.Name):
            self.variables[node.target.id] = {
                'type': 'loop_var',
                'dependencies': dependencies,
                'line': node.lineno
            }
        
        # Visit loop body
        for stmt in node.body:
            self.visit(stmt)
    
    def visit_With(self, node: ast.With):
        """Visit with statement."""
        if not self.in_target_function:
            return
            
        for item in node.items:
            # Get dependencies from context expression
            self.current_dependencies = set()
            self.visit(item.context_expr)
            dependencies = self.current_dependencies.copy()
            
            # Add context variable
            if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                self.variables[item.optional_vars.id] = {
                    'type': 'context_var',
                    'dependencies': dependencies,
                    'line': node.lineno
                }
        
        # Visit body
        for stmt in node.body:
            self.visit(stmt)
    
    def visit_Name(self, node: ast.Name):
        """Visit variable name."""
        if self.in_target_function and isinstance(node.ctx, ast.Load):
            # Variable is being used (read)
            self.current_dependencies.add(node.id)
    
    def visit_Return(self, node: ast.Return):
        """Visit return statement."""
        if not self.in_target_function or not node.value:
            return
            
        # Track what the return depends on
        self.current_dependencies = set()
        self.visit(node.value)
        
        # Add a special "return" node
        self.variables['__return__'] = {
            'type': 'return',
            'dependencies': self.current_dependencies.copy(),
            'line': node.lineno
        }


class DFGGenerator:
    """Generates clean, readable Data Flow Graphs."""
    
    def __init__(self, output_dir: str = "dfg_outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Initialized DFGGenerator with output directory: {self.output_dir}")
    
    def generate_dfg(self, code: str, function_name: str) -> str:
        """
        Generate a clean DFG for a specific function.
        
        Args:
            code: Python source code
            function_name: Name of the function to analyze
            
        Returns:
            Path to generated DFG image
        """
        try:
            # Parse code and analyze data flow
            tree = ast.parse(code)
            analyzer = DataFlowAnalyzer(function_name)
            analyzer.visit(tree)
            
            if not analyzer.variables:
                logger.warning(f"No variables found in function: {function_name}")
                return None
            
            # Create visualization
            output_path = self._create_visualization(
                analyzer.variables,
                function_name
            )
            
            logger.info(f"✅ Generated DFG for {function_name}: {output_path}")
            return output_path
            
        except SyntaxError as e:
            logger.error(f"Syntax error in code: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating DFG: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_visualization(self, variables: Dict, function_name: str) -> str:
        """
        Create a Graphviz visualization of the data flow graph.
        
        Args:
            variables: Dictionary of variable information
            function_name: Name of the function
            
        Returns:
            Path to generated image
        """
        dot = Digraph(comment=f'DFG: {function_name}')
        dot.attr(rankdir='TB')  # Top to bottom
        dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
        dot.attr('edge', fontname='Arial', fontsize='10')
        
        # Color scheme
        colors = {
            'parameter': '#FFD700',      # Gold
            'variable': '#87CEEB',       # Sky blue
            'loop_var': '#98FB98',       # Pale green
            'context_var': '#DDA0DD',    # Plum
            'return': '#FFB6C1'          # Light pink
        }
        
        # Add nodes
        for var_name, info in variables.items():
            node_type = info['type']
            line = info['line']
            
            # Format label
            if var_name == '__return__':
                label = f"return\n(line {line})"
            else:
                label = f"{var_name}\n({node_type}, line {line})"
            
            color = colors.get(node_type, '#E0E0E0')
            
            # Special shapes for different node types
            if node_type == 'parameter':
                dot.node(var_name, label, shape='ellipse', fillcolor=color)
            elif node_type == 'return':
                dot.node(var_name, label, shape='diamond', fillcolor=color)
            else:
                dot.node(var_name, label, fillcolor=color)
        
        # Add edges (dependencies)
        for var_name, info in variables.items():
            for dependency in info['dependencies']:
                if dependency in variables:
                    # Add edge from dependency to current variable
                    dot.edge(dependency, var_name, label='uses')
        
        # Render to file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{function_name}_{timestamp}"
        output_path = os.path.join(self.output_dir, filename)
        dot.render(output_path, format='png', cleanup=True)
        
        return f"{output_path}.png"
    
    def generate_dfg_for_all_functions(self, code: str) -> Dict[str, str]:
        """
        Generate DFGs for all functions in the code.
        
        Args:
            code: Python source code
            
        Returns:
            Dictionary mapping function names to image paths
        """
        result = {}
        
        try:
            tree = ast.parse(code)
            functions = [node.name for node in ast.walk(tree) 
                        if isinstance(node, ast.FunctionDef)]
            
            logger.info(f"Found {len(functions)} function(s): {functions}")
            
            for func_name in functions:
                dfg_path = self.generate_dfg(code, func_name)
                if dfg_path:
                    result[func_name] = dfg_path
            
            logger.info(f"✅ Generated {len(result)} DFG(s)")
            return result
            
        except Exception as e:
            logger.error(f"Error generating DFGs: {e}")
            return result


# Test
if __name__ == "__main__":
    test_code = """
def fibonacci_with_decimal_places(n: int, decimal_places: int = 2) -> list[float]:
    '''Generate Fibonacci sequence with decimal formatting'''
    if n <= 0:
        return []
    
    sequence = []
    a, b = 0, 1
    
    for i in range(n):
        formatted_value = round(a, decimal_places)
        sequence.append(formatted_value)
        a, b = b, a + b
    
    return sequence
"""
    
    generator = DFGGenerator("test_output")
    result = generator.generate_dfg(test_code, "fibonacci_with_decimal_places")
    print(f"Generated DFG: {result}")
