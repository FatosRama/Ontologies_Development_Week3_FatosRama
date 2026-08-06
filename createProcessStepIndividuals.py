import pandas as pd

excel_file = "../materials/Week 2/Dataset 1_ Fatos Rama/DS1_SMT_2020_Model_Data_-_HVLM.xlsx"

# Read both sheets
p3_df = pd.read_excel(excel_file, sheet_name="Route_Product_3")
p4_df = pd.read_excel(excel_file, sheet_name="Route_Product_4")

ttl_lines = [
    "#################################################################",
    "#    Individuals: All Process Steps (926 Individuals)",
    "#################################################################\n"
]

def generate_route_ttl(df, route_prefix, class_type):
    declarations = []
    connections = []
    
    for i, row in df.iterrows():
        step_num = row['STEP']
        step_desc = str(row['STEP DESCRIPTION']).strip().replace(" ", "_")
        area = str(row['AREA']).strip().replace(" ", "_")
        toolgroup = str(row['TOOLGROUP']).strip()
        
        ind_uri = f":{route_prefix}_Step_{step_num:03d}_{step_desc}"
        
        # Individual declaration
        decl = f"""{ind_uri} rdf:type owl:NamedIndividual , :Step , {class_type} ;
    :hasStepNumber {step_num} ;
    :performedIn :{area} ;
    :requiresToolGroup :{toolgroup} ."""
        declarations.append(decl)
        
        # Sequence connection
        if i > 0:
            prev_row = df.iloc[i - 1]
            prev_step_num = prev_row['STEP']
            prev_desc = str(prev_row['STEP DESCRIPTION']).strip().replace(" ", "_")
            prev_uri = f":{route_prefix}_Step_{prev_step_num:03d}_{prev_desc}"
            connections.append(f"{prev_uri} :nextStep {ind_uri} .")
            
    return declarations, connections

# Process Product 3 (583 steps)
p3_decls, p3_conns = generate_route_ttl(p3_df, "P3", ":P3_Step")

# Process Product 4 (343 steps)
p4_decls, p4_conns = generate_route_ttl(p4_df, "P4", ":P4_Step")

# Combine and save
with open("All_926_Process_Steps.ttl", "w") as f:
    f.write("\n".join(ttl_lines))
    f.write("\n\n# --- Product 3 Declarations (583) ---\n")
    f.write("\n\n".join(p3_decls))
    f.write("\n\n# --- Product 3 Flow Connections ---\n")
    f.write("\n".join(p3_conns))
    
    f.write("\n\n# --- Product 4 Declarations (343) ---\n")
    f.write("\n\n".join(p4_decls))
    f.write("\n\n# --- Product 4 Flow Connections ---\n")
    f.write("\n".join(p4_conns))

print("Successfully generated All_926_Process_Steps.ttl!")