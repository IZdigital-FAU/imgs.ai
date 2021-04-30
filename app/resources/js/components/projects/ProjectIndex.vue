<template>
    <b-container>
        <b-button variant="outline-success">
            <b-icon icon="plus-square"></b-icon> Create new
        </b-button>

        <Table
            :items="projects"
            :fields="fields"
            :loading="loading"

            :pagination="{}"
            
            @onRowDblClicked="onRowDblClicked">

            <template #cell(nimgs)="project">
                <b-badge variant="primary" pill>{{project.item.nimgs}}</b-badge>
            </template>

            <template #cell(nimgs)="project">
                <b-badge variant="primary" pill>{{project.item.nimgs}}</b-badge>
            </template>

            <template #table-caption>Manage your projects</template>

        </Table>
    </b-container>
</template>

<script>
import axios from 'axios';
import Table from '../layout/Table.vue';

export default {
    name: 'ProjectIndex',
    components: {Table},

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
            loading: true,
            pagination: {}
        }
    },

    created() {
        axios.get('api/projects').then(response => {
            this.projects = response.data
            this.loading = false;
        })
    },

    methods: {
        onRowDblClicked(record, index) {
            console.log('I GOT HERE!')
            this.$router.push({name: 'project.show', params: record})
        }
    }
}
</script>