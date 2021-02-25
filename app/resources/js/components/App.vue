<template>
    <div>
        <Navbar></Navbar>

        <Sidebar></Sidebar>

        <Main></Main>

        <transition name="slide">
            <router-view></router-view>
        </transition>
    </div>
</template>

<script>
import Main from './Main.vue'
import Navbar from './layout/Navbar.vue'
import Sidebar from './layout/Sidebar.vue'

export default {
    name: 'App',
    components: {Navbar, Sidebar, Main},

}
</script>