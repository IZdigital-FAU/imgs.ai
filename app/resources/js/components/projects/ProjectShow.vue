<template>
    <b-jumbotron :header="model.name">
        <b-row>
            <b-col>
                <b-table hover :busy="loading"
                    :items="imgs"
                    :fields="fields"
                    selectable
                    select-mode="multi"
                    @row-selected="onRowSelected"
                    :tbody-transition-props="transProps">

                    <template #cell(name)="{ item, rowSelected }">
                        <template v-if="rowSelected">
                            <span aria-hidden="true">✅</span> {{item.name}}
                            <span class="sr-only">Selected</span>
                        </template>
                        <template v-else>
                            <span aria-hidden="true">&nbsp;</span> {{item.name}}
                            <span class="sr-only">Not selected</span>
                        </template>
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

                </b-table>

                <b-pagination @page-click="getPage" v-model="currentPage"
                            :per-page="per_page" :total-rows="total"
                            first-text="⏮" last-text="⏭"
                            pills align="center">

                    <template #prev-text>
                        <b-icon icon="chevron-left"></b-icon>
                    </template>

                    <template #next-text>
                        <b-icon icon="chevron-right"></b-icon>
                    </template>

                </b-pagination>
            </b-col>
            <b-col>
                <Embedder></Embedder>
            </b-col>
        </b-row>
    </b-jumbotron>
</template>

<script>
import axios from 'axios'

import Embedder from '../embedder/Embedder.vue'

export default {
    name: 'ProjectShow',
    components: {Embedder},

    data() {
        return {
            model: {},
            imgs: [],

            fields: [
                {key: 'name', sortable: true},
                {key: 'actions', label: 'actions'}
            ],

            loading: true,

            selected: [],

            transProps: {
                // Transition name
                name: 'flip-list'
            },

            currentPage: 1,
            total: 0,
            per_page: 0,

            csrf: document.querySelector('#csrf').value
        }
    },

    activated() {
        this.model = this.$route.params

        this.getPage({}, 1)

        console.log('imgs', this.imgs)

    },

    deactivated() {
        this.imgs = []
    },

    methods: {
        post() {
            console.log('hi')
        },

        delete(item) {
            console.log('DELETE', item)
            axios.delete(item.url)
        },
        onRowSelected(items) {
            this.selected = items
        },

        getPage(event, page) {
            axios.get(`/api/project/${this.model.id}`, { params: { page: page } }).then(resp => {
                let data = resp.data.data

                // data.forEach((img, i) => {
                //     if (!img.is_stored) data[i]._rowVariant = 'danger'
                // })

                this.imgs = data;

                this.total = resp.data.total
                this.per_page = resp.data.per_page
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