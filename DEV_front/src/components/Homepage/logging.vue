<template>
    <div class="container">
        <div v-if="error.length > 0" class="p-2 d-flex justify-content-center">
            <p style="color: crimson;">{{ error }}</p>
        </div>
        <div class="m-2 bg-white" style="border: 1px solid black; padding: 20px">
            <p>To extract a log from the SLURM system, you can use the following form (by clicking on SLURM Logging
                Form). The log provides information about the jobs currently running in the SLURM queue, such as ACCOUNT,
                the
                associated account and COMMAND the command to be
                executed.Find more information in
                <a href="https://slurm.schedmd.com/squeue.html">
                    https://slurm.schedmd.com/squeue.html.</a>
            </p>
        </div>
        <div class="col d-flex" style="justify-content:space-between">
            <button class="btn btn-secondary btn-outline-dark pt-0 pb-0" data-bs-target="#StartLoggingForm"
                data-bs-toggle="modal" data-bs-dismiss="modal">
                <div class="d-flex flex-row justify-content-center align-items-center">
                    <i class="bi bi-pencil-square text-white mr-2"></i>
                    <p class="text-white pt-3">SLURM Logging Form</p>
                </div>
            </button>
            <LoggingFormModal />
            <button class="btn btn-light btn-outline-success" style="margin-bottom: 5px; margin-top: 5px;" type="button"
                @click="get_slurm_log_description">
                Get log description
            </button>
        </div>
        <div class="mt-2 col d-flex justify-content-end">
            <a class="link text-primary" @click="download_slurm_log">Download SLURM log</a>
        </div>
        <div v-if="s_log_desc_loading" class="p-4 d-flex justify-content-center">
            <h3 class="text-warning">Loading...</h3>
        </div>
        <div v-if="s_log_description.length != 0" class="p-3 d-flex justify-content-center" style="width: 99%">
            <ul class="list-group" style="width: 100%">
                <li class="list-group-item list-group-item-secondary d-flex justify-content-between align-items-center">
                    Start Time
                    <h6><span class="badge badge-dark badge-pill p-2">{{ s_log_description['startTime'] }}</span></h6>
                </li>
                <li class="list-group-item list-group-item-secondary d-flex justify-content-between align-items-center">
                    End Time
                    <span class="badge badge-dark badge-pill p-2">{{ s_log_description['endTime'] }}</span>
                </li>
                <li class="list-group-item list-group-item-secondary d-flex justify-content-between align-items-center">
                    Number of events in the SLURM log
                    <span class="badge badge-dark badge-pill p-2">{{ s_log_description['eventsNumber'] }}</span>
                </li>
                <li class="list-group-item list-group-item-secondary d-flex justify-content-between align-items-center">
                    Number of unique submitted jobs in the SLURM log
                    <span class="badge badge-dark badge-pill p-2">{{ s_log_description['jobNumber'] }}</span>
                </li>
                <li class="list-group-item list-group-item-secondary d-flex justify-content-between align-items-center">
                    Number of unique accounts in the SLURM log
                    <span class="badge badge-dark badge-pill p-2">{{ s_log_description['accountNumber'] }}</span>
                </li>
                <li class="list-group-item list-group-item-secondary d-flex justify-content-between align-items-center">
                    Percentage of accounts who submitted their jobs with explicit interdependencies
                    <span class="badge badge-dark badge-pill p-2">{{ s_log_description['SLURMaccountsPercentage'] }}</span>
                </li>
                <li class="list-group-item list-group-item-secondary d-flex justify-content-between align-items-center">
                    Percentage of jobs were defined with explicit interdependencies
                    <span class="badge badge-dark badge-pill p-2">{{ s_log_description['SLURMjobssPercentage'] }}</span>
                </li>
                <li class="list-group-item list-group-item-secondary d-flex justify-content-between align-items-center">
                    The average number of allocated CPUs
                    <span class="badge badge-dark badge-pill p-2">{{ s_log_description['CPUusageAvg'] }}</span>
                </li>
                <li class="list-group-item list-group-item-secondary d-flex justify-content-between align-items-center">
                    The average number of allocated RAMs
                    <span class="badge badge-dark badge-pill p-2">{{ s_log_description['RAMusageAvg'] }}</span>
                </li>
            </ul>
        </div>
    </div>
</template>
  
<script type="text/javascript">
import LoggingFormModal from "./Modals/LoggingFormModal.vue";
import { mapActions } from "pinia";
import { slurmLogQueries } from "../../stores/APIs";
import { mapWritableState } from "pinia";

export default {
    name: "StartLogging",
    components: { LoggingFormModal },

    methods: {
        sleep(time) {
            return new Promise((resolve) => setTimeout(resolve, time));
        },
        download(url) {
            window.location.href = url;
        },

        async download_slurm_log() {
            try {
                this.slurm_log_content = ""
                this.getData("");
                while (this.slurm_log_content.length == 0) {
                    await this.sleep(1);
                }
                var a = document.createElement('a');
                a.href = this.slurm_log_content;
                let random_name = (Math.random() + 1).toString(36).substring(7);
                a.download = random_name + '.csv';
                document.body.appendChild(a);
                a.click();
            } catch (error) {
                console.log("error: ", error)
            }
        },
        ...mapActions(slurmLogQueries, ["getData"]),


        async get_slurm_log_description() {
            try {
                this.slurmLogDescription()
            } catch (error) {
                console.log("error: ", error)
            }
        },
        ...mapActions(slurmLogQueries, ["slurmLogDescription"]),
    },
    computed: {
        ...mapWritableState(slurmLogQueries, [
            "s_log_description",
            "s_log_desc_loading",
            "slurm_log_content",
            "error"
        ])
    },
    beforeMount() {
        this.error = ""
    },
};
</script>
  