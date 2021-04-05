<template>
    <div>
        <b-form-group
            label="Data:"
            label-for="data"
            label-cols-sm="3"
            label-align-sm="right"
        >
            <b-form-select id="data" :options="datasets" v-model="query.model"></b-form-select>
        </b-form-group>

        <b-form-group
            label="Embedders:"
            label-for="embedders"
            label-cols-sm="3"
            label-align-sm="right"
        >
            <b-form-select id="embedders" :options="query.emb_types" v-model="query.emb_type" @change="update"></b-form-select>
        </b-form-group>

        <b-form-group
            label="Ordering:"
            label-for="ordering"
            label-cols-sm="3"
            label-align-sm="right"
        >
            <b-form-select id="ordering" :options="orderings" v-model="query.mode" @change="update"></b-form-select>
        </b-form-group>

        <b-form-group
            label="Distance:"
            label-for="distance"
            label-cols-sm="3"
            label-align-sm="right"
        >
            <b-form-select id="distance" :options="query.distance_metrics" v-model="query.metric" @change="update"></b-form-select>
        </b-form-group>

        <b-form-group
            label="#imgs:"
            label-for="nImages"
            label-cols-sm="3"
            label-align-sm="right">

            <b-input-group>
                <b-form-input id="nImages" type="range" v-model="query.n" @change="update"></b-form-input>
                <b-input-group-append is-text class="text-monospace">
                    {{ query.n }}
                </b-input-group-append>
            </b-input-group>
        </b-form-group>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'SearchPanel',

    data : () => ({
        selectedData: '',
        selectedEmbedder: 'vgg19',
        selectedOrdering: 'rank',
        selectedDistance: 'manhattan',

        datasets: [],
        orderings: [
            {value: 'ranking', text: 'Ranking'},
            {value: 'centroid', text: 'Centroid'}
        ],
    }),

    async created() {
        await axios.get('api/datasets').then(response => {
            this.datasets = response.data.map(name => ({value: name, text: name}))
        })
    },

    computed: {
        query() {
            return this.$parent.querySelection
        },
        positiveImages() {
            return this.$parent.positiveImages
        },
        negativeImages() {
            return this.$parent.negativeImages
        }
    },

    methods: {
        update() {
            this.$emit('update')
        }
    }
}
</script>