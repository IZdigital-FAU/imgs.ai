<template>
    <div>
        <b-form-group
            label="Data:"
            label-for="data"
            label-cols-sm="3"
            label-align-sm="right"
        >
            <b-form-select id="data" :options="metadata.projects" v-model="query.project"></b-form-select>
        </b-form-group>

        <b-form-group
            label="Embedders:"
            label-for="embedders"
            label-cols-sm="3"
            label-align-sm="right"
        >
            <b-form-select id="embedders" :options="metadata.embedders" v-model="query.embedder" @change="update"></b-form-select>
        </b-form-group>

        <b-form-group
            label="Ordering:"
            label-for="ordering"
            label-cols-sm="3"
            label-align-sm="right"
        >
            <b-form-select id="ordering" :options="metadata.orderings" v-model="query.mode" @change="update"></b-form-select>
        </b-form-group>

        <b-form-group
            label="Distance:"
            label-for="distance"
            label-cols-sm="3"
            label-align-sm="right"
        >
            <b-form-select id="distance" :options="metadata.distance_metrics" v-model="query.metric" @change="update"></b-form-select>
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
        metadata: {}
    }),

    async activated() {
        await axios.get('api/metadata').then(response => {
            this.metadata = response.data
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