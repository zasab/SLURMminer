<template>
    <div v-if="jobid_st_error.length > 0" class="p-2 d-flex justify-content-center">
        <p style="color: crimson;">{{ jobid_st_error }}</p>
    </div>
    <div class="mt-3 pt-2">
        <div v-if="jobid_st_loading" class="p-4 d-flex justify-content-center">
            <h3 class="text-warning">Loading...</h3>
        </div>
        <div v-if="jobid_st_error.length == 0 && jobid_st_freq_model.length > 0"
            class="p-4 d-flex flex-column justify-content-center">
            <div class="bg-white" style="border: 1px solid black; padding: 20px">
                <p>By examining the extracted SLURM log, if we consider JOBID as case identifier and ST as activity notion,
                    and
                    then apply process discovery technique on that we will observe the lifecycle of job execution.The
                    typical
                    states involved in the lifecycle of job execution on a SLURM system are as follows
                <ul>
                    <li><span style="color: brown;">PD (PENDING)</span>: Job is awaiting resource allocation. </li>
                    <li><span style="color: brown;">CF (CONFIGURING)</span>: Job has been allocated resources, but are
                        waiting for them to become ready for use
                        (e.g. booting). </li>
                    <li><span style="color: brown;">R (RUNNING)</span>: Job currently has an allocation. </li>
                    <li><span style="color: brown;">CG ( COMPLETING)</span>: Job is in the process of completing. Some
                        processes on some nodes may still be
                        active. </li>
                </ul>
                <span>More information in <a href="https://slurm.schedmd.com/squeue.html">
                        https://slurm.schedmd.com/squeue.html.</a></span>
                </p>
            </div>
            <a download="jobid_st_freq_model.png" @click="download(jobid_st_freq_model)" class="link text-primary">Download
                frequency view</a>
            <img :src="jobid_st_freq_model" style="width:100%; margin-top: 10px;" alt="">

            <!-- <hr class="m-5 col-xs-12"> -->
            <a download="jobid_st_pref_model.png" @click="download(jobid_st_pref_model)" class="link text-primary">Download
                performance view</a>
            <img :src="jobid_st_pref_model" style="width:100%; margin-top: 10px;" alt="">
        </div>
    </div>
</template>
  
<script type="text/javascript">
import LoggingFormModal from "./Modals/LoggingFormModal.vue";
import { mapActions } from "pinia";
import { discoverModelQuery } from "../../stores/APIs";
import { slurmLogQueries } from "../../stores/APIs";
import { mapWritableState } from "pinia";

export default {
    name: "JOBID_ST_processmining",
    components: { LoggingFormModal },

    methods: {
        download(url) {
            window.location.href = url;
        },
        async discover_model() {
            this.getJobidSTModel("");
        },
        ...mapActions(discoverModelQuery, ["getJobidSTModel"]),
    },
    computed: {
        ...mapWritableState(discoverModelQuery, [
            "jobid_st_freq_model",
            "jobid_st_pref_model",
            "jobid_st_error",
            "jobid_st_loading"
        ])
    },
    beforeMount() {
        this.error = ""
    },
    mounted() {
        this.discover_model();
    },
};
</script>
  