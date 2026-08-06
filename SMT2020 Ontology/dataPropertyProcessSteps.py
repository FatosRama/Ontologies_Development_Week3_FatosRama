import pandas as pd
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import OWL, RDF, XSD

# 1. Load existing ontology graph
g = Graph()
g.parse("ontology_development_week3_updated2.ttl", format="ttl")

NS = Namespace(
    "http://www.semanticweb.org/fatos/ontologies/2026/7/ontology_development_week3/"
)
excel_path = "../materials/Week 2/Dataset 1_ Fatos Rama/DS1_SMT_2020_Model_Data_-_HVLM.xlsx"

# 2. Define Data Property Mappings for Process_Step
# Format: 'Excel Column Name': ('OntologyPropertyName', XSD_Datatype)
step_property_mappings = {
    # Cascading Interval
    "CASCADING INTERVAL": ("hasCascadingInterval", XSD.float),
    # Batch properties
    "BATCH MINIMUM": ("hasBatchMinimum", XSD.integer),
    "BATCH MAXIMUM": ("hasBatchMaximum", XSD.integer),
    # Setup timing
    "SETUP": ("hasSetupTiming", XSD.string),
    # LTL Dedication Step
    "STEP FOR LTL DEDICATION": ("hasLTLDedicationStep", XSD.string),
    # Rework properties
    "REWORK PROBABILITY in %": ("hasReworkProbability", XSD.float),
    "R UNIT": ("hasReworkUnit", XSD.string),
    # Processing Probability (Sampling)
    "PROCESSING PROBABILITY in % (Sampling)": ("hasProcessingProbability", XSD.float),
}

# 3. Declare all data properties explicitly as owl:DatatypeProperty
for prop_name, _ in step_property_mappings.values():
    g.add((NS[prop_name], RDF.type, OWL.DatatypeProperty))

# 4. Index existing Process_Step URIs in the graph for reliable lookup
existing_steps = list(g.subjects(RDF.type, NS.Process_Step))
print(f"Indexed {len(existing_steps)} Process_Step individuals from ontology.")

def find_step_uri(route_prefix, step_num):
    """Find matching step URI in the indexed ontology graph."""
    formatted_num = str(step_num).zfill(3)
    
    # Matching patterns to look for inside existing URIs
    pattern_padded = f"{route_prefix}_Step_{formatted_num}"
    pattern_unpadded = f"{route_prefix}_Step_{step_num}"

    for uri in existing_steps:
        uri_str = str(uri)
        if pattern_padded in uri_str or pattern_unpadded in uri_str:
            return uri
    return None

def cast_value(val, xsd_type):
    """Safely convert pandas cell value to python type for RDF Literal."""
    if pd.isna(val) or str(val).strip() == "" or str(val).strip().lower() == "nan":
        return None
    
    try:
        if xsd_type == XSD.integer:
            return int(float(val))  # Handles float formatted strings like "1.0"
        elif xsd_type == XSD.float:
            return float(val)
        else:
            return str(val).strip()
    except (ValueError, TypeError):
        return None

# 5. Load and Process Excel Data
print("\nLoading Excel data...")
route3_df = pd.read_excel(excel_path, sheet_name="Route_Product_3")
route4_df = pd.read_excel(excel_path, sheet_name="Route_Product_4")

def process_route_steps(df, route_prefix):
    """Process steps from a route sheet and add properties to existing Process_Step individuals"""
    added_count = 0
    found_count = 0
    not_found_count = 0
    
    for idx, row in df.iterrows():
        step_num = row.get('STEP')
        step_desc = row.get('STEP DESCRIPTION', '')
        
        if pd.isna(step_num):
            continue
            
        step_uri = find_step_uri(route_prefix, step_num)
        
        if not step_uri:
            not_found_count += 1
            print(f"  WARNING: Could not find Step {step_num} ({step_desc}) for {route_prefix} in ontology")
            continue
        
        found_count += 1
        props_added = 0
        
        # Dynamically map and add properties from step_property_mappings dictionary
        for col_name, (prop_name, xsd_type) in step_property_mappings.items():
            if col_name in row:
                raw_val = row[col_name]
                typed_val = cast_value(raw_val, xsd_type)
                
                if typed_val is not None:
                    g.add((step_uri, NS[prop_name], Literal(typed_val, datatype=xsd_type)))
                    props_added += 1
        
        if props_added > 0:
            added_count += props_added
            print(f"  Added {props_added} properties to Step {step_num} ({step_desc})")
            
    return added_count, found_count, not_found_count

# 6. Process both route sheets
print("\nProcessing Route_Product_3...")
route3_added, route3_found, route3_not_found = process_route_steps(route3_df, "P3")

print("\nProcessing Route_Product_4...")
route4_added, route4_found, route4_not_found = process_route_steps(route4_df, "P4")

# 7. Save updated ontology graph
print("\nSaving updated ontology...")
output_file = "ontology_development_week3_with_step_properties.ttl"
g.serialize(output_file, format="ttl")

print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"Route_Product_3: Found {route3_found} | Missing {route3_not_found} | Triples Added: {route3_added}")
print(f"Route_Product_4: Found {route4_found} | Missing {route4_not_found} | Triples Added: {route4_added}")
print(f"Total properties added: {route3_added + route4_added}")
print(f"Updated ontology saved to: {output_file}")