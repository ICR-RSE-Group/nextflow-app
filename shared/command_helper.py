import os


def get_path_to_script(selected_pipeline, selected_project, selected="all"):
    NX_SHARED_PATH = "/data/scratch/shared/RSE/NF-project-configurations"
    # e.g., /data/scratch/shared/RSE/NF-project-configurations/epi2me-human-variation/nf-long-reads/scripts
    base_path = os.path.join(NX_SHARED_PATH, selected_pipeline, selected_project, "scripts")

    script_mapping = {
        "all": "launch_samples.sh",
        "demo": "launch_demo.sh",
        "customised": "launch_samples.sh",
    }

    if selected in script_mapping:
        return os.path.join(base_path, script_mapping[selected])

    raise ValueError(f"Invalid selection '{selected}'. Only 'customised' and 'demo' are supported.")


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
    bed_file=""
):
    def get_pipeline_command():
        """Generate the pipeline execution command based on the sample selection."""
        path_to_script = get_path_to_script(selected_pipeline, selected_project, selected_samples)

        # not sure if this is the best thing-using job id for filenamne
        log_out = f"{work_dir}/logs/%j.out"
        log_err = f"{work_dir}/logs/%j.err"

        args = []
        base_cmd = f"sbatch -o {log_out} -e {log_err}"

        if selected_samples == "demo":
            args = [path_to_script, work_dir, output_dir]

        elif selected_samples == "all":
            #./your_script.sh --env "/my/custom/env" --work-dir "my_work" --outdir "my_output" --config "my_config" --params "parans.json" --bed file.bed
            args = [
                path_to_script,
                "--work-dir", work_dir,
                "--outdir", output_dir,
            ]
            if bed_file:
                args += ["--bed", bed_file]

        elif selected_samples == "customised":
            if not custom_sample_list:
                raise ValueError("custom_sample_list cannot be empty")
            args = [
                path_to_script,
                "--work-dir", work_dir,
                "--outdir", output_dir,
                "--samples", "\t".join(custom_sample_list),
            ]
            if bed_file:
                args += ["--bed", bed_file]
        # elif selected_samples == "test": #this will become dry-run, but I should develop it for all scripts
        #     cmd_pipeline += f"sbatch  -o {log_out} -e {log_err} /data/scratch/DCO/DIGOPS/SCIENCOM/msarkis/NF-project-configurations/test.sh --work-dir {work_dir} --outdir {output_dir}"
 
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
