import json
import zstandard
import io
import statistics

def compute():
    out_path = "artifacts/research/cp_source_feasibility_2026_07/raw/cp_source_root_results.jsonl.zst"
    
    roots_attempted = 0
    roots_success = 0
    roots_failed = 0
    
    total_legal = 0
    total_obs = 0
    cp_alts = 0
    mate_alts = 0
    
    list_legal = []
    list_cp = []
    list_pairs = []
    
    with open(out_path, "rb") as f:
        dctx = zstandard.ZstdDecompressor()
        with dctx.stream_reader(f) as reader:
            for line in io.TextIOWrapper(reader, encoding="utf-8"):
                if not line.strip(): continue
                rec = json.loads(line)
                roots_attempted += 1
                if rec["status"] == "SUCCESS":
                    roots_success += 1
                    res = rec["result"]
                    obs_list = res["observations"]
                    L = len(obs_list)
                    C = 0
                    M = 0
                    for o in obs_list:
                        if o["type"] == "cp":
                            C += 1
                        elif o["type"] == "mate":
                            M += 1
                    total_legal += L
                    total_obs += len(obs_list)
                    cp_alts += C
                    mate_alts += M
                    
                    pairs = C * (C - 1) // 2
                    
                    list_legal.append(L)
                    list_cp.append(C)
                    list_pairs.append(pairs)
                else:
                    roots_failed += 1
                    
    def dist(data):
        if not data: return {}
        s = sorted(data)
        return {
            "min": s[0],
            "median": statistics.median_low(s),
            "p90": s[int(len(s)*0.9)],
            "p95": s[int(len(s)*0.95)],
            "max": s[-1]
        }
        
    print("Roots attempted:", roots_attempted)
    print("Roots successful:", roots_success)
    print("Roots failed:", roots_failed)
    print("Total legal:", total_legal)
    print("Total obs:", total_obs)
    print("CP alts:", cp_alts)
    print("Mate alts:", mate_alts)
    print("CP fraction:", cp_alts / max(1, total_obs))
    print("Roots >=2 CP:", sum(1 for c in list_cp if c >= 2))
    print("Roots <2 CP:", sum(1 for c in list_cp if c < 2))
    print("Roots 0 pairs:", sum(1 for p in list_pairs if p == 0))
    print("Total CP/CP pairs:", sum(list_pairs))
    print("Dist Legal:", dist(list_legal))
    print("Dist CP:", dist(list_cp))
    print("Dist Pairs:", dist(list_pairs))

if __name__ == "__main__":
    compute()
