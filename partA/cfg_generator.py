"""
Enhanced Control Flow Graph Generator
Generates detailed control flow graphs from Python code using AST analysis
"""

import ast
import os
from typing import List, Dict, Optional, Set, Tuple
import logging
import graphviz
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CFGNode:
    """Represents a node in the control flow graph"""
    
    _id_counter = 0
    
    def __init__(self, label: str, node_type: str = "statement"):
        self.id = CFGNode._id_counter
        CFGNode._id_counter += 1
        self.label = label
        self.node_type = node_type  # statement, condition, return, entry, exit
        self.successors: List['CFGNode'] = []
        self.edge_labels: Dict['CFGNode', str] = {}
    
    def add_successor(self, node: 'CFGNode', label: str = ""):
        if node not in self.successors:
            self.successors.append(node)
            if label:
                self.edge_labels[node] = label
    
    def __repr__(self):
        return f"CFGNode({self.id}, {self.label[:20]})"


class CFGGenerator:
    """
    Enhanced CFG generator using AST traversal
    """
    
    def __init__(self, output_dir: str = "generated_artifacts/cfg"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Initialized CFGGenerator with output directory: {output_dir}")
    
    def generate_cfg(self, code: str) -> Dict[str, str]:
        """
        Generate CFG for each function in the code
        
        Args:
            code: Python source code
            
        Returns:
            Dictionary mapping function names to CFG image paths
        """
        result = {}
        
        try:
            tree = ast.parse(code)
            
            # Find all function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_name = node.name
                    logger.info(f"Generating CFG for function: {function_name}")
                    
                    # Build CFG
                    entry_node = self._build_cfg_from_function(node)
                    
                    # Visualize
                    cfg_path = self._visualize_cfg(entry_node, function_name)
                    
                    if cfg_path:
                        result[function_name] = cfg_path
            
            logger.info(f"✅ Generated {len(result)} CFG(s)")
            return result
            
        except Exception as e:
            logger.error(f"Error generating CFGs: {e}")
            import traceback
            traceback.print_exc()
            return result
    
    def _build_cfg_from_function(self, func_node: ast.FunctionDef) -> CFGNode:
        """
        Build CFG from a function AST node
        
        Args:
            func_node: Function definition AST node
            
        Returns:
            Entry CFG node
        """
        # Reset node counter for each function
        CFGNode._id_counter = 0
        
        # Create entry node
        args_str = ", ".join([arg.arg for arg in func_node.args.args])
        entry = CFGNode(f"def {func_node.name}({args_str})", "entry")
        
        # Build CFG from function body
        if func_node.body:
            first_stmt_node = self._build_cfg_from_statements(func_node.body)
            if first_stmt_node:
                entry.add_successor(first_stmt_node)
        
        return entry
    
    def _build_cfg_from_statements(self, statements: List[ast.stmt], 
                                   next_node: Optional[CFGNode] = None) -> Optional[CFGNode]:
        """
        Build CFG from a list of statements
        
        Args:
            statements: List of AST statement nodes
            next_node: Node to connect to after all statements
            
        Returns:
            First node in the statement sequence
        """
        if not statements:
            return next_node
        
        # Process statements in reverse to build the CFG
        current = next_node
        
        for stmt in reversed(statements):
            if isinstance(stmt, ast.If):
                current = self._build_if_cfg(stmt, current)
            elif isinstance(stmt, ast.While):
                current = self._build_while_cfg(stmt, current)
            elif isinstance(stmt, ast.For):
                current = self._build_for_cfg(stmt, current)
            elif isinstance(stmt, ast.Return):
                label = f"return {ast.unparse(stmt.value)}" if stmt.value else "return"
                node = CFGNode(label, "return")
                current = node
            elif isinstance(stmt, (ast.Break, ast.Continue)):
                node = CFGNode(ast.unparse(stmt), "control")
                if current:
                    node.add_successor(current)
                current = node
            else:
                # Regular statement
                label = ast.unparse(stmt)
                if len(label) > 50:
                    label = label[:47] + "..."
                node = CFGNode(label, "statement")
                if current:
                    node.add_successor(current)
                current = node
        
        return current
    
    def _build_if_cfg(self, if_node: ast.If, next_node: Optional[CFGNode]) -> CFGNode:
        """Build CFG for if statement"""
        # Condition node
        condition_label = f"if {ast.unparse(if_node.test)}"
        if len(condition_label) > 50:
            condition_label = condition_label[:47] + "..."
        condition = CFGNode(condition_label, "condition")
        
        # True branch
        true_branch = self._build_cfg_from_statements(if_node.body, next_node)
        if true_branch:
            condition.add_successor(true_branch, "True")
        elif next_node:
            condition.add_successor(next_node, "True")
        
        # False branch (else/elif)
        if if_node.orelse:
            false_branch = self._build_cfg_from_statements(if_node.orelse, next_node)
            if false_branch:
                condition.add_successor(false_branch, "False")
            elif next_node:
                condition.add_successor(next_node, "False")
        elif next_node:
            condition.add_successor(next_node, "False")
        
        return condition
    
    def _build_while_cfg(self, while_node: ast.While, next_node: Optional[CFGNode]) -> CFGNode:
        """Build CFG for while loop"""
        # Condition node
        condition_label = f"while {ast.unparse(while_node.test)}"
        if len(condition_label) > 50:
            condition_label = condition_label[:47] + "..."
        condition = CFGNode(condition_label, "condition")
        
        # Loop body (connects back to condition)
        body_first = self._build_cfg_from_statements(while_node.body, condition)
        if body_first:
            condition.add_successor(body_first, "True")
        else:
            condition.add_successor(condition, "True")
        
        # Exit loop
        if next_node:
            condition.add_successor(next_node, "False")
        
        return condition
    
    def _build_for_cfg(self, for_node: ast.For, next_node: Optional[CFGNode]) -> CFGNode:
        """Build CFG for for loop"""
        # Loop header
        header_label = f"for {ast.unparse(for_node.target)} in {ast.unparse(for_node.iter)}"
        if len(header_label) > 50:
            header_label = header_label[:47] + "..."
        header = CFGNode(header_label, "condition")
        
        # Loop body (connects back to header)
        body_first = self._build_cfg_from_statements(for_node.body, header)
        if body_first:
            header.add_successor(body_first, "iterate")
        else:
            header.add_successor(header, "iterate")
        
        # Exit loop
        if next_node:
            header.add_successor(next_node, "done")
        
        return header
    
    def _visualize_cfg(self, entry_node: CFGNode, function_name: str) -> Optional[str]:
        """
        Create Graphviz visualization of CFG
        
        Args:
            entry_node: Entry node of CFG
            function_name: Name of function (for filename)
            
        Returns:
            Path to saved PNG file
        """
        try:
            graph = graphviz.Digraph(
                name=function_name,
                format='png',
                graph_attr={
                    'rankdir': 'TB',
                    'fontname': 'Arial',
                    'fontsize': '11',
                    'bgcolor': 'white',
                    'splines': 'ortho',
                    'nodesep': '0.5',
                    'ranksep': '0.7'
                },
                node_attr={
                    'shape': 'box',
                    'style': 'rounded,filled',
                    'fontname': 'Courier',
                    'fontsize': '10',
                    'margin': '0.2,0.1'
                },
                edge_attr={
                    'fontname': 'Arial',
                    'fontsize': '9',
                    'arrowsize': '0.8'
                }
            )
            
            # Traverse CFG and add nodes/edges
            visited = set()
            self._add_nodes_to_graph(entry_node, graph, visited)
            
            # Save graph with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{function_name}_{timestamp}"
            output_path = os.path.join(self.output_dir, filename)
            graph.render(output_path, cleanup=True)
            
            png_path = f"{output_path}.png"
            logger.info(f"✅ CFG saved to: {png_path}")
            return png_path
            
        except Exception as e:
            logger.error(f"Error visualizing CFG: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _add_nodes_to_graph(self, node: CFGNode, graph: graphviz.Digraph, visited: Set[int]):
        """Recursively add nodes and edges to graph"""
        if node.id in visited:
            return
        
        visited.add(node.id)
        
        # Choose color based on node type
        color_map = {
            "entry": "lightgreen",
            "return": "lightcoral",
            "condition": "lightyellow",
            "statement": "lightblue",
            "control": "lavender"
        }
        fillcolor = color_map.get(node.node_type, "lightgray")
        
        # Add node
        graph.node(
            str(node.id),
            label=node.label,
            fillcolor=fillcolor
        )
        
        # Add edges to successors
        for successor in node.successors:
            edge_label = node.edge_labels.get(successor, "")
            graph.edge(str(node.id), str(successor.id), label=edge_label)
            self._add_nodes_to_graph(successor, graph, visited)


if __name__ == "__main__":
    # Test the enhanced CFG generator
    test_code = """
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
"""
    
    generator = CFGGenerator()
    result = generator.generate_cfg(test_code)
    print(f"Generated CFGs: {result}")
