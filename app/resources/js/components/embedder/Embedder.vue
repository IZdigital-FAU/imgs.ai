<template>
    <b-jumbotron header="Embedder" lead="Vectorize your images">
        <b-form @submit="post">
            <b-row>
                <b-col>
                    <b-form-group
                        id="name"
                        label="Collection name:"
                        label-for="name"
                        description="Give your image collection a suggestive name"
                    >
                        <b-form-input v-model="model.name" placeholder="my_image_collection" required id="name"></b-form-input>
                    </b-form-group>
                </b-col>
                <b-col>
                    <b-form-group
                        id="file"
                        label="Upload .csv:"
                        label-for="fileInput"
                        description="Upload image collection">
                        
                        <b-form-file id="fileInput" required
                            v-model="model.file"
                            :state="Boolean(model.file)"
                            placeholder="Choose a file or drop it here..."
                            drop-placeholder="Drop file here..."
                            v-b-tooltip.hover title="csv or line separated image URLs"
                        ></b-form-file>
                    </b-form-group>
                </b-col>
            </b-row>

            <b-list-group>
                
                <b-list-group-item v-for="embedder in embedders">
                    <b-form-checkbox v-model="embedder.active" switch>{{embedder.name}}</b-form-checkbox>
                    <b-collapse :visible="embedder.active" :id="embedder.name">
                        <b-row>
                            <b-col>
                                <b-card>
                                    <b-input-group :prepend="param" v-for="(value, param) in embedder.params">
                                        <b-form-input :id="param" :type="embedder.params[param].input_type"
                                                    :min="embedder.params[param].meta.minVal" :max="embedder.params[param].meta.maxVal" :step="embedder.params[param].meta.step"
                                                    v-model="embedder.params[param].value"></b-form-input>
                                        <b-input-group-append is-text class="text-monospace">{{ embedder.params[param].value }}</b-input-group-append>
                                    </b-input-group>
                                </b-card>
                            </b-col>
                            <b-col>
                                <b-button variant="outline-success" v-if="!embedder.reducer.active" @click="addReducer(embedder)">
                                    <b-icon icon="plus-circle"></b-icon> Add dimensionality reduction
                                </b-button>

                                <div v-else>
                                    <b-card>
                                        <b-input-group prepend="Reducer">
                                            <b-form-select v-model="embedder.reducer.name" :options="reducerOptions">
                                                <template #first><b-form-select-option :value="null" disabled>-- Please select a reducer --</b-form-select-option></template>
                                            </b-form-select>
                                            
                                            <b-input-group :prepend="param" v-for="(value, param) in embedder.reducer.params">
                                                <b-form-input :id="param" :type="embedder.reducer.params[param].input_type"
                                                            :min="embedder.reducer.params[param].meta.minVal" :max="embedder.reducer.params[param].meta.maxVal" :step="embedder.reducer.params[param].meta.step"
                                                            v-model="embedder.reducer.params[param].value"></b-form-input>
                                                <b-input-group-append is-text class="text-monospace">{{ embedder.reducer.params[param].value }}</b-input-group-append>
                                            </b-input-group>
                                        </b-input-group>
                                    </b-card>

                                    <b-button variant="outline-danger" @click="removeReducer(embedder)">
                                        <b-icon icon="x-circle"></b-icon> Remove dimensionality reduction
                                    </b-button>
                                </div>
                            </b-col>
                        </b-row>
                    </b-collapse>
                </b-list-group-item>

            </b-list-group>

            <b-button type="submit" variant="outline-primary">Embed</b-button>
        </b-form>
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
            },
            reducerOptions: [
                {text: 'PCA', value: 'pca'},
                {text: 'TSNE', value: 'tsne'}
            ],
            progress: []
        }
    },

    async created() {
        await axios.get('api/embedders').then(response => {
            this.embedders = response.data.data
        })

        var evtSource = new EventSource('/api/progress')

        evtSource.onmessage = function(e) {
            this.progress.push(e.data)
        }
    },

    computed: {
        selectedEmbedders() {
            let result = this.embedders.filter(e => e.active)

            result = result.map(embedder => {
                let embedderParams = {}
                let reducerParams = {}
                
                for (const param in embedder.params){
                    embedderParams[param] = embedder.params[param].value
                }

                for (const param in embedder.reducer.params){
                    reducerParams[param] = embedder.reducer.params[param].value
                }

                return {name: embedder.name, params: embedderParams,
                        reducer: embedder.reducer.active ? {name: embedder.reducer.name, params: reducerParams} : null}
            })

            console.log('Result', result)

            return result
        }
    },

    methods: {
        post(event) {
            event.preventDefault()

            console.log('File', this.model.file)
            let data = new FormData()
            data.append('name', this.model.name)
            data.append('file', this.model.file)
            data.append('embedders', JSON.stringify(this.selectedEmbedders))

            axios.post('api/embedders', data)
        },

        addReducer: embedder => embedder.reducer.active = true,
        removeReducer: embedder => embedder.reducer.active = false
    }
}
</script>