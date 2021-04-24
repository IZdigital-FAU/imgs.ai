<template>
    <b-container>
        <b-button variant="outline-success">
            <b-icon icon="plus-square"></b-icon> Create new
        </b-button>

        <b-table
            :items="projects"
            :fields="fields"
            :busy="loading"

            @row-dblclicked="showProject"

            hover>

            <template #table-caption>Manage your projects</template>

            <template #table-busy>
                <div class="text-center text-danger my-2">
                    <b-spinner class="align-middle"></b-spinner>
                    <strong>Loading...</strong>
                </div>
            </template>

            <template #cell(nimgs)="project">
                <b-badge variant="primary" pill>{{project.item.nimgs}}</b-badge>
            </template>

        </b-table>
    </b-container>
</template>

<script>
import axios from 'axios';

export default {
    name: 'ProjectIndex',

    data() {
        return {
            projects: [],
            fields: [
                {
                    key: 'name',
                    sortable: true,
                    // variant: 'primary'
                },
                {
                    key: 'nimgs',
                    label: '#imgs',
                    sortable: true
                },
                {
                    key: 'category',
                    sortable: true
                }
            ],
            loading: true
        }
    },

    created() {
        axios.get('api/projects').then(response => {
            this.projects = response.data
            this.loading = false;
        })
    },

    methods: {
        showProject(record, index) {
            this.$router.push({name: 'project.show', params: record})
        }
    }
}
</script>