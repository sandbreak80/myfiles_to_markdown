"""CSV converter using pandas for markdown table generation."""

from pathlib import Path
from typing import Optional
import pandas as pd
from loguru import logger

from converters.base_converter import DocumentContent


class CsvConverter:
    """Convert CSV files to markdown tables."""
    
    def __init__(self, config: dict):
        """Initialize CSV converter.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
    
    def convert(self, file_path: Path) -> DocumentContent:
        """Convert CSV file to DocumentContent.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            DocumentContent object with markdown table
        """
        logger.info(f"Converting CSV: {file_path.name}")
        
        try:
            # Read CSV with pandas — keep_default_na=False preserves literal
            # strings like "NULL", "NA", "NaN" instead of converting to NaN
            df = pd.read_csv(file_path, keep_default_na=False)

            # Get basic stats
            total_rows, cols = df.shape
            logger.info(f"CSV dimensions: {total_rows} rows x {cols} columns")

            # Limit rows to prevent massive responses
            max_rows = self.config.get('csv', {}).get('max_rows', 1000)
            truncated = total_rows > max_rows
            rows = total_rows
            if truncated:
                df_display = df.head(max_rows)
                logger.warning(f"CSV truncated from {total_rows} to {max_rows} rows")
            else:
                df_display = df

            # Convert to markdown table
            markdown_table = df_display.to_markdown(index=False)
            
            # Build content
            content_parts = []
            
            # Add summary
            content_parts.append(f"# {file_path.stem}\n")
            content_parts.append(f"**CSV Data**: {rows} rows × {cols} columns\n")
            
            # Add column info
            if cols <= 20:  # Only show column names if not too many
                content_parts.append("\n## Columns\n")
                for col in df.columns:
                    dtype = str(df[col].dtype)
                    content_parts.append(f"- **{col}** ({dtype})")
            
            # Add the table
            content_parts.append(f"\n## Data\n")
            content_parts.append(markdown_table)

            if truncated:
                content_parts.append(f"\n*Showing first {max_rows} of {total_rows} rows.*\n")
            
            # Add statistics if numeric columns exist
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0 and rows > 1:
                content_parts.append(f"\n## Statistics\n")
                stats_df = df[numeric_cols].describe()
                content_parts.append(stats_df.to_markdown())
            
            full_text = "\n".join(content_parts)
            
            # Create DocumentContent
            content = DocumentContent()
            content.title = file_path.stem
            content.text = full_text
            content.metadata = {
                'rows': rows,
                'columns': cols,
                'column_names': list(df.columns),
                'numeric_columns': len(numeric_cols),
                'file_size': file_path.stat().st_size
            }
            
            logger.success(f"CSV converted: {rows} rows, {cols} columns")
            return content
            
        except Exception as e:
            logger.error(f"Failed to convert CSV {file_path.name}: {e}")
            # Return minimal content on error
            content = DocumentContent()
            content.title = file_path.stem
            content.text = f"# {file_path.stem}\n\nError converting CSV: {str(e)}"
            content.metadata = {'error': str(e)}
            return content

