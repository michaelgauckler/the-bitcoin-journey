from openai import OpenAI
import re
import os

# Initialize the OpenAI client
client = OpenAI()

def parse_markdown_to_tree(md_path):
    """Parse markdown file into a nested data structure based on heading levels."""
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    tree = []
    current_h1 = None
    current_h2 = None
    current_h3 = None

    for line in lines:
        line = line.strip()
        
        if line.startswith('# ') and not line.startswith('## '):  # H1
            current_h1 = {"title": line[2:], "H2": []}
            tree.append(current_h1)
            current_h2 = None
            current_h3 = None
            
        elif line.startswith('## '):  # H2
            if current_h1:
                current_h2 = {"title": line[3:], "H3": []}
                current_h1["H2"].append(current_h2)
                current_h3 = None
                
        elif line.startswith('### '):  # H3
            if current_h2:
                current_h3 = {"title": line[4:], "content": []}
                current_h2["H3"].append(current_h3)
                
        else:  # Regular text
            if current_h3:
                current_h3["content"].append(line)
    
    return tree

def call_openai_api(prompt):
    """Call OpenAI's API with the given prompt."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant and expert on Bitcoin who writes well-structured content with clear paragraphs and headlines."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        # Wrap each paragraph with '####', make content italic, and add newline
        content = response.choices[0].message.content.strip()
        paragraphs = content.split('\n\n')
        content_with_separators = '\n\n'.join(f'#### *{p.strip()}* ####' for p in paragraphs if p.strip())
        return content_with_separators
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return None

def traverse_and_process(tree, max_calls=1000):
    """Traverse the tree and call OpenAI's API for each leaf node."""
    call_count = 0

    def traverse(node):
        nonlocal call_count
        if call_count >= max_calls:
            return
        
        if "H3" in node:
            for h3 in node["H3"]:
                if call_count < max_calls:
                    prompt = f"In the context of an educational course on Bitcoin write half a page, well structured in paragraphs on this point: {h3['title']}"
                    print(f"Calling OpenAI API for: {h3['title']}")
                    response = call_openai_api(prompt)
                    if response:
                        print(f"Response received for: {h3['title']}")
                        # Store the response in the tree structure
                        h3['generated_content'] = response
                    call_count += 1
        else:
            for child in node.get("H2", []):
                traverse(child)

    for h1 in tree:
        traverse(h1)
    
    return tree

def export_tree_to_markdown(tree, output_path):
    """Export the tree structure to a markdown file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for h1 in tree:
            # Write H1
            f.write(f"# {h1['title']}\n\n")
            
            # Write H1 content if any
            if 'content' in h1:
                for line in h1['content']:
                    f.write(f"{line}\n")
                f.write("\n")
            
            # Process H2 sections
            for h2 in h1.get("H2", []):
                f.write(f"## {h2['title']}\n\n")
                
                # Write H2 content if any
                if 'content' in h2:
                    for line in h2['content']:
                        f.write(f"{line}\n")
                    f.write("\n")
                
                # Process H3 sections
                for h3 in h2.get("H3", []):
                    f.write(f"### {h3['title']}\n\n")
                    
                    # Write original H3 content if any
                    if 'content' in h3 and h3['content']:
                        for line in h3['content']:
                            f.write(f"{line}\n")
                        f.write("\n")
                    
                    # Write generated content if available
                    if 'generated_content' in h3:
                        f.write(f"{h3['generated_content']}\n\n")
                    
                f.write("\n")  # Extra space between sections
            
            f.write("\n")  # Extra space between main sections

if __name__ == "__main__":
    try:
        # Input and output paths
        md_path = "skeleton.md"
        output_path = "output.md"
        
        print(f"Reading markdown from: {md_path}")
        tree = parse_markdown_to_tree(md_path)
        print("Parsed markdown structure")
        
        # Process and get updated tree with generated content
        processed_tree = traverse_and_process(tree)
        print("Finished generating content")
        
        # Export the processed tree to markdown
        export_tree_to_markdown(processed_tree, output_path)
        print(f"Generated markdown saved to: {output_path}")
        
    except Exception as e:
        print(f"Error in main execution: {str(e)}") 