<template>
    <b-jumbotron :header="model.name">
                
                <b-table hover :busy="loading"
                    :items="imgs"
                    :fields="fields"
                    selectable
                    select-mode="multi"
                    @row-selected="onRowSelected"
                    :tbody-transition-props="transProps">

                    <template #cell(url)="{ item, rowSelected }">
                        <template v-if="rowSelected">
                            <span aria-hidden="true">✅</span> {{item.url}}
                            <span class="sr-only">Selected</span>
                        </template>
                        <template v-else>
                            <span aria-hidden="true">&nbsp;</span> {{item.url}}
                            <span class="sr-only">Not selected</span>
                        </template>
                    </template>

                    <template #cell(actions)="row">
                        <b-button variant="outline-info" size="sm" @click="row.toggleDetails" class="mr-2">
                            <b-icon :icon="row.detailsShowing ? 'x-circle' : 'search'"></b-icon>
                        </b-button>

                        <b-button variant="outline-warning" size="sm" @click="" class="mr-2">
                            <b-icon icon="lightning-fill"></b-icon>
                        </b-button>

                        <b-button variant="outline-danger" size="sm" class="mr-2" @click="delete(row.item)">
                            <b-icon icon="trash-fill"></b-icon>
                        </b-button>
                    </template>

                    <template #row-details="row">
                        <b-img :src="row.item.url" fluid center></b-img>
                    </template>

                </b-table>

    </b-jumbotron>
</template>

<script>
import axios from 'axios'

export default {
    name: 'ProjectShow',

    data() {
        return {
            model: {},
            imgs: [],

            fields: [
                {key: 'url', label: 'src'},
                {key: 'actions', label: 'actions'}
            ],

            loading: true,

            selected: [],

            transProps: {
                // Transition name
                name: 'flip-list'
            },

            csrf: document.querySelector('#csrf').value
        }
    },

    activated() {
        this.model = this.$route.params

        axios.get(`/api/project/${this.model.id}`).then(resp => {
            let data = resp.data.data

            data.forEach((img, i) => {
                if (!img.is_stored) data[i]._rowVariant = 'danger'
            })

            this.imgs = data;

            this.model.name = resp.data.name
            this.loading = false;
        })

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
    }
}
</script>

<style scoped>
table .flip-list-move {
    transition: transform 1s;
}
</style>