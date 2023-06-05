<template>
    <div v-if="error.length > 0" class="p-2 d-flex justify-content-center">
        <p style="color: crimson;">{{ error }}</p>
    </div>
    <div class="bg-white" style="border: 1px solid black; padding: 10px">
        <p>
            Batching occurs when a user or account initiates multiple jobs within a limited timeframe. For instance, they
            may launch 500 computations simultaneously using similar or slightly different scripts with varying parameters.
            Analyzing this pattern is valuable, especially when examining the HPC log, as some users heavily utilize
            batching. To identify batching, we can count the number of jobs triggered by an account within a fixed time
            interval (specified in the "Time interval" text field, such as 15 minutes). By setting a threshold, we can
            filter accounts that have submitted more jobs than the specified "Threshold" value within certain intervals. The
            resulting plot will display the number of intervals in which an account has exceeded the threshold, allowing us
            to identify batches on the cluster.<br>

            Ideally, we can further refine the analysis by filtering the event log to include only the events or jobs
            associated with a specific account, such as "default." Visualizing the filtered data as a dotted chart, we can
            identify batches by observing the vertical segments within the chart.
        </p>
    </div>
    <div class="d-flex flex-row justify-content-center" style="justify-content:center;width:95%; align-items: center;">
        <p>Time interval</p>
        <div class="form-inputs">
            <i class="bi bi-clock"></i>
            <input type="text" placeholder="" v-model="time_interval" />
        </div>
        <p>Threshold</p>
        <div class="form-inputs">
            <i class="bi bi-arrow-bar-down"></i>
            <input type="text" placeholder="" v-model="batchs_threshold" />
        </div>
        <button class="btn btn-light btn-outline-success" style="margin-bottom: 5px; margin-top: 5px;" type="button"
            @click="get_account_batches_distribution">
            Batches Bar Chart
        </button>
    </div>
    <div class="d-flex flex-row justify-content-center" style="justify-content:center;width:95%; align-items: center;">
        <div v-if="batches_loading">
            <span class="badge badge-dark badge-pill p-2 text-warning">Loading...</span>
        </div>
    </div>
    <div class="d-flex flex-row justify-content-center" style="justify-content:center; align-items: center;"
        v-if="batches_account.length > 0">
        <div style="width:95%">
            <div class="d-flex flex-row" style="justify-content:space-between;">
                <div class="row p-4" style="width:100%">
                    <div class="card m-auto">
                        <div class="card-body">
                            <div id="accountBatchesPlot"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="d-flex flex-row justify-content-center" style="justify-content:center;width:95%; align-items: center;"
        v-if="batches_account.length > 0">
        <div class="form-inputs">
            <i class="bi bi-person"></i>
            <input type="text" placeholder="" v-model="batchs_account" />
        </div>
        <button class="btn btn-light btn-outline-success" style="margin-bottom: 5px; margin-top: 5px;" type="button"
            @click="get_account_dotted_chart_info">
            Dotted Chart
        </button>
    </div>
    <div class="d-flex flex-row justify-content-center" style="justify-content:center;width:95%; align-items: center;">
        <div v-if="account_dotted_loading">
            <span class="badge badge-dark badge-pill p-2 text-warning">Loading...</span>
        </div>
    </div>
    <div class="d-flex flex-row justify-content-center" style="justify-content:center; align-items: center;">
        <div style="width:95%">
            <div class="d-flex flex-row" style="justify-content:space-between;">
                <div class="row p-4" style="width:100%" v-if="accountdottedinfo.length > 0">
                    <div class="card m-auto">
                        <div class="card-body">
                            <div id="accountdottedchartplot"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { mapActions, mapWritableState } from "pinia";
import { slurmLogQueries } from "../../stores/APIs";
export default {
    name: "BIdottedanalysis",
    methods: {
        sleep(time) {
            return new Promise((resolve) => setTimeout(resolve, time));
        },
        download(url) {
            window.location.href = url;
        },
        set_x_axis(x) {
            this.x_axis = x;
        },
        set_y_axis(y) {
            this.y_axis = y;
        },

        async get_account_dotted_chart_info() {
            this.accountdottedinfo = ""
            this.getAccountDottedChartInfo("")
            while (this.accountdottedinfo.length == 0) {
                await this.sleep(1);
            }
            var accountdottedinfo = JSON.parse(this.accountdottedinfo);

            var trace1 = {
                x: accountdottedinfo['CURRENT_TIMESTAMP'],
                y: accountdottedinfo['JOBID'],
                mode: 'markers',
                type: 'scatter',
                name: accountdottedinfo['ACCOUNT'],
                marker: {
                    color: '#856b7c'
                }
            };

            var data = [trace1];
            var layout = {
                title: 'JobID over Submitted time, colored by duration',
                showlegend: false,
                fixedrange: false,
                xaxis: {
                    title: "time",
                }
            };
            Plotly.plot('accountdottedchartplot', data, layout, { scrollZoom: true });

        },
        ...mapActions(slurmLogQueries, ["getAccountDottedChartInfo"]),

        async get_account_batches_distribution() {
            try {
                this.batches_account = ""
                this.accountdottedinfo = ""
                this.getAccountDidBatches("");
                while (this.batches_account.length == 0) {
                    await this.sleep(1);
                }
                var batches_account = JSON.parse(this.batches_account);

                var plot_dimensions1 = {
                    x: batches_account["ACCOUNTS"],
                    y: batches_account["batches_count"],
                    type: 'bar'
                };
                var plot_data = [plot_dimensions1];
                var layout = {
                    title: 'Number of Time Intervals the Account did Batches more than the Threshold',
                    showlegend: false,
                    fixedrange: false,
                    xaxis: {
                        title: "accounts",
                    },
                    yaxis: {
                        title: "#interval the account appears",
                        type: 'linear',
                    },
                };

                Plotly.plot('accountBatchesPlot', plot_data, layout, { scrollZoom: true });
            } catch (error) {
                console.log("error: ", error)
            }
        },
        ...mapActions(slurmLogQueries, ["getAccountDidBatches"]),
    },
    computed: {
        ...mapWritableState(slurmLogQueries, [
            "error",
            "batches_account",
            "batchs_account",
            "accountdottedinfo",
            "batchs_threshold",
            "time_interval",
            "batches_loading",
            "account_dotted_loading"
        ]),
    },
    beforeMount() {
        this.error = ""
    },
};
</script>