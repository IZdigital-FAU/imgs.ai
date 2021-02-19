<template>
    <div>
        <Navbar></Navbar>

        <Sidebar></Sidebar>

        <ProjectCreator></ProjectCreator>

    </div>
</template>

<script>
import Navbar from './embedder/ProjectCreator.vue'
import Navbar from './layout/Navbar.vue'
import Sidebar from './layout/Sidebar.vue'

export default {
    name: 'Interface',
    components: {Navbar, Sidebar, ProjectCreator},

}
</script>