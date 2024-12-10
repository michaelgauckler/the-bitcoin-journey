import re
import os

def extract_headings_and_text_with_h4(md_path):
    """
    Extract headings (H1, H2, H3, H4) and their associated text from a Markdown document.
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    content = {"H1": []}
    current_h1 = None
    current_h2 = None
    current_h3 = None
    current_text = []

    for line in lines:
        line = line.strip()
        
        if not line:  # Handle empty lines
            if current_text:  # Add accumulated text to current section
                if current_h3 and current_h3.get("H4"):
                    current_h3["H4"][-1]["text"].extend(current_text)
                elif current_h3:
                    current_h3["text"].extend(current_text)
                elif current_h2:
                    current_h2["text"].extend(current_text)
                elif current_h1:
                    current_h1["text"].extend(current_text)
                current_text = []
            continue

        # Process headings - remove any asterisks and trailing hashtags from the title
        if line.startswith('# ') and not line.startswith('## '):  # H1
            if current_text:  # Add any accumulated text before switching sections
                if current_h3 and current_h3.get("H4"):
                    current_h3["H4"][-1]["text"].extend(current_text)
                elif current_h3:
                    current_h3["text"].extend(current_text)
                elif current_h2:
                    current_h2["text"].extend(current_text)
                elif current_h1:
                    current_h1["text"].extend(current_text)
                current_text = []
            
            title = line[2:].strip()
            # Remove asterisks and trailing hashtags
            title = re.sub(r'\*+', '', title)
            title = re.sub(r'\s*#*\s*$', '', title)  # Remove trailing hashtags
            current_h1 = {"title": title, "H2": [], "text": []}
            content["H1"].append(current_h1)
            current_h2 = None
            current_h3 = None
            
        elif line.startswith('## '):  # H2
            if current_text:
                if current_h3 and current_h3.get("H4"):
                    current_h3["H4"][-1]["text"].extend(current_text)
                elif current_h3:
                    current_h3["text"].extend(current_text)
                elif current_h2:
                    current_h2["text"].extend(current_text)
                elif current_h1:
                    current_h1["text"].extend(current_text)
                current_text = []
            
            if current_h1:
                title = line[3:].strip()
                # Remove asterisks and trailing hashtags
                title = re.sub(r'\*+', '', title)
                title = re.sub(r'\s*#*\s*$', '', title)  # Remove trailing hashtags
                current_h2 = {"title": title, "H3": [], "text": []}
                current_h1["H2"].append(current_h2)
                current_h3 = None
                
        elif line.startswith('### '):  # H3
            if current_text:
                if current_h3 and current_h3.get("H4"):
                    current_h3["H4"][-1]["text"].extend(current_text)
                elif current_h3:
                    current_h3["text"].extend(current_text)
                elif current_h2:
                    current_h2["text"].extend(current_text)
                current_text = []
            
            if current_h2:
                title = line[4:].strip()
                # Remove asterisks and trailing hashtags
                title = re.sub(r'\*+', '', title)
                title = re.sub(r'\s*#*\s*$', '', title)  # Remove trailing hashtags
                current_h3 = {"title": title, "H4": [], "text": []}
                current_h2["H3"].append(current_h3)
                
        elif line.startswith('#### '):  # H4
            if current_text:
                if current_h3 and current_h3.get("H4"):
                    current_h3["H4"][-1]["text"].extend(current_text)
                current_text = []
            
            if current_h3:
                title = line[5:].strip()
                # Remove asterisks and trailing hashtags
                title = re.sub(r'\*+', '', title)
                title = re.sub(r'\s*#*\s*$', '', title)  # Remove trailing hashtags
                h4_entry = {"title": title, "text": []}
                current_h3["H4"].append(h4_entry)
                
        else:  # Regular text or lists
            # Convert markdown formatting to HTML
            # Bold
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            # Italic
            line = re.sub(r'\*(.*?)\*', r'<em>\1</em>', line)
            
            # Handle lists
            if line.startswith(('- ', '* ')):
                line = f'<li>{line[2:]}</li>'
            elif re.match(r'^\d+\.', line):
                text = re.sub(r'^\d+\.\s*', '', line)
                line = f'<li>{text}</li>'
            else:
                line = f'<p>{line}</p>'
            
            current_text.append(line)

    # Add any remaining text
    if current_text:
        if current_h3 and current_h3.get("H4"):
            current_h3["H4"][-1]["text"].extend(current_text)
        elif current_h3:
            current_h3["text"].extend(current_text)
        elif current_h2:
            current_h2["text"].extend(current_text)
        elif current_h1:
            current_h1["text"].extend(current_text)

    return content

def generate_toc(content):
    """
    Generate the Table of Contents as a separate HTML block.
    """
    toc_html = "<h1>Table of Contents</h1><ul>"
    for i, h1 in enumerate(content["H1"], 1):
        toc_html += f'<li><a href="#section{i}" class="scroll-link">{h1["title"]}</a><ul>'
        for j, h2 in enumerate(h1["H2"], 1):
            toc_html += f'<li><a href="#section{i}-{j}" class="scroll-link">{h2["title"]}</a><ul>'
            for k, h3 in enumerate(h2["H3"], 1):
                toc_html += f'<li><a href="#section{i}-{j}-{k}" class="scroll-link">{h3["title"]}</a><ul>'
                for l, h4 in enumerate(h3["H4"], 1):
                    toc_html += f'<li><a href="#section{i}-{j}-{k}-{l}" class="scroll-link">{h4["title"]}</a></li>'
                toc_html += "</ul></li>"
            toc_html += "</ul></li>"
        toc_html += "</ul></li>"
    toc_html += "</ul>"
    toc_html += """
    <script>
    document.querySelectorAll('.scroll-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetID = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetID);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    </script>
    """
    return toc_html

def generate_section_html(h1, section_index):
    """
    Generate HTML content for a single H1 section.
    """
    section_html = f'<h1 id="section{section_index}">{h1["title"]}</h1>'
    for paragraph in h1["text"]:
        if paragraph.strip():
            # Check if the paragraph starts with ####
            if paragraph.strip().startswith('####'):
                section_html += f"<b>{paragraph[5:-5]}</b>"  # Keep the #### format
            else:
                section_html += f"{paragraph}"
    for j, h2 in enumerate(h1["H2"], 1):
        section_html += f'<h2 id="section{section_index}-{j}">{h2["title"]}</h2>'
        for paragraph in h2["text"]:
            if paragraph.strip():
                if paragraph.strip().startswith('####'):
                    section_html += f"<b>{paragraph[5:-5]}</b>"  # Keep the #### format
                else:
                    section_html += f"{paragraph}"
        for k, h3 in enumerate(h2["H3"], 1):
            section_html += f'<h3 id="section{section_index}-{j}-{k}">{h3["title"]}</h3>'
            for paragraph in h3["text"]:
                if paragraph.strip():
                    if paragraph.strip().startswith('####'):
                        section_html += f"<b>{paragraph[5:-5]}</b>"  # Keep the #### format
                    else:
                        section_html += f"{paragraph}"
    return section_html

def generate_html_sections(content_structure):
    """Generate HTML sections with styling that matches the reference design"""
    html = '''
    <style>
        /* Base styles */
        body {
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            background-color: #ffffff;
            margin: 0;
            padding: 0;
        }

        /* Typography scale and spacing */
        h1, h2, h3, h4, p {
            margin: 0;
            padding: 0;
            font-weight: normal;
        }

        h1 {
            font-size: 2.81em;
            line-height: 1.2;
            font-weight: 700;
            margin-bottom: 2rem;
            color: #111827;
            letter-spacing: -0.02em;
        }

        h2 {
            font-size: 2.31em;
            line-height: 1.3;
            font-weight: 600;
            margin-top: 3rem;
            margin-bottom: 1.5rem;
            color: #1f2937;
            letter-spacing: -0.01em;
        }

        h3 {
            font-size: 1.45em;
            line-height: 1.4;
            font-weight: 600;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            color: #374151;
        }

        h4 {
            font-size: 1.25em;
            line-height: 1.5;
            font-weight: 600;
            margin-top: 2rem;
            margin-bottom: 0.75rem;
            color: #4b5563;
        }

        p {
            /* font-size: 1.15em; */
            line-height: 1.6;
            margin-bottom: 1rem;
            color: #374151;
        }

        /* Container and spacing */
        .container {
            max-width: 65rem;      /* Increased from 48rem for better readability */
            margin: 0 auto;
            padding: 2rem;
        }

        .section {
            margin-bottom: 3rem;    /* Reduced from 4rem */
            padding: 2rem;
            background: #ffffff;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }

            h1 {
                font-size: 2.25em;
                margin-bottom: 1.5rem;
            }

            h2 {
                font-size: 1.85em;
                margin-top: 2.5rem;
                margin-bottom: 1.25rem;
            }

            h3 {
                font-size: 1.35em;
                margin-top: 2rem;
                margin-bottom: 0.875rem;
            }

            h4 {
                font-size: 1.15em;
                margin-top: 1.75rem;
                margin-bottom: 0.625rem;
            }

            p {
                font-size: 1.1em;
                margin-bottom: 0.875rem;  /* Reduced from 1.25rem */
            }
        }

        /* List styles */
        ul, ol {
            margin: 0 0 1.5rem 0;
            padding-left: 1.5rem;
        }

        li {
            font-size: 1.125rem;
            line-height: 1.75;
            margin-bottom: 0.5rem;
            color: #374151;
        }

        /* Links */
        a {
            color: #2563eb;
            text-decoration: none;
            transition: color 0.2s ease;
        }

        a:hover {
            color: #1d4ed8;
            text-decoration: underline;
        }
    </style>
    '''

    def convert_text_formatting(text):
        """Convert Word-style formatting to HTML tags"""
        # Handle bold text (wrapped in **)
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # Handle italic text (wrapped in *)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        return text

    def convert_lists(text):
        """Convert Word-style lists to HTML lists"""
        lines = text.split('\n')
        html_lines = []
        current_list = None
        list_items = []
        
        for line in lines:
            # Check for bullet points (- or •)
            if line.strip().startswith(('-', '•')):
                if current_list != 'ul':
                    if current_list:
                        html_lines.append(f"</{current_list}>")
                    html_lines.append("<ul>")
                    current_list = 'ul'
                list_items.append(line.strip()[1:].strip())
                
            # Check for numbered lists (1. 2. etc)
            elif re.match(r'^\d+\.', line.strip()):
                if current_list != 'ol':
                    if current_list:
                        html_lines.append(f"</{current_list}>")
                    html_lines.append("<ol>")
                    current_list = 'ol'
                list_items.append(re.sub(r'^\d+\.', '', line).strip())
                
            else:
                if current_list:
                    for item in list_items:
                        html_lines.append(f"<li>{convert_text_formatting(item)}</li>")
                    html_lines.append(f"</{current_list}>")
                    current_list = None
                    list_items = []
                html_lines.append(line)
        
        # Close any remaining list
        if current_list:
            for item in list_items:
                html_lines.append(f"<li>{convert_text_formatting(item)}</li>")
            html_lines.append(f"</{current_list}>")
        
        return '\n'.join(html_lines)

    # Process content structure
    for section in content_structure:
        # Apply text formatting and list conversion to section content
        if 'content' in section:
            section['content'] = convert_lists(convert_text_formatting(section['content']))
    
    try:
        # Base HTML template with styles
        base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <link href="https://fonts.googleapis.com/css2?display=swap&family=Inter:ital,wght@0,400;0,500;1,400;1,500" rel="stylesheet" type="text/css" />
    <style>
        body {
            font-family: 'Inter', sans-serif;
            line-height: 1.0;
            background-color: #FAFAFA;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 55rem;
            margin: 0;
            padding: 2rem;
            text-align: left;
        }
        h1, h2, h3, h4 {
            color: #3B3B3B;
            font-weight: 500;
            line-height: 1.125;
            text-align: left;
        }
        h1 { font-size: 2.81em; }
        h2 { font-size: 1.31em; }
        h3 { font-size: 1.05em; }
        h4 { font-size: 0.75em; }
        p {
            color: #3B3B3B;
            /* font-size: 0.45em; */    
            line-height: 1.75;
            text-align: left;
        }
        a {
            color: #FF7A00;
            text-decoration: none;
            transition: color 0.25s ease;
        }
        a:hover {
            color: #FF8719;
        }
        .toc {
            padding: 1.5rem;
            background: #FFFFFF;
            box-shadow: 0rem 1.625rem 2.25rem 0rem rgba(0,0,0,0.059);
            border-radius: 1rem;
            text-align: left;
        }
        .toc ul {
            list-style: none;
            padding-left: 1.5rem;
            text-align: left;
        }
        .toc li {
            text-align: left;
            margin-top: 1rem;
        }
        .section {
            margin: 3rem 0;
            padding: 1.5rem;
            background: #FFFFFF;
            box-shadow: 0rem 1.625rem 2.25rem 0rem rgba(0,0,0,0.059);
            border-radius: 1rem;
            text-align: left;
        }
    </style>
</head>
<body>
'''

        # Generate TOC
        print("Generating TOC...")
        toc_html = base_template + '<div class="container toc"><h1>Table of Contents</h1><ul>'
        sections_html = []
        
        # Generate TOC entries and sections
        for i, h1 in enumerate(content_structure["H1"], 1):
            # Add TOC entry
            toc_html += f'<li><a href="#section{i}" class="scroll-link">{h1["title"]}</a><ul>'
            
            # Generate section content
            section_content = generate_section_html(h1, i)
            full_section = base_template + f'<div class="container section">{section_content}</div></body></html>'
            sections_html.append(full_section)
            
            # Add H2 entries to TOC
            for j, h2 in enumerate(h1["H2"], 1):
                toc_html += f'<li><a href="#section{i}-{j}" class="scroll-link">{h2["title"]}</a><ul>'
                
                # Add H3 entries to TOC
                for k, h3 in enumerate(h2["H3"], 1):
                    toc_html += f'<li><a href="#section{i}-{j}-{k}" class="scroll-link">{h3["title"]}</a></li>'
                
                toc_html += '</ul></li>'
            toc_html += '</ul></li>'
        
        toc_html += '</ul></div></body></html>'
        
        return toc_html, sections_html

    except Exception as e:
        print(f"Error in generate_html_sections: {str(e)}")
        raise

def save_sections_to_files(toc_html, sections_html, output_dir=""):
    """
    Save TOC and each section to separate HTML files.
    """
    try:
        import os
        
        # If output_dir is empty, use current directory
        output_dir = output_dir or "."
        
        # Create output directory if it doesn't exist and it's not the current directory
        if output_dir != ".":
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created/verified output directory: {output_dir}")
        
        # Save TOC
        toc_path = os.path.join(output_dir, "toc.html")
        print(f"Saving TOC to {toc_path}")
        with open(toc_path, "w", encoding="utf-8") as f:
            f.write(toc_html)
        
        # Save each section
        for i, section in enumerate(sections_html, 1):
            filename = f"section{i}.html"
            filepath = os.path.join(output_dir, filename)
            print(f"Saving section {i} to {filepath}")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(section)

        print("All files saved successfully")

    except Exception as e:
        print(f"Error in save_sections_to_files: {str(e)}")
        raise

def generate_toc_item(section):
    """Generate TOC item with proper styling"""
    try:
        if not isinstance(section, dict):
            print(f"Warning: section is not a dictionary: {section}")
            return ""
            
        section_id = section.get("id", "")
        title = section.get("title", "Untitled")
        
        result = f'<li><a href="#{section_id}">{title}</a>'
        
        if section.get('subsections'):
            result += '<ul>'
            for subsection in section['subsections']:
                result += generate_toc_item(subsection)
            result += '</ul>'
        result += '</li>'
        return result

    except Exception as e:
        print(f"Error in generate_toc_item: {str(e)}")
        return ""

def generate_section_content(section):
    """Generate section content with proper styling"""
    try:
        if not isinstance(section, dict):
            print(f"Warning: section is not a dictionary: {section}")
            return ""
            
        section_id = section.get("id", "")
        title = section.get("title", "Untitled")
        level = section.get("level", 1)
        content = section.get("content", "")
        
        result = f'<div id="{section_id}">'
        result += f'<h{level}>{title}</h{level}>'
        
        if content:
            result += f'<p>{content}</p>'
            
        if section.get('subsections'):
            for subsection in section['subsections']:
                result += generate_section_content(subsection)
                
        result += '</div>'
        return result

    except Exception as e:
        print(f"Error in generate_section_content: {str(e)}")
        return ""

# Example usage
if __name__ == "__main__":
    try:
        print("Starting HTML generation...")
        md_path = "output.md"
        print(f"Reading markdown from: {md_path}")
        
        content_structure = extract_headings_and_text_with_h4(md_path)
        print(f"Extracted content structure")
        
        toc_html, sections_html = generate_html_sections(content_structure)
        print(f"Generated TOC and {len(sections_html)} section files")
        
        save_sections_to_files(toc_html, sections_html)
        print(f"Successfully generated {len(sections_html) + 1} files in the 'output' directory")
        
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
