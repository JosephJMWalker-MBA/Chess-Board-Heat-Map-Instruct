import json

def get_channel_status(sq, d_val, r_earliest, r_lines, b_moves, b_size):
    d_status = "not observed"
    if d_val > 0:
        if d_val >= 0.15:
            d_status = "observed-selected (val: {:.2f}, predicate: >=0.15)".format(d_val)
        else:
            d_status = "observed-rejected (val: {:.2f}, predicate: <0.15)".format(d_val)
            
    r_status = "not observed"
    if r_earliest is not None:
        if r_earliest <= 2 and r_lines >= 3:
            r_status = f"observed-selected (earliest: {r_earliest}, lines: {r_lines}, predicate: <=2 and >=3)"
        else:
            if r_earliest > 2:
                r_status = f"observed-rejected (earliest: {r_earliest}, lines: {r_lines}, predicate: earliest_ply > 2)"
            else:
                r_status = f"observed-rejected (earliest: {r_earliest}, lines: {r_lines}, predicate: distinct_lines < 3)"
                
    b_status = "not observed"
    if b_moves > 0:
        if b_moves >= 3 and b_size <= 15:
            b_status = f"observed-selected (moves: {b_moves}, size: {b_size}, predicate: moves>=3 and size<=15)"
        else:
            if b_moves < 3:
                b_status = f"observed-rejected (moves: {b_moves}, size: {b_size}, predicate: moves < 3)"
            else:
                b_status = f"observed-rejected (moves: {b_moves}, size: {b_size}, predicate: size > 15)"
                
    return d_status, r_status, b_status

def generate_report():
    print("=== M8.6.4 CHANNEL INDEPENDENCE AUDIT ===")
    
    # We will parse the output from our previous audit_m8_6_3_output.txt to extract the expected square native values
    # Because they contain precisely the data we need (d_val, r_earliest, r_lines, b_moves, b_size).
    # Wait, the output format was:
    # e8: Dir=0.05, Rec=(ply:1, lines:1), Bun=(moves:1, size:13)
    
    targets = ["W2_Two_Line_Recurrence", "W3_Single_Consequential_Move", "W4_Legitimate_Broad_Bundle", "W12_Disjoint_Regions"]
    
    import re
    with open("/Users/josephjmwalker-mba/.gemini/antigravity/brain/26efe2e2-9972-489d-8885-11e47c116bc1/scratch/audit_m8_6_3_output.txt") as f:
        lines = f.readlines()
        
    current_fx = None
    for line in lines:
        if " - Mate Moves" in line:
            current_fx = line.split(" - ")[0].strip()
        if current_fx in targets and "Dir=" in line:
            # Parse line: a2: Dir=0.14, Rec=(ply:1, lines:4), Bun=(moves:14, size:15)
            # Regex or simple string split
            parts = line.strip().split(":")
            sq = parts[0].strip()
            
            # Use regex to extract numbers
            d_match = re.search(r"Dir=([\d\.]+)", line)
            r_ply_match = re.search(r"ply:(\d+|None)", line)
            r_lines_match = re.search(r"lines:(\d+)", line)
            b_moves_match = re.search(r"moves:(\d+)", line)
            b_size_match = re.search(r"size:(\d+)", line)
            
            if not d_match: continue
            
            d_val = float(d_match.group(1))
            r_ply = int(r_ply_match.group(1)) if r_ply_match.group(1) != "None" else None
            r_lines = int(r_lines_match.group(1))
            b_moves = int(b_moves_match.group(1))
            b_size = int(b_size_match.group(1))
            
            print(f"\n{current_fx} - Square: {sq}")
            d_stat, r_stat, b_stat = get_channel_status(sq, d_val, r_ply, r_lines, b_moves, b_size)
            print(f"  Direct: {d_stat}")
            print(f"  Recurrence: {r_stat}")
            print(f"  Bundle: {b_stat}")
            
if __name__ == "__main__":
    generate_report()
