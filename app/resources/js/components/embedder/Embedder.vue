<template>
    <b-jumbotron header="Embedder" lead="Vectorize your images">
        
        <b-form-input v-model="model.name" placeholder="collection name"></b-form-input>

        <b-form-file
            v-model="model.file"
            :state="Boolean(model.file)"
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

        <b-button variant="outline-primary" @click="post">Embed</b-button>

    </b-jumbotron>
</template>

<script>
import axios from 'axios'

export default {
    name: 'Embedder',

    data() {
        return {
            embedders: [],
            model: {
                name: '',
                file: null
            }
        }
    },

    async created() {
        await axios.get('api/embedders').then(response => {
            this.embedders = response.data.data
        })
    },

    methods: {
        post() {
            console.log('File', this.model.file)
            let data = new FormData()

            data.append('name', this.model.name)
            data.append('file', this.model.file)
            data.append('embedders', this.embedders.filter(e => e.active))

            axios.post('api/embedders', data)
        }
    }
}
</script>