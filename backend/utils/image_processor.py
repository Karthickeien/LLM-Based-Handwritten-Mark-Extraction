import re
import json
import os
from pathlib import Path
import google.generativeai as genai

class ImageProcessor:
    def __init__(self, api_key=None):
        """Initialize the image processor with Google API key"""
        if api_key:
            genai.configure(api_key=api_key)
        
        # Safety settings for the Gemini model
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUAL",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        # Initialize the Gemini model
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            safety_settings=self.safety_settings
        )
    
    def format_image(self, image_path):
        """Format image for Gemini API input"""
        img = Path(image_path)
        if not img.exists():
            raise FileNotFoundError(f"Could not find image: {img}")
        
        image_part = [
            {
                "mime_type": "image/jpeg",
                "data": img.read_bytes()
            }
        ]
        return image_part
    
    def extract_data_from_image(self, image_path):
        """Process image with Gemini to extract marksheet data"""
        system_prompt = """
        You are a specialist in comprehending marksheets.
        Input images in the form of marksheets will be provided to you,
        and your task is to extract all marks and related information.
        Return the data in properly formatted JSON.
        """
        
        user_prompt = """
        Extract all marksheet data into JSON format with the following structure:
        {
          "SI.No.": "student serial number or registration number",
          "Question Nos": {
            "1": marks for question 1,
            "2": marks for question 2,
            ...and so on for all questions
          },
          "Subtotal": total marks
        }
        Make sure to include all questions visible in the marksheet.
        Ensure all marks are extracted as numbers, not strings.
        """
        
        try:
            # Format the image for API input
            image_info = self.format_image(image_path)
            input_prompt = [system_prompt, image_info[0], user_prompt]
            
            # Generate response from Gemini
            response = self.model.generate_content(input_prompt)
            
            # Process and return the results
            return self.process_json_output(response.text)
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            raise
    
    def process_json_output(self, output):
        """Parse and clean JSON output from Gemini"""
        try:
            # First, try to clean the output by removing markdown code blocks
            cleaned_output = output.strip("```json").strip("```").strip()
            output_dict = json.loads(cleaned_output)
            
            # Extract relevant fields and ensure proper formatting
            result = {
                "SI_No": output_dict.get("SI.No.", ""),
                "Question_Nos": {},
                "Subtotal": output_dict.get("Subtotal", 0)
            }
            
            # Process question data
            questions_data = output_dict.get("Question Nos", {})
            
            # Convert question numbers and marks to the right format
            for q_num, marks in questions_data.items():
                # Extract numeric part if question number has non-numeric characters
                q_num_clean = re.sub(r'\D', '', str(q_num))
                
                # If q_num_clean is empty after removing non-digits, use original
                if not q_num_clean:
                    q_num_clean = q_num
                    
                # Ensure marks are numeric
                try:
                    marks_numeric = float(marks)
                    # Store as integer if it's a whole number
                    if marks_numeric.is_integer():
                        marks_numeric = int(marks_numeric)
                except (ValueError, TypeError):
                    marks_numeric = 0
                    
                result["Question_Nos"][q_num_clean] = marks_numeric
            
            # Ensure subtotal is numeric
            try:
                subtotal = float(result["Subtotal"])
                if subtotal.is_integer():
                    result["Subtotal"] = int(subtotal)
                else:
                    result["Subtotal"] = subtotal
            except (ValueError, TypeError):
                pass  # Keep as is if conversion fails
                
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw output: {repr(output)}")
            raise ValueError(f"Failed to parse JSON: {e}")