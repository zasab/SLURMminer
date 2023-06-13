<template>
  <div class="container" style="justify-content: center; align-items: center;">
    <div v-if="error.length > 0" class="p-2 d-flex justify-content-center">
      <p style="color: crimson;">{{ error }}</p>
    </div>
    <div v-if="get_log_loading" class="p-4 d-flex justify-content-center">
      <h3 class="text-warning">Loading...</h3>
    </div>
    <div v-if="discovery_error.length > 0" class="p-2 d-flex justify-content-center">
      <p style="color: crimson;">{{ discovery_error }}</p>
    </div>
    <div class="col d-flex" style="justify-content:space-between">
      <button class="btn btn-dark btn-outline-dark pt-0 pb-0" type="button" @click="download_normal_log">
        <div class="d-flex flex-row justify-content-center align-items-center">
          <i class="bi bi-download text-white mr-2"></i>
          <p class="text-white pt-3">Generate and Download Normal Log</p>
        </div>
      </button>
      <button class="btn btn-dark btn-outline-dark pt-0 pb-0" type="button" @click="download_ocel_log">
        <div class="d-flex flex-row justify-content-center align-items-center">
          <i class="bi bi-download text-white mr-2"></i>
          <p class="text-white pt-3">Generate and Download OCEL Log</p>
        </div>
      </button>
    </div>
    <div class="mt-3 pt-2 border-top">
      <div>
        <h3>Project based discovery</h3>
        <div class="dropdown">
          <button class="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton"
            data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            List of the projects
          </button>
          <div class="dropdown-menu" aria-labelledby="dropdownMenuButton" id="topicsDropDown">
            <a class="dropdown-item">
              <p v-if="this.topic_list.length == 0" class="text-warning">Loading...</p>
            </a>
          </div>
        </div>
        <div class="mt-3 mb-3 w-80 p-3 d-flex flex-row border justify-content-between">
          <div>
            <h5 class="text-info">Selected Topic: </h5>
            <p id="selectedTopic">no topic is selected.</p>
          </div>
          <div>
            <h5 class="text-info">Noise Threshold: </h5>
            <input type="number" placeholder="0" step="0.1" min="0" max="1" name="noise_threshold" id="noise_threshold"
              value="0">
          </div>
        </div>
        <div class="mb-3 d-flex justify-content-end">
          <button class="btn btn-primary" type="button" @click="discover_model_based_on_project">
            Discover model based on <span class="fw-bold text-danger">project</span>
          </button>
        </div>
      </div>
      <div>
        <h3>Account based discovery</h3>
        <div class="col-sm-12 col-md-12 col-lg-12 col-xl-12">
          <div class="mb-3">
            <label for="account" class="py-2 form-label-custom text-success text-center">Please note that you need to
              generate the normal event log first, then discover a model for an account or a list of account (separated
              by
              ',')!</label>
            <div class="form-inputs">
              <i class="bi bi-person"></i>
              <input type="text" placeholder="" v-model="account" />
            </div>
          </div>
        </div>
        <button class="btn btn-light btn-outline-success" style="margin-bottom: 5px; margin-top: 5px;" type="button"
          @click="get_accounts_list">
          Show Accounts List
        </button>
        <div class="column p-2">
          <div class="card m-auto" style="width:90%;">
            <div class="card-body" v-if="unique_accounts.length > 0">
              <div>
                <p>To refresh, simply click on the "Show Accounts List" button located above.</p>
                <input type="text" placeholder="Search.." name="search" id="search_account">
                <button type="button" @click="search('account')">search</button>
                <button type="button" class="close" aria-label="Close" @click="close('account')">
                  <span aria-hidden="true">&times;</span>
                </button>
              </div>
              <p class="mt-3 text-secondary">
              <h6 class="text-dark">Accounts List: </h6>{{ unique_accounts }}</p>
              <h6>Please concat your chosen account with , between them e.g. account1, account2 and then press "discover
                model" button.</h6>
              <h6 style="color: brown;">Please be aware that if you come across a group of accounts here that appear smaller 
                than those displayed in the "Number of Submitted Jobs per Account" chart in the BI tab, it is because we are filtering 
                based on the condition that the account should have at least a "Running" status in the log.</h6>
            </div>
          </div>
        </div>
        <div class="mb-3 d-flex justify-content-end">
          <button class="btn btn-primary" type="button" @click="discover_model_based_on_account">
            Discover model based on <span class="fw-bold text-danger">account</span>
          </button>
        </div>
      </div>
      <div>
        <p v-if="recorded_users.length > 0" class="text-success">{{ recorded_users }}
        </p>
        <div v-if="loading" class="p-4 d-flex justify-content-center">
          <h3 class="text-warning">Loading...</h3>
        </div>
        <div v-if="error.length == 0 && cc_model.length > 0" class="p-4 d-flex flex-column justify-content-center">
          <h4 class="text-info">Dependency Study (connected components)</h4>
          <a download="cc_model.png" @click="download(cc_model)" class="link text-primary">Download</a>
          <p>Average Trace Fitness: {{ cc_fitness }}</p>
          <img :src="cc_model" style="width:100%; margin-top: 10px;" alt="">
          <hr class="m-5 col-xs-12">
          <h4 class="text-info">Account and Project Group Study</h4>
          <a download="ag_model.png" @click="download(ag_model)" class="link text-primary">Download</a>
          <p>Average Trace Fitness: {{ ag_fitness }}</p>
          <img :src="ag_model" style="width:100%; margin-top: 10px;" alt="">
        </div>
      </div>
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
  name: "ProcessMining",
  components: { LoggingFormModal },

  methods: {
    sleep(time) {
      return new Promise((resolve) => setTimeout(resolve, time));
    },

    search(search_type) {
      var searchInput = document.getElementById("search_account");
      var searchValue = searchInput.value;
      var acc_list = []
      if (search_type == "account") {
        this.unique_accounts.find((str) => {
          if (str.includes(searchValue)) {
            acc_list.push(str)
          }
        })
        this.unique_accounts = acc_list
      }
    },
    close(close_type) {
      if (close_type == "account") {
        this.unique_accounts = ""
      }
    },
    download(url) {
      window.location.href = url;
    },

    async discover_model_based_on_project() {
      this.error = ""
      this.discovery_error = ""
      var selected_topic = document.getElementById("selectedTopic").innerHTML;
      var selected_noise_threshold = document.getElementById("noise_threshold").value;
      this.unique_accounts = ""
      this.cc_model = ""
      this.ag_model = ""
      this.getModel(selected_topic, selected_noise_threshold, true);
    },
    ...mapActions(discoverModelQuery, ["getModel"]),

    async discover_model_based_on_account() {
      this.error = ""
      this.discovery_error = ""
      var selected_topic = document.getElementById("selectedTopic").innerHTML;
      var selected_noise_threshold = document.getElementById("noise_threshold").value;
      this.unique_accounts = ""
      this.cc_model = ""
      this.ag_model = ""
      this.getModel(selected_topic, selected_noise_threshold, false);
    },
    ...mapActions(discoverModelQuery, ["getModel"]),

    async add_option(select_id, option_text) {
      this.error = ""
      this.discovery_error = ""
      var select = document.getElementById(select_id);
      var newOption = document.createElement("option");
      var newOptionVal = document.createTextNode(option_text);
      newOption.appendChild(newOptionVal)
      select.appendChild(newOption);
    },

    async get_accounts_list() {
      this.error = ""
      this.discovery_error = ""
      this.getSlurmLogColumnValues()
      while (this.unique_accounts.length == 0) {
        await this.sleep(1);
      }
    },
    ...mapActions(slurmLogQueries, ["getSlurmLogColumnValues"]),

    async get_topic_list() {
      this.error = ""
      this.discovery_error = ""
      this.getProjectIDTopicList()
      while (this.topic_list.length == 0) {
        await this.sleep(1);
      }
    },
    ...mapActions(slurmLogQueries, ["getProjectIDTopicList"]),

    async download_normal_log() {
      this.error = ""
      this.discovery_error = ""
      try {
        this.normal_log_content = ""
        this.getNormalEventLog("");
        while (this.normal_log_content.length == 0) {
          await this.sleep(1);
        }
        var a = document.createElement('a');
        a.href = this.normal_log_content;
        let random_name = (Math.random() + 1).toString(36).substring(7);
        a.download = random_name + '.csv';
        document.body.appendChild(a);
        a.click();
      } catch (error) {
        console.log("error+: ", error)
      }
    },
    ...mapActions(slurmLogQueries, ["getNormalEventLog"]),

    async download_ocel_log() {
      this.error = ""
      this.discovery_error = ""
      try {
        this.ocel_log_content = ""
        this.getOCELLog("");
        while (this.ocel_log_content.length == 0) {
          await this.sleep(1);
        }
        var ocel_a = document.createElement('a');
        ocel_a.href = this.ocel_log_content;
        let random_name = (Math.random() + 1).toString(36).substring(7);
        ocel_a.download = random_name + '.jsonocel';
        document.body.appendChild(ocel_a);
        ocel_a.click();
      } catch (error) {
        console.log("error+: ", error)
      }
    },
    ...mapActions(slurmLogQueries, ["getOCELLog"]),

    async add_accounts() {
      this.error = ""
      this.discovery_error = ""
      while (this.topic_list.length == 0) {
        await this.sleep(1);
      }
      for (var u_topic in this.topic_list) {
        const new_node = document.createElement("button");
        new_node.innerText = this.topic_list[u_topic];
        new_node.type = "button";
        new_node.id = this.topic_list[u_topic];
        new_node.onclick = function () {
          var element = document.getElementById("selectedTopic");
          element.innerHTML = this.id;
        };
        new_node.className = 'dropdown-item'
        document.getElementById("topicsDropDown").appendChild(new_node);
      }
    }
  },
  computed: {
    ...mapWritableState(discoverModelQuery, [
      "account",
      "cc_model",
      "cc_fitness",
      "recorded_users",
      "ag_model",
      "ag_fitness",
      "discovery_error",
      "loading"
    ]),
    ...mapWritableState(slurmLogQueries, [
      'unique_accounts',
      "topic_list",
      "project_IDs",
      "all_topic_list",
      "normal_log_content",
      "ocel_log_content",
      "get_log_loading",
      "error"
    ])
  },
  beforeMount() {
    this.error = ""
  },
  mounted() {
    this.get_topic_list()
    this.add_accounts()
  },
};
</script>
