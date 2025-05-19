import os
from typing import Tuple, Optional

def get_path_to_script(
    selected_pipeline: str,
    selected_project: str,
    selected: str = ""
):
    NX_SHARED_PATH = "/data/scratch/shared/RSE/NF-project-configurations"
    base_path = os.path.join(NX_SHARED_PATH, selected_pipeline, selected_project)

    script_mapping = {
        "demo": "scripts/launch_demo.sh",
        "customised": "scripts/launch_samples.sh"
    }

    if selected not in script_mapping:
        raise ValueError(f"Invalid selection '{selected}'. Only 'customised', 'demo' are supported.")

    primary_script = os.path.join(base_path, script_mapping.get(selected, ""))

    return primary_script

# launch command based on the project
def pipe_cmd(
    username,
    selected_pipeline="",
    selected_project="",
    cmd_num=0,
    selected_samples="all",
    work_dir="work",
    output_dir="output",
    custom_sample_list=[],
    bed_file="",
    dry_run=False,
    adapt_samples=False
):
    def get_pipeline_command():
        """Generate the pipeline execution command based on the sample selection."""
        path_to_script = get_path_to_script(selected_pipeline, selected_project, selected_samples)
        
        args = []
        base_cmd = f"bash {path_to_script}" #default

        if selected_samples == "demo":
            log_out = f"{work_dir}/logs/log_demo.out"
            log_err = f"{work_dir}/logs/log_demo.err"
            base_cmd = f"sbatch -o {log_out} -e {log_err}"
            args += [path_to_script, work_dir, output_dir]

        elif selected_samples == "customised":
            if not custom_sample_list:
                raise ValueError("custom_sample_list cannot be empty")
            if dry_run:
                args.append("--dry-run")
            args += [
                "--work-dir", work_dir,
                "--outdir", output_dir,
                "--samples", "\t".join(custom_sample_list),
            ]
            if adapt_samples:
                args += ["--adapt-samples"]
            if bed_file:
                args += ["--bed", bed_file]
        
        # note: I use logs/log_{samplename} for sample logs
        preamble = f"""
        mkdir -p {work_dir}/logs
        cd {work_dir}
        """
        # Combine all into the final shell command
        cmd_pipeline = preamble + f"{base_cmd} {' '.join(args)}"
        return cmd_pipeline.strip()

    # Command mappings
    command_map = {
        0: get_pipeline_command(),
        1: f"squeue -u {username}",
        2: (
            f"sacct --user {username} "
            "--format UID,User,JobID,JobName,Submit,Elapsed,Partition,"
            "NNodes,NCPUS,TotalCPU,CPUTime,ReqMem,MaxRSS,WorkDir,State,"
            "Account,AllocTres -P"
        ),
        3: "echo hello from nextflow-on-Alma app",
    }

    # Return the corresponding command
    return command_map.get(cmd_num, "echo 'Invalid command number'")
