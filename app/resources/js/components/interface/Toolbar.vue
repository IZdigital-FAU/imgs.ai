<template>

    <b-btn-toolbar class="toolbar">
        <b-form-select v-model="query.project" :options="metadata.projects" @change="update" class="dataSelect mr-2"></b-form-select>

        <b-btn-group>
            <!-- <b-dd text="data">
                <b-dd-item v-for="project in metadata.projects" :key="project" v-model="query.project" @change="update">{{project}}</b-dd-item>
            </b-dd> -->

            <b-dd text="more settings ⚙️">
                <b-dd-form>
                    <b-form-group
                        label="Embedders:"
                        label-for="embedders"
                        size="sm"
                        class="settings"
                    >
                        <b-form-select id="embedders" :options="getOptions(embedders)" v-model="query.embedder" @change="update"></b-form-select>
                    </b-form-group>

                    <b-form-group
                        label="Sort by:"
                        label-for="sort"
                        size="sm"
                    >
                        <b-form-select id="sort" :options="getOptions(metadata.orderings)" v-model="query.mode" @change="update"></b-form-select>
                    </b-form-group>

                    <b-form-group
                        label="Distance:"
                        label-for="distance"
                        size="sm"
                    >
                        <b-form-select id="distance" :options="getOptions(metadata.distance_metrics)" v-model="query.metric" @change="update"></b-form-select>
                    </b-form-group>
                </b-dd-form>
            </b-dd>
        </b-btn-group>

        <b-btn-group v-if="this.selected_imgs.length > 0" class="ml-2">
            <b-btn variant="success" @click="makePositive()"><b-icon icon="plus-circle"></b-icon> Positive</b-btn>
            <b-btn variant="danger" @click="makeNegative()"><b-icon icon="dash-circle"></b-icon> Negative</b-btn>
        </b-btn-group>

        <b-btn-group class="ml-2" v-if="this.positiveImages.length > 0 || this.negativeImages.length > 0">
            <b-btn variant="danger" @click="remove()" v-if="this.selected_query_imgs.length > 0">Remove</b-btn>
            <b-btn variant="info" @click="clear()">Clear</b-btn>
        </b-btn-group>

        <b-btn variant="info" class="ml-2" v-if="eop" @click="loadMoreImgs()"><b-icon icon="arrow-clockwise"></b-icon> Load more imgs</b-btn>

    </b-btn-toolbar>

</template>

<script>
import axios from 'axios'

export default {
    name: 'Toolbar',

    props: {
        selected_imgs: Array,
        selected_query_imgs: Array,
        embedders: Array,
        negativeImages: Array,
        positiveImages: Array,
        query: Object
    },

    data : () => ({
        metadata: {},
        eop: false
    }),

    mounted () {
        window.onscroll = () => {
            this.eop = window.pageYOffset / (document.documentElement.offsetHeight - window.innerHeight) >= .9;
        }
    },

    async activated() {
        await axios.get('api/metadata').then(response => {
            this.metadata = response.data;
        })
    },

    computed: {
        // query() {
        //     return this.$parent.querySelection
        // },

        // selected_imgs() {
        //     return this.$parent.querySelection;
        // },

        // embedders() {
        //     return this.$parent.embedders
        // }
    },

    methods: {
        makePositive() {
            this.$emit('makePositive');
        },

        makeNegative() {
            this.$emit('makeNegative');
        },

        clear() {
            this.$emit('clear');
        },

        remove() {
            this.$emit('remove');
        },

        update() {
            this.$emit('update');
        },

        getOptions(arr) {
            return arr.map(name => ({text: name, value: name}))
        },

        loadMoreImgs() {
            this.query.n *= 2
            this.update()
        }
    }
}
</script>

<style scoped>
    .toolbar {
        position: fixed;
        top: 90vh;
        left: 30vw;
    }

    .settings {
        min-width: 15vw;
    }

    .dataSelect {
        width: 20vw;
    }
</style>