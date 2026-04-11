#!/usr/bin/env python3
import sys
import re
import argparse
from pathlib import Path

def parse_frip(frip_path):
    """Parses FRiP value from file (assumes key\tvalue or tab-separated headered)."""
    try:
        with open(frip_path, 'r') as f:
            lines = f.readlines()
            if not lines: return None
            # Check if it has a header 'sample\tfrip'
            if "sample" in lines[0].lower():
                parts = lines[1].strip().split('\t')
                return float(parts[1])
            else:
                parts = lines[0].strip().split('\t')
                return float(parts[1])
    except Exception as e:
        print(f"Error parsing FRiP: {e}", file=sys.stderr)
    return None

def parse_tss(tss_path):
    """Parses TSS Enrichment value from the R script output (headered TSV)."""
    try:
        with open(tss_path, 'r') as f:
            lines = f.readlines()
            if len(lines) < 2: return None
            # Column 2 is TSS_Enrichment
            parts = lines[1].strip().split('\t')
            if len(parts) >= 2:
                return float(parts[1])
    except Exception as e:
        print(f"Error parsing TSS Enrichment: {e}", file=sys.stderr)
    return None

def parse_samtools_stats(stats_path):
    """Parses total reads and mapping rate from samtools stats."""
    metrics = {
        "total_reads": None,
        "mapped_properly": None,
        "duplicates": None
    }
    try:
        with open(stats_path, 'r') as f:
            for line in f:
                if not line.startswith("SN\t"):
                    continue
                if "sequences:" in line:
                    metrics["total_reads"] = int(line.split('\t')[2])
                elif "percentage of properly paired reads:" in line:
                    metrics["mapped_properly"] = float(line.split('\t')[2].replace('%', ''))
                elif "reads duplicated:" in line:
                    metrics["duplicates"] = int(line.split('\t')[2])
    except Exception as e:
        print(f"Error parsing samtools stats: {e}", file=sys.stderr)
    return metrics

def main():
    parser = argparse.ArgumentParser(description="Robustly parse and validate ATAC-seq QC metrics.")
    parser.add_argument("--sample", required=True)
    parser.add_argument("--frip-file", required=True)
    parser.add_argument("--tss-file", required=True)
    parser.add_argument("--stats-file", required=True)
    parser.add_argument("--min-frip", type=float, required=True)
    parser.add_argument("--min-tss", type=float, required=True)
    parser.add_argument("--min-mapping-rate", type=float, required=True)
    parser.add_argument("--max-duplicate-rate", type=float, required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    errors = []
    log_content = [f"QC Report for {args.sample}", "-------------------------------"]
    
    # Parse all
    frip = parse_frip(args.frip_file)
    tss = parse_tss(args.tss_file)
    stats = parse_samtools_stats(args.stats_file)
    
    # Check for parsing failures
    if frip is None: errors.append("FRiP")
    if tss is None: errors.append("TSS Enrichment")
    if any(v is None for v in stats.values()): errors.append("Samtools Stats")
    
    if errors:
        with open(args.log, 'w') as f:
            f.write("\n".join(log_content) + "\n")
            f.write(f"[ERROR] Failed to parse metrics: {', '.join(errors)}\n")
        sys.exit(1)
        
    # Calculate duplicates
    dup_rate = (stats["duplicates"] * 100.0 / stats["total_reads"]) if stats["total_reads"] > 0 else 100.0
    mapping_rate = stats["mapped_properly"]
    
    log_content.append(f"FRiP: {frip:.4f} (Target: >= {args.min_frip})")
    log_content.append(f"TSS Enrichment: {tss:.4f} (Target: >= {args.min_tss})")
    log_content.append(f"Mapping Rate (%): {mapping_rate:.2f} (Target: >= {args.min_mapping_rate})")
    log_content.append(f"Duplicate Rate (%): {dup_rate:.2f} (Target: <= {args.max_duplicate_rate})")
    
    # Validation logic
    failures = []
    if frip < args.min_frip: failures.append(f"FRiP {frip:.4f} < {args.min_frip}")
    if tss < args.min_tss: failures.append(f"TSS Enrichment {tss:.4f} < {args.min_tss}")
    if mapping_rate < args.min_mapping_rate: failures.append(f"Mapping Rate {mapping_rate:.2f} < {args.min_mapping_rate}")
    if dup_rate > args.max_duplicate_rate: failures.append(f"Duplicate Rate {dup_rate:.2f} > {args.max_duplicate_rate}")
    
    if failures:
        log_content.append("-------------------------------")
        log_content.append("RESULT: FAILED")
        for fail in failures:
            log_content.append(f"[QC FAILURE] {fail}")
        with open(args.log, 'w') as f:
            f.write("\n".join(log_content) + "\n")
        print("\n".join(log_content), file=sys.stderr)
        sys.exit(2)
        
    log_content.append("-------------------------------")
    log_content.append("RESULT: PASSED")
    with open(args.log, 'w') as f:
        f.write("\n".join(log_content) + "\n")
        
    with open(args.output, 'w') as f:
        f.write(f"{args.sample}\tPASSED\n")

if __name__ == "__main__":
    main()
