import Vue from 'vue';
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

import '../css/css.css'

import {routes} from './router'
import Router from 'vue-router'
Vue.use(Router)

const router = new Router({
    mode: 'history',
    routes
})

import App from './components/App.vue'

// Make BootstrapVue available throughout your project
Vue.use(BootstrapVue)
// Optionally install the BootstrapVue icon components plugin
Vue.use(IconsPlugin)


new Vue({
    el: '#app',
    render: h => h(App),
    router
})