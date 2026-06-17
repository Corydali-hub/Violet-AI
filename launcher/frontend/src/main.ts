import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import Groups from './views/Groups.vue'
import GroupDetail from './views/GroupDetail.vue'
import Setup from './views/Setup.vue'
import Logs from './views/Logs.vue'
import QrPage from './views/QrPage.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/groups', component: Groups },
  { path: '/groups/:gid', component: GroupDetail },
  { path: '/qr', component: QrPage },
  { path: '/setup', component: Setup },
  { path: '/logs', component: Logs },
]

const router = createRouter({ history: createWebHashHistory(), routes })
const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.mount('#app')
