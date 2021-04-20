<template>
    <b-sidebar id="sidebar-1" no-header shadow
        backdrop backdrop-variant="dark">
        
        <b-card no-body>
            <template #header>
                <h4 class="mb-0"><b-link :to="{name: 'projects.index'}">My projects</b-link></h4>
            </template>

            <b-list-group flush>
                <b-list-group-item v-for="project in projects" v-bind:key="project.name" class="d-flex justify-content-between align-items-center">
                    {{project.name}}
                    <b-badge variant="primary" pill>{{project.nimgs}}</b-badge>
                </b-list-group-item>
            </b-list-group>
        </b-card>
    </b-sidebar>
</template>

<script>
import axios from 'axios'

export default {
    name: 'Sidebar',
    data: () => ({
        projects: []
    }),

    created() {
        axios.get('api/projects').then(response => {
            this.projects = response.data
            this.loading = false;
        })
    }
}
</script>