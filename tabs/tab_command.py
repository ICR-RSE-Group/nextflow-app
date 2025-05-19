import re

import streamlit as st

import shared.command_helper as cmd_hlp
import shared.helpers as hlp


def tab(
    username,
    MY_SSH,
    selected_pipeline,
    selected_project,
    selected_samples="",
    work_dir="work",
    output_dir="output",
    custom_sample_list=[],
    bed_file="",
    dry_run=False,
    adapt_samples=False
):
    # --- Initialize session state ---
    st.session_state.setdefault("username", username)
    st.session_state.setdefault("JOB_ID", "")
    st.session_state.setdefault("run_pipeline_clicked", False)

    # --- Display username input ---
    cols = st.columns([1])
    with cols[0]:
        st.session_state["username"] = st.text_input("Username(s):", st.session_state["username"])

    # --- Log display helper ---
    def display_log(title, log_path, output_container):
        try:
            log_file = MY_SSH.read_file(log_path)
            log_content = log_file.read() if hasattr(log_file, "read") else str(log_file)
            output_container.code(log_content, language="bash")
        except Exception as e:
            st.error(f"❌ Failed to read {title.lower()} log: {e}")

    # --- Run pipeline logic ---
    def run_nextflow():
        cmd_pipeline = cmd_hlp.pipe_cmd(
            st.session_state["username"],
            selected_pipeline,
            selected_project,
            cmd_num=0,
            selected_samples=selected_samples,
            output_dir=output_dir,
            work_dir=work_dir,
            custom_sample_list=custom_sample_list,
            bed_file=bed_file,
            dry_run=dry_run,
            adapt_samples=adapt_samples
        )
        st.code(cmd_pipeline)
        result = MY_SSH.run_cmd(cmd_pipeline)
        match = re.search(r"Submitted batch job (\d+)", result["output"])
        job_id = match.group(1) if match else None
        st.session_state["JOB_ID"] = job_id
        st.success(f"✅ Job submitted. ID: {job_id}")
        return job_id

    # --- Tabs ---
    tabP, tabL, tabQ = st.tabs(["Run pipeline", "Check logs", "Check queues"])

    # --- Pipeline tab ---
    with tabP:
        if st.button("Run the selected pipeline"):
            st.session_state["run_pipeline_clicked"] = True
            with st.spinner("Submitting pipeline..."):
                try:
                    run_nextflow()
                except Exception as e:
                    st.error(f"Pipeline error: {e}")

        if st.session_state["JOB_ID"]:
            st.success(f"Running Job ID: {st.session_state['JOB_ID']}")

    get_sample_list = lambda selected_samples, custom_sample_list: [selected_samples] if selected_samples == 'demo' else custom_sample_list
    parsed_sample_list = get_sample_list(selected_samples, custom_sample_list)
    # --- Logs tab ---
    with tabL:
        def show_logs():
            sample = st.session_state.get("sample_to_log", "")
            if not sample:
                st.error("No job was launched yet")
                return

            log_out = f"{work_dir}/logs/log_{sample}.out"
            log_err = f"{work_dir}/logs/log_{sample}.err"
            tO, tE = st.tabs(["Output", "Error"])
            outputO, outputE = tO.empty(), tE.empty()
            with st.spinner("Fetching logs..."):
                display_log("Output", log_out, outputO)
                display_log("Error", log_err, outputE)
        # when checking logs, ask user to select one (drop-down list) of his samples at a time : demo or customised sample
        st.selectbox("Choose an option", parsed_sample_list, key="sample_to_log", index=0)

        if st.button("Get Logs"):
            show_logs()
            #job_id = st.session_state.get("JOB_ID")
            #st.write("📌 Accessed JOB_ID:", job_id)  # DEBUG

    # --- Queues tab ---
    with tabQ:
        if st.button("Check slurm queues"):
            output = st.empty()
            with st.spinner("Checking queue..."):
                with hlp.st_capture(output.code):
                    cmd_pipeline = cmd_hlp.pipe_cmd(st.session_state["username"], cmd_num=1)
                    try:
                        results = MY_SSH.run_cmd(cmd_pipeline)
                        if results["err"] is not None:
                            st.error(results["err"])
                        else:
                            print(results["output"])
                    except Exception as e:
                        st.error(f"Error {e}")
