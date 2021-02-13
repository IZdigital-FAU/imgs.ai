<template>
    <div>
        <Navbar></Navbar>

        <Sidebar></Sidebar>

        <Interface></Interface>

    </div>
</template>

<script>
import Interface from './components/Interface.vue'
import Navbar from './components/Navbar.vue'
import Sidebar from './components/Sidebar.vue'

export default {
    name: 'App',
    components: {Navbar, Sidebar, Interface},

}
</script>