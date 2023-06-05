import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Index',
      component: () => import('../components/homepageHeader.vue'),
      children: [
        {
          path: '/',
          name: 'Logging',
          component: () => import('../components/Homepage/logging.vue'),
        },
        {
          path: '/process_mining',
          name: 'Processmining',
          component: () => import('../components/Homepage/process_mining.vue'),
        },
        {
          path: '/jobid_st',
          name: 'JOBID_ST_processmining',
          component: () => import('../components/Homepage/JOBID_ST_processmining.vue'),
        },
        {
          path: '/bi',
          name: 'BI',
          component: () => import('../components/BI/bianalysis.vue')
        },
        {
          path: '/bi_dotted_charts',
          name: 'BIdottedcharts',
          component: () => import('../components/BI/bidotted.vue')
        },
      ]
    }
  ],
})

export default router
