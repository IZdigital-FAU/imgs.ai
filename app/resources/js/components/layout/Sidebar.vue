<template>
    <b-sidebar id="sidebar-1" title="Saved projects" shadow>
        <b-list-group>
            <b-list-group-item v-for="project in projects">{{project.name}}</b-list-group-item>
        </b-list-group>
    </b-sidebar>
</template>

<script>
export default {
    name: 'Sidebar',
    data: () => ({
        projects: [
            {name: 'Project1'},
            {name: 'Project2'},
            {name: 'Project3'}
        ]
    })
}
</script>