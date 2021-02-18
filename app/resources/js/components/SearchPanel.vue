<template>
    <b-row>
        <b-col>
            <b-row>
                <b-col>
                    <b-img class="grid-item-img pos"
                        v-for="img in positiveImages" v-bind:key="img.id"
                        :src="img.url" :ref="img.id"
                        @click="select(img)"></b-img>
                </b-col>
                <b-col>
                    <b-img class="grid-item-img neg"
                        v-for="img in negativeImages" v-bind:key="img.id"
                        :src="img.url" :ref="img.id"
                        @click="select(img)"></b-img>
                </b-col>
            </b-row>

            <b-button-group>
                <b-button variant="outline-danger">Remove</b-button>
                <b-button variant="outline-info" @click="clear()">Clear</b-button>
            </b-button-group>
        </b-col>
        <b-col>
            <b-form-group
                label="Data:"
                label-for="data"
                label-cols-sm="3"
                label-align-sm="right"
            >
                <b-form-select id="data" :options="datasets" v-model="query.data"></b-form-select>
            </b-form-group>

            <b-form-group
                label="Embedders:"
                label-for="embedders"
                label-cols-sm="3"
                label-align-sm="right"
            >
                <b-form-select id="embedders" :options="embedders" v-model="query.embedder" @change="update"></b-form-select>
            </b-form-group>

            <b-form-group
                label="Ordering:"
                label-for="ordering"
                label-cols-sm="3"
                label-align-sm="right"
            >
                <b-form-select id="ordering" :options="orderings" v-model="query.order" @change="update"></b-form-select>
            </b-form-group>

            <b-form-group
                label="Distance:"
                label-for="distance"
                label-cols-sm="3"
                label-align-sm="right"
            >
                <b-form-select id="distance" :options="distances" v-model="query.distance" @change="update"></b-form-select>
            </b-form-group>

            <b-form-group
                label="#imgs:"
                label-for="nImages"
                label-cols-sm="3"
                label-align-sm="right">
                <b-form-input id="nImages" type="range" v-model="query.n" @change="update"></b-form-input>
            </b-form-group>
        </b-col>
    </b-row>
</template>

<script>

export default {
    name: 'SearchPanel',

    data : () => ({
        selectedData: '',
        selectedEmbedder: 'vgg19',
        selectedOrdering: 'rank',
        selectedDistance: 'manhattan',

        datasets: [
            {value: 'met', text: 'Met'},
            {value: 'celeba', text: 'CelebA'},
            {value: 'moma', text: 'MoMA'},
            {value: 'harvard', text: 'Harvard'},
            {value: 'rezeption', text: 'Rezeption'},
            {value: 'annunc', text: 'Annunciations'},
            {value: 'rijks', text: 'Rijksmuseum'},
        ],
        embedders: [
            {value: 'vgg19', text: 'VGG19'},
            {value: 'poses', text: 'Poses'},
            {value: 'raw', text: 'Raw'},
        ],
        orderings: [
            {value: 'rank', text: 'Ranking'},
            {value: 'centroid', text: 'Centroid'}
        ],
        distances: [
            {value: 'manhattan', text: 'Manhattan'},
            {value: 'angular', text: 'Angular'},
            {value: 'euclidean', text: 'Euclidean'}
        ],
    }),

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