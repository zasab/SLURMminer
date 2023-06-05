<template>
  <header
    class="d-flex flex-wrap align-items-center justify-content-center justify-content-md-between mb-4 navbar navbar-light bg-white border-bottom">
    <div class="container">
      <router-link to="/" class="navbar-brand d-flex align-items-center text-decoration-none">
        <img style="width: 40%" src="../assets/logo.png" alt="logo" />
      </router-link>
      <ul class="nav nav-pills">
        <li class="nav-item">
          <router-link to="/" class="nav-link" @click.prevent="setActive('StartLogging')"
            :class="{ active: isActive('StartLogging') }">Logging</router-link>
        </li>
        <li class="nav-item">
          <router-link to="/process_mining" class="nav-link" @click.prevent="setActive('ProcessMining')"
            :class="{ active: isActive('ProcessMining') }">Process Mining</router-link>
        </li>
        <li class="nav-item">
          <router-link to="/jobid_st" class="nav-link" @click.prevent="setActive('JOBID_ST_processmining')"
            :class="{ active: isActive('JOBID_ST_processmining') }">JOBID-STATE process model</router-link>
        </li>
        <li class="nav-item">
          <router-link to="/bi" class="nav-link" @click.prevent="setActive('BIanalysis')"
            :class="{ active: isActive('BIanalysis') }">BI</router-link>
        </li>
        <li class="nav-item">
          <router-link to="/bi_dotted_charts" class="nav-link" @click.prevent="setActive('BIdottedanalysis')"
            :class="{ active: isActive('BIdottedanalysis') }">BI(dotted charts)</router-link>
        </li>
      </ul>
    </div>
  </header>

  <div class="tab-content">
    <router-view></router-view>
  </div>
</template>
<script>
export default {
  name: "StartLogging",
  data() {
    return {
      activeItem: "StartLogging",
    };
  },
  methods: {
    isActive(menuItem) {
      return this.activeItem === menuItem;
    },
    setActive(menuItem) {
      this.activeItem = menuItem;
    },
  },
};
</script>
