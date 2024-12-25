import json

def check_creativity_questions():
    """Debug function to check Creativity questions across all age groups"""
    age_group_files = [
        'questions_under_12.json',
        'questions_12_17.json',
        'questions_above_18.json'
    ]
    
    for file_name in age_group_files:
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                questions = json.load(file)
                print(f"\nChecking {file_name}:")
                
                # Check if Creativity exists in the file
                if 'Creativity' in questions:
                    print(f"✓ Creativity key found in {file_name}")
                    creativity_questions = questions['Creativity']
                    print(f"Number of Creativity questions: {len(creativity_questions)}")
                    
                    # Check each question's structure
                    for i, q in enumerate(creativity_questions):
                        print(f"\nQuestion {i+1}:")
                        print(f"Question text: {q.get('question', 'NO QUESTION TEXT')}")
                        print("Options:", q.get('options', 'NO OPTIONS'))
                        print("Answer mapping:", q.get('answer_mapping', 'NO MAPPING'))
                        
                        # Verify answer mapping matches options
                        options = q.get('options', [])
                        mapping = q.get('answer_mapping', {})
                        
                        # Check if all options have mappings
                        for opt in options:
                            key = opt.split(':')[0] if ':' in opt else opt[0]
                            if key not in mapping:
                                print(f"WARNING: No mapping found for option {key}")
                else:
                    print(f"✗ No Creativity key found in {file_name}")
                    
        except FileNotFoundError:
            print(f"✗ File not found: {file_name}")
        except json.JSONDecodeError as e:
            print(f"✗ JSON error in {file_name}: {e}")
        except Exception as e:
            print(f"✗ Error processing {file_name}: {e}")

# Function to modify the predict route to debug Creativity specifically
def debug_creativity_processing(form_data):
    """Debug function to trace Creativity value processing"""
    print("\nDebugging Creativity Processing:")
    print("1. Raw form data for Creativity:", form_data.get('Creativity'))
    
    try:
        creativity_value = int(form_data.get('Creativity', 0))
        print("2. Converted Creativity value:", creativity_value)
    except ValueError as e:
        print("2. Error converting Creativity value:", e)
        creativity_value = 0
        
    print("3. Final Creativity value:", creativity_value)
    return creativity_value

# Add this to your Flask routes
@app.route('/debug-creativity', methods=['GET'])
def debug_creativity():
    """Route to run creativity debugging"""
    check_creativity_questions()
    return "Check console for debug output"