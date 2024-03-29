<template>
    <b-container class="embedder">

        <h4>
            <b-badge v-for="embedder in embedders" :key="embedder.name"
                    @dragstart="dragStart"
                    @drag="dragging"
                    :draggable="true"
                    :id="embedder.name"
                    variant="primary" class="mr-2">{{embedder.name}}
            </b-badge>
        </h4>

        <b-overlay :show="working" rounded no-center>
            <b-card no-body @drop="drop" @dragover="allowDrop">
                <b-tabs card>
                    <!-- Render Tabs, supply a unique `key` to each tab -->
                    <b-tab v-for="emb in embedderSelection" :key="emb.name" :title="emb.name" :active="isLast(emb.name)">

                        <template #title>
                            {{emb.name}} <b-icon icon="x" class="ml-2" @click="closeTab(emb.name)"></b-icon>
                        </template>

                        <b-input-group :prepend="param" v-for="(value, param) in emb.params" :key="param.name" class="mb-1">
                            <b-form-input :id="param" :type="emb.params[param].input_type"
                                        :min="emb.params[param].meta.minVal" :max="emb.params[param].meta.maxVal" :step="emb.params[param].meta.step"
                                        v-model="emb.params[param].value">
                            </b-form-input>
                            <b-input-group-append is-text class="text-monospace">{{ emb.params[param].value }}</b-input-group-append>
                        </b-input-group>

                        <b-card no-body class="mt-5">
                            <b-tabs pills card vertical>
                                <b-tab v-for="reducer in reducers" :key="reducer.name" :title="reducer.name" :active="emb.reducer.name === reducer.name">
                                    <b-card-text>
                                        <b-input-group :prepend="param" v-for="(value, param) in reducer.params" :key="param.name">
                                            <b-form-input :id="param" :type="reducer.params[param].input_type"
                                                        :min="reducer.params[param].meta.minVal" :max="reducer.params[param].meta.maxVal" :step="reducer.params[param].meta.step"
                                                        v-model="emb.reducer.params[param].value"></b-form-input>
                                            <b-input-group-append is-text class="text-monospace">{{ emb.reducer.params[param].value }}</b-input-group-append>
                                        </b-input-group>

                                    </b-card-text>
                                </b-tab>
                            </b-tabs>
                        </b-card>
                    </b-tab>

                    <template #empty>
                        <div class="text-center text-muted">
                            There are no embedders attached 🤷<br>
                            Add one by dragging the above badges here.
                        </div>
                    </template>
                </b-tabs>
            </b-card>

            <template #overlay>
                <div class="text-center">
                    <b-spinner
                        variant="success"
                        class="mb-3 mt-3"
                    ></b-spinner>

                    <b-progress :max="total" show-progress striped animated class="mb-2 mt-2 w-75 mx-auto">
                        <b-progress-bar :value="progress" variant="success"></b-progress-bar>
                    </b-progress>

                    <p id="cancel-label">Running feature extraction...</p>
                    <b-button
                        ref="cancel"
                        variant="outline-danger"
                        size="sm"
                        aria-describedby="cancel-label"
                        @click="cancelProcess(false)"
                    >
                        Cancel
                    </b-button>
                </div>
            </template>

        </b-overlay>

        <b-row align-h="center">
            <b-button @click="post" variant="outline-primary" class="mt-2" :disabled="working">🚀 Extract all</b-button>
        </b-row>

    </b-container>
</template>

<script>
import axios from 'axios'

export default {
    name: 'Embedder',

    props: ['id', 'total'],

    data() {
        return {
            embedders: [],
            reducers: [],

            model: {
                name: '',
                file: null
            },

            task: {},
            working: false,

            progress: 0,
            intervalID: null,

            embedderSelection: [],
            tabCounter: 0,

            csrf: document.querySelector('#csrf').value
        }
    },

    async created() {
        await axios.get('api/embedders').then(response => {
            this.embedders = response.data.embedders
            this.reducers = response.data.reducers
        })
    },
    methods: {
        post() {   
            let data = this.dispatch();

            axios.post(`api/${this.id}/embedders`, data, {headers: {"X-CSRFToken": this.csrf}})
                .then(resp => {
                    this.task = resp.data.task;

                    if (!this.task) {
                        this.cancelProcess();
                        this.$bvToast.toast('Embedder config exists', {
                            title: '❗ Warning',
                            autoHideDelay: 3000,
                            variant: 'danger',
                            solid: true,
                            appendToast: true
                        })
                    }

                })

            this.working = true;

            this.$nextTick( function () {
                this.intervalID = window.setInterval(() => {
                    axios.get(`/api/progress/${this.task.embeddingJob}`).then(resp => {
                        this.progress = resp.data.progress
                    })
                    if (this.progress === this.total) this.cancelProcess(true);
                }, 5000);
            })
            
        },

        dispatch() {
            let result = this.embedderSelection.map(embedder => {
                let embedderParams = {}
                let reducerParams = {}
                
                for (const param in embedder.params){
                    embedderParams[param] = embedder.params[param].value
                }

                for (const param in embedder.reducer.params){
                    reducerParams[param] = embedder.reducer.params[param].value
                }

                return {name: embedder.name, params: embedderParams,
                        reducer: {name: embedder.reducer.name, params: reducerParams}}
            })

            return result
        },

        addReducer: embedder => embedder.reducer.active = true,
        removeReducer: embedder => embedder.reducer.active = false,

        newTab(name) {
            if (this.embedderSelection.map(emb => emb.name).includes(name)) return;
            let embedder = this.embedders.find(emb => emb.name === name);
            embedder.reducer = this.reducers[0]
            this.embedderSelection.push(embedder);
        },

        isLast(name) {
            return this.embedderSelection.map(emb => emb.name).indexOf(name) === this.embedderSelection.length - 1
        },

        closeTab(name) {
            let idx = this.embedderSelection.map(emb => emb.name).indexOf(name);
            this.embedderSelection.splice(idx, 1)
        },

        dragStart(event) {
            event.dataTransfer.setData('name', event.target.id);
        },

        dragging:function(event) {
            event.preventDefault();
        },

        drop(event) {
            event.preventDefault();
            let name = event.dataTransfer.getData('name');
            
            this.newTab(name);

        },

        allowDrop(event) {
            event.preventDefault();
        },

        makeFile(){
            let data = new FormData()
            data.append('name', this.model.name)
            data.append('file', this.model.file)
            data.append('embedders', JSON.stringify(this.embedderSelection))
        },
        
        getProgress() {
            axios.get('/api/progress')
        },

        cancelProcess(success) {
            clearInterval(this.intervalID)
            this.intervalID = null;
            this.working = false;

            if (success){
                this.$bvToast.toast('Feature extraction complete', {
                    title: '✅ Success',
                    autoHideDelay: 3000,
                    variant: 'success',
                    solid: true,
                    appendToast: true
                })
            }
        }
    }
}
</script>

<style scoped>
    .embedder {
        position: fixed;
        width: 45vw;
    }
</style>