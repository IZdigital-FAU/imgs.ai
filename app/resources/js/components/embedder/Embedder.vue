<template>
    <b-jumbotron header="Embedder" lead="Vectorize your images">
        
        <b-form-file
            v-model="inputFile"
            :state="Boolean(inputFile)"
            placeholder="Choose a file or drop it here..."
            drop-placeholder="Drop file here..."
            v-b-tooltip.hover title="csv or line separated image URLs"
        ></b-form-file>

        <b-list-group>
            <b-list-group-item v-for="embedder in embedders">
                <b-form-checkbox v-model="embedder.active" switch>{{embedder.name}}</b-form-checkbox>
                <b-collapse :visible="embedder.active" :id="embedder.name">
                    <b-card>
                        <b-input-group :prepend="param" v-for="(value, param) in embedder.params">
                            <b-form-input :id="param" type="range" v-model="embedder.params[param]"></b-form-input>
                            <b-input-group-append is-text class="text-monospace">{{ value }}</b-input-group-append>
                        </b-input-group>
                    </b-card>
                </b-collapse>
            </b-list-group-item>
        </b-list-group>

        <b-button variant="outline-primary">Embed</b-button>

    </b-jumbotron>
</template>

<script>
export default {
    name: 'Embedder',

    data() {
        return {
            inputFile: null,
            embedders: [
                {name: 'raw', params: {resolution: 48}, active: false},
                {name: 'vgg19', params: {}, active: false},
                {name: 'face', params: {dim: 128, numPeople: 2}, active: false},
                {name: 'poses', params: {minConf: .9, numPeople: 2}, active: false},
            ]
        }
    },

    methods: {
        post() {
            axios.post()
        }
    }

}
</script>