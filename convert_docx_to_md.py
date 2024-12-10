import docx
import re

def convert_docx_to_markdown(docx_path, output_path):
    """Convert Word document to markdown format"""
    # Load the Word document
    doc = docx.Document(docx_path)
    markdown_lines = []
    
    # Track list state
    in_list = False
    list_count = 0
    
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if not text:  # Skip empty paragraphs
            if in_list:  # End list if we hit empty line
                in_list = False
                list_count = 0
            markdown_lines.append('')
            continue
        
        # Get paragraph style name
        style = paragraph.style.name.lower()
        
        # Convert headings
        if 'heading 1' in style:
            markdown_lines.append(f'# {text}')
        elif 'heading 2' in style:
            markdown_lines.append(f'## {text}')
        elif 'heading 3' in style:
            markdown_lines.append(f'### {text}')
        elif 'heading 4' in style:
            markdown_lines.append(f'#### {text}')
        
        # Handle lists
        elif text.startswith(('•', '-', '* ')):  # Bullet list
            in_list = True
            markdown_lines.append(f'- {text.lstrip("•-* ")}')
        elif re.match(r'^\d+\.', text):  # Numbered list
            in_list = True
            list_count += 1
            markdown_lines.append(f'{list_count}. {text.lstrip("0123456789. ")}')
        
        # Handle regular paragraphs with formatting
        else:
            formatted_text = text
            
            # Convert formatting within the paragraph
            for run in paragraph.runs:
                if run.bold:
                    formatted_text = formatted_text.replace(
                        run.text, f'**{run.text}**'
                    )
                if run.italic:
                    formatted_text = formatted_text.replace(
                        run.text, f'*{run.text}*'
                    )
            
            markdown_lines.append(formatted_text)
    
    # Write to output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown_lines))

if __name__ == "__main__":
    # Convert the document
    convert_docx_to_markdown('tbj.docx', 'output.md')
    print("Conversion complete! Check output.md") 