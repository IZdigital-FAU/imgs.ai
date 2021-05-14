<template>
    <b-jumbotron :header="model.name">
        <b-row>
            <b-col>
                <Table
                    :loading="loading"
                    :items="imgs"
                    :fields="fields"
                    selectable
                    select-mode="multi"

                    :pagination="pagination"
                    @getPage="getPage"

                    @onRowSelected="onRowSelected"
                    :tbody-transition-props="transProps">

                    <template #cell(features)="row">
                        <b-badge v-for="label in row.item.features" class="mr-1">{{label}}</b-badge>
                    </template>

                    <template #cell(actions)="row">
                        <b-button variant="outline-info" size="sm" @click="row.toggleDetails" class="mr-2">
                            <b-icon :icon="row.detailsShowing ? 'chevron-up' : 'search'"></b-icon>
                        </b-button>

                        <b-button variant="outline-warning" size="sm" @click="" class="mr-2">
                            <b-icon icon="lightning-fill"></b-icon>
                        </b-button>

                        <b-button variant="outline-danger" size="sm" class="mr-2" @click="delete(row.item)">
                            <b-icon icon="trash-fill"></b-icon>
                        </b-button>
                    </template>

                    <template #row-details="row">
                        <b-img :src="getImg(row.item.name)" width="300" fluid center></b-img>
                    </template>
                </Table>

            </b-col>
            <b-col>
                <Embedder :id="model.id" :total="pagination.total"></Embedder>
            </b-col>
        </b-row>
    </b-jumbotron>
</template>

<script>
import axios from 'axios'

import Embedder from '../embedder/Embedder.vue'
import Table from '../layout/Table.vue'

export default {
    name: 'ProjectShow',
    components: {Embedder, Table},

    data() {
        return {
            model: {},
            imgs: [],

            fields: [
                {key: 'name', sortable: true},
                {key: 'features', sortable: true},
                {key: 'actions', label: 'actions'}
            ],

            loading: true,

            selected: [],

            transProps: {
                // Transition name
                name: 'flip-list'
            },

            pagination: {
                currentPage: 1,
                total: 0,
                per_page: 0
            },

            csrf: document.querySelector('#csrf').value
        }
    },

    activated() {
        this.model = this.$route.params

        this.getPage({}, 1)

    },

    deactivated() {
        this.imgs = []
    },

    methods: {
        post() {
        },

        delete(item) {
            axios.delete(item.url)
        },
        onRowSelected(items) {
            this.selected = items
        },

        getPage(event, page) {
            axios.get(`/api/${this.model.id}`, { params: { page: page } }).then(resp => {
                let data = resp.data.data

                this.imgs = data;

                this.pagination.total = resp.data.total
                this.pagination.per_page = resp.data.per_page
                this.model.name = resp.data.name
                this.loading = false;
            })
        },

        getImg(name) {
            return `/api/${this.model.id}/${name}`
        }
    }
}
</script>


<style scoped>
table .flip-list-move {
    transition: transform 1s;
}
</style>