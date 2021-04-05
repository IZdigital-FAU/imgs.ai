<template>
    <div>
        <Navbar></Navbar>

        <Sidebar></Sidebar>

        <keep-alive>
            <router-view></router-view>
        </keep-alive>
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