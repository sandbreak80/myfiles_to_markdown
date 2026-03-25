"""Jupyter Notebook converter."""

from pathlib import Path
from typing import Optional, List, Dict
import json
from loguru import logger

from converters.base_converter import DocumentContent


class JupyterConverter:
    """Convert Jupyter Notebook (.ipynb) files to markdown."""
    
    def __init__(self, config: dict):
        """Initialize Jupyter converter.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
    
    def convert(self, file_path: Path) -> DocumentContent:
        """Convert Jupyter Notebook to DocumentContent.
        
        Args:
            file_path: Path to .ipynb file
            
        Returns:
            DocumentContent object with notebook content
        """
        logger.info(f"Converting Jupyter Notebook: {file_path.name}")
        
        try:
            # Load notebook JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                nb = json.load(f)
            
            # Get metadata
            nb_metadata = nb.get('metadata', {})
            kernel_info = nb_metadata.get('kernelspec', {})
            kernel_name = kernel_info.get('display_name', kernel_info.get('name', 'Unknown'))
            
            # Get cells
            cells = nb.get('cells', [])
            
            logger.info(f"Notebook has {len(cells)} cells, kernel: {kernel_name}")
            
            # Build content
            content_parts = []
            
            # Add header
            content_parts.append(f"# {file_path.stem}\n")
            content_parts.append(f"**Jupyter Notebook** - Kernel: {kernel_name}\n")
            content_parts.append(f"**Cells**: {len(cells)}\n")
            
            # Process cells
            code_cell_count = 0
            markdown_cell_count = 0
            
            for i, cell in enumerate(cells):
                cell_type = cell.get('cell_type', 'unknown')
                source = cell.get('source', [])
                
                # Convert source to string
                if isinstance(source, list):
                    source_text = ''.join(source)
                else:
                    source_text = str(source)
                
                if not source_text.strip():
                    continue
                
                if cell_type == 'markdown':
                    # Add markdown cell content directly
                    content_parts.append(f"\n{source_text}\n")
                    markdown_cell_count += 1
                    
                elif cell_type == 'code':
                    # Add code cell with syntax highlighting
                    content_parts.append(f"\n### Code Cell {code_cell_count + 1}\n")
                    
                    # Detect language (default to python)
                    language = kernel_info.get('language', 'python')
                    content_parts.append(f"```{language}")
                    content_parts.append(source_text)
                    content_parts.append("```\n")
                    
                    # Add outputs if present
                    outputs = cell.get('outputs', [])
                    if outputs:
                        content_parts.append("\n**Output:**\n")
                        for output in outputs:
                            output_type = output.get('output_type', '')
                            
                            if output_type == 'stream':
                                # stdout/stderr
                                text = ''.join(output.get('text', []))
                                content_parts.append(f"```\n{text}\n```\n")
                                
                            elif output_type == 'execute_result' or output_type == 'display_data':
                                # Result data
                                data = output.get('data', {})
                                
                                # Try text/plain first
                                if 'text/plain' in data:
                                    text = ''.join(data['text/plain']) if isinstance(data['text/plain'], list) else data['text/plain']
                                    content_parts.append(f"```\n{text}\n```\n")
                                
                                # Note if image/html output exists
                                if 'image/png' in data or 'image/jpeg' in data:
                                    content_parts.append("*[Image output]*\n")
                                if 'text/html' in data:
                                    content_parts.append("*[HTML output]*\n")
                                    
                            elif output_type == 'error':
                                # Error output
                                ename = output.get('ename', 'Error')
                                evalue = output.get('evalue', '')
                                content_parts.append(f"```\n{ename}: {evalue}\n```\n")
                    
                    code_cell_count += 1
                
                elif cell_type == 'raw':
                    # Raw cell
                    content_parts.append(f"\n```\n{source_text}\n```\n")
            
            full_text = "\n".join(content_parts)
            
            # Create DocumentContent
            content = DocumentContent()
            content.title = file_path.stem
            content.text = full_text
            content.metadata = {
                'total_cells': len(cells),
                'code_cells': code_cell_count,
                'markdown_cells': markdown_cell_count,
                'kernel': kernel_name,
                'language': kernel_info.get('language', 'python'),
                'file_size': file_path.stat().st_size
            }
            
            logger.success(f"Notebook converted: {code_cell_count} code cells, {markdown_cell_count} markdown cells")
            return content
            
        except Exception as e:
            logger.error(f"Failed to convert Jupyter Notebook {file_path.name}: {e}")
            # Return minimal content on error
            content = DocumentContent()
            content.title = file_path.stem
            content.text = f"# {file_path.stem}\n\nError converting notebook: {str(e)}"
            content.metadata = {'error': str(e)}
            return content

