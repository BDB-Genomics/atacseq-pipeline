# ATACseq-Pipeline

> **Mentorship & Guidance**
> This pipeline was developed under the guidance of **Jessica Evangeline KC**, PhD Student,
> Institute of Bioinformatics and Applied Biotechnology (IBAB), Bangalore.
> Her mentorship shaped the design principles, QC strategy, and analytical rigor of this workflow.


A modular Snakemake workflow for paired-end ATAC-seq processing, from raw FASTQ files to QC, peak calling, annotation, motif discovery, and reporting.

## Status

- DAG-resolved on the current workflow layout.
- Smoke tests, benchmark baselines, and regression coverage are still pending.

## Workflow Summary

This pipeline performs:

- FASTQ trimming and QC with `fastp` and `FastQC`
- Alignment with `bowtie2`
- Post-alignment processing with `samtools`
- Mitochondrial read removal
- Duplicate marking and filtering
- Tn5 shifting
- Coverage generation and normalization
- Peak calling and blacklist filtering
- Peak annotation and motif discovery
- QC metrics, FRiP, TSS enrichment, and QC gating
- MultiQC aggregation

## Repository Layout

```text
Snakefile                 # Main Snakemake entry point
config.yaml               # Workflow configuration
data/                     # Input FASTQs, references, motif database
rules/                    # Rule files and helper scripts
rules/envs/               # Rule-specific conda environments
scripts/run_pipeline.sh   # Wrapper for validation and execution
results/                  # Generated outputs
logs/                     # Per-rule logs
benchmarks/               # Per-rule benchmark files
```

## Inputs

The workflow expects these inputs:

- `config.yaml`
- `data/fastp/samples.tsv`
- Reference files under `data/reference/`
- Motif database under `data/motifs/`

### Sample Sheet Format

`data/fastp/samples.tsv` must contain at least these columns:

- `sample`
- `fastq_r1`
- `fastq_r2`
- `replicate`
- `condition`

Optional:

- `control`

Rules enforced by the validator:

- Sample names must match `^[A-Za-z0-9._-]+$`
- `replicate` must be a positive integer
- `condition` must be present
- `fastq_r1` and `fastq_r2` must resolve to real files
- `control`, if present, must refer to another sample ID or `NONE`

Example:

```tsv
sample	fastq_r1	fastq_r2	replicate	condition
sample1	data/fastp/input/sample1_R1.fastq.gz	data/fastp/input/sample1_R2.fastq.gz	1	ATACseq
sample2	data/fastp/input/sample2_R1.fastq.gz	data/fastp/input/sample2_R2.fastq.gz	2	ATACseq
```

## Quick Start

1. Ensure either `snakemake` is on `PATH` or Conda can provide the `snakemake_runner` environment.
2. Review `config.yaml` and `data/fastp/samples.tsv`.
3. Run a dry run:

```bash
scripts/run_pipeline.sh --dry-run
```

4. Run the workflow:

```bash
scripts/run_pipeline.sh --cores 8
```

The wrapper script:

- validates the config before Snakemake starts
- uses `--use-conda` by default
- writes a combined log to `pipeline.log`
- supports `--unlock`, `--no-use-conda`, `--keep-going`, and `--no-rerun-incomplete`

## Configuration

`config.yaml` is organized by rule/module:

- `global`
- `fastp`
- `fastqc`
- `bowtie2`
- `samtools_*`
- `tss_enrichment`
- `bedtools_genomecov`
- `bigwig`
- `correlation_analysis`
- `normalize_coverage`
- `macs2`
- `blacklist_filter`
- `frip_calculation`
- `peak_annotation`
- `motif_analysis`
- `preseq`
- `qualimap_bamqc`
- `qc_gate`
- `multiqc`

The per-rule conda environment files are kept under `rules/envs/` and are referenced from the rule files.

## Outputs

Typical output directories include:

- `results/fastp/`
- `results/fastqc/`
- `results/bowtie2/`
- `results/samtools_sort/`
- `results/remove_mito_reads/`
- `results/samtools_markdup/`
- `results/samtools_view/`
- `results/tn5_shift/`
- `results/samtools_stats/`
- `results/fragment_size_analysis/`
- `results/picard/`
- `results/tss_enrichment/`
- `results/bedtools_genomecov/`
- `results/sorted_bedgraph_file/`
- `results/bigwig/`
- `results/normalized_coverage/`
- `results/correlation_analysis/`
- `results/heatmap/`
- `results/macs2_peakcall/`
- `results/filtered_peaks/`
- `results/frip_calculation/`
- `results/peak_annotation/`
- `results/motif_analysis/`
- `results/preseq/`
- `results/qualimap/`
- `results/qc_gate/`
- `results/multiqc/`

Logs and benchmarks are written to:

- `logs/`
- `benchmarks/`

## Notes

- The workflow validates its config at startup through `rules/scripts/validate_config.py`.
- `rules/envs/` is the intended environment location for this tree.
- `backup/` contains historical snapshots and is not used by the main workflow.
- If you move files around, update `config.yaml`, `Snakefile`, and the rule paths together.

## License

See [LICENSE](LICENSE).
