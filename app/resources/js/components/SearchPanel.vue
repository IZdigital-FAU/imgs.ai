<template>
    <div>
        <b-form-group
        label-cols-lg="3"
        label="Search parameters"
        label-size="lg"
        label-class="font-weight-bold pt-0"
        class="mb-0"
        >

            <b-form-group
                label="Data:"
                label-for="data"
                label-cols-sm="3"
                label-align-sm="right"
            >
                <b-form-select id="data" :options="datasets" v-model="selectedData"></b-form-select>
            </b-form-group>

            <b-form-group
                label="Embedders:"
                label-for="embedders"
                label-cols-sm="3"
                label-align-sm="right"
            >
                <b-form-select id="embedders" :options="embedders" v-model="selectedEmbedder"></b-form-select>
            </b-form-group>

            <b-form-group
                label="Ordering:"
                label-for="ordering"
                label-cols-sm="3"
                label-align-sm="right"
            >
                <b-form-select id="ordering" :options="orderings" v-model="selectedOrdering"></b-form-select>
            </b-form-group>

            <b-form-group
                label="Distance:"
                label-for="distance"
                label-cols-sm="3"
                label-align-sm="right"
            >
                <b-form-select id="distance" :options="distances" v-model="selectedDistance"></b-form-select>
            </b-form-group>

        </b-form-group>
    </div>
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
            {value: '', text: 'Met'},
            {value: '', text: 'CelebA'},
            {value: '', text: 'MoMA'},
            {value: '', text: 'Harvard'},
            {value: '', text: 'Rezeption'},
            {value: '', text: 'Annunciations'},
            {value: '', text: 'Rijksmuseum'},
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
}
</script>