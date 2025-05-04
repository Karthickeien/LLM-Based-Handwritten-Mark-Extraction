import pandas as pd
import re
import json
import os
import csv
from io import StringIO

class ExcelHandler:
    def __init__(self):
        """Initialize the Excel handler"""
        pass
    
    def create_csv_from_data(self, data):
        """Create CSV content from the extracted data"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(["Data Type", "Value"])
        
        # Write serial number if available
        if data.get("SI_No"):
            writer.writerow(["Serial Number", data["SI_No"]])
        
        # Write question marks
        if data.get("Question_Nos"):
            writer.writerow(["", ""])  # Empty row as separator
            writer.writerow(["Question", "Marks"])
            
            for q_num, marks in sorted(data["Question_Nos"].items(), key=lambda x: self._natural_sort_key(x[0])):
                writer.writerow([f"Question {q_num}", marks])
        
        # Write subtotal if available
        if data.get("Subtotal") is not None:
            writer.writerow(["", ""])  # Empty row as separator
            writer.writerow(["Subtotal", data["Subtotal"]])
        
        return output.getvalue()
    
    def export_to_excel(self, data, output_path):
        """Export the extracted data to an Excel file"""
        # Create a new DataFrame for Excel export
        df = pd.DataFrame()
        
        # Set serial number
        if data.get("SI_No"):
            df.at[0, 0] = "Serial Number"
            df.at[0, 1] = data["SI_No"]
        
        # Set question marks
        row_idx = 2  # Start after a blank row
        df.at[row_idx, 0] = "Question"
        df.at[row_idx, 1] = "Marks"
        row_idx += 1
        
        if data.get("Question_Nos"):
            for q_num, marks in sorted(data["Question_Nos"].items(), key=lambda x: self._natural_sort_key(x[0])):
                df.at[row_idx, 0] = f"Question {q_num}"
                df.at[row_idx, 1] = marks
                row_idx += 1
        
        # Set subtotal
        if data.get("Subtotal") is not None:
            row_idx += 1  # Skip a row
            df.at[row_idx, 0] = "Subtotal"
            df.at[row_idx, 1] = data["Subtotal"]
        
        # Save to Excel
        df.to_excel(output_path, index=False, header=False, engine='openpyxl')
        return output_path
    
    def update_existing_excel(self, data, file_path, marks_row_index=5, sl_no_index=0, subtotal_row=12):
        """Update an existing Excel file with the extracted data"""
        try:
            # Read the Excel file
            df = pd.read_excel(file_path, header=None)
            
            # Extract serial number
            serial_no = data.get("SI_No", "")
            if serial_no:
                # Extract numeric part if needed
                serial_no_match = re.findall(r'\d+', str(serial_no))
                serial_no = serial_no_match[0] if serial_no_match else serial_no
                
                # Insert serial number
                df.at[0, sl_no_index] = serial_no
            
            # Insert marks into corresponding columns
            question_data = data.get("Question_Nos", {})
            for col_num, marks in question_data.items():
                try:
                    col_num_int = int(col_num)
                    # Adjust column index based on your Excel structure
                    col_index = sl_no_index + (col_num_int - 1) * 2
                    df.at[marks_row_index, col_index] = marks
                except (ValueError, TypeError):
                    pass  # Skip if column number is not a valid integer
            
            # Insert subtotal
            if data.get("Subtotal") is not None:
                df.at[subtotal_row, sl_no_index] = data["Subtotal"]
            
            # Save updated Excel file
            df.to_excel(file_path, index=False, header=False, engine='openpyxl')
            return True
            
        except Exception as e:
            print(f"Error updating Excel file: {str(e)}")
            return False
    
    def _natural_sort_key(self, s):
        """Helper function for natural sorting of alphanumeric strings"""
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]