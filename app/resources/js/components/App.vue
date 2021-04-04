<template>
    <div>
        <Navbar></Navbar>

        <Sidebar></Sidebar>

        <transition name="fade">
            <router-view></router-view>
        </transition>
    </div>
</template>

<script>
import Navbar from './layout/Navbar.vue'
import Sidebar from './layout/Sidebar.vue'

export default {
    name: 'App',
    components: {Navbar, Sidebar},

}
</script>