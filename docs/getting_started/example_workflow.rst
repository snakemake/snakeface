.. _getting_started-example-workflow:

================
Example Workflow
================

Downloading Tutorial
====================

You likely want to start with an example workflow. We will use the same one from
the `snakemake tutorial <https://snakemake.readthedocs.io/en/stable/tutorial/tutorial.html>_`.
We assume that you have already installed ``snakeface`` (and thus Snakemake and it's
dependencies are on your system). So you can download the example as follows:

.. code:: console

    $ mkdir snakemake-tutorial
    $ cd snakemake-tutorial
    $ wget https://github.com/snakemake/snakemake-tutorial-data/archive/v5.24.1.tar.gz
    $ tar --wildcards -xf v5.24.1.tar.gz --strip 1 "*/data" "*/environment.yaml"


This should extract a ``data`` folder and an ``environment.yaml``.
You should also create the `Snakefile <https://snakemake.readthedocs.io/en/stable/tutorial/basics.html#summary>_`.
This Snakefile is the same as in the tutorial, with the addition of adding the ``environment.yaml`` to each
section.

.. code:: console

    SAMPLES = ["A", "B"]

    rule all:
        input:
            "plots/quals.svg"


    rule bwa_map:
        input:
            "data/genome.fa",
            "data/samples/{sample}.fastq"
        output:
            "mapped_reads/{sample}.bam"
        conda:
             "environment.yaml"
        shell:
            "bwa mem {input} | samtools view -Sb - > {output}"


    rule samtools_sort:
        input:
            "mapped_reads/{sample}.bam"
        output:
            "sorted_reads/{sample}.bam"
        conda:
             "environment.yaml"
        shell:
            "samtools sort -T sorted_reads/{wildcards.sample} "
            "-O bam {input} > {output}"


    rule samtools_index:
        input:
            "sorted_reads/{sample}.bam"
        output:
            "sorted_reads/{sample}.bam.bai"
        conda:
             "environment.yaml"
        shell:
            "samtools index {input}"


    rule bcftools_call:
        input:
            fa="data/genome.fa",
            bam=expand("sorted_reads/{sample}.bam", sample=SAMPLES),
            bai=expand("sorted_reads/{sample}.bam.bai", sample=SAMPLES)
        output:
            "calls/all.vcf"
        conda:
             "environment.yaml"
        shell:
            "samtools mpileup -g -f {input.fa} {input.bam} | "
            "bcftools call -mv - > {output}"


    rule plot_quals:
        input:
            "calls/all.vcf"
        output:
            "plots/quals.svg"
        conda:
             "environment.yaml"
        script:
            "scripts/plot-quals.py"



Running Snakeface
=================

At this point, from this working directory you can run Snakeface. For example, you
might run a notebook (:ref:`getting_started-notebook`). Make sure to select ``--use-conda``
or else the environment above won't be properly sourced. This is one deviation from the main
Snakemake tutorial, which has you install dependencies on the command line before running
the workflow, and the workflow doesn't have the ``conda`` sections.
